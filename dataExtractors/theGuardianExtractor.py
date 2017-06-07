"""
The Guardian data extractor module
API: b90595fd-be2a-4488-88bd-538a28af1be2
"""
import time

from   dataExtractors.document import Document

#The Guardian API
from   theguardian import theguardian_content

#Web Scrapping
from   bs4 import BeautifulSoup

class TheGuardianExtractor:
    """
    The Guardian Extractor Class
    """

    def __init__(self):
        self.__contentTAG = 'content__article-body from-content-api js-article__body'
        self.__API        = 'b90595fd-be2a-4488-88bd-538a28af1be2'
        self.__toolbarIt  = 0
        self.__timeStamp  = 0
        self.__toolbarLen = 0

    def __printProgressBar(self, iteration, total, tStamp, prefix='', decimals=1, length=50, fill='█'):
        """
        Call in a loop to create terminal progress bar

        :Parameters:
        - `iteration`: Current iteration (Int)
        - `total`: Total iterations (Int)
        - `tStamp`: Start time (Int)
        - `prefix` (optional): Prefix string (Str)
        - `suffix` (optional): Suffix string (Str)
        - `decimals` (optional): Positive number of decimals in percent complete (Int)
        - `length` (optional): Character length of bar (Int)
        - `fill` (optional): Bar fill character (Str)

        :Returns:
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        progress = fill * filledLength + '-' * (length - filledLength)
        timeStamp = time.clock() - tStamp
        print('\r%s |%s| %s%% - Time: %.3f Sec' % (prefix, progress, percent, timeStamp), end = '\r')
        # Print New Line on Complete
        if iteration == total:
            print()

    def getContent(self, event, location, fromDate, toDate):
        """
        Returns an array of Documents obtained by the query to The Guardian.

        :Parameters:
        - `event`:
        - `location`:
        - `fromDate`:
        - `toDate`:
        """

        bSONResult   = []
        weatherQuery = {'q':event,
                        'section':'weather',
                        'show-fields':'body',
                        'from-date':'{0}-01-01'.format(fromDate),
                        'to-date':'{0}-12-31'.format(toDate) }
        # Get weather content
        content = theguardian_content.Content(api=self.__API, **weatherQuery)
        # Get content response
        response = content.get_content_response()
        # Setup toolbar
        self.__toolbarIt  = 0
        self.__toolbarLen = len(content.get_results(response))
        if self.__toolbarLen > 0:
            self.__timeStamp = time.clock()
            self.__printProgressBar(self.__toolbarIt, self.__toolbarLen, self.__timeStamp, prefix='Progress:')
            # Create documents from database
            for itDoc in content.get_results(response):
                if itDoc['type'] == "article" :
                    docName    = itDoc['webTitle']
                    docUrl     = itDoc['webUrl']
                    docDate    = itDoc['webPublicationDate']
                    docBody    = itDoc['fields']['body']
                    docContent = ""
                    #Extract a Web Page
                    for article in BeautifulSoup(docBody, 'lxml').find_all('p'):
                        docContent = docContent + article.get_text() + "\n"
                    bSON = Document(docName, docUrl, docDate, docContent).dictDump()
                    bSONResult.append(bSON)
                self.__toolbarIt += 1
                self.__printProgressBar(self.__toolbarIt, self.__toolbarLen, self.__timeStamp, prefix='Retrieving: ')
        else:
            print("No results found")

        return bSONResult
