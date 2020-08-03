from .entities import BUILT_IN_NAMES
from . import parser

def lark_repl():
    print("REPL")
    runtime = dict(BUILT_IN_NAMES)
    ...

    while True:
        command = input("|> ")

        if command == "quit":
            print("Bye for now!")
            break

        try:
            expressions = parser.parse(command)
            for expression in expressions:
                result = expression.reduce(runtime)
                print(result)
        except Exception as e:
            print(e.__class__.__name__, e)

lark_repl()