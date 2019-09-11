# DESCRIPTION
Given an input file of urls or a list of urls, of a variety of protocols(https, ftp, http, sftp), this API will handing iterating through and downloading all urls from the input.  See below for a variety of features.

# REQUIREMENTS
- Python 3+ (preferably 3.7)
- pip install requests
- pip install paramiko

# USAGE
- cd /path/to/src/folder
- python /path/to/extracted_folder/main.py -s "/path/to/input_file_list.ext" -d "/path/to/outputs_folder" [-n 10 -c 8192 -t 60.0 -r "," -l "DEBUG"]
- DEFAULTS:  
    - n (int): 5  
    Numer of parallel downloads)
    - c (int): 8192  
    Max size (Bytes) of chunks to download files with  
    - t (float): 60.0  
    Max timeout to cut connection if there's no activity from the server
    - r (string): ,
    Delimiter to separate any urls that are on the same line.
    - l (string): INFO
    Debugging level.  Levels follow python logging (INFO, DEBUG, WARNING, CRITICAL).  See https://docs.python.org/3/library/logging.html  

# SOURCE LIST FORMATTER
The API supports the following standard protocols **(http, https, ftp, sftp)**. The source list format should be either delimited by the delimiter specified by the delimiter parameter or the per line or a combination of both.  

Note: You can have multiple URLs per line, but if a URL is truncated and is part of 2 separate lines, the URL won’t download properly  

Example format (w/ delimiter = ,):
```
<url1>
<url2>,
<url3>,<url4>,<url5>
<url6>
<url7>,<url8>
```

# STANDARD BEHAVIOR  
- The library will always run 10 threads (download 10 files in parallel) at a time unless overwritten via the -t parameter  

- The library will always download files in 8KB chunks to avoid potential memory issues when downloading very large files unless the chunk size is overridden via the -c parameter
- Duplicated URLs will be skipped  

- The library will automatically continue FTP downloads if internet connection gets disconnected but restored before the timeout cuts the connection  

- The library produces two metadata files for convenience.
    1. **downloads.map**: Shows all URLs that were successfully downloaded and their associated output file path
    2. **downloads.error**: Shows all URLs that failed, and the reason

# ADDING CUSTOM BEHAVIOR
You can register a custom protocol the API doesn't already support or overwrite the current ones with your own implementation.  The following steps are required:  
1. Create a class that inherits from BaseDownloader
2. Impelement the function: **download(self, urlInfo: UrlInfo, outputFile: str) -> (bool, str)**
3. Register the new protocol before you call **startDownloads()**
4. **UrlInfo** definition:  
    - inputUrl – The original URL  
    - isValid – returns if the URL was valid  
    - outputFilename – filename, usually parsed from the URL  
    - outputFilenameSuffix – A unique identifier  
    - outputExtension – File type, usually parsed from the URL  
    - scheme – scheme or protocol  
    - netloc – full hostname  
    - hostname – hostname  
    - path – URL path  
    - params – URL params  
    - query – URL query  
    - fragment – URL fragment  
    - username – username, parsed from the netloc section of the URL  
    - password – password, parsed from the netloc section of the URL  
    - message – Error message is URL failed to parse  

**Example Usage**  
```
class CustomDownloader(BaseDownloader):
    download(self, urlInfo: UrlInfo, outputFile: str) -> (bool, str):
        :  
        : 
        :
downloader = GenericDownloader(sourceList, destination)
downloader.registerDownloader(‘custom’, CustomDownloader())
downloader.startDownloads()
```  

# OUTPUT FILES NAMING CONVENTION
- The output filenames are parsed from the url path. (e.g. https://thumbs.gfycat.com/CheerfulDarlingGlobefish-mobile.mp4)  
- Parsed filename for URL: CheerfulDarlingGlobefish-mobile.mp4  
- A unique identifier is added as the filename suffix: CheerfulDarlingGlobefish-mobile_1566319230.9721715.mp4  
- This is to prevent conflicts with different URLs having the same filename in their URL path.  
- For convenience, a file downloads.map is created in the destination directory that shows all URLs that were successfully downloaded and their associated output filenames  
- The programs outputs to the console all the URLs that succeeds or failed. But the program saves a downloads.error file in the destination directory that shows all URLs that failed and a reason