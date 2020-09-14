import fitz
import unidecode
from whoosh.analysis import LanguageAnalyzer


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


test = decodePdf("true_or_false_question.pdf")
print("------------------------------------------------------------------------")
print("PDF Text before text simplification:")
print("")
print(test)
print("------------------------------------------------------------------------")
print("PDF Text after text simplification:")
print("")
print(analyzeText(test))
print("------------------------------------------------------------------------")
