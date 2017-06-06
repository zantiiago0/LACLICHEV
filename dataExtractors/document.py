"""
Document Object Definition
"""

class Document(object):
    """
    Contains all the article information to be stored in the database.

    :Parameters:
    - `name`:    Name of the document.
    - `url`:     URL where the document has been extracted.
    - `date`:    Document's Publication Date.
    - `content`: Content of the document (Plain text data).

    :Returns:
        - An instance of :class:`~dataExtractors.document`.
    """
    def __init__(self, name, url, date, content):
        self.name    = name
        self.url     = url
        self.date    = date
        self.content = content

    def dictDump(self):
        """
        Return a Dictionary of the current object
        """
        return self.__dict__
