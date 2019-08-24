import time 
from enum import Enum, unique
from dataclasses import dataclass, field
from urllib.parse import urlparse

@dataclass
class UrlInfo:
    inputUrl: str
    isValid: bool = True
    message: str = ''
    port:str = 0
    outputFilenameSuffix:str = str(time.time())
    outputFilename:str = ''
    outputFilenameExtension:str = ''

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

    def __post_init__(self):
        o = urlparse(self.inputUrl)
        self.scheme, self.netloc, self.path, self.params, self.query, self.fragment = o
        self.username = o.username
        self.password = o.password
        self.hostname = o.hostname

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
    