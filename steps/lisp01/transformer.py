import lark
import json
from .entities import (
    Integer, String, Name, Call
)

@lark.v_args(inline=True)
class AlmostLispTransformer(lark.Transformer):
    @staticmethod
    def start(*expressions):
        return expressions

    @staticmethod
    def string(token):
        return String(json.loads(token.value))

    @staticmethod
    def integer(token):
        number = int(token.value)
        return Integer(number)

    @staticmethod
    def name(identifier_token):
        identifier = identifier_token.value
        return Name(identifier)

    call = Call