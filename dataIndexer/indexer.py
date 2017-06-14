"""
Indexer

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
from org.apache.lucene.document            import Document, TextField, Field, LongPoint, StringField
from org.apache.lucene.index               import IndexWriter, IndexWriterConfig,IndexReader, DirectoryReader, Term
from org.apache.lucene.store               import SimpleFSDirectory, RAMDirectory
from org.apache.lucene.util                import Version
from org.apache.lucene.search              import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser

###################################################################################################
#CONSTANTS
###################################################################################################

###################################################################################################
#FUNCTIONS
###################################################################################################
class Indexer:
    """
    The Guardian Extractor Class
    """

    def __init__(self, indexDir="", debug=False, verbose=False):
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
        # Print Indexer Information
        if verbose:
            print("Lucene version is: ", lucene.VERSION)
            print("Index Directory: ", INDEX_DIR)

    def __del__(self):
        self.__indexDir.close()

    @staticmethod
    def __getTimestamp(dateTime):
        tm    = time.strptime(dateTime, '%Y-%m-%dT%H:%M:%SZ')
        sTime = "{0:0>4}{1:0>2}{2:0>2}{3:0>2}{4:0>2}{5:0>2}".format(tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec)
        return int(sTime)

    @staticmethod
    def __getDateTime(timeStamp):
        date = datetime.datetime(year=int(timeStamp[0:4]),
                                 month=int(timeStamp[4:6]),
                                 day=int(timeStamp[6:8]),
                                 hour=int(timeStamp[8:10]),
                                 minute=int(timeStamp[10:12]),
                                 second=int(timeStamp[12:14]))
        return date.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def __qualifyTags(tags):
        sTags = ""
        for tag in tags:
            sTags += tag + '|'
        return sTags[:-1]

    def IndexDocs(self, documents, verbose=False):
        # Get the Writer Configuration
        writerConfig = IndexWriterConfig(StandardAnalyzer())
        # Get index writer
        writer       = IndexWriter(self.__indexDir, writerConfig)

        for document in documents:
            # Create a document that would we added to the index
            doc = Document()
            # Add a field to this document
            doc.add(TextField("name",    document['name'],    Field.Store.YES))
            doc.add(TextField("content", document['content'], Field.Store.YES))
            doc.add(LongPoint("date",    self. __getTimestamp(document['date'])))
            doc.add(StringField("url",   document['url'],     Field.Store.YES))
            doc.add(TextField("tags", self.__qualifyTags(document['tags']), Field.Store.YES))
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
                writer.updateDocument(Term("name", document['name']), doc)

        # Print index information and close writer
        print("Indexed %d documents (%d docs in index)" % (len(documents), writer.numDocs()))
        writer.close()

    def Search(self, query, maxResult=1000):
        # Get the Index Directory
        reader      = DirectoryReader.open(self.__indexDir)
        searcher    = IndexSearcher(reader)
        # Create a query
        queryParser = QueryParser("tags", StandardAnalyzer()).parse(query)
        # Do a search
        hits        = searcher.search(queryParser, maxResult)
        print("Found %d document(s) that matched query '%s':" % (hits.totalHits, queryParser))
        for hit in hits.scoreDocs:
            doc = searcher.doc(hit.doc)
            print("Document Nº: %d - Score: %.5f" % (hit.doc, hit.score))
            print("Name: " + doc.get('name'))
            print("Tags: " + doc.get('tags') + "\n")
        reader.close()

###################################################################################################
#END OF FILE
###################################################################################################
