"""
Indexer Module


About LuceneTM
Is a high-performance, full-featured text search engine library written entirely in Java.
It is a technology suitable for nearly any application that requires full-text search,
especially cross-platform.

About PyLucene
PyLucene is a Python extension for accessing Java LuceneTM. Its goal is to allow you
to use Lucene's text indexing and searching capabilities from Python
"""
###################################################################################################
#IMPORTS
###################################################################################################
import os
import time
import datetime
import math
import sys

# Lucene
import lucene

from java.nio.file                              import Paths
from org.apache.lucene.analysis.standard        import StandardAnalyzer
from org.apache.lucene.analysis.snowball        import SnowballFilter
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.document                 import Document, TextField, Field, LongPoint, StringField, FieldType
from org.apache.lucene.index                    import IndexWriter, IndexWriterConfig, IndexReader, DirectoryReader, Term, IndexOptions, TermsEnum
from org.apache.lucene.store                    import SimpleFSDirectory, RAMDirectory
from org.apache.lucene.util                     import BytesRefIterator
from org.apache.lucene.search                   import IndexSearcher
from org.apache.lucene.queryparser.classic      import QueryParser

# Natural Language Toolkit
import nltk

# Geocoding
from geopy.geocoders import GoogleV3

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

#DB
from dataDB.dbHandler import DBHandler

###################################################################################################
#CONSTANTS
###################################################################################################

###################################################################################################
#CLASS
###################################################################################################
class Indexer:
    """
    Indexer Class
    """
    (NAME, CONTENT, DATE, URL, TAGS) = ("name", "content", "date", "url", "tags")

    def __init__(self, indexDir="", debug=False, verbose=False):
        """
        :Parameters:
        - `indexDir`: Path where the Index will be saved. (Str)
        - `debug`: Create the Index in RAM Memory (indexDir will be ignored). (Boolean)
        - `verbose`: Provide additional information about the initialization process. (Boolean)
        """
        if indexDir != "":
            INDEX_DIR = indexDir
        else:
            INDEX_DIR = os.path.dirname(os.path.realpath(__file__)) + "/luceneIndex"

        if not os.path.exists(INDEX_DIR):
            os.makedirs(INDEX_DIR)
            self.__boAppend = False
        else:
            self.__boAppend = True
        # Initialize lucene and JVM
        lucene.initVM()
        # Get index storage
        if debug:
            # Store the index in memory
            self.__indexDir = RAMDirectory()
            self.__boAppend = False
            INDEX_DIR       = "RAM Memory"
        else:
            # Store an index on disk
            self.__indexDir = SimpleFSDirectory(Paths.get(INDEX_DIR))

        # Create Content FieldType
        self.__contentType = FieldType()
        self.__contentType.setIndexOptions(IndexOptions.DOCS_AND_FREQS)
        self.__contentType.setTokenized(True)
        self.__contentType.setStored(True)
        self.__contentType.setStoreTermVectors(True)
        self.__contentType.setStoreTermVectorPositions(True)
        self.__contentType.freeze()

        # Get the Analyzer
        self.__analyzer = StandardAnalyzer(StandardAnalyzer.ENGLISH_STOP_WORDS_SET)

        # Print Indexer Information
        if verbose:
            print("Lucene version is: ", lucene.VERSION)
            print("Index Directory: ", INDEX_DIR)

    def __del__(self):
        self.__indexDir.close()

    @staticmethod
    def __getTimestamp(dateTime):
        """
        Converts the document's date to an integer timestamp

        :Parameters:
        - `dateTime`: Document's date  (Str)

        :Returns:
        - Date timestamp (Int)
        """
        tm    = time.strptime(dateTime, '%Y-%m-%dT%H:%M:%SZ')
        sTime = "{0:0>4}{1:0>2}{2:0>2}{3:0>2}{4:0>2}{5:0>2}".format(tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec)
        return int(sTime)

    @staticmethod
    def __getDateTime(timeStamp):
        """
        Converts the document's timestamp to date

        :Parameters:
        - `timeStamp`: Document's timestamp

        :Returns:
        - Date (Str)
        """
        date = datetime.datetime(year=int(timeStamp[0:4]),
                                 month=int(timeStamp[4:6]),
                                 day=int(timeStamp[6:8]),
                                 hour=int(timeStamp[8:10]),
                                 minute=int(timeStamp[10:12]),
                                 second=int(timeStamp[12:14]))
        return date.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def __qualifyTags(tags):
        """
        Creates the qualify string for tags

        :Parameters:
        - `tags`: List of document's tags

        :Return:
        - Qualify Tags (Str)
        """
        sTags = ""
        for tag in tags:
            sTags += tag + '|'
        return sTags[:-1]

    @staticmethod
    def __printProgressBar(iteration, total, tStamp, prefix='', decimals=1, length=50, fill='█'):
        """
        Call in a loop to create terminal progress bar

        :Parameters:
        - `iteration`: Current iteration (Int)
        - `total`: Total iterations (Int)
        - `tStamp`: Start time (Int)
        - `prefix` (optional): Prefix string (Str)
        - `suffix` (optional): Suffix string (Str)
        - `decimals` (optional): Positive number of decimals in percent complete (Int)
        - `length` (optional): Character length of bar (Int)
        - `fill` (optional): Bar fill character (Str)

        :Returns:
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        progress = fill * filledLength + '-' * (length - filledLength)
        timeStamp = time.clock() - tStamp
        print('\r%s |%s| %s%% - %.3fs - %d of %d' % (prefix, progress, percent, timeStamp, iteration, total), end = '\r')
        # Print New Line on Complete
        if iteration == total:
            print()

    def IndexDocs(self, documents, verbose=False):
        """
        Index documents under the directory

        :Parameters:
        - `documents`: Documents to be indexed (List)
        - `verbose`: Provide additional information about the indexation process. (Boolean)
        """
        # Get the Writer Configuration
        writerConfig = IndexWriterConfig(self.__analyzer)
        # Get index writer
        writer       = IndexWriter(self.__indexDir, writerConfig)

        for document in documents:
            # Create a document that would we added to the index
            doc = Document()
            # Add a field to this document
            doc.add(TextField(Indexer.NAME,    document['name'],    Field.Store.YES))
            doc.add(Field(Indexer.CONTENT,     document['content'], self.__contentType))
            doc.add(LongPoint(Indexer.DATE,    self. __getTimestamp(document['date'])))
            doc.add(StringField(Indexer.URL,   document['url'],     Field.Store.YES))
            doc.add(TextField(Indexer.TAGS,    self.__qualifyTags(document['tags']), Field.Store.YES))
            # Add or update the document to the index
            if not self.__boAppend:
                # New index, so we just add the document (no old document can be there):
                if verbose:
                    print("Adding " + document['name'])
                writer.addDocument(doc)
            else:
                # Existing index (an old copy of this document may have been indexed) so
                # we use updateDocument instead to replace the old one matching the exact
                # path, if present:
                if verbose:
                    print("Updating " + document['name'])
                writer.updateDocument(Term(Indexer.NAME, document['name']), doc)

        # Print index information and close writer
        print("Indexed %d documents (%d docs in index)" % (len(documents), writer.numDocs()))
        writer.close()

    def Search(self, query, field=NAME, maxResult=1000):
        """
        Search for a document into the Lucene's Index

        :Parameters:
        - `query`: Request to be made to the Index (Str).
        - `field`: Field to be consulted by the query (NAME, CONTENT, DATE, URL, TAGS).
        - `maxResult`: Maximum number of results.
        """
        # Get the Index Directory
        reader      = DirectoryReader.open(self.__indexDir)
        searcher    = IndexSearcher(reader)
        # Create a query
        queryParser = QueryParser(field, self.__analyzer).parse(query)
        # Do a search
        hits        = searcher.search(queryParser, maxResult)
        print("Found %d document(s) that matched query '%s':" % (hits.totalHits, queryParser))
        for hit in hits.scoreDocs:
            doc = searcher.doc(hit.doc)
            print("Document Nº: %d - Score: %.5f" % (hit.doc, hit.score))
            print("Name: " + doc.get('name'))
            print("Tags: " + doc.get('tags') + "\n")
        reader.close()

    def StemDocument(self, docIdx):
        """
        Return an array of the document's stemmed terms

        :Parameters:
        - `docIdx`: Document's index ID (Int).
        """
        stemmedTerms = []
        reader       = DirectoryReader.open(self.__indexDir)
        doc          = reader.document(docIdx)
        tknStream    = self.__analyzer.tokenStream(Indexer.CONTENT, doc.get(Indexer.CONTENT))
        stemmed      = SnowballFilter(tknStream, "English")
        stemmed.reset()
        while stemmed.incrementToken():
            stemmedTerms.append(stemmed.getAttribute(CharTermAttribute.class_).toString())

        tknStream.close()
        reader.close()
        return stemmedTerms

    def FreqMatrix(self, byTerms=True, saveMtx=False, verbose=False):
        """
        Generates a Frequency Matrix of the current Index

        :Parameters:
        - `saveMtx`: Save the Frequency Matrix to a .txt file. (Boolean)
        - `verbose`: Provide additional information about the initialization process. (Boolean)
        """
        freqMtx   = {} # Terms - DocumentID Matrix
        reader    = DirectoryReader.open(self.__indexDir)
        numDocs   = reader.numDocs()
        timeStamp = time.clock()
        print("Generating Frequency Matrix...")
        self.__printProgressBar(0, numDocs - 1, timeStamp, prefix='Progress:')
        for docIdx in range(numDocs):
            doc      = reader.document(docIdx)
            termItr  = self.StemDocument(docIdx)
            termSize = len(termItr)
            docStr   = '{0}'.format(docIdx)
            termDict = {}
            if verbose:
                print("Processing file: %s - Terms: %d" % (doc.get(Indexer.NAME), termSize))
            for termText in termItr:
                if byTerms:
                    # Check if the term exists
                    if termText in freqMtx:
                        # Check if the document exists
                        if docStr in freqMtx[termText]:
                            termCount = int(math.ceil(((freqMtx[termText][docStr] * termSize) / 100)))
                            freqMtx[termText].update({ docStr : ((termCount + 1) / termSize) * 100 })
                        else:
                            freqMtx[termText].update({ docStr : (1 / termSize) * 100 })
                    else:
                        termIdx = { termText : { docStr : (1 / termSize) * 100 } }
                        freqMtx.update(termIdx)
                else:
                    # Check if the term exists
                    # :TODO Replace '.' from terms
                    termText = termText.replace('.', '_')
                    if termText in termDict:
                        termCount          = int(math.ceil((termDict[termText] * termSize) / 100))
                        termDict[termText] = ((termCount + 1) / termSize) * 100
                    else:
                        termIdx = { termText : (1 / termSize) * 100 }
                        termDict.update(termIdx)
            if not byTerms:
                freqMtx.update({docStr : termDict})
            self.__printProgressBar(docIdx, numDocs - 1, timeStamp, prefix='Progress:')

        if saveMtx and byTerms:
            pathMatrix = os.path.dirname(os.path.realpath(__file__)) + "/freqMtx.txt"
            fMatrix    = open(pathMatrix, 'w')
            numWords   = len(freqMtx)
            timeStamp  = time.clock()
            wordsIt    = 0

            print("Saving Frequency Matrix File: ", pathMatrix)
            self.__printProgressBar(wordsIt, numWords, timeStamp, prefix='Progress:')
            # File Generation Start
            print("+========= Frequency Matrix =========+", file=fMatrix)
            print("%20s" % (' '), end=' ', file=fMatrix)
            for docIdx in range(numDocs):
                print("D{0:0>4}".format(docIdx), end=' ', file=fMatrix)
            print(file=fMatrix)
            for word in sorted(freqMtx):
                print("%20s" % (word), end=' ', file=fMatrix)
                for docIdx in range(reader.numDocs()):
                    try:
                        termCount = freqMtx[word][str(docIdx)]
                        print("%02.03f" % (termCount), end=' ', file=fMatrix)
                    except KeyError:
                        print("  0  ", end=' ', file=fMatrix)
                print(file=fMatrix)
                wordsIt += 1
                self.__printProgressBar(wordsIt, numWords, timeStamp, prefix='Progress:')
            # Close File
            fMatrix.close()

        # Close IndexReader
        reader.close()
        return freqMtx

    def AnalyzeDocument(self, docIdx):
        """
        Generates a list of (entity, relation, entity) tuples as its output.

        :Parameters:
        - `docIdx`: Document's index ID (Int).
        """
        gpeList    = {}
        geolocator = GoogleV3()
        reader     = DirectoryReader.open(self.__indexDir)
        doc        = reader.document(docIdx)
        # Load NLTK Data
        nltkPath = os.path.dirname(os.path.realpath(__file__)) + '/../nltk_data'
        nltk.data.path.append(nltkPath)

        # Named Entity Recognition
        content   = doc.get(Indexer.CONTENT)
        sentences = nltk.sent_tokenize(content)
        # Loop over each sentence and tokenize it separately
        for sentence in sentences:
            ner = nltk.word_tokenize(sentence)
            ner = nltk.pos_tag(ner)
            ner = nltk.ne_chunk(ner)
            # Get all the Geo-Political Entities
            for subtrees in list(ner.subtrees(filter=lambda subtree: subtree.label()=='GPE')):
                for gpe in subtrees:
                    if not gpe[0] in gpeList:
                        location = geolocator.geocode(gpe[0])
                        if ('locality' in location.raw['types'][0]) or ('country' in location.raw['types'][0]) or ('administrative' in location.raw['types'][0]):
                            gpe = { gpe[0]: { 'location':location.address,
                                              'latitude':location.latitude,
                                              'longitude':location.longitude } }
                        else:
                            for raw in location.raw['address_components']:
                                if (('locality' in raw['types'][0]) or ('country' in raw['types'][0]) or ('administrative' in raw['types'][0])) and (gpe[0] in raw['long_name']):
                                    gpe = { gpe[0]: { 'location':raw['long_name'],
                                                      'latitude':location.latitude,
                                                      'longitude':location.longitude } }
                                    break
                        gpeList.update(gpe)

        return gpeList

###################################################################################################
#TEST
###################################################################################################
if __name__ == "__main__":
    """
    Info Link
    https://lucene.apache.org/core/6_5_1/demo/src-html/org/apache/lucene/demo/SearchFiles.html
    http://nullege.com/codes/show/src%40l%40u%40lupyne-1.6%40examples%40__main__.py/2/lucene.initVM/python
    https://gist.github.com/mocobeta/0d2feeb59295bfad157ed06e36fd626a
    https://www.adictosaltrabajo.com/tutoriales/lucene-ana-lyzers-stemming-more-like-this/
    """
    os.system('clear')
    """
    documentIndexer = Indexer(verbose=True)
    
    matrix          = documentIndexer.FreqMatrix()
    matrixDB        = DBHandler('TermsDB')
    for value in sorted(matrix):
        doc = { 'stem' : value,
                'docs' : matrix[value] }
        matrixDB.Insert(doc)
    del matrixDB
    """
    """
    matrixDB = DBHandler('DocsDB')
    matrix   = documentIndexer.FreqMatrix(byTerms=False)
    for value in matrix:
        doc = { 'doc'   : int(value),
                'stems' : matrix[value] }
        matrixDB.Insert(doc)

    cities = documentIndexer.AnalyzeDocument(0)
    import webbrowser

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
    """
###################################################################################################
#END OF FILE
###################################################################################################
