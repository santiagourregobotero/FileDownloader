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
from .downloader_details import DownloaderDetails
from .downloaders import FtpDownloader, HttpDownloader, SftpDownloader

logging.config.fileConfig('./config/logging.conf')
logger = logging.getLogger('fileDownloader')

class GenericDownloader:

    downloaders = {}
        
    def __init__(self, urlsList, numThreads = 5, destination = '', chunkSize=8192, timeout=60.0):
        
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
    def fromList(cls, urlsList, numThreads = 5, destination = '', chunkSize = 8192):
        return cls(urlsList, numThreads, destination, chunkSize)

    @classmethod
    def fromInputFile(cls, sourceList, sourceListDelimiter, numThreads = 5, destination = '', chunkSize = 8192):
        urlsList = GenericDownloader.parseInputSources(sourceList, sourceListDelimiter)
        return cls(urlsList, numThreads, destination, chunkSize)
    
    def downloadFile(self, url, threadId):        
        logger.info('[%s]Downloading URL:%s',threading.get_ident(), url)

        urlInfo = GenericDownloader.parseUrl(url)

        if not urlInfo[DownloaderDetails.isValidKey]:
            self.handleDownloadResult(url, False, 'Invalid URL')
            return False
        
        scheme = urlInfo[DownloaderDetails.schemeKey]
        if scheme not in GenericDownloader.downloaders:
            self.handleDownloadResult(url, False, 'Protocol mising or not supported')
            return False

        outputFile = self.outputDir
        outputFile = outputFile + urlInfo[DownloaderDetails.outputFilenameKey] + '_' + urlInfo[DownloaderDetails.outputFilenameSuffixKey] + '.' + urlInfo[DownloaderDetails.outputExtensionKey]
        myFile = Path(outputFile)
        result, msg = GenericDownloader.downloaders[scheme].download(urlInfo, outputFile)
        self.handleDownloadResult(url, result, msg, outputFile)

        #if the downloaded failed then delete the partial file
        if not result and myFile.exists():
            myFile.unlink()

        return True

    def handleDownloadResult(self, url, result, msg, outputFile=''):
        resultObj = {
            DownloaderDetails.urlKey: url,
            DownloaderDetails.msgKey: msg,
            DownloaderDetails.outputKey: outputFile,
            'status': result
        }

        threadId = threading.get_ident()

        if result:
            self.successes.append(resultObj)
            logger.info('[%s]SUCCESS:%s', threadId, url)
        else:
            self.failures.append(resultObj)
            logger.error('[%s]FAILURE:%s', threadId, url)
    
    def startDownloads(self):        
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
            return DownloaderDetails.Status.SUCCESS

        if len(self.failures) == len(self.downloadsList):
            return DownloaderDetails.Status.FAILURE
        
        return DownloaderDetails.Status.WARNING
        
    def registerDownloader(self, id, downloader):
            GenericDownloader.downloaders[id] = downloader

    @staticmethod
    def parseUrl(url):
        results = {}        
        results[DownloaderDetails.inputUrlKey] = url
        results[DownloaderDetails.isValidKey] = True
        results[DownloaderDetails.messageKey] = ''
        results[DownloaderDetails.outputFilenameKey] = ''
        results[DownloaderDetails.outputFilenameSuffixKey] = str(time.time())
        results[DownloaderDetails.outputExtensionKey] = ''
        
        try:
            o = urlparse(url)

            #check if scheme is empty, url can still be valid.
            #(e.g. www.test.com/file.ext)
            results[DownloaderDetails.schemeKey] = o.scheme
            results[DownloaderDetails.netlocKey] = o.netloc
            results[DownloaderDetails.hostnameKey] = o.hostname
            results[DownloaderDetails.pathKey] = o.path
            results[DownloaderDetails.paramsKey] = o.params
            results[DownloaderDetails.queryKey] = o.query
            results[DownloaderDetails.fragmentKey] = o.fragment
            results[DownloaderDetails.portKey] = o.port
            results[DownloaderDetails.usernameKey] = o.username
            results[DownloaderDetails.passwordKey] = o.password

            if results[DownloaderDetails.pathKey]:
                paths = results[DownloaderDetails.pathKey].split('/')
                filenameComponents = paths[-1].split('.')
                results[DownloaderDetails.dirKey] = '/'.join(paths[:-1])
                if len(filenameComponents) == 2:
                    results[DownloaderDetails.outputFilenameKey] = filenameComponents[0]
                    results[DownloaderDetails.outputExtensionKey] = filenameComponents[1]

        except ValueError:
            results[DownloaderDetails.isValidKey] = False
            results[DownloaderDetails.messageKey] = 'Unable to parse URL, due to format not matching Internet RFC standards'

        return results
        
    @staticmethod
    def initDownloaders(chunkSize, timeout):
        GenericDownloader.downloaders['https'] = HttpDownloader(chunkSize, timeout)
        GenericDownloader.downloaders['http'] = HttpDownloader(chunkSize, timeout)
        GenericDownloader.downloaders['ftp'] = FtpDownloader(chunkSize, timeout)
        GenericDownloader.downloaders['sftp'] = SftpDownloader(chunkSize, timeout)

    @staticmethod
    def parseInputSources(pathToFile, delimiter):
        with open(pathToFile, "r") as f:
            lines = f.readlines()

        urlList = set()
        for l in lines:
            sources = l.strip().split(delimiter)
            urlList.update(sources)
            
        return list(urlList)

    @staticmethod
    def cleanUrlsList(urlsList):
        urlSet = set()
        
        urls = [u.strip() for u in urlsList if u]
        urlSet.update(urls)

        return list(urlSet)

    @staticmethod
    def outputResults(outputFile, outputList):
        if len(outputList) == 0:
            return

        with(open(outputFile, 'w+')) as f:
            for o in outputList:
                line = ''
                if o['status']:
                    line = '{},{}'.format(o[DownloaderDetails.urlKey], o[DownloaderDetails.outputKey])
                else:
                    line = '{} - {}'.format(o[DownloaderDetails.urlKey], o[DownloaderDetails.msgKey])

                f.write(line + '\n')