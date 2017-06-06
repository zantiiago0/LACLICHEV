"""
The Guardian data extractor module
"""
from   dataExtractors.document import Document

#The Guardian API
from   theguardian import theguardian_section
from   theguardian import theguardian_content

#Web Scrapping
import requests
from   bs4 import BeautifulSoup
from   bs4 import SoupStrainer

class TheGuardianExtractor:
    """
    The Guardian Extractor Class
    """

    def __init__(self):
        self.__contentTAG = "content__article-body from-content-api js-article__body"

    def getContent(self, **query):
        """
        Returns an array of Documents obtained by the query to The Guardian.

        Attributes:
            :param query: Request to be made to The Guardian API
        """
        bSONResult = []

        # Weather apiUrl
        weatherAPI = "https://content.guardianapis.com/weather"

        # Get weather content
        content = theguardian_content.Content(api='test', url=weatherAPI, **query)

        # Get content response
        response = content.get_content_response()

        for itDoc in response['response']['results']:
            if itDoc['type'] == "article" :
                docName    = itDoc['webTitle']
                docUrl     = itDoc['webUrl']
                docDate    = itDoc['webPublicationDate']
                docContent = ""
                #Extract a Web Page
                try :
                    webRequest = requests.get(docUrl)
                    findTag = SoupStrainer("div", class_=self.__contentTAG)
                    soup    = BeautifulSoup(webRequest.text, 'lxml', parse_only=findTag)
                    for article in soup.find_all('p'):
                        docContent = docContent + article.get_text() + "\n"

                    bSON = Document(docName, docUrl, docDate, docContent).dictDump()
                    bSONResult.append(bSON)
                except requests.exceptions.RequestException as e:
                    print("Error obtaining the webpage" + e)

        return bSONResult
