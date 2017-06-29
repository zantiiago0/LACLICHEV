"""
This example deals with returning content of section.
"""

###################################################################################################
#IMPORTS
###################################################################################################
import os
import datetime

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

    # Remove Duplicates
    print('Removing Duplicates...')
    archivedDB.RemoveDuplicates('name')
    print('Duplicates Removed.\n')

    # Index Documents
    print('Indexing Documents...')
    documentIndexer = Indexer(debug=True, verbose=True)
    documentIndexer.IndexDocs(theGuardianContent)
    print('Indexing Done.\n')

    documentIndexer.FreqMatrix()

    print("\nSearching documents with Tag : Weather")
    documentIndexer.Search("weather", Indexer.TAGS)
#END OF FILE
