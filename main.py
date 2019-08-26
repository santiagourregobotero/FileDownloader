import sys, getopt
import configparser
from mypackages.file_downloader import GenericDownloader
import logging
import logging.config

def configureLogger(logLevel: str):
    logging.config.fileConfig('./config/logging.conf', disable_existing_loggers=False)

    if (not logLevel): return
    numeric_level = getattr(logging, logLevel.upper(), None)
    if  not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % logLevel)

    logging.getLogger().setLevel(numeric_level)


def main(argv):

    helpMsg = 'file_downloader.py -s <sourcelist> -d <destination> [-n <numthreads=5> -c <chunksize=1014> -t <timeout=60.0> -r <delimiter=none> -l <logLevel>]'
    sourceList = ''
    destination = ''

    config = configparser.ConfigParser()
    config.read('./config/file_downloader.ini')
    defaults = config['DEFAULT']

    numThreads = 5
    if 'numThreads' in defaults:
        numThreads = int(defaults['numThreads'])

    chunkSize = 8192
    if 'chunkSize' in defaults:
        chunkSize = int(defaults['chunkSize'])
    
    timeout = 60.0
    if 'timeout' in defaults:
        timeout = float(defaults['timeout'])

    delimiter = None
    if 'delimiter' in defaults:
        delimiter = defaults['delimiter']
    
    logLevel = 'INFO'
    if 'logLevel' in defaults: 
        logLevel = defaults['logLevel']

    try:
        opts, args = getopt.getopt(argv, "hs:d:n:c:t:r:l:")
    except:
        print(helpMsg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(helpMsg)
            sys.exit()
        elif opt in ('-s'):
            sourceList = arg
        elif opt in ('-d'):
            destination = arg
        elif opt in ('-n'):
            numThreads = arg
        elif opt in ('-c'):
            chunkSize = arg
        elif opt in ('-t'):
            timeout = arg
        elif opt in ('-r'):
            delimiter = arg
        elif opt in ('-l'):
            logLevel = arg
        else:
            print('Unrecognized argument: {}'.format(opt))

    if not sourceList or not destination:
        print(helpMsg)
        sys.exit(2)
    try:
        configureLogger(logLevel)

        downloader = GenericDownloader.fromInputFile(sourceList=sourceList, sourceListDelimiter=delimiter, numThreads=numThreads, destination=destination, chunkSize=chunkSize, timeout=timeout)
        downloader.startDownloads()
    except (ValueError, OSError) as e:
        print('An unexpected error occured: {}'.format(str(e)))
        
    print('Done!')
    
if __name__ == "__main__":
    main(sys.argv[1:])