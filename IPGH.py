"""
This example deals with returning content of section.
"""

###################################################################################################
#IMPORTS
###################################################################################################
import json
import time

#MongoDB
from   pymongo import MongoClient

#Extractor
from dataExtractors.theGuardianExtractor import TheGuardianExtractor

###################################################################################################
#FUNCTIONS
###################################################################################################

###################################################################################################
#MAIN
###################################################################################################
startOne   = time.clock()

#Start MongoDB Client (Default Host) and get the WebScrappedData Collection
scrappedCollection = MongoClient().local.WebScrappedData

headers = {"q": "business"}  # q=query parameter/search parameter
#jsonContent = json.dumps(response, ensure_ascii=False)

arrayBSON = TheGuardianExtractor().getContent(**headers)

for bSON in arrayBSON:
    scrappedCollection.insert(bSON)

#Execution Time
print(time.clock() - startOne)

#END OF FILE
