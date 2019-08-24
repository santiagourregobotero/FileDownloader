#!/usr/bin/env python
# coding: utf-8

import threading
import time 
import os
import logging
import logging.config
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from collections import namedtuple
from typing import List
from .downloader_details import UrlInfo, Status, DownloadResult
from .downloaders import FtpDownloader, HttpDownloader, SftpDownloader

logging.config.fileConfig('./config/logging.conf')
logger = logging.getLogger('fileDownloader')

class GenericDownloader:

    downloaders = {}
        
    def __init__(self, urlsList: List[str], destination:str, numThreads:int = 5, chunkSize:int = 8192, timeout:float = 60.0):
        
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
    def fromList(cls, urlsList:list, destination:str, numThreads:int = 5, chunkSize:int = 8192):
        return cls(urlsList=urlsList, numThreads=numThreads, destination=destination, chunkSize=chunkSize)

    @classmethod
    def fromInputFile(cls, sourceList:str, destination:str, sourceListDelimiter:str = ',', numThreads:int = 5, chunkSize:int = 8192):
        urlsList = GenericDownloader.parseInputSources(sourceList, sourceListDelimiter)
        return cls(urlsList=urlsList, numThreads=numThreads, destination=destination, chunkSize=chunkSize)
    
    def downloadFile(self, url:str, threadId:int) -> bool:        
        logger.info('[%s]Downloading URL:%s',threading.get_ident(), url)

        urlInfo = GenericDownloader.parseUrl(url)

        if not urlInfo.isValid:
            self.handleDownloadResult(url, False, 'Invalid URL')
            return False
        
        scheme = urlInfo.scheme
        if scheme not in GenericDownloader.downloaders:
            self.handleDownloadResult(url, False, 'Protocol mising or not supported')
            return False

        outputFile = self.buildOutputFileFromUrl(urlInfo)
        result, msg = GenericDownloader.downloaders[scheme].download(urlInfo, outputFile)
        self.handleDownloadResult(url, result, msg, outputFile)

        myFile = Path(outputFile)
        if not result and myFile.exists():
            myFile.unlink()

        return True

    def buildOutputFileFromUrl(self, urlInfo:UrlInfo) -> str:
        outputFile = self.outputDir + urlInfo.outputFilename + '_' + urlInfo.outputFilenameSuffix + '.' + urlInfo.outputFilenameExtension
        return outputFile

    def handleDownloadResult(self, url:str, result:bool, msg:str, outputFile:str='') -> None:
        downloadResult = DownloadResult(url=url, msg=msg, output=outputFile, status=result)

        threadId = threading.get_ident()

        if result:
            self.successes.append(downloadResult)
            logger.info('[%s]SUCCESS:%s', threadId, url)
        else:
            self.failures.append(downloadResult)
            logger.info('[%s]FAILURE:%s', threadId, url)
    
    def startDownloads(self) -> Status:        
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
        
    def registerDownloader(self, id:str, downloader) -> None:
        GenericDownloader.downloaders[id] = downloader

    @staticmethod
    def parseUrl(url:str) -> UrlInfo:
        try:
            urlInfo = UrlInfo(url)
            if urlInfo.path:
                paths = urlInfo.path.split('/')
                filenameComponents = paths[-1].split('.')
                urlInfo.dirName = '/'.join(paths[:-1])
                if len(filenameComponents) == 2:
                    urlInfo.outputFilename = filenameComponents[0]
                    urlInfo.outputFilenameExtension = filenameComponents[1]

        except ValueError:
            urlInfo.isValid = False
            urlInfo.message = 'Unable to parse URL, due to format not matching Internet RFC standards'

        return urlInfo
        
    @staticmethod
    def initDownloaders(chunkSize, timeout):
        GenericDownloader.downloaders['https'] = HttpDownloader(chunkSize, timeout)
        GenericDownloader.downloaders['http'] = HttpDownloader(chunkSize, timeout)
        GenericDownloader.downloaders['ftp'] = FtpDownloader(chunkSize, timeout)
        GenericDownloader.downloaders['sftp'] = SftpDownloader(chunkSize, timeout)

    @staticmethod
    def parseInputSources(pathToFile, delimiter):
        if not pathToFile:
            raise ValueError('Empty input parameter for the path/to/input_source_list')

        with open(pathToFile, "r") as f:
            lines = f.readlines()

        urlSet = set()
        for l in lines:
            sources = l.strip().split(delimiter)
            urlSet.update(sources)
            
        return list(urlSet)

    @staticmethod
    def cleanUrlsList(urlsList):
        urlSet = set()
        
        urls = [u.strip() for u in urlsList if u]
        urlSet.update(urls)

        return list(urlSet)

    @staticmethod
    def outputResults(outputFile:str, outputList: List[DownloadResult]):
        if len(outputList) == 0:
            return

        with(open(outputFile, 'w+')) as f:
            for o in outputList:
                line = '{},{}'.format(o.url, o.output) if o.status else '{} - {}'.format(o.url, o.msg)
                f.write(line + '\n')