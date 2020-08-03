import lark
from os.path import join, dirname, realpath

DIR = dirname(realpath(__file__))
GRAMMAR_FILENAME = join(DIR, "grammar.lark")

with open(GRAMMAR_FILENAME) as grammar_file:
    grammar = grammar_file.read()

parser = lark.Lark(grammar)

PROGRAM = """
(function 1 2 3)
(lorem ipsum (dolor (sit amet) 4) 5)

(my
    (really
        (nested
            (function
                (call)))))
"""

tree = parser.parse(PROGRAM)
print(tree.pretty())