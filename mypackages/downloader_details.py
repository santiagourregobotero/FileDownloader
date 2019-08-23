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