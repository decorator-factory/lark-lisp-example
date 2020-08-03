import lark
from os.path import join, dirname, realpath
from . import transformer

DIR = dirname(realpath(__file__))
GRAMMAR_FILENAME = join(DIR, "grammar.lark")

with open(GRAMMAR_FILENAME) as grammar_file:
    grammar = grammar_file.read()

parser = lark.Lark(
      grammar,
      parser="lalr",
      transformer=transformer.AlmostLispTransformer()
)

from . import test_entities