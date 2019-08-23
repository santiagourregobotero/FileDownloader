import sys, getopt
from mypackages.file_downloader import GenericDownloader

def main(argv):

    helpMsg = 'file_downloader.py -s <sourcelist> -d <destination> [-n <numthreads=5> -c <chunksize=1014>]'
    sourceList = ''
    destination = ''
    numThreads = 5
    chunkSize = 8192

    try:
        opts, args = getopt.getopt(argv, "hs:d:n:c:")
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
        else:
            print('Unrecognized argument: {}'.format(opt))

    if (not sourceList or not destination):
        print(helpMsg)
        sys.exit(2)

    downloader = GenericDownloader.fromInputFile(sourceList=sourceList, sourceListDelimiter=',', numThreads=numThreads, destination=destination, chunkSize=chunkSize)
    downloader.startDownloads()
    print('Done!')
    
if __name__ == "__main__":
    main(sys.argv[1:])