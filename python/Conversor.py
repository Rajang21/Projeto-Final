# -*- coding: utf-8 -*-
import fitz  # PyMUPDF
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode
from pylatexenc.latex2text import LatexNodes2Text


def decodePdf(path):
    doc = fitz.open(path)
    for page in doc:
        text = page.getText()
    return text


def decodeTex(path):
    doc = " ".join(open(path, "r").readlines()).encode("ISO-8859-1").decode("utf-8")
    return LatexNodes2Text().latex_to_text(doc)


print(decodePdf("true_or_false_question.pdf"))
print(decodeTex("answer_1_true.tex"))
