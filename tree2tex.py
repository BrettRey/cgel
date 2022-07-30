"""
Convert a CGEL tree to LaTeX.

Not yet supported: fused heads

@author: Nathan Schneider (@nschneid)
@since: 2022-07-29
"""

import re, sys
from itertools import chain
from pylatexenc.latexencode import unicode_to_latex
import cgel

def latex_quote(s):
    return unicode_to_latex(s).replace("'", r'\textquoteright{}').replace("`", r'\textquoteleft{}')

# Example tree
r'''
(.Clause.
    (.\NL{Subj}{NP}.
        (.\NL{Head}{Nom}.
            (.\NL{Head}{N}. `it')))
    (.\NL{Head}{VP}.
        (.\NL{Head}{V}. `\textquoteright s' )
        (.\NL{PredComp}{AdjP}.
            (.\NL{Head}{Adj}. `alright' )))
    (.\NL{ExtraposedSubject}{Clause}.
        (.\NL{Head}{VP}.
            (.\NL{Marker}{Subordinator}. `to' )
        (.\NL{Head}{VP}.  `say they\textquoteright re white' )
)))
'''

QTD = r'"(?:[^"\\]|\\"|\\\\)+"'
def cgel2tex(s: str) -> str:
    t = re.sub(r' (:p|:l|:subt|:subp|:note) '+QTD, '', s)   # remove punctuation, lemmas, subtokens, notes
    t = t.replace('N_pro', r'N\textsubscript{\textsc{pro}}')
    t = t.replace('V_aux', r'V\textsubscript{\textsc{aux}}')
    t = t.replace('Clause_rel', r'Clause\textsubscript{rel}')
    t = t.replace('Obj_dir', r'Obj\textsubscript{dir}')
    t = t.replace('Obj_ind', r'Obj\textsubscript{ind}')
    t = t.replace('Comp_ind', r'Comp\textsubscript{ind}')
    assert '_' not in t,t
    t = re.sub(r'^\((\S+)', r'(.\1.', t)    # root
    t = re.sub(r'(\s+):(\S+) \((\S+) / GAP',
                r'\1:\2 (\3 / GAP :t "--"', t)  # add -- terminal for gap
    t = re.sub(r'(\s+):(\S+) \((\S+) / ([^\s\)]+)',
                r'\1:\2 (\4\\textsubscript{\3}', t) # coindexation subscript
    t = re.sub(r'(\s+):(\S+) \(([^\s\)]+)',
                r'\1(.\\NL{\2}{\3}.', t)    # non-root nonterminal
    t = re.sub(r'( :t ('+QTD+'))? :correct ('+QTD+')',    # token with correction
                lambda m: "  `"+latex_quote(cgel.cgel_unquote(m.group(2) or '""') + ' [' + cgel.cgel_unquote(m.group(3)) + ']') + "'", t)
    t = re.sub(r' :t ('+QTD+')',    # token
                lambda m: "  `"+latex_quote(cgel.cgel_unquote(m.group(1)))+"'", t)
    return SHEADER + t + SFOOTER


HEADER = r'''
\documentclass[12pt]{standalone}
\usepackage{times}
\usepackage{parsetree}
\usepackage{textcomp}
\pagestyle{empty}
%----------------------------------------------------------------------
% Node labels in CGEL trees are defined with \NL, which is defined so that
% \NL{Abcd}{Xyz} yields a label with the function Abcd on the top, in
% sanserif font, followed by a colon, and the category Xyz on the bottom.
\newcommand{\NL}[2]{\begin{tabular}[t]{c}\small\textsf{#1:}\\
#2\end{tabular}}
%----------------------------------------------------------------------
\begin{document}
'''

SHEADER = r'''
\begin{parsetree}
'''

SFOOTER = r'''
\end{parsetree}
'''

FOOTER = '''
\end{document}
'''

if __name__=='__main__':
    with open('datasets/twitter.cgel') as f, open('datasets/ewt.cgel') as f2:
        i = 0
        print(HEADER)
        for tree in cgel.trees(chain(f,f2)):
            s = tree.draw()
            print(cgel2tex(s))
            i += 1
            #if i>=2: break
        print(FOOTER)
