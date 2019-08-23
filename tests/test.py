import unittest
import importlib.util
spec = importlib.util.spec_from_file_location("file_downloader", "./../mypackages/file_downloader.py")
Downloader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Downloader)

class TestDownloader(unittest.TestCase):

    def test_input_filepath_not_found(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\does_not_exist.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.INVALID_INPUT)

    def test_input_filepath_empty(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.INVALID_INPUT)
    
    def test_unsupported_protocol(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\unsupported_protocol.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.FAILURE)

    def test_output_filepath_empty(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\https_success.in', destination='')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.INVALID_INPUT)

    def test_https_downloader_success(self):
        """
        Test the downloader can download an http file successfully
        """
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\https_success.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.SUCCESS)

    def test_https_downloader_failure(self):
        """
        Test the downloader http failure with an invalid URL that returns 404 - Not Found
        """
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\https_failure.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.FAILURE)

    def test_https_downloader_warning(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\https_warning.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.WARNING)
    
    def test_empty_input_file(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\empty.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.SUCCESS)

    def test_ftp_anon_downloader_success(self):
        """
        Test the downloader can download an ftp file successfully with anonymous login
        """
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\ftp_anon_success.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.SUCCESS)

    def test_ftp_anon_downloader_file_not_found(self):
        """
        Test the downloader can download an ftp file successfully with anonymous login
        """
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\ftp_anon_failure_file_not_found.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.FAILURE)

    def test_ftp_login_success(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\ftp_login_success.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.SUCCESS)

    def test_ftp_login_auth_failure(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\ftp_login_auth_failure.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.FAILURE)

    def test_sftp_success(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\sftp_success.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.SUCCESS)

    def test_sftp_auth_failure(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\sftp_auth_failure.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.FAILURE)

    def test_nonstandard_input_format(self):
        downloader = Downloader.GenericDownloader(numThreads=1, sourceList = '.\\data\\nonstandard_input_format.in', destination='.\\outputs')
        result = downloader.startDownloads()
        self.assertEqual(result, Downloader.DownloaderDetails.Status.SUCCESS)

if __name__ == '__main__':
    unittest.main()