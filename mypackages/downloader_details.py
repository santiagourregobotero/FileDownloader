from enum import Enum, unique
from dataclasses import dataclass

@dataclass
class DownloaderDetails:
    success: str = 'success'
    failure: str = 'failure'

    hostnameKey: str = 'hostname'
    portKey: str = 'port'
    usernameKey: str = 'username'
    passwordKey: str = 'password'
    isValidKey: str = 'isValid'
    schemeKey: str = 'scheme'
    pathKey: str = 'path'
    dirKey: str = 'dir'
    outputFilenameKey: str = 'outputFilename'
    outputExtensionKey: str = 'outputExtension'
    outputFilenameSuffixKey: str = 'outputFilenameSuffix'
    paramsKey: str = 'params'
    queryKey: str = 'query'
    netlocKey: str = 'netloc'
    fragmentKey: str = 'fragment'
    messageKey: str = 'message'
    inputUrlKey: str = 'inputUrl'
    urlKey: str = 'url'
    msgKey: str = 'msg'
    outputKey: str = 'output'

    @unique
    class Status(Enum):
        SUCCESS = 0,
        WARNING = 1,
        FAILURE = 2,
        INVALID_INPUT = 3,