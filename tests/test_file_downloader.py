import unittest
from mypackages.file_downloader import GenericDownloader
from mypackages.downloader_details import Status, UrlInfo
from mypackages.downloaders import HttpDownloader, FtpDownloader, SftpDownloader

class TestHttpFileDownloader(unittest.TestCase):
    def setUp(self):
        self.httpOutputFile = '.\\tests\\outputs\\test_http_download.jpg'
        self.chunkSize = 8192
        self.timeout=60.0

    def test_http_file_download_success(self):
        url = 'https://i.imgur.com/slmM8rc.jpg'

        urlInfo = UrlInfo(url)
        urlInfo.inputUrl='https://i.imgur.com/slmM8rc.jpg' 

        downloader = HttpDownloader(chunkSize=self.chunkSize, timeout=self.timeout)
        result, str = downloader.download(urlInfo, self.httpOutputFile)
        self.assertEqual(result, True)

class TestFtpFileDownloader(unittest.TestCase):
    def setUp(self):
        self.ftpOutputFile = '.\\tests\\outputs\\test_ftp_download.zip'
        self.sftpOutputFile = '.\\tests\\outputs\\test_sftp_download.zip'
        self.chunkSize = 8192
        self.timeout= 60.0

        self.ftpUrl = 'ftp://speedtest.tele2.net/512KB.zip'
        self.ftpUrlInfo = UrlInfo(self.ftpUrl)
        self.ftpUrlInfo.isValid=True
        self.ftpUrlInfo.message=''
        self.ftpUrlInfo.port=0
        self.ftpUrlInfo.outputFilename='512KB'
        self.ftpUrlInfo.outputFilenameExtension='zip'
        self.ftpUrlInfo.outputFilenameSuffix=''
        self.ftpUrlInfo.scheme='ftp'
        self.ftpUrlInfo.netloc='speedtest.tele2.net'
        self.ftpUrlInfo.hostname='speedtest.tele2.net'
        self.ftpUrlInfo.path='/512KB.zip'
        self.ftpUrlInfo.username = ''
        self.ftpUrlInfo.password = ''
        self.ftpUrlInfo.dirName = ''

        self.sftpUrl = 'sftp://demo-user:demo-user@demo.wftpserver.com:2222/download/manual_en.pdf'
        self.sftpUrlInfo = UrlInfo(self.sftpUrl)
        self.sftpUrlInfo.isValid=True
        self.sftpUrlInfo.message=''
        self.sftpUrlInfo.port=2222
        self.sftpUrlInfo.outputFilename='manual_en'
        self.sftpUrlInfo.outputFilenameExtension='pdf'
        self.sftpUrlInfo.outputFilenameSuffix=''
        self.sftpUrlInfo.scheme='sftp'
        self.sftpUrlInfo.netloc='demo-user:demo-user@demo.wftpserver.com:2222'
        self.sftpUrlInfo.hostname='demo.wftpserver.com'
        self.sftpUrlInfo.path='/download/manual_en.pdf'
        self.sftpUrlInfo.username = 'demo-user'
        self.sftpUrlInfo.password = 'demo-user'
        self.sftpUrlInfo.dirName = '/download'

    def test_ftp_download_success(self):
        downloader = FtpDownloader(chunkSize=self.chunkSize, timeout=self.timeout)
        result, str = downloader.download(self.ftpUrlInfo, self.ftpOutputFile)
        self.assertEqual(result, True)
    
    def test_ftp_download_file_not_found(self):
        downloader = FtpDownloader(chunkSize=self.chunkSize, timeout=self.timeout)

        self.ftpUrl = 'ftp://speedtest.tele2.net/not_found.zip'
        self.ftpUrlInfo.outputFilename = 'not_found'

        result, str = downloader.download(self.ftpUrlInfo, self.ftpOutputFile)
        self.assertEqual(result, False)
    
    def test_sftp_download_success(self):
        downloader = SftpDownloader(chunkSize=self.chunkSize, timeout=self.timeout)
        result, str = downloader.download(self.sftpUrlInfo, self.sftpOutputFile)
        self.assertEqual(result, True)
    
    def test_sftp_auth_failure(self):
        downloader = SftpDownloader(chunkSize=self.chunkSize, timeout=self.timeout)
        self.sftpUrlInfo.password = 'invalid password'
        result, str = downloader.download(self.sftpUrlInfo, self.sftpOutputFile)
        self.assertEqual(result, False)

    def test_sftp_invalid_path(self):
        downloader = SftpDownloader(chunkSize=self.chunkSize, timeout=self.timeout)
        self.sftpUrlInfo.dirName = '/invalid_path'
        result, str = downloader.download(self.sftpUrlInfo, self.sftpOutputFile)
        self.assertEqual(result, False)

class TestGenericDownloader(unittest.TestCase):
    def setUp(self):
        self.outputDir = '.\\tests\\outputs'

    def test_parse_http_url_success(self):
        url = 'https://i.imgur.com/slmM8rc.jpg'
        urlInfo = GenericDownloader.parseUrl(url)
        urlInfo.outputFilenameSuffix = ''

        expectedUrlInfo = UrlInfo(url)
        expectedUrlInfo.inputUrl='https://i.imgur.com/slmM8rc.jpg' 
        expectedUrlInfo.isValid=True
        expectedUrlInfo.message=''
        expectedUrlInfo.port=0
        expectedUrlInfo.outputFilename='slmM8rc'
        expectedUrlInfo.outputFilenameExtension='jpg'
        expectedUrlInfo.outputFilenameSuffix=''
        expectedUrlInfo.scheme='https'
        expectedUrlInfo.netloc='i.imgur.com'
        expectedUrlInfo.hostname='i.imgur.com'
        expectedUrlInfo.path='/slmM8rc.jpg'
        expectedUrlInfo.params=''
        expectedUrlInfo.query=''
        expectedUrlInfo.fragment=''
        expectedUrlInfo.username=None
        expectedUrlInfo.password=None
        expectedUrlInfo.dirName=''

        self.assertEqual(urlInfo, expectedUrlInfo)

    def test_parse_http_url_invalid(self):
        url = 'INVALID_URL'
        urlInfo = GenericDownloader.parseUrl(url)
        self.assertEqual(urlInfo.isValid, False)

    def test_parse_ftp_url_anon_success(self):
        url = 'ftp://speedtest.tele2.net/512KB.zip'
        urlInfo = GenericDownloader.parseUrl(url)
        urlInfo.outputFilenameSuffix = ''

        expectedUrlInfo = UrlInfo(url)
        expectedUrlInfo.isValid=True
        expectedUrlInfo.message=''
        expectedUrlInfo.port=0
        expectedUrlInfo.outputFilename='512KB'
        expectedUrlInfo.outputFilenameExtension='zip'
        expectedUrlInfo.outputFilenameSuffix=''
        expectedUrlInfo.scheme='ftp'
        expectedUrlInfo.netloc='speedtest.tele2.net'
        expectedUrlInfo.hostname='speedtest.tele2.net'
        expectedUrlInfo.path='/512KB.zip'
        expectedUrlInfo.params=''
        expectedUrlInfo.query=''
        expectedUrlInfo.fragment=''
        expectedUrlInfo.username=None
        expectedUrlInfo.password=None
        expectedUrlInfo.dirName=''

        self.assertEqual(urlInfo, expectedUrlInfo)

    def test_parse_ftp_url_login_success(self):
        url = 'ftp://demo-user:demo-pass@speedtest.tele2.net:21/path/to/file/512KB.zip'

        urlInfo = GenericDownloader.parseUrl(url)
        urlInfo.outputFilenameSuffix = ''

        expectedUrlInfo = UrlInfo(url)
        expectedUrlInfo.isValid=True
        expectedUrlInfo.message=''
        expectedUrlInfo.port=21
        expectedUrlInfo.outputFilename='512KB'
        expectedUrlInfo.outputFilenameExtension='zip'
        expectedUrlInfo.outputFilenameSuffix=''
        expectedUrlInfo.scheme='ftp'
        expectedUrlInfo.netloc='demo-user:demo-pass@speedtest.tele2.net:21'
        expectedUrlInfo.hostname='speedtest.tele2.net'
        expectedUrlInfo.path='/path/to/file/512KB.zip'
        expectedUrlInfo.params=''
        expectedUrlInfo.query=''
        expectedUrlInfo.fragment=''
        expectedUrlInfo.username='demo-user'
        expectedUrlInfo.password='demo-pass'
        expectedUrlInfo.dirName='/path/to/file'

        self.assertEqual(urlInfo, expectedUrlInfo)
    
    def test_clean_urls_lists(self):
        urlsList = [' https://i.imgur.com/mINAmnD.gifv   ','',' https://i.imgur.com/Zd2ybNv.png', 'https://i.imgur.com/Zd2ybNv.png']
        cleanUrlsList = GenericDownloader.cleanUrlsList(urlsList)
        expectedUrlList = ['https://i.imgur.com/Zd2ybNv.png', 'https://i.imgur.com/mINAmnD.gifv']
        self.assertEqual(cleanUrlsList, expectedUrlList)
    
    def test_parse_input_sourcses_success(self):
        pathToInput = '.\\tests\\data\\nonstandard_input_format.in'
        urlsList = GenericDownloader.parseInputSources(pathToInput, ',')
        expectedUrlsList = ['', ' https://i.imgur.com/Zd2ybNv.png', 'https://i.imgur.com/SnRktzt.gifv', 'https://i.imgur.com/mINAmnD.gifv', 'https://i.imgur.com/slmM8rc.jpg']
        self.assertEqual(urlsList, expectedUrlsList)
    
    def test_parse_input_sources_not_found(self):
        pathToInvalidInput = '.\\path\\to\\not_found.in'
        with self.assertRaises(FileNotFoundError):
            GenericDownloader.parseInputSources(pathToInvalidInput, ',')
    
    def test_parse_input_sources_invalid_input_source_parameter(self):
        with self.assertRaises(ValueError):
            GenericDownloader.parseInputSources('', ',')

    def test_input_filepath_not_found(self):
        with self.assertRaises(FileNotFoundError):
            GenericDownloader.fromInputFile(numThreads=1, sourceList = '.\\does_not_exist.in', sourceListDelimiter=',', destination=self.outputDir)

    def test_input_filepath_empty(self):
        with self.assertRaises(ValueError):
            GenericDownloader.fromInputFile(numThreads=1, sourceList = '', destination=self.outputDir)

    def test_output_filepath_empty(self):
        with self.assertRaises(ValueError):
            GenericDownloader.fromInputFile(numThreads=1, sourceList = '.\\tests\\data\\https_success.in', destination='')
 
    def test_empty_input_file(self):
        with self.assertRaises(ValueError):
            GenericDownloader.fromInputFile(numThreads=1, sourceList = '.\\tests\\data\\empty.in', destination=self.outputDir)

    def test_empty_urls_list(self):
        with self.assertRaises(ValueError):
            GenericDownloader.fromList(numThreads=1, urlsList=[], destination=self.outputDir)

    def test_unsupported_protocol(self):
        urlsList = ['file://path/to/file.txt']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.FAILURE)
      
    def test_https_downloader_success(self):
        urlsList = ['https://i.imgur.com/slmM8rc.jpg']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.SUCCESS)

    def test_https_downloader_failure(self):
        urlsList = ['https://i.imgur.com/slsdjfldjfl.jpg']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.FAILURE)

    def test_https_downloader_warning(self):
        urlsList = ['https://i.imgur.com/slmM8rc.jpg','https://i.imgur.com/sldjflsdjfs.jpg']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.WARNING)
    
    def test_ftp_anon_downloader_success(self):
        urlsList = ['ftp://speedtest.tele2.net/512KB.zip']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.SUCCESS)

    def test_ftp_anon_downloader_file_not_found(self):
        urlsList = ['ftp://speedtest.tele2.net/path/to/file/512KB.zip']
        downloader = GenericDownloader.fromList(numThreads=1,  urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.FAILURE)

    def test_ftp_login_success(self):
        urlsList = ['ftp://demo-user:demo-user@demo.wftpserver.com:21/download/manual_en.pdf']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.SUCCESS)

    def test_ftp_login_auth_failure(self):
        urlsList = ['ftp://invalid-user:invalid-pass@demo.wftpserver.com:21/download/manual_en.pdf']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.FAILURE)

    def test_sftp_success(self):
        urlsList = ['sftp://demo-user:demo-user@demo.wftpserver.com:2222/download/manual_en.pdf']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.SUCCESS)

    def test_sftp_auth_failure(self):
        urlsList = ['sftp://invalid-user:invalid-pass@demo.wftpserver.com:2222/download/manual_en.pdf']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.FAILURE)

    def test_nonstandard_input_format_from_list(self):
        urlsList = [' https://i.imgur.com/mINAmnD.gifv   ','',' https://i.imgur.com/Zd2ybNv.png']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.SUCCESS)
    
    
    def test_nonstandard_input_format_from_input_file(self):
        downloader = GenericDownloader.fromInputFile(numThreads=1, sourceList='.\\tests\\data\\nonstandard_input_format.in', sourceListDelimiter=',', destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.SUCCESS)

if __name__ == '__main__':
    unittest.main()