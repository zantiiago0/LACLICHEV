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

# Lucene
import lucene
from java.nio.file                         import Paths
from org.apache.lucene.analysis.standard   import StandardAnalyzer
from org.apache.lucene.document            import Document, TextField, Field
from org.apache.lucene.index               import IndexWriter, IndexWriterConfig,IndexReader, DirectoryReader
from org.apache.lucene.store               import SimpleFSDirectory
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

    def __init__(self, indexDir="", verbose=False):
        if indexDir != "":
            INDEX_DIR = indexDir
        else:
            INDEX_DIR = os.path.dirname(os.path.realpath(__file__)) + "/luceneIndex"

        if not os.path.exists(INDEX_DIR):
            os.makedirs(INDEX_DIR)
        # Initialize lucene and JVM
        lucene.initVM()
        # Get index storage
        self.__indexDir = SimpleFSDirectory(Paths.get(INDEX_DIR))
        if verbose:
            print("Lucene version is: ", lucene.VERSION)
            print("Index Directory: ", INDEX_DIR)

    def IndexDocument(self, *documents):
        # Get the Writer Configuration
        writerConfig = IndexWriterConfig(StandardAnalyzer())
        # Get index writer
        writer       = IndexWriter(self.__indexDir, writerConfig)

        for document in documents:
            # Create a document that would we added to the index
            doc = Document()
            # Add a field to this document
            doc.add(TextField("name",    document['name'],    Field.Store.YES))
            doc.add(TextField("url",     document['url'],     Field.Store.YES))
            doc.add(TextField("date",    document['date'],    Field.Store.YES))
            doc.add(TextField("content", document['content'], Field.Store.YES))
            #doc.add(TextField("tags",    document['tags'],    Field.Store.YES))
            # Add the document to the index
            writer.addDocument(doc)
        # Print index information and close writer
        print("Indexed %d documents (%d docs in index)" % (len(documents), writer.numDocs()))
        writer.close()
        return

    def Search(self, query, maxResult=1000):
        # Get the Index Directory
        reader      = DirectoryReader.open(self.__indexDir)
        searcher    = IndexSearcher(reader)
        # Create a query
        queryParser = QueryParser("name", StandardAnalyzer()).parse(query)
        # Do a search
        hits        = searcher.search(queryParser, maxResult)
        print("Found %d document(s) that matched query '%s':" % (hits.totalHits, queryParser))
        for hit in hits.scoreDocs:
            print(hit.score, hit.doc, hit.toString())
            doc = searcher.doc(hit.doc)
            print(doc.get("name").encode("utf-8"))

###################################################################################################
#END OF FILE
###################################################################################################
