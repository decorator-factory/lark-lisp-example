import lark
from . import transformer

parser = lark.Lark.open(
    "grammar.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=transformer.AlmostLispTransformer()
)

from . import test_entities