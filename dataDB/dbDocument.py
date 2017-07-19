"""
DataBase Document module
"""
###################################################################################################
#IMPORTS
###################################################################################################
import os

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
        - An instance of :class:`~dataExtractors.document`.
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

###################################################################################################
#TEST
###################################################################################################
if __name__ == "__main__":
    """
    TEST CODE
    """
    from plotly import offline as pOff
    from plotly.graph_objs import Scatter, Layout

    pOff.init_notebook_mode(connected=True)

    pOff.iplot({
        "data": [Scatter(x=[1, 2, 3, 4], y=[4, 3, 2, 1])],
        "layout": Layout(title="hello world")
    })