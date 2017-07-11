"""
DataBase Handler module
"""
###################################################################################################
#IMPORTS
###################################################################################################
import os

#MongoDB
from pymongo import MongoClient

###################################################################################################
#CONSTANTS
###################################################################################################

###################################################################################################
#CLASS
###################################################################################################
class DBHandler:
    """
    DataBase Handler Class
    """

    def __init__(self, dbName):
        """
        :Parameters:
        - `dbName`: Database's name (Str)
        """
        #Start MongoDB Client (Default Host)
        self.__mongoDB = MongoClient().local

        # Get the dbName Collection
        if dbName in self.__mongoDB.collection_names():
            self.__collection = self.__mongoDB[dbName]
        else:
            self.__mongoDB.create_collection(dbName)
            self.__collection = self.__mongoDB[dbName]

    def RemoveDuplicatesBy(self, keyName):
        """
        Remove duplicated documents from a Collection
        """
        pipeline = [
            {"$group": {
                "_id": {
                    keyName:"${0}".format(keyName)
                },
                "uniqueIds": {
                    "$addToSet": "$_id"
                },
                "count": {
                    "$sum": 1
                }}
            }]

        cursor = self.__collection.aggregate(pipeline)
        duplicatedIds = []
        for doc in cursor:
            # Keep one document
            del doc["uniqueIds"][0]
            # Get the duplicated document's ID
            for duplicatedID in doc["uniqueIds"]:
                duplicatedIds.append(duplicatedID)
        # Delete all duplicated IDs
        self.__collection.remove({"_id": {"$in": duplicatedIds}})

    def Insert(self, data):
        """
        Insert a document to the Collection

        :Parameters:
        - `data`: Document to be inserted (Dict | Dict List)
        """
        if not isinstance(data, list):
            self.__collection.insert_one(data)
        else:
            for bSON in data:
                self.__collection.insert_one(bSON)

    def GetDocuments(self):
        """
        Get all documents of the Collection
        """
        dataList = []
        cursor  = self.__collection.find({})
        for document in cursor:
            dataList.append(document)

        return dataList

    def Empty(self):
        """
        Remove all documents of the Collection
        """
        self.__collection.drop()


###################################################################################################
#TEST
###################################################################################################
if __name__ == "__main__":
    os.system('clear')

    testDB    = DBHandler('QueryDB')

    testDoc = { "query":"Test", "value":1234}
    testDB.Insert(testDoc)
