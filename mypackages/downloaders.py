import requests 
import ftplib
import paramiko
from .downloader_details import DownloaderDetails

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