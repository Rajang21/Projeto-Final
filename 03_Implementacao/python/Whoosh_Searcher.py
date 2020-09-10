import os
import fitz
import unidecode
import shutil

from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

import voila
import ipywidgets

from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode
from pylatexenc.latex2text import LatexNodes2Text

from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh.analysis import LanguageAnalyzer
from whoosh.analysis import StemmingAnalyzer
from whoosh.index import EmptyIndexError


def analyzeText(text):
    """
    Analyzes the text to facilitate the searching of words.

    Creates an analizer for the Portuguese language which creates a lower case filter,
    a stop word filter and a stemming filter to process the text it receives.

    Parameters
    ----------
    arg1 : string
        Document in simple text format

    Returns
    -------
    string
        Document text after being processed

    """

    languageAnalyzer = LanguageAnalyzer("pt")
    langText = ""

    for token in languageAnalyzer(text):
        langText += "".join(token.text)
        langText += " "

    return langText


class WhooshHandler:
    """
    Responsible for the creation, modification and deletion of Indexes.
    Creates using the function createIndex.
    Deletes using the function deleteIndex.
    Modifies using the funcion writeDoc.
    """

    specialCharacters = ["´", "¸", "˜", "`", "^"]
    indexFolder = None
    homeWorkIndex = None
    directory = None
    questionFolders = None

    def __init__(self, indexFolder):
        """
        WhooshHandler constructor.

        Creates an instance of the class WhooshHandler with the desired folder.

        Parameters
        ----------
        arg1 : string
            Name of the desired folder.

        """
        assert indexFolder != None, "Index folder name cannot be None"
        assert isinstance(indexFolder, str), "Index folder name must be a string"
        assert indexFolder, "Index folder name cannot be empty"

        """assert directory != None, 'Documents directory cannot be None'
        assert isinstance(directory,str), 'Documents directory must be a string'
        assert directory , 'Documents directory cannot be empty"""

        self.indexFolder = indexFolder
        self.homeWorkIndex = self.indexFolder + "_HomeWork"
        # self.directory = directory
        # self.questionFolders = [x for x in os.listdir(self.directory)]

    # ----------------------------------------------------------------------------

    def createIndex(self):
        """
        Creates an index to store documents and apply the search in.

        Creates an index that serves as an database to store processed documents in and later apply the search
        in with the desired parameters.

        Returns
        -------
        Index
            Index created.

        """
        schema = Schema(
            path=ID(stored=True, unique=True),
            content=TEXT(stored=True, lang="pt"),
            date=DATETIME(stored=True, sortable=True),
            tags=KEYWORD(stored=True),
            nOccurrences=NUMERIC(stored=True, sortable=True),
        )

        if not os.path.exists("IndexFiles.txt"):
            f = open("IndexFiles.txt", "w").close()

        if not os.path.exists(self.indexFolder):
            os.mkdir(self.indexFolder)

        txtFile = open("IndexFiles.txt", "r").readlines()
        txtFile = [index.replace("\n", "") for index in txtFile]

        boolea = self.indexFolder in txtFile

        if not (self.indexFolder in txtFile):
            with open("IndexFiles.txt", "a") as out:
                out.write(self.indexFolder + "\n")

        #         homeWorkSchema = Schema(number=ID(stored=True, unique=True),
        #                          content=TEXT(stored=True))

        #         if not os.path.exists(self.homeWorkIndex):
        #             os.mkdir(self.homeWorkIndex)

        ix = create_in(self.indexFolder, schema)
        #         hix = create_in(self.homeWorkIndex, homeWorkSchema)

        return ix

    # ----------------------------------------------------------------------------

    def __decodePdf(self, path):
        """
        Decodes pdf files.

        Using the PyMuPDF module, decodes pdf files into plain text ready to be processed.

        Parameters
        ----------
        arg1 : string
            Path to the desired pdf file

        Returns
        -------
        string
            Document in plain text without special characters.

        """
        doc = fitz.open(path)
        for page in doc:
            text = page.getText()
        return self.__removeSpecialChar(text)

    def __decodeTex(self, path):
        """
        Decodes LaTeX files.

        Using the pylatexenc module, decodes LaTeX files into plain text ready to be processed.

        Parameters
        ----------
        arg1 : string
            Path to the desired LaTeX file

        Returns
        -------
        string
            Document in plain text without special characters.

        """
        doc = " ".join(open(path, "r").readlines()).encode("ISO-8859-1").decode("utf-8")
        a = LatexNodes2Text().latex_to_text(doc)
        a = unidecode.unidecode(a)
        return self.__removeSpecialChar(a)

    def __decodePy(self, path):
        """
        Decodes python files.

        Because python files are already in plain text we just remove every special character in the file.

        Parameters
        ----------
        arg1 : string
            Path to the desired pdf file

        Returns
        -------
        string
            Document in plain text without special characters.

        """
        if os.path.isfile(path):
            doc = open(path, "r")
            return self.__removeSpecialChar(doc.read())
        else:
            return None

    def __removeSpecialChar(self, text):
        """
        Removes every special character in the text.

        Replaces every special character in the text with nothing.

        Parameters
        ----------
        arg1 : string
            The text to remove special characters from.

        Returns
        -------
        string
            Text without special characters.

        """
        for sChar in self.specialCharacters:
            text = text.replace(sChar, "")

        return str(text)

    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def deleteIndex(self, name):
        """
        Deletes an index.

        Deletes an index from the computer after checking if an index with the desired name exists in the
        IndexFiles file. Also deletes the index name from the IndexFiles file.

        Parameters
        ----------
        arg1 : string
            Name of the index to be deleted.

        Returns
        -------
        bool
            Result of the operation.
        string
            Message to be displayed.

        """
        deleted = False
        message = "Error"

        if os.path.exists("IndexFiles.txt"):
            with open("IndexFiles.txt", "r") as f:
                indexListFile = f.readlines()

        else:
            deleted = False
            message = "No valid Indexes exist."
            return [deleted, message]

        for i in indexListFile:
            if i.strip("\n") == name:
                try:
                    shutil.rmtree(name)
                    shutil.rmtree(name + "_HomeWork")
                    deleted = True
                    message = "Index successfully deleted."
                    break

                except:
                    deleted = False
                    message = "Error ocurred. Please verify that the desired Index directory exists."
                    break
            else:
                deleted = False
                message = "Please insert a valid Index name."

        if deleted == True:
            with open("IndexFiles.txt", "w") as f:
                for line in indexListFile:
                    if line.strip("\n") != name:
                        f.write(line)

        return [deleted, message]

    def writeDoc(self, directory, occurrences=0):
        """
        Writes one or several documents in the index.

        Walks the directory path provided looking for directories with question in the name,
        opens the first version of every question found and adds the question in pdf format and LaTeX and python
        if available.

        Parameters
        ----------
        arg1 : string
            Path of the directory of questions to be added
        arg2 : int
            Inicial number of occurrences of the files to be added.

        Returns
        -------
        bool
            Result of the operation.
        string
            Message to be displayed.

        """
        flag = False
        try:
            ix = open_dir(self.indexFolder)
        except EmptyIndexError:
            return (
                False,
                (
                    "The index provided does not exist, make sure you add it before using it and do not "
                    + "delete it manually"
                ),
            )

        addedDirs = ""

        for root, dirs, files in os.walk(directory):
            for d in dirs:
                if d.find("question") >= 0:
                    addedDirs += root + "\\" + d + ", "
                    path = root + "\\" + d + "\\version_1\\"
                    if os.path.exists(path):
                        if not flag:
                            flag = self.__writeDoc2(ix, path, occurrences)
                        else:
                            self.__writeDoc2(ix, path, occurrences)
        if not flag:
            return (
                False,
                (
                    "Unfortunately it was not possible to find any exercises in the directory provided!"
                    + "Make sure the exercises contain the following format"
                    + " ...\\question_x\\version_x\\true_or_false_question.x"
                ),
            )
        else:
            return (
                True,
                (
                    "The following exercise folders were found and added to the index:"
                    + addedDirs
                ),
            )

    def __writeDoc2(self, ix, path, occurrences):
        """
        Writes single documents into the Index.

        Receives the path to a single question directory and grabs the necessary pdf, LaTeX and python files to add
        to the Index. Also checks to see if the files are already in the Index before adding them.

        Parameters
        ----------
        arg1 : Index
            Index to add the documents to.
        arg2 : string
            Path to the question directory.
        arg3 : int
            Inicial number of occurrences for the file.

        Returns
        -------
        bool
            Value of the operation.

        """
        writer = ix.writer()
        dateNow = dt.now()
        pathPdf = path + "true_or_false_question.pdf"
        textPdf = self.__decodePdf(pathPdf)
        pathPy = path + "program.py"
        textPy = self.__decodePy(pathPy)
        pathTex = path + "true_or_false_question.tex"
        textTex = self.__decodeTex(pathTex)

        finalPdfText = analyzeText(textPdf)
        #         print(finalPdfText)
        flag = False

        with ix.searcher() as seacher:
            query = QueryParser("content", schema=ix.schema)
            parse = query.parse(finalPdfText)
            result = seacher.search(parse)
            flag = True
            if not result.is_empty():
                prevOc = result[0]["nOccurrences"]
                prevPath = result[0]["path"]
                prevDate = result[0]["date"]
                prevTags = result[0]["tags"]
                writer.update_document(
                    path=prevPath,
                    content=finalPdfText,
                    date=prevDate,
                    tags=prevTags,
                    nOccurrences=prevOc + 1,
                )
            else:
                writer.add_document(
                    path=pathPdf,
                    content=finalPdfText,
                    date=dateNow,
                    tags="pdf",
                    nOccurrences=1,
                )

            if textPy is not None:
                writer.add_document(
                    path=pathPy, content=analyzeText(textPy), date=dateNow, tags="py"
                )

            if textPy is not None:
                textTex += textPy
            writer.add_document(
                path=pathTex, content=analyzeText(textTex), date=dateNow, tags="tex"
            )

        writer.commit()

        return flag

    # ----------------------------------------------------------------------------
    """
    def addHomeWork(self,questionsPath):

        ix = open_dir(self.indexFolder)

        hix = open_dir(self.homeWorkIndex)
        hixWriter = hix.writer()
        documentsNum = hix.searcher().doc_count_all()

        with ix.searcher() as searcher:
            query = QueryParser("path", schema=ix.schema)

            for path in questionsPath:
                questionPath = path + "\\version_1\\true_or_false_question.pdf"

                parse = query.parse(questionPath)
                result = searcher.search(parse)
#                 print(result)
                if(not result.is_empty()):
                    self.writeDoc(path, False, result[0]["nOccurrences"] + 1);
                else:
                    self.writeDoc(path, False, 0);

        hixWriter.commit()
"""


# ----------------------------------------------------------------------------


class Searcher:
    """
    Responsible for the searching and deleting of documents in an Index.
    """

    specialCharacters = ["´", "¸", "˜", "`", "^"]
    indexFolder = None

    def __init__(self, indexFolder):
        """
        Searcher constructor.

        Creates a instance of the Searcher class using the path to the folder of the desired Index.

        Parameters
        ----------
        arg1 : string
            Path to the Index folder

        """
        assert indexFolder != None, "Index folder name cannot be None"
        assert isinstance(indexFolder, str), "Index folder name must be a string"
        assert indexFolder, "Index folder name cannot be empty"

        self.indexFolder = indexFolder

    def deleteEntry(self, doc_path):
        """
        Deletes a document from the Index.

        Given the path to the question directory, deletes every pdf, LaTeX and python file
        referent to that question from the Index.

        Parameters
        ----------
        arg1 : string
            Path to the question directory.

        Returns
        -------
        bool
            Result of the operation.
        string
            Message to display.

        """
        try:
            ix = open_dir(self.indexFolder)
        except EmptyIndexError:
            return [
                False,
                (
                    "The index provided does not exist, make sure you add it before using it and do not "
                    + "delete it manually"
                ),
            ]
        writer = ix.writer()
        message = ""
        deleted = False
        doc_path += "\\version_1\\"
        try:
            writer.delete_by_term("path", doc_path + "true_or_false_question.pdf")
            writer.delete_by_term("path", doc_path + "program.py")
            writer.delete_by_term("path", doc_path + "true_or_false_question.tex")
            writer.commit()
            message = "Document successfully deleted."
            deleted = True
        except:
            message = "Please verify the document exists."
            deleted = False

        return [deleted, message]

    def parser(self, keyword, docType="all", sortType="None", fromDate="all time"):
        """
        Searches an Index for documents.

        Searches the Index for documents containing the selected keywords, with the selected parameters and the
        selected sorting method.

        Parameters
        ----------
        keyword : string
            Keywords to look for in the documents
        docType : string{'all',pdf','tex','py'}
            Type of document to look for.
        sortType: string{'None','By Number of ocurrences', 'By Date'}
            Sorting method to use.
        fromDate : string{'all time','this year', 'this month', 'this week'}
            Time interval to look for documents in.

        Returns
        -------
        bool
            Result of the operation.
        array
            Documents found in the search.

        """
        try:
            ix = open_dir(self.indexFolder)
        except EmptyIndexError:
            return [
                False,
                (
                    "The index provided does not exist, make sure you add it before using it and do not "
                    + "delete it manually"
                ),
            ]

        resultArray = []
        keyword = analyzeText(unidecode.unidecode(keyword))

        today = dt.now()
        date = ""

        if keyword == "":
            parseQuery = ""
        else:
            parseQuery = "content:" + keyword

        if fromDate != "all time":
            if fromDate == "this year":
                date = today - relativedelta(years=1)
            elif fromDate == "this month":
                date = today - relativedelta(months=1)
            elif fromDate == "this week":
                date = today - relativedelta(weeks=1)

            parseQuery = (
                parseQuery
                + " "
                + u"date:["
                + date.strftime("%Y%m%d")
                + " to "
                + today.strftime("%Y%m%d")
                + "]"
            )

        with ix.searcher() as searcher:
            if docType == "all":
                query = MultifieldParser(["content", "date"], schema=ix.schema).parse(
                    parseQuery
                )
            else:
                query = MultifieldParser(
                    ["content", "date", "tags"], schema=ix.schema
                ).parse(parseQuery + " tags:" + docType)

            results = ""

            if sortType == "By Date":
                results = searcher.search(query, sortedby="date", reverse=True)
            elif sortType == "By Number of ocurrences":
                results = searcher.search(query, sortedby="nOccurrences", reverse=True)
            else:
                results = searcher.search(query)

            if results.is_empty():
                return (
                    False,
                    (
                        "Não foram encontrados resultados com estes parâmetros de pesquisa"
                    ),
                )
            else:
                for result in results:
                    #                     result["nOccurrences"]
                    path = result["path"]
                    tag = result["tags"]

                    resultArray.append([path, tag])

        return True, resultArray
