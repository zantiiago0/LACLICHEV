"""
Data Explorer Module
"""
###################################################################################################
#IMPORTS
###################################################################################################
import os
import nltk

from nltk                 import Tree
from IPython.core.display import HTML

###################################################################################################
#CONSTANTS
###################################################################################################

###################################################################################################
#CLASS
###################################################################################################
class DTExplorer:
    """
    DTExplorer Class
    """

    def __init__(self):
        # Load NLTK Data
        nltkPath = os.path.dirname(os.path.realpath(__file__)) + '/../tools/nltk_data'
        nltk.data.path.append(nltkPath)
        self.__NE = []

    @staticmethod
    def HideCodeCells():
        """
        Hide code cell on Jupyter Notebook
        """
        # Hide Code Cells Jupyter
        hideCodeCSS = '''<script>
        code_show=true; 
        function code_toggle() {
        if (code_show){
        $("div.input").hide();
        } else {
        $("div.input").show();
        }
        code_show = !code_show
        } 
        $( document ).ready(code_toggle);
        </script>
        The raw code for this IPython notebook is by default hidden for easier reading.
        To toggle on/off the raw code, click <a href="javascript:code_toggle()">here</a>.'''
        return HTML(hideCodeCSS)

    @staticmethod
    def __highlightNER():
        highlightCSS = ''' <style>
        .entities {
            line-height: 2;
        }
        [data-entity] {
            padding: 0.25em 0.35em;
            margin: 0px 0.25em;
            line-height: 1;
            display: inline-block;
            border-radius: 0.25em;
            border: 1px solid;
        }
        [data-entity]::after {
            box-sizing: border-box;
            content: attr(data-entity);
            font-size: 0.6em;
            line-height: 1;
            padding: 0.35em;
            border-radius: 0.35em;
            text-transform: uppercase;
            display: inline-block;
            vertical-align: middle;
            margin: 0px 0px 0.1rem 0.5rem;
        }
        [data-entity][data-entity="PERSON"] {
            background: rgba(166, 226, 45, 0.2);
            border-color: rgb(166, 226, 45);
        }
        [data-entity][data-entity="PERSON"]::after {
            background: rgb(166, 226, 45);
        }
        [data-entity][data-entity="GPE"] {
            background: rgba(67, 198, 252, 0.2);
            border-color: rgb(67, 198, 252);
        }
        [data-entity][data-entity="GPE"]::after {
            background: rgb(67, 198, 252);
        }
        [data-entity][data-entity="DATE"] {
            background: rgba(47, 187, 171, 0.2);
            border-color: rgb(47, 187, 171);
        }
        [data-entity][data-entity="DATE"]::after {
            background: rgb(47, 187, 171);
        }
        [data-entity][data-entity="ORGANIZATION"] {
            background: rgba(255, 153, 0, 0.2);
            border-color: rgb(255, 153, 0);
        }
        [data-entity][data-entity="ORGANIZATION"]::after {
            background: rgb(255, 153, 0);
        }
        </style> '''
        return highlightCSS


    def Parse(self, contentText, showHTML=True):
        """
        Parse a Text Tree to HTML for data exploration of the content.

        :Parameters:
        - `content Tree`: NLTK Text Tree

        :Return:
        HTML String
        """
        # Named Entity Recognition
        sentences = nltk.sent_tokenize(contentText)
        # Loop over each sentence and tokenize it separately
        parsedContent = ''
        for sentence in sentences:
            ner = nltk.word_tokenize(sentence)
            ner = nltk.pos_tag(ner)
            ner = nltk.ne_chunk(ner)
            for node in ner:
                if isinstance(node, Tree):
                    entityName = ' '.join([child[0] for child in node])
                    self.__NE.append((entityName, node.label()))
                    if showHTML:
                        htmlString = '<mark data-entity="{0}">{1}</mark> '.format(node.label(), entityName)
                        parsedContent += htmlString
                elif showHTML:
                    parsedContent += '{0} '.format(node[0])

        if showHTML:
            htmlString  = DTExplorer.__highlightNER()
            htmlString += '<div class="entities">{0}</div>'.format(parsedContent)
            return HTML(htmlString)

    def GetNamedEntities(self, neTag="GPE"):
        neList = []
        for ne in self.__NE:
            if ne[1] == neTag:
                neList.append(ne[0])

        return list(set(neList))
###################################################################################################
#TEST
###################################################################################################
#if __name__ == "__main__":
