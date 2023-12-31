import time 
from enum import Enum, unique
from dataclasses import dataclass, field
from urllib.parse import urlparse

@dataclass
class UrlInfo:
    """Represents all the components for a variety of different URL formats (https, ftp, sftp).  
    Also encapsulates the filename name information that is used to construct an output file from
    the url.
    """
    inputUrl: str
    isValid: bool = True
    message: str = ''
    port:str = 0
    outputFilename:str = ''
    outputFilenameExtension:str = ''
    outputFilenameSuffix:str = str(time.time())

    scheme:str = field(init=False)
    netloc:str = field(init=False)
    hostname:str = field(init=False)
    path:str = field(init=False)
    params:str = field(init=False)
    query:str = field(init=False)
    fragment:str = field(init=False)
    username:str = field(init=False)
    password:str = field(init=False)
    dirName:str = field(init=False)

    def parse(self):
        o = urlparse(self.inputUrl)
        self.scheme, self.netloc, self.path, self.params, self.query, self.fragment = o
        self.username = o.username
        self.password = o.password
        self.hostname = o.hostname
        if o.port:
            self.port = o.port
        
        if not self.hostname:
            raise ValueError('Invalid URL, missing hostname')
        
@unique
class Status(Enum):
    SUCCESS = 0,
    WARNING = 1,
    FAILURE = 2,
    INVALID_INPUT = 3

@dataclass
class DownloadResult:
    url: str
    msg: str
    output: str
    status: bool
    