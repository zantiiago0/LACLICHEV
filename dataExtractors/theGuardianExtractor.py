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
        pass

    def getContent(self, **query):
        """
        Returns an array of Documents obtained by the query to The Guardian.

        Attributes:
            :param query: Request to be made to The Guardian API
        """
        bSONResult = []

        section = theguardian_section.Section(api='test', **query)
        # get the results
        section_content = section.get_content_response()
        results = section.get_results(section_content)

        # get different editions from the results
        editions = results[0]['editions']

        # get uk/sports edition apiUrl
        uk_sports = [edi["apiUrl"] for edi in editions if edi["id"] == "uk/business"][0]

        # use this api url to sports content
        content = theguardian_content.Content(api='test', url=uk_sports)

        # get section response
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
