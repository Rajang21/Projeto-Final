# -*- coding: utf-8 -*-
import fitz
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode
from pylatexenc.latex2text import LatexNodes2Text


def decode(path):
    doc = fitz.open(path)
    for page in doc:
        text = page.getText()
    return text


# print(decode("true_or_false_question.pdf"))

t = LatexNodes2Text.read_input_file(fn="answer_1_true.tex")
tex = LatexWalker(open("answer_1_true.tex", "r"))
(nodelist, pos, len_) = tex.get_latex_nodes(pos=0)
