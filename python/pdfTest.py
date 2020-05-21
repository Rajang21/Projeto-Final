# Import PyPDF2 Library
import PyPDF2
import re
import os

os.chdir(
    "C:\\Users\\ASUS\\Desktop\\Semestre6\\Projeto\\Projeto1\\Projeto-Final\\python"
)


def pdftotext(pdfFile):
    pdfText = []
    numPages = pdfFile.getNumPages()

    for i in range(0, numPages):
        pdfPage = pdfFile.getPage(i)
        Text = pdfPage.extractText()
        pdfText.append(Text)

    return pdfText


def searchtext(keyword, text):
    search = re.search(keyword, text)
    return search


pdf = PyPDF2.PdfFileReader("python/true_or_false_question.pdf")
print(pdf)
