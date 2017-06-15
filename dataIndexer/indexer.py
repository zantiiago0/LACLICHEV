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

# Lucene
import lucene

from java.nio.file                         import Paths
from org.apache.lucene.analysis.standard   import StandardAnalyzer
from org.apache.lucene.document            import Document, TextField, Field, LongPoint, StringField, FieldType
from org.apache.lucene.index               import IndexWriter, IndexWriterConfig, IndexReader, DirectoryReader, Term, IndexOptions, TermsEnum
from org.apache.lucene.store               import SimpleFSDirectory, RAMDirectory
from org.apache.lucene.util                import BytesRefIterator
from org.apache.lucene.search              import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser

# Numpy
import numpy as np

###################################################################################################
#CONSTANTS
###################################################################################################

###################################################################################################
#FUNCTIONS
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

    def FreqMatrix(self, verbose=False, saveMtx=False):
        freqDict  = {}
        reader    = DirectoryReader.open(self.__indexDir)
        numDocs   = reader.numDocs()
        timeStamp = time.clock()
        print("Generating Frequency Matrix...")
        self.__printProgressBar(0, numDocs - 1, timeStamp, prefix='Progress:')
        for docIdx in range(numDocs):
            doc      = reader.document(docIdx)
            termSize = reader.getTermVector(docIdx, Indexer.CONTENT).size()
            termItr  = reader.getTermVector(docIdx, Indexer.CONTENT).iterator()
            if verbose:
                print("Processing file: %s - Terms: %d" % (doc.get(Indexer.NAME), termSize))
            for term in BytesRefIterator.cast_(termItr):
                termText     = term.utf8ToString()
                try:
                    freqDict[termText].append(docIdx)
                except KeyError:
                    termIdx      = {termText:[docIdx]}
                    freqDict.update(termIdx)

                if verbose:
                    termInstance = Term(Indexer.CONTENT, term)
                    # Total number of occurrences of term across all documents
                    termFreq     = reader.totalTermFreq(termInstance)
                    # Number of documents containing the term.
                    docCount     = reader.docFreq(termInstance)
                    print("term: %s, termFreq = %d, docCount = %d" % (termText, termFreq, docCount))
            self.__printProgressBar(docIdx, numDocs - 1, timeStamp, prefix='Progress:')

        if saveMtx:
            fMatrix   = open(os.path.dirname(os.path.realpath(__file__)) + "/freqMtx.txt", 'w')
            numWords  = len(freqDict)
            timeStamp = time.clock()
            wordsIt   = 0

            print("Generating Frequency Matrix File...")
            self.__printProgressBar(wordsIt, numWords, timeStamp, prefix='Progress:')
            # File Generation Start
            print("+========= Frequency Matrix =========+", file=fMatrix)
            print("%20s" % (' '), end=' ', file=fMatrix)
            for docIdx in range(numDocs):
                print("D{0:0>4}".format(docIdx), end=' ', file=fMatrix)
            print(file=fMatrix)
            for word in freqDict:
                print("%20s" % (word), end=' ', file=fMatrix)
                docIt = 0
                for docIdx in range(reader.numDocs()):
                    if docIdx == freqDict[word][docIt]:
                        print("  1  ", end=' ', file=fMatrix)
                        docIt = docIt + 1 if docIt < (len(freqDict[word]) - 1) else docIt
                    else:
                        print("  0  ", end=' ', file=fMatrix)
                print(file=fMatrix)
                wordsIt += 1
                self.__printProgressBar(wordsIt, numWords, timeStamp, prefix='Progress:')

        # Close File
        fMatrix.close()
        # Close IndexReader
        reader.close()

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

    documentIndexer = Indexer(verbose=True)

    documentIndexer.FreqMatrix()
###################################################################################################
#END OF FILE
###################################################################################################
