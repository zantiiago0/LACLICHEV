"""
The Guardian data extractor module
API: b90595fd-be2a-4488-88bd-538a28af1be2
"""
###################################################################################################
#IMPORTS
###################################################################################################
import re
#Web Scrapping
from   bs4 import BeautifulSoup

#The Guardian API
from   tools.theguardian        import theguardian_content

from   dataExtractors.eDocument import EDocument
from   tools.progressBar        import ProgressBar

###################################################################################################
#CONSTANTS
###################################################################################################

###################################################################################################
#CLASS
###################################################################################################
class TheGuardianExtractor:
    """
    The Guardian Extractor Class
    """

    def __init__(self, query):
        """
        :Parameters:
        - `query`: Request to be made to The Guardian API. (Str)
                   Supports AND(&), OR(|) and NOT(!) operators, and exact phrase queries.
        """
        self.__contentTAG = 'content__article-body from-content-api js-article__body'
        self.__API        = 'b90595fd-be2a-4488-88bd-538a28af1be2'
        self.__keywords   = []
        self.__query      = ''

        #Check if the query contains conditional operators
        if re.search(r'\&|\||\!|\(|\)', query):
            #Remove all spaces from string
            query = query.replace(" ", "")
            for word in re.split(r'(\W)', query):
                if   word == '&':
                    self.__query += " AND "
                elif word == '|':
                    self.__query += " OR "
                elif word == '!':
                    self.__query += "NOT "
                elif word.isalpha():
                    self.__keywords.append(word)
                    self.__query += word
                else:
                    self.__query += word
        else:
            self.__query = '"' + query + '"'

    def getContent(self, fromDate=0, toDate=0):
        """
        Returns an array of Documents obtained by the query to The Guardian.

        :Parameters:
        - `fromDate`: The start date for the search.
        - `toDate`: The end date for the search.

        :Return:
        - List of retrieved documents.
        """
        bSONResult   = []
        weatherQuery = {'q':self.__query,
                        'show-fields':'body',
                        'show-tags':'keyword',
                        'page-size':200,
                        'order-by':'newest',
                        'page':1
                       }
        # Get weather content
        content  = theguardian_content.Content(api=self.__API, **weatherQuery)
        response = content.get_content_response()
        # Setup toolbar
        toolbarLen = response['response']['total']
        if toolbarLen > 0:
            pages = response['response']['pages']
            pB    = ProgressBar(toolbarLen, prefix='Retrieving:')
            while True:
                # Create documents from database
                for itDoc in content.get_results(response):
                    if itDoc['type'] == "article" :
                        docName    = itDoc['webTitle']
                        docUrl     = itDoc['webUrl']
                        docDate    = itDoc['webPublicationDate']
                        docBody    = itDoc['fields']['body']
                        docTags    = []
                        docContent = ""
                        #Extract the Web Page body content
                        for article in BeautifulSoup(docBody, 'lxml').find_all('p'):
                            docContent = docContent + article.get_text() + "\n"
                        # Extract Tags
                        for tag in itDoc['tags']:
                            try:
                                docTags.append(tag['sectionId'])
                            except:
                                pass
                        # Create Document
                        bSON = EDocument(docName, docUrl, docDate, docTags, docContent).dictDump()
                        bSONResult.append(bSON)
                    pB.updateProgress()
                # Check if there's more content to obtain
                if weatherQuery['page'] < pages:
                    weatherQuery['page'] += 1
                    content  = theguardian_content.Content(api=self.__API, **weatherQuery)
                    response = content.get_content_response()
                else:
                    break
        else:
            print("No results found")

        return bSONResult if isinstance(bSONResult, list) else [bSONResult]

    def getQuery(self):
        """
        Return the query for The Guardian API
        """
        return self.__query

    def getKeywords(self):
        """
        Return a list of the keywords of the query
        """
        return self.__keywords

###################################################################################################
#TEST
###################################################################################################
if __name__ == "__main__":
    theGuardian        = TheGuardianExtractor("heavy storms")
    theGuardianContent = theGuardian.getContent()
