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

    helpMsg = 'file_downloader.py -s <sourcelist> -d <destination> [-n <numthreads=5> -c <chunksize=8192> -t <timeout=60.0> -r <delimiter=none> -l <logLevel>]'
    sourceList = ''
    destination = ''

    config = configparser.ConfigParser()
    config.read('./config/file_downloader.ini')
    defaults = config['DEFAULT']

    numThreads = int(defaults['numThreads']) if 'numThreads' in defaults else 5
    chunkSize = int(defaults['chunkSize']) if 'chunkSize' in defaults else 8192    
    timeout = float(defaults['timeout']) if 'timeout' in defaults else 60.0
    delimiter = delimiter = defaults['delimiter'] if 'delimiter' in defaults else None
    logLevel = logLevel = defaults['logLevel'] if 'logLevel' in defaults else 'INFO'

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
            numThreads = int(arg)
        elif opt in ('-c'):
            chunkSize = int(arg)
        elif opt in ('-t'):
            timeout = float(arg)
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