import unittest
from mypackages.file_downloader import GenericDownloader
from mypackages.downloader_details import Status

class TestGenericDownloader(unittest.TestCase):
    def setUp(self):
        self.outputDir = '.\\tests\\outputs'

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
        """
        Test the downloader can download an http file successfully
        """
        urlsList = ['https://i.imgur.com/slmM8rc.jpg']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.SUCCESS)

    def test_https_downloader_failure(self):
        """
        Test the downloader http failure with an invalid URL that returns 404 - Not Found
        """
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
        """
        Test the downloader can download an ftp file successfully with anonymous login
        """
        urlsList = ['ftp://speedtest.tele2.net/512KB.zip']
        downloader = GenericDownloader.fromList(numThreads=1, urlsList=urlsList, destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.SUCCESS)

    def test_ftp_anon_downloader_file_not_found(self):
        """
        Test the downloader can download an ftp file successfully with anonymous login
        """
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
        downloader = GenericDownloader.fromInputFile(numThreads=1, sourceList='.\\tests\\data\\nonstandard_input_format.in', destination=self.outputDir)
        result = downloader.startDownloads()
        self.assertEqual(result, Status.SUCCESS)

if __name__ == '__main__':
    unittest.main()