# Import PyPDF2 Library
import PyPDF2
import re
import os


def pdftotext(pdfFile):
    page = pdfFile.getPage(0)
    text = page.extractText().encode("utf-8")
    return text


def searchtext(keyword, text):
    search = re.search(keyword, text)
    return search


pdf = PyPDF2.PdfFileReader("true_or_false_question.pdf")
print(pdftotext(pdf))
