import fitz
import unidecode

from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode
from pylatexenc.latex2text import LatexNodes2Text


def decodePdf(path):
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
    return removeSpecialChar(text)


def decodeTex(path):
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
    return removeSpecialChar(a)


def removeSpecialChar(text):
    specialCharacters = ["´", "¸", "˜", "`", "^"]
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
    for sChar in specialCharacters:
        text = text.replace(sChar, "")

    return str(text)


print("------------------------------------------------------------------------")
print("PDF File decoded to Simple Text:")
print("")
print(decodePdf("true_or_false_question.pdf"))
print("")
print("------------------------------------------------------------------------")
print("")
print("LaTeX File decoded to Simple Text:")
print(decodeTex("true_or_false_question.tex"))
print("------------------------------------------------------------------------")
