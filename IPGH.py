"""
This example deals with returning content of section.
"""

###################################################################################################
#IMPORTS
###################################################################################################
import os
import datetime
import webbrowser

#Extractor
from dataExtractors.theGuardianExtractor import TheGuardianExtractor

#Indexer
from dataIndexer.indexer import Indexer

#DB
from dataDB.dbHandler import DBHandler

###################################################################################################
#CONSTANTS
###################################################################################################
archivedDB = DBHandler('ArchivedDB')
queryDB    = DBHandler('QueryDB')

###################################################################################################
#FUNCTIONS
###################################################################################################
clear = lambda:os.system('clear')

def Menu():
    """
    Print Application Menu
    """
    clear()
    print (32 * "-" , "LACLICHEV" , 32 * "-")
    print(' Request content containing this free text.')
    print(' Supports AND(&), OR(|) and NOT(!) operators, and exact phrase queries')
    print(' e.g. storm, heavy storm, snow & (rain | storms), storm & ! snow')
    print (75 * "-")

###################################################################################################
#MAIN
###################################################################################################
# Print Menu
Menu()
# Get the search query
userInput = input('What are you searching? ')

#Generate The Guardian Query
theGuardian        = TheGuardianExtractor(userInput)
theGuardianContent = theGuardian.getContent()

# Save the query to QueryDB
queryDoc = { "query":theGuardian.getQuery(),
             "date":datetime.datetime.utcnow(),
             "articlesSize": len(theGuardianContent),
             "keys": theGuardian.getKeywords()
           }
queryDB.Insert(queryDoc)

if len(theGuardianContent) > 0:
    print('\nStoring Content...')
    archivedDB.Insert(theGuardianContent)
    print('Content Stored.\n')
    archivedDB.RemoveDuplicatesBy('name')

    theGuardianContent = archivedDB.GetDocuments()
    archivedDB.Empty()

    # Index Documents
    print('Indexing Documents...')
    documentIndexer = Indexer(debug=True, verbose=True)
    documentIndexer.IndexDocs(theGuardianContent)
    print('Indexing Done.\n')

    #Generate Frequency Matrix
    documentIndexer.FreqMatrix()

    #Do a index search
    print("\nSearching documents with Tag : Weather")
    documentIndexer.Search("weather", Indexer.TAGS)

    #Analyze Document (DEMO)
    cities = documentIndexer.AnalyzeDocument(0)

    #Generate HTML
    html = ''
    for city, value in cities.items():
        api  = "AIzaSyAelNyWCvnF0s2g8gfhwN31jFuCGeNjs3s"
        url  = "https://www.google.com/maps/embed/v1/place?key={0}&q={1}&center={2},{3}".format(api, value['location'], value['latitude'], value['longitude'])
        html += '<iframe width="600" height="450" frameborder="0" style="border:0" src="{0}" allowfullscreen></iframe>\n'.format(url)
    path = os.path.abspath('maps.html')
    url = 'file://' + path
    with open(path, 'w') as f:
        f.write(html)
        #Open url in new tab if possible
        webbrowser.open_new_tab(url)
#END OF FILE
