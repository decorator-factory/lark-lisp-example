from . import parser

def lark_repl():
    print("REPL")
    while True:
        command = input("|> ")

        if command == "quit":
            print("Bye for now!")
            break

        try:
            tree = parser.parse(command)
            print(tree.pretty())
        except Exception:
            print("Syntax error!")

lark_repl()