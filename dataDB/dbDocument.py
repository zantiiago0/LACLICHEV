"""
DataBase Document module
"""
###################################################################################################
#IMPORTS
###################################################################################################

###################################################################################################
#CONSTANTS
###################################################################################################

###################################################################################################
#CLASS
###################################################################################################
class DBDocument:
    """
    Contains all the article information to be stored in the database.

    :Parameters:
    - `name`:    Name of the document.
    - `url`:     URL where the document has been extracted.
    - `date`:    Document's Publication Date.
    - `content`: Content of the document (Plain text data).

    :Returns:
        - An instance of :class:`~dbDocument.DBDocument`.
    """
    def __init__(self, name, url, date, tags, content):
        self.name    = name
        self.url     = url
        self.date    = date
        self.content = content
        self.tags    = list(set(tags))

    def dictDump(self):
        """
        Return a Dictionary of the current object
        """
        return self.__dict__

class CDocument:
    """
    :Curated Document:
    - Contains all the article information to be persistently stored in the database.

    :Parameters:
    - `title`:     Name of the document. (Str)
    - `url`:       URL where the document has been extracted. (Str)
    - `date`:      Document's Publication Date. (Str)
    - `content`:   Content of the document. (Text)
    - `tags`:      Tags from the original source. (List)
    - `qTags`:     Tags obtained by the query search. (List)
    - `cities`:    Cities FeatureCollection (GeoJSON).
    - `nEntities`: Named Entities found in the document. (List of Tuples)

    :Returns:
        - An instance of :class:`~dbDocument.CDocument`.
    """
    def __init__(self, title, url, date, content, tags, qTags, cities, nEntities):
        self.title     = title
        self.url       = url
        self.date      = date
        self.content   = content
        self.tags      = list(set(tags))
        self.qTags     = list(set(qTags))
        self.cities    = cities
        self.nEntities = nEntities

    def dictDump(self):
        """
        Return a Dictionary of the current object
        """
        return self.__dict__

###################################################################################################
#TEST
###################################################################################################
if __name__ == "__main__":
    """
    TEST CODE
    """
