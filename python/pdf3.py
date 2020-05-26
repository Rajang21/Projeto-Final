# -*- coding: utf-8 -*-
import fitz  # PyMUPDF
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode
from pylatexenc.latex2text import LatexNodes2Text


def decode(path):
    doc = fitz.open(path)
    for page in doc:
        text = page.getText()
    return text


# print(decode("true_or_false_question.pdf"))

a = (
    " ".join(open("answer_1_true.tex", "r").readlines())
    .encode("ISO-8859-1")
    .decode("utf-8")
)


print(LatexNodes2Text().latex_to_text(a))
# tex = LatexWalker(
#     " ".join(open("answer_1_true.tex", "r").readlines()).encode("utf-8").decode("utf-8")
# )
# print(tex)
# (nodelist, pos, len_) = tex.get_latex_nodes(pos=0)
