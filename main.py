import sys, getopt
import configparser
from mypackages.file_downloader import GenericDownloader

def main(argv):

    helpMsg = 'file_downloader.py -s <sourcelist> -d <destination> [-n <numthreads=5> -c <chunksize=1014> -t <timeout=60.0>]'
    sourceList = ''
    destination = ''

    config = configparser.ConfigParser()
    config.read('./config/file_downloader.ini')
    defaults = config['DEFAULT']

    numThreads = int(defaults['numThreads'])
    chunkSize = int(defaults['chunkSize'])
    timeout = float(defaults['timeout'])
    delimiter = defaults['delimiter']

    try:
        opts, args = getopt.getopt(argv, "hs:d:n:c:t:r:")
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
        else:
            print('Unrecognized argument: {}'.format(opt))

    if (not sourceList or not destination):
        print(helpMsg)
        sys.exit(2)
    try:
        downloader = GenericDownloader.fromInputFile(sourceList=sourceList, sourceListDelimiter=delimiter, numThreads=numThreads, destination=destination, chunkSize=chunkSize, timeout=timeout)
        downloader.startDownloads()
    except (ValueError) as e:
        print('An unexpected error occured: {}'.format(str(e)))
        
    print('Done!')
    
if __name__ == "__main__":
    main(sys.argv[1:])