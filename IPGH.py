"""
This example deals with returning content of section.
"""

###################################################################################################
#IMPORTS
###################################################################################################
#import json
import time
import os

#MongoDB
from   pymongo        import MongoClient
from   pymongo.errors import DuplicateKeyError

#Extractor
from dataExtractors.theGuardianExtractor import TheGuardianExtractor

###################################################################################################
#FUNCTIONS
###################################################################################################
clear = lambda:os.system('clear')

###################################################################################################
#MAIN
###################################################################################################
clear()
startOne = time.clock()

#Start MongoDB Client (Default Host)
mongoDB = MongoClient().local

# Get the ArchivedData Collection
if "ArchivedData" in mongoDB.collection_names():
    archivedCollection = mongoDB.ArchivedData
else:
    mongoDB.create_collection("ArchivedData")
    archivedCollection = mongoDB.ArchivedData
    archivedCollection.create_index([('name', "text")], unique=True)

# Get the search term
term = input("What are you searching? ")

query = {"q": term}  # q=query parameter/search parameter

arrayBSON = TheGuardianExtractor().getContent(**query)
#jsonContent = json.dumps(arrayBSON, ensure_ascii=False)

for bSON in arrayBSON:
    try:
        archivedCollection.insert_one(bSON)
        print("New: \"{0}\"".format(bSON['name']))
    except DuplicateKeyError:
        print("Duplicated: \"{0}\"".format(bSON['name']))

#Execution Time
print(time.clock() - startOne)

#END OF FILE
