import requests 
import ftplib
import paramiko
import logging
from .downloader_details import UrlInfo, Status

logger = logging.getLogger(__name__)

class BaseDownloader:
    success = 'success'
    def __init__(self, chunkSize: int, timeout: float):
        self.chunkSize = chunkSize
        self.timeout = timeout

    def download(self, urlInfo: UrlInfo, outputFile: str) -> (bool, str): pass

class SftpDownloader(BaseDownloader):
    def download(self, urlInfo: UrlInfo, outputFile: str) -> (bool, str):
        try:
            dirToFetch = urlInfo.dirName
            fileToFetch = urlInfo.outputFilename + '.' + urlInfo.outputFilenameExtension

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=urlInfo.hostname, port=urlInfo.port, username=urlInfo.username, password=urlInfo.password, timeout=self.timeout)

            with (ssh_client.open_sftp()) as sftp_client:
                sftp_client.get_channel().settimeout(self.timeout)
                sftp_client.get(dirToFetch  + '/' + fileToFetch, outputFile)

            return True, BaseDownloader.success 
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException, paramiko.SSHException, IOError) as e:
            logging.exception('Error occurred while downloading via sftp: %s', urlInfo.inputUrl)
            return False, str(e)

class HttpDownloader(BaseDownloader):
    def download(self, urlInfo: UrlInfo, outputFile: str) -> (bool, str):
        try:
            with requests.get(urlInfo.inputUrl, timeout=self.timeout, stream=True) as r:
                r.raise_for_status()
                with open(outputFile, 'wb') as f:
                    for chunk in r.iter_content(chunk_size = self.chunkSize):
                        if chunk:
                            f.write(chunk)
            
            return True, BaseDownloader.success
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            logging.exception('Error occurred while downloading url: %s', urlInfo.inputUrl)
            return False, str(e)
        

class FtpDownloader(BaseDownloader):
    def download(self, urlInfo: UrlInfo, outputFile: str) -> (bool, str):
        try:
            fileToFetch = urlInfo.outputFilename + '.' + urlInfo.outputFilenameExtension
            with ftplib.FTP() as ftp:
                ftp.connect(host=urlInfo.hostname, port=urlInfo.port, timeout=self.timeout)
                ftp.login(urlInfo.username, urlInfo.password)
                ftp.cwd(urlInfo.dirName)
                with open(outputFile, 'wb') as op:
                    ftp.retrbinary('RETR ' + fileToFetch, op.write, blocksize=self.chunkSize)
            return True, BaseDownloader.success
        except ftplib.all_errors as e:
            logging.exception('Error occurred while downloading via ftp: %s', urlInfo.inputUrl)
            return False, str(e)