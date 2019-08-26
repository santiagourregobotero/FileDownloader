#!/usr/bin/env python
# coding: utf-8

import threading
import os
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List
from .downloader_details import UrlInfo, Status, DownloadResult
from .downloaders import FtpDownloader, HttpDownloader, SftpDownloader

logger = logging.getLogger(__name__)

class GenericDownloader:
    downloaders = {}
        
    def __init__(self, urlsList: List[str], destination:str, numThreads:int = 5, chunkSize:int = 8192, timeout:float = 60.0):
        """Will take the list of url inputs as specified as by the parameter urlsList and will attempt to download each of them.
        The downloader can download multiple files in parallel, by default, it's set to download 5 files in parallel but it can 
        be changed via numThreads parameter.  The output file will be saved in the location specified by the destination parameter.
        If the destination folder does not exist, the download will attemp to create it.

        Args:
            urlsList (List[str]): List of urls to be downloaded.  
            destination (str): path/to/output directory for where all downloaded files should be saved to.
            numThreads (int, optional): Determines how many files to download in parallel
            chunkSize (int, optional): Determines the number of bytes to download at a time for a single file.
            timeout (float, optioan): Sets the timeout limit for waiting for a connection or for waiting for any activitiy from the server

        Raises:
            ValueError: If parameters urlsList or destination is empty
            OSError: If destination directory is invalid, or inaccessible
        """
        if not urlsList or not destination:
            raise ValueError('Required params are missing or empty: urlsList or destination')
        
        GenericDownloader.initDownloaders(chunkSize, timeout)

        self.numThreads = numThreads
        self.outputDir = destination
        self.downloadsList = GenericDownloader.cleanUrlsList(urlsList)
        self.successes = []
        self.failures = []

        if not self.outputDir.endswith('\\'):
            self.outputDir = self.outputDir + '\\'

        if not Path(self.outputDir).exists():
            logger.debug('Attempting to create output dir: %s', self.outputDir)
            os.makedirs(self.outputDir)

    @classmethod
    def fromList(cls, urlsList: List[str], destination: str, numThreads: int = 5, chunkSize: int = 8192, timeout: float = 60.0):
        """Factory method that creates an instance of GenericDownloader class given a List of URLs as input.

        Args:
            urlsList (List[str]): List of urls to be downloaded.  Supported URLs are (http, https, ftp, sftp)
            destination (str): path/to/output directory for where all downloaded files should be saved to.
            numThreads (int, optional): Determines how many files to download in parallel
            chunkSize (int, optional): Determines the number of bytes to download at a time for a single file.
            timeout (float, optioan): Sets the timeout limit for waiting for a connection or for waiting for any activitiy from the server

        Returns: 
            GenericDownloader instance

        Raises:
            ValueError: If parameters urlsList or destination is empty
            OSError: If destination directory is invalid, or inaccessible
        """
        return cls(urlsList=urlsList, numThreads=numThreads, destination=destination, chunkSize=chunkSize, timeout=timeout)

    @classmethod
    def fromInputFile(cls, sourceList: str, destination: str, sourceListDelimiter: str = None, numThreads: int = 5, chunkSize: int = 8192, timeout: float = 60.0):
        """Factory method that creates in instance of GenericDownloader class given a path to an input file consisting of URLs list
        
        Args:
            sourceList (str): /path/to/input_file  where the contents of the file should list urls per line.  
                You can have multiple urls per line separated by a delimiter specified by sourceListDelimiter
            destination (str): path/to/output directory for where all downloaded files should be saved to.
            sourceListDelimiter (str, optional): If the input file contains multiple urls per line, they can 
                also be parsed by specifying the delimiter with the sourceListDelimiter parameter
            numThreads(int, optional): Determines how many files to download in parallel
            chunkSize(int, optional): Determines the number of bytes to download at a time for a single file.
            timeout(float, optioan): Sets the timeout limit for waiting for a connection or for waiting for 
                any activitiy from the server

        Returns: 
            GenericDownloader instance

        Raises:
            ValueError: If parameters urlsList or destination is empty
            OSError: If destination directory is invalid, or inaccessible
            FileNotFoundError: If the file specified by 'pathToFile' does not exist
        """
        urlsList = GenericDownloader.parseInputSources(sourceList, sourceListDelimiter)
        return cls(urlsList=urlsList, numThreads=numThreads, destination=destination, chunkSize=chunkSize, timeout=timeout)

    def startDownloads(self) -> Status:
        """Will start the download process for all the URLs in the downloadList property of the class.

        Returns:
            SUCCESS (DownloaderDetails.Status): If every URL in the downloadList were successful.
            WARNING (DownloaderDetails.Status): If the downloadList had partial success
            FAILURE (DownloaderDetails.Status): If all URLs from the downloadList failed.
        """      
        numDownlaods = len(self.downloadsList)
        logger.info('Number of Downloads: %s', str(len(self.downloadsList)))

        with ThreadPoolExecutor(max_workers=self.numThreads) as executor:
            for index, url in enumerate(self.downloadsList):
                executor.submit(self.downloadFile, url, index)
        
        GenericDownloader.outputResults(self.outputDir + 'downloads.error', self.failures)
        GenericDownloader.outputResults(self.outputDir + 'downloads.map', self.successes)

        logger.info('Failed: %s', str(len(self.failures)))
        logger.info('Success: %s', str(len(self.successes)))

        if len(self.successes) == numDownlaods:
            return Status.SUCCESS

        if len(self.failures) == len(self.downloadsList):
            return Status.FAILURE
        
        return Status.WARNING
    
    def downloadFile(self, url: str, threadId: int = 0) -> bool:  
        """Download the file specified by the URL.  Records more details of a failure
        int the failures list.  If the download fails midway, the partially downloaded file 
        will be deleted.

        Args:
            url (str): URL to be downloaded.
            threadId(int, optional): Used to give an Id by the calling code, if it's being called by 
                a threadpool

        Returns:
            True (bool): If the file downloaded successfully
            False (bool): If the file failed to download
        """      
        logger.info('[%s]Downloading URL:%s',threading.get_ident(), url)

        urlInfo = GenericDownloader.parseUrl(url)

        if not urlInfo.isValid:
            self.handleDownloadResult(url, False, 'Invalid URL: {}'.format(urlInfo.message))
            return False
        
        scheme = urlInfo.scheme
        if scheme not in GenericDownloader.downloaders:
            self.handleDownloadResult(url, False, 'Protocol mising or not supported')
            return False

        outputFile = GenericDownloader.buildOutputFileFromUrl(self.outputDir, urlInfo)
        result, msg = GenericDownloader.downloaders[scheme].download(urlInfo, outputFile)
        self.handleDownloadResult(url, result, msg, outputFile)
        return True

    def handleDownloadResult(self, url: str, result: bool, msg: str, outputFile: str = '') -> None:
        """Records the status of a download along with any relevant messages.  Successful downloads
        is stored in the successes member variable and failures are stored in the failures member
        variable.

        Args:
            url (str): The download result of the url specified by this parameter
            result (bool): Whether the download was successful or not
            msg (bool): Any relevant message associated with the download process
            outputFile (str): If the download was a success, this parameter will store the
                path of where downloaded file.
        """
        downloadResult = DownloadResult(url=url, msg=msg, output=outputFile, status=result)

        threadId = threading.get_ident()

        if result:
            self.successes.append(downloadResult)
            logger.info('[%s]SUCCESS:%s', threadId, url)
        else:
            self.failures.append(downloadResult)
            logger.info('[%s]FAILURE:%s', threadId, url)

        
        logger.debug('[%s]%s - %s', threadId, url, downloadResult.msg)

        if outputFile and not result:
            myFile = Path(outputFile)
            if myFile.exists():
                logger.debug('Incomplete download found, deleting: %s', outputFile)
                myFile.unlink()
    
    def registerDownloader(self, id: str, downloader) -> None:
        """Add a custone URL to support

        Args:
            id (str): The id to represent what kind of URLs the API should support.  The id is 
                usually the URL protocol (e.g. for URL: https://somehost.com/file.ext, id: https)
        
            downlaoder (BaseDownload instance): Some class derived from downloaders.BaseDownloader and 
                implemented the download method
        """
        logger.debug('Adding new downloader: %s', id)
        GenericDownloader.downloaders[id] = downloader

    @staticmethod
    def buildOutputFileFromUrl(outputDir: str, urlInfo: UrlInfo) -> str:
        outputFile = outputDir + urlInfo.outputFilename + '_' + urlInfo.outputFilenameSuffix + '.' + urlInfo.outputFilenameExtension
        logger.debug('Output File: %s, URL: %s', outputFile, urlInfo.inputUrl)
        return outputFile

    @staticmethod
    def parseUrl(url: str) -> UrlInfo:
        """Parses the url into its invidual components.  It also uses the relevant parts of the URL to build the output filename

        Args:
            url (str): url to parse

        Returns:
            downloader_details.UrlInfo: Dataclass that encapsulates URL metadata as well as output filename metadata
        """
        urlInfo = UrlInfo(url)

        try:
            urlInfo.parse()

            if urlInfo.path:
                paths = urlInfo.path.split('/')
                filenameComponents = paths[-1].split('.')
                urlInfo.dirName = '/'.join(paths[:-1])
                if len(filenameComponents) == 2:
                    urlInfo.outputFilename, urlInfo.outputFilenameExtension = filenameComponents[0], filenameComponents[1] 

        except ValueError as e:
            urlInfo.isValid = False
            urlInfo.message = str(e)

        return urlInfo
        
    @staticmethod
    def initDownloaders(chunkSize: int, timeout: float) -> None:
        GenericDownloader.downloaders['https'] = HttpDownloader(chunkSize, timeout)
        GenericDownloader.downloaders['http'] = HttpDownloader(chunkSize, timeout)
        GenericDownloader.downloaders['ftp'] = FtpDownloader(chunkSize, timeout)
        GenericDownloader.downloaders['sftp'] = SftpDownloader(chunkSize, timeout)

    @staticmethod
    def parseInputSources(pathToFile: str, delimiter: str = None) -> List[str]:
        """Reads the file specified by the pathToFile parameter line by line and returns
        a list of contents. If a line contains a delimited specified by the delimiter parameter
        the line is further split into multiple strings and is returned as a flat list.

        Args:
            pathToFile (str): The path of the file to be read.
            delimiter (str): The delimiter to further split any lines in multiple components.
                The is useful if a single line contains multiple components that needs to be 
                evaluated as a sinple compoenent.
        
        Returns:
            List[str]: List from each line of pathToFile contents and further elements if any 
                line contains a delimiter specified by the delimiter paramter.
        
        Raises:
            ValueError: If 'pathToFile' is empty
            FileNotFoundError: If the file specified by 'pathToFile' does not exist

        """
        if not pathToFile:
            raise ValueError('Missing required parameters: path/to/inputsources')

        with open(pathToFile, "r") as f:
            lines = f.readlines()

        urlSet = set()
        for l in lines:
            sources = l.strip().split(delimiter)
            urlSet.update(sources)
        
        urlsList = list(urlSet)
        urlsList.sort()
        return urlsList

    @staticmethod
    def cleanUrlsList(urlsList: List[str]) -> List[str]:
        """Cleans the list of URLs by removing any leading and trailing whitespace from the urls.  Also removes duplicates.

        Args:
            urlsList (List[str]): List of URLs to clean.

        Returns:
            List[str]: Sorted, unique list of URLs
        """
        urlSet = set()
        
        urls = [u.strip() for u in urlsList if u]
        urlSet.update(urls)

        cleanUrls = list(urlSet)
        cleanUrls.sort()

        return cleanUrls

    @staticmethod
    def outputResults(outputFile:str, outputList: List[DownloadResult]) -> None:
        if len(outputList) == 0:
            return

        with(open(outputFile, 'w+')) as f:
            for o in outputList:
                line = '{},{}'.format(o.url, o.output) if o.status else '{} - {}'.format(o.url, o.msg)
                f.write(line + '\n')