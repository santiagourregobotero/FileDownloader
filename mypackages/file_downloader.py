#!/usr/bin/env python
# coding: utf-8

import threading
import time 
import requests 
import ftplib
import paramiko
import sys, getopt
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from collections import namedtuple
from enum import Enum, unique

class DownloaderDetails:
    success = 'success'
    failure = 'failure'

    hostnameKey = 'hostname'
    portKey = 'port'
    usernameKey = 'username'
    passwordKey = 'password'
    isValidKey = 'isValid'
    schemeKey = 'scheme'
    pathKey = 'path'
    dirKey = 'dir'
    outputFilenameKey = 'outputFilename'
    outputExtensionKey = 'outputExtension'
    outputFilenameSuffixKey = 'outputFilenameSuffix'
    paramsKey = 'params'
    queryKey = 'query'
    netlocKey = 'netloc'
    fragmentKey = 'fragment'
    messageKey = 'message'
    inputUrlKey = 'inputUrl'
    urlKey = 'url'
    msgKey = 'msg'
    outputKey = 'output'

    @unique
    class Status(Enum):
        SUCCESS = 0,
        WARNING = 1,
        FAILURE = 2,
        INVALID_INPUT = 3,

class BaseDownloader:
    def download(self, urlInfo, outputFile, chunkSize): pass

class LocalFileDownloader(BaseDownloader):
    def download(self, urlInfo, outputFile, chunkSize): pass

class SftpDownloader(BaseDownloader):
    def download(self, urlInfo, outputFile, chunkSize):
        
        hostname = urlInfo[DownloaderDetails.hostnameKey]
        port = 0
        if urlInfo[DownloaderDetails.portKey]:
            port = urlInfo[DownloaderDetails.portKey]

        username = urlInfo[DownloaderDetails.usernameKey]
        password = urlInfo[DownloaderDetails.passwordKey]
        dirName = urlInfo[DownloaderDetails.dirKey]
        fileName = urlInfo[DownloaderDetails.outputFilenameKey] + '.' + urlInfo[DownloaderDetails.outputExtensionKey]
        
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=hostname, port=port, username=username, password=password, timeout=60)

            with (ssh_client.open_sftp()) as ftp_client:
                ftp_client.get(dirName  + '/' + fileName, outputFile)

            return True, DownloaderDetails.success 
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException,paramiko.SSHException) as e:
            return False, str(e)
  

class HttpDownloader(BaseDownloader):
    def download(self, urlInfo, outputFile, chunkSize):
        try:
            url = urlInfo[DownloaderDetails.inputUrlKey]
            with requests.get(url, stream=True) as r:
                
                r.raise_for_status()
                with open(outputFile, 'wb') as f:
                    for chunk in r.iter_content(chunk_size = chunkSize):
                        if chunk:
                            f.write(chunk)
                return True, DownloaderDetails.success
        except requests.exceptions.HTTPError as e:
            return False, str(e)
        except requests.exceptions.RequestException as e:
            return False, str(e)
        
class FtpDownloader(BaseDownloader):
    def download(self, urlInfo, outputFile, chunkSize):

        hostname = urlInfo[DownloaderDetails.hostnameKey]
        port = 0
        if urlInfo[DownloaderDetails.portKey]:
            port = urlInfo[DownloaderDetails.portKey]

        username = urlInfo[DownloaderDetails.usernameKey]
        password = urlInfo[DownloaderDetails.passwordKey]
        dirName = urlInfo[DownloaderDetails.dirKey]
        fileName = urlInfo[DownloaderDetails.outputFilenameKey] + '.' + urlInfo[DownloaderDetails.outputExtensionKey]

        try:
            with ftplib.FTP() as ftp:
                ftp.connect(host=hostname, port=port, timeout=60)
                ftp.login(username, password)
                ftp.cwd(dirName)
                with open(outputFile, 'wb') as op:
                    ftp.retrbinary('RETR ' + fileName, op.write, blocksize=chunkSize)
            return True, DownloaderDetails.success
        except ftplib.all_errors as e:
            return False, str(e)
        
class GenericDownloader:
        
    downloaders = {}
        
    def __init__(self, sourceList= "", numThreads = 5, destination = "", chunkSize=8192):
        GenericDownloader.initDownloaders()

        self.sourceList = sourceList
        self.numThreads = numThreads
        self.outputDir = destination
        self.chunkSize = chunkSize

        self.downloadsList = []
        self.successes = []
        self.failures = []

        if self.outputDir and not self.outputDir.endswith('\\'):
            self.outputDir = self.outputDir + '\\'
    
    def downloadFile(self, url, threadId):        
        print('[{}]Downloading URL:{}'.format(threading.get_ident(), url))

        #parses the url and returns True if the url is supported.
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
        result, msg = GenericDownloader.downloaders[scheme].download(urlInfo, outputFile, self.chunkSize)
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
            print('[{}]SUCCESS:{}'.format(threadId, url))
        else:
            self.failures.append(resultObj)
            print('[{}]FAILURE:{}'.format(threadId, url))

    def parseInputSources(self):
        pathToFile = self.sourceList
        delimiter = ','

        urlSet = set()
        try:
            with open(pathToFile, "r") as f:
                if (f.mode != 'r'):
                    print('Invalid source list file: {}'.format(pathToFile))
                    return False

                line = f.readline()

                while line:
                    if (not line):
                        continue
                    #strip any whitespace
                    stripped = line.strip()
                    #separate any sources by 'delimiter', in case there are multiple sources on a single line
                    sources = stripped.strip(delimiter).split(delimiter)
                    for s in sources:
                        if not s:
                            continue
                        s = s.strip()
                        urlSet.add(s)
                        
                    line = f.readline()
                
                self.downloadsList = list(urlSet)

                return True
        except FileNotFoundError:
            print('Input file not found: {}'.format(pathToFile))
            return False
    
    def validateInputs(self):
        if not self.sourceList or not self.outputDir:
            print('Required input params missing')
            return DownloaderDetails.Status.INVALID_INPUT
            
        if not Path(self.outputDir).exists():
            try:
                print('Attempting to create output dir: {}'.format(self.outputDir))
                os.makedirs(self.outputDir)
            except OSError as e:
                print('Failed to create directory {}:{}'.format(self.outputDir, str(e)))
                return DownloaderDetails.Status.INVALID_INPUT

        if not self.parseInputSources():
            print('Error parsing input source list: {}'.format(self.sourceList))
            return DownloaderDetails.Status.INVALID_INPUT

        return DownloaderDetails.Status.SUCCESS

    def startDownloads(self):

        validationStatus = self.validateInputs()
        if validationStatus != DownloaderDetails.Status.SUCCESS:
            return validationStatus 
        
        numDownlaods = len(self.downloadsList)
        print('Number of Downloads: {}'.format(len(self.downloadsList)))
        with ThreadPoolExecutor(max_workers=self.numThreads) as executor:
            for index, url in enumerate(self.downloadsList):
                executor.submit(self.downloadFile, url, index)
        
        self.outputResults(self.outputDir + 'downloads.error', self.failures)
        self.outputResults(self.outputDir + 'downloads.map', self.successes)

        print('Failed:{}'.format(len(self.failures)))
        print('Success:{}'.format(len(self.successes)))

        if len(self.successes) == numDownlaods:
            return DownloaderDetails.Status.SUCCESS

        if len(self.failures) == len(self.downloadsList):
            return DownloaderDetails.Status.FAILURE
        
        return DownloaderDetails.Status.WARNING
    
    def outputResults(self, outputFile, outputList):
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
    def initDownloaders():
        GenericDownloader.downloaders['https'] = HttpDownloader()
        GenericDownloader.downloaders['http'] = HttpDownloader()
        GenericDownloader.downloaders['ftp'] = FtpDownloader()
        GenericDownloader.downloaders['sftp'] = SftpDownloader()
        #GenericDownloader.downloaders['file'] = FileDownloader()

def main(argv):

    helpMsg = 'file_downloader.py -s <sourcelist> -d <destination> [-n <numthreads=5> -c <chunksize=1014>]'
    sourceList = ''
    destination = ''
    numThreads = 5
    chunkSize = 8192

    try:
        opts, args = getopt.getopt(argv, "hs:d:n:c:")
    except NameError as e:
        print(e)
        print(helpMsg)
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(helpMsg)
            sys.exit()
        elif opt in ('-s', '--sourcelist'):
            sourceList = arg
        elif opt in ('-d', '--destination'):
            destination = arg
        elif opt in ('-n', '--numthreads'):
            numThreads = arg

        elif opt in ('-c', '--chunksize'):
            chunkSize = arg
        else:
            print('Unrecognized argument: {}'.format(opt))
    
    if (not sourceList or not destination):
        print(helpMsg)
        sys.exit(2)

    downloader = GenericDownloader(sourceList=sourceList, numThreads=numThreads, destination=destination, chunkSize=chunkSize)
    #Testing adding a custom downloader
    downloader.registerDownloader('file', LocalFileDownloader())
    downloader.startDownloads()

    print('Done!')
    
if __name__ == "__main__":
    main(sys.argv[1:])