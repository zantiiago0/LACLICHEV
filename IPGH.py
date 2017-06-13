"""
This example deals with returning content of section.
"""

###################################################################################################
#IMPORTS
###################################################################################################
import os
import datetime

#MongoDB
from   pymongo        import MongoClient
from   pymongo.errors import DuplicateKeyError

#Extractor
from dataExtractors.theGuardianExtractor import TheGuardianExtractor

###################################################################################################
#CONSTANTS
###################################################################################################


###################################################################################################
#FUNCTIONS
###################################################################################################
clear = lambda:os.system('clear')

def RemoveDuplicates(mongoCollection):
    """
    Remove duplicated documents from a Mongo Collection

    :Parameters:
    - `mongoCollection`: Mongo Collection Object.
    """
    pipeline = [
        {"$group": {
            "_id": {
                "name":"$name"
            },
            "uniqueIds": {
                "$addToSet": "$_id"
            },
            "count": {
                "$sum": 1
            }}
        }]

    cursor = mongoCollection.aggregate(pipeline)
    duplicatedIds = []
    for doc in cursor:
        # Keep one document
        del doc["uniqueIds"][0]
        # Get the duplicated document's ID
        for duplicatedID in doc["uniqueIds"]:
            duplicatedIds.append(duplicatedID)
    # Delete all duplicated IDs
    mongoCollection.remove({"_id": {"$in": duplicatedIds}})

def Menu():
    """
    Print Application Menu
    """
    clear()
    print (32 * "-" , "LACLICHEV" , 32 * "-")
    print(' Request content containing this free text.')
    print(' Supports AND(&), OR(|) and NOT(!) operators, and exact phrase queries(>)')
    print(' e.g. storm, heavy storm, snow & (rain | storms), storm & ! snow')
    print (75 * "-")
###################################################################################################
#MAIN
###################################################################################################
#Start MongoDB Client (Default Host)
mongoDB = MongoClient().local

# Get the ArchivedData Collection
if 'ArchivedData' in mongoDB.collection_names():
    archivedCollection = mongoDB.ArchivedData
else:
    mongoDB.create_collection('ArchivedData')
    archivedCollection = mongoDB.ArchivedData

# Get the QueryCollection Collection
if 'QueryDB' in mongoDB.collection_names():
    queryCollection = mongoDB.QueryDB
else:
    mongoDB.create_collection('QueryDB')
    queryCollection = mongoDB.QueryDB

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

queryCollection.insert_one(queryDoc)

for bSON in theGuardianContent:
    try:
        archivedCollection.insert_one(bSON)
        #print('New: "{0}"'.format(bSON['name']))
    except DuplicateKeyError:
        print('Duplicated: "{0}"'.format(bSON['name']))

# Remove Duplicates
RemoveDuplicates(archivedCollection)

#END OF FILE
