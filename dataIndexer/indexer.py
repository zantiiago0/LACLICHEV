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
sys.path.insert(1, os.getcwd())

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

from dataDB.dbHandler  import DBHandler
from tools.progressBar import ProgressBar
from tools.dtExplorer  import DTExplorer

# Geocoding
from dataEnhancer.geocode import Geocode

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
    (NAME, CONTENT, DATE, URL, TAGS, TIMESTAMP) = ("name", "content", "date", "url", "tags", "timestamp")

    def __init__(self, indexDir="", debug=False, verbose=False):
        """
        :Parameters:
        - `indexDir`: Path where the Index will be saved. (Str)
        - `debug`: Create the Index in RAM Memory (indexDir will be ignored). (Boolean)
        - `verbose`: Provide additional information about the initialization process. (Boolean)
        """
        self.__verbose = verbose
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
        print("Lucene version is: ", lucene.VERSION)
        print("Index Directory: ", INDEX_DIR)

    def __del__(self):
        self.__indexDir.close()

    ##################################################
    #Private Methods
    ##################################################
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
    def __scatterMatrix(numDocs, freqMtx):
        print("Scattering Frequency Matrix...")
        pB = ProgressBar(len(freqMtx), prefix='Progress:')
        matrix        = []
        innerMatrix   = ['Term']

        #Generate Document Columns
        for docIdx in range(numDocs):
            innerMatrix.append("D{0:0>4}".format(docIdx))
        matrix.append(innerMatrix)

        #Generate Word Rows and Columns
        for word in sorted(freqMtx):
            innerMatrix = []
            innerMatrix.append(word)
            for docIdx in range(numDocs):
                try:
                    termCount = round(freqMtx[word][str(docIdx)], 3)
                    innerMatrix.append(termCount)
                except KeyError:
                    innerMatrix.append(0)
            matrix.append(innerMatrix)
            pB.updateProgress()
        return matrix

    @staticmethod
    def __saveMatrix(numDocs, freqMtx):
        pathMatrix = os.path.dirname(os.path.realpath(__file__)) + "/freqMtx.txt"
        fMatrix    = open(pathMatrix, 'w')

        print("Saving Frequency Matrix File: ", pathMatrix)
        pB = ProgressBar(len(freqMtx), prefix='Progress:')
        # File Generation Start
        print("+========= Frequency Matrix =========+", file=fMatrix)
        print("%20s" % (' '), end=' ', file=fMatrix)
        for docIdx in range(numDocs):
            print("D{0:0>4}".format(docIdx), end=' ', file=fMatrix)
        print(file=fMatrix)
        for word in sorted(freqMtx):
            print("%20s" % (word), end=' ', file=fMatrix)
            for docIdx in range(numDocs):
                try:
                    termCount = freqMtx[word][str(docIdx)]
                    print("%02.03f" % (termCount), end=' ', file=fMatrix)
                except KeyError:
                    print("  0  ", end=' ', file=fMatrix)
            print(file=fMatrix)
            pB.updateProgress()
        # Close File
        fMatrix.close()

    
    def __stemString(self, stringToStem):
        stemmedTerms = []
        tknStream    = self.__analyzer.tokenStream('STEM', stringToStem)
        stemmed      = SnowballFilter(tknStream, "English")
        stemmed.reset()
        while stemmed.incrementToken():
            stemmedTerms.append(stemmed.getAttribute(CharTermAttribute.class_).toString())

        tknStream.close()
        return stemmedTerms

    @staticmethod
    def __normalize(qVector, freqMtx):
        for term in qVector:
            for docId in freqMtx:
                if (term in freqMtx[docId]) and (freqMtx[docId][term] > qVector[term]):
                    qVector[term] = freqMtx[docId][term]

    @staticmethod
    def __dotProduct(aVector, bVector):
        """
        Calculate Dot Product

        :Parameters:
        - `aVector`: A Vector. (Dict)
        - `bVector`: B Vector. (Dict)

        :Returns:
        - Dot Product. (Int)
        """
        dotProduct = 0
        for term in aVector:
            if term in bVector:
                product     = aVector[term] * bVector[term]
                dotProduct += product

        return dotProduct

    @staticmethod
    def __magnitude(vector):
        """
        Calculate Dot Product

        :Parameters:
        - `vector`: Query Vector. (Dict)

        :Returns:
        - Vector Magnitude. (Int)
        """
        # Magnitude of the vector is the square root of the dot product of the vector with itself.
        vectorMagnitude = Indexer.__dotProduct(vector, vector)
        vectorMagnitude = math.sqrt(vectorMagnitude)

        return vectorMagnitude
    ##################################################
    #Public Methods
    ##################################################
    def IndexDocs(self, documents):
        """
        Index documents under the directory

        :Parameters:
        - `documents`: Documents to be indexed (List)
        """
        # Get the Writer Configuration
        writerConfig = IndexWriterConfig(self.__analyzer)
        # Get index writer
        writer       = IndexWriter(self.__indexDir, writerConfig)

        for document in documents:
            # Create a document that would we added to the index
            doc = Document()
            # Add a field to this document
            doc.add(TextField(Indexer.NAME,      document['name'],    Field.Store.YES))
            doc.add(Field(Indexer.CONTENT,       document['content'], self.__contentType))
            doc.add(StringField(Indexer.DATE,    document['date'],    Field.Store.YES))
            doc.add(StringField(Indexer.URL,     document['url'],     Field.Store.YES))
            doc.add(TextField(Indexer.TAGS,      self.__qualifyTags(document['tags']), Field.Store.YES))
            doc.add(LongPoint(Indexer.TIMESTAMP, self.__getTimestamp(document['date'])))
            # Add or update the document to the index
            if not self.__boAppend:
                # New index, so we just add the document (no old document can be there):
                if self.__verbose:
                    print("Adding " + document['name'])
                writer.addDocument(doc)
            else:
                # Existing index (an old copy of this document may have been indexed) so
                # we use updateDocument instead to replace the old one matching the exact
                # path, if present:
                if self.__verbose:
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
        reader       = DirectoryReader.open(self.__indexDir)
        doc          = reader.document(docIdx).get(Indexer.CONTENT)
        reader.close()

        return self.__stemString(doc)

    def FreqMatrix(self, scattered=False, byTerms=True, saveMtx=False):
        """
        Generates a Frequency Matrix of the current Index

        :Parameters:
        - `saveMtx`: Save the Frequency Matrix to a .txt file. (Boolean)
        """
        freqMtx   = {} # Terms - DocumentID Matrix
        reader    = DirectoryReader.open(self.__indexDir)
        numDocs   = reader.numDocs()
        print("Generating Frequency Matrix...")
        pB = ProgressBar(numDocs - 1, prefix='Progress:')
        for docIdx in range(numDocs):
            termItr  = self.StemDocument(docIdx)
            termSize = len(termItr)
            docStr   = '{0}'.format(docIdx)
            termDict = {}
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
                    termText = termText.replace('.', '_')
                    if termText in termDict:
                        termCount          = int(math.ceil((termDict[termText] * termSize) / 100))
                        termDict[termText] = ((termCount + 1) / termSize) * 100
                    else:
                        termIdx = { termText : (1 / termSize) * 100 }
                        termDict.update(termIdx)
            if not byTerms:
                freqMtx.update({docStr : termDict})
            pB.updateProgress()

        if saveMtx and byTerms:
            self.__saveMatrix(numDocs, freqMtx)

        if scattered and byTerms:
            freqMtx = self.__scatterMatrix(numDocs, freqMtx)

        # Close IndexReader
        reader.close()

        return freqMtx

    def GetSimilarity(self, query, freqMtx):
        """
        Cosine Similarity
        """
        qVector = { }
        qList   = self.__stemString(query)
        for stem in qList:
            qVector.update({ stem : 0 })
        self.__normalize(qVector, freqMtx)

        qList = []
        #Get similarity between query and doc[n]
        for docIdx, dVector in freqMtx.items():
            dP = self.__dotProduct(qVector, dVector)
            qM = self.__magnitude(qVector)
            dM = self.__magnitude(dVector)
            cosSimilarity = dP / (qM * dM)
            qList.append((docIdx, cosSimilarity))

        return sorted(qList, key=lambda similarity: similarity[1], reverse=True)

    def AnalyzeDocument(self, docIdx):
        """
        Generates a list of (entity, relation, entity) tuples as its output.

        :Parameters:
        - `docIdx`: Document's index ID (Int).
        """
        gpeList    = {}
        geolocator = Geocode()
        reader     = DirectoryReader.open(self.__indexDir)
        doc        = reader.document(docIdx)
        # Load NLTK Data
        nltkPath = os.path.dirname(os.path.realpath(__file__)) + '/../tools/nltk_data'
        nltk.data.path.append(nltkPath)

        # Named Entity Recognition
        content   = doc.get(Indexer.CONTENT)
        sentences = nltk.sent_tokenize(content)

        #ProgressBar
        print("Analazing Document {0}".format(docIdx))

        pB = ProgressBar(len(sentences), prefix='Progress:')
        # Loop over each sentence and tokenize it separately
        for sentence in sentences:
            ner = nltk.word_tokenize(sentence)
            ner = nltk.pos_tag(ner)
            ner = nltk.ne_chunk(ner)
            # Get all the Geo-Political Entities
            for subtrees in list(ner.subtrees(filter=lambda subtree: subtree.label()=='GPE')):
                entityName = ' '.join([child[0] for child in subtrees])
                if entityName not in gpeList:
                    location = geolocator.GetGPE(entityName)
                    if location:
                        gpeList.update(location)
            pB.updateProgress()
        gpeList = geolocator.GetFeatureCollection(gpeList)

        return gpeList

    def GetDocField(self, docIdx, field=CONTENT):
        """
        Get the document's field

        :Parameters:
        - `docIdx`: Document's index ID (Int).
        - `field`: Field to retrieve (Str).

        :Returns:
        - Document's field. (Str)
        """
        reader    = DirectoryReader.open(self.__indexDir)
        doc       = reader.document(docIdx)
        content   = doc.get(field)
        reader.close()

        return content

###################################################################################################
#TEST
###################################################################################################
def saveFreqMatrixByTerms():
    """
    Save the Frequency Matrix Terms vs Docs
    """
    freqMatrix = documentIndexer.FreqMatrix()
    matrixDB   = DBHandler('TermsDB')
    for value in sorted(freqMatrix):
        doc = { 'stem' : value,
                'docs' : freqMatrix[value] }
        matrixDB.Insert(doc)
    del matrixDB

def saveFreqMatrixByDocs():
    """
    Save the Frequency Matrix Docs vs Terms
    """
    freqMatrix = documentIndexer.FreqMatrix(byTerms=False)
    matrixDB   = DBHandler('DocsDB')
    for value in freqMatrix:
        doc = { 'doc'   : int(value),
                'stems' : freqMatrix[value] }
        matrixDB.Insert(doc)

def showCities(docID):
    """
    Create an HTML with the GPE in the docID
    """
    cities = documentIndexer.AnalyzeDocument(docID)
    import webbrowser

    html = ''
    for city, value in cities.items():
        apiJS = "AIzaSyCjBzqKcJoUUd1ALelOL1qeG6jgRPHYmcA"
        api   = "AIzaSyAelNyWCvnF0s2g8gfhwN31jFuCGeNjs3s"
        url   = "https://www.google.com/maps/embed/v1/place?key={0}&q={1}&center={2},{3}".format(api, value['location'], value['latitude'], value['longitude'])
        html += '<iframe width="600" height="450" frameborder="0" style="border:0" src="{0}" allowfullscreen></iframe>\n'.format(url)

    path = os.path.abspath('maps.html')
    url = 'file://' + path
    with open(path, 'w') as f:
        f.write(html)
        #Open url in new tab if possible
        webbrowser.open_new_tab(url)

###################################################################################################
#MAIN
###################################################################################################
if __name__ == "__main__":
    """
    Info Link
    https://lucene.apache.org/core/6_5_1/demo/src-html/org/apache/lucene/demo/SearchFiles.html
    http://nullege.com/codes/show/src%40l%40u%40lupyne-1.6%40examples%40__main__.py/2/lucene.initVM/python
    https://gist.github.com/mocobeta/0d2feeb59295bfad157ed06e36fd626a
    https://www.adictosaltrabajo.com/tutoriales/lucene-ana-lyzers-stemming-more-like-this/
    http://www.nltk.org/book/ch07.html
    """
    os.system('clear')

    documentIndexer = Indexer(verbose=True)
    #freqMatrix      = documentIndexer.FreqMatrix(byTerms=False)
    #List            = documentIndexer.GetSimilarity("heavy storms", freqMatrix)
    #features = documentIndexer.AnalyzeDocument(0)
    documentIndexer.GetDocField(0, "date")
###################################################################################################
#END OF FILE
###################################################################################################
