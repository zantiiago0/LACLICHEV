"""
This example deals with returning content of section.
"""

###################################################################################################
#IMPORTS
###################################################################################################
#import json
import os

#MongoDB
from   pymongo        import MongoClient
from   pymongo.errors import DuplicateKeyError

# Natural Language Toolkit
import nltk
from nltk.tag import StanfordNERTagger

#Extractor
from dataExtractors.theGuardianExtractor import TheGuardianExtractor

###################################################################################################
#CONSTANTS
###################################################################################################


###################################################################################################
#FUNCTIONS
###################################################################################################
clear = lambda:os.system('clear')

def InformationExtraction(sentence, useStanford=False):
    """
    This system takes the raw text of a document as its input, and generates a list of
    (entity, relation, entity) tuples as its output.
    """
    # Load NLTK Data
    nltkPath = os.path.dirname(os.path.realpath(__file__)) + '/nltk_data'
    nltk.data.path.append(nltkPath)

    if not useStanford :
        # Named Entity Recognition
        ner = nltk.word_tokenize(sentence)
        ner = nltk.pos_tag(ner)
        ner = nltk.ne_chunk(ner)
    else :
        nerJar   = nltkPath + '/stanford/stanford-ner.jar'
        nerModel = nltkPath + '/stanford/english.all.3class.distsim.crf.ser.gz'
        ner      = StanfordNERTagger(nerModel, nerJar).tag(sentence)

    return ner

###################################################################################################
#MAIN
###################################################################################################
clear()

#Start MongoDB Client (Default Host)
mongoDB = MongoClient().local

# Get the ArchivedData Collection
if 'ArchivedData' in mongoDB.collection_names():
    archivedCollection = mongoDB.ArchivedData
else:
    mongoDB.create_collection('ArchivedData')
    archivedCollection = mongoDB.ArchivedData
    archivedCollection.create_index([('name', 'text')], unique=True)

# Get the search query
query = "Storms in Guadalajara between January 2000 and September 2017"#input('What are you searching? ')
info = InformationExtraction(query)

print(info)

event    = info[0][0]
location = info[2][0][0]
fromDate = info[5][0]
toDate   = info[8][0]

arrayBSON = TheGuardianExtractor().getContent(event, location, fromDate, toDate)
#jsonContent = json.dumps(arrayBSON, ensure_ascii=False)

for bSON in arrayBSON:
    try:
        archivedCollection.insert_one(bSON)
        print('New: "{0}"'.format(bSON['name']))
    except DuplicateKeyError:
        print('Duplicated: "{0}"'.format(bSON['name']))

#END OF FILE
