# Creating a lisp-like language in Python using Lark

---

# 0. LISP

Lisp is a very old functional language famous for its extremely simple
syntax. Nowadays, people ue dialects of Lisp such as `Scheme`, `Racket`, and
`Clojure`.

We're going to build a simplified version of `Lisp` at first, and then add
advanced features like closures and user-defined functions.

Let's call our language `AlmostLisp`.

# 1. Basic version of `AlmostLisp`

## 1-1. Syntax of our language

Each program in `AlmostLisp` is a sequence of expressions. To execute
a program, a virtual machine will execute each expression step-by-step.

An expression is either of:

1. Integer (like `5` or `0` or `-1024`)
2. String (like `"Hello, world!"` or `"Line 1\nLine 2"` or `""`)
3. Name (like `greeting` or `my-name`)
4. Function call (like `(square 6)` or `(+ 10 3)`)

And that's it for now. Function calls are expressed as _s-expressions_:
it's a way of expressing a tree-like structure.

The syntax for calling a function `foo-bar` with arguments `x` and `y` is
`(foo-bar x y)`.

As you can see, a name can contain special characters like `-` and `+`.

## 1-2. Defining the grammar for `lark-parser`

First of all, let's ignore all whitespace and python-style comments:

```js
COMMENT: /#.*/
%import common.WS
%ignore COMMENT
%ignore WS
```

A program is a sequence of one or more expression:

```js
start: expression+
```

An expression is either an integer, a string, a name or a function call.

```js
expression: integer
          | string
          | name
          | call
```

We can import `SIGNED_INTEGER` and `ESCAPED_STRING` terminals
from the `common` grammar:

```js
integer: SIGNED_INT
string: ESCAPED_STRING

%import common.SIGNED_INT
%import common.ESCAPED_STRING
```

An identifier can consist of letters, digits, and some special
characters, but cannot start with a digit or a minus and a digit
(to prevent collsions with numbers).

```js
IDENTIFIER: /(?![0-9])(?!-[0-9])[-+*\/^?!a-zA-Z0-9]+/
name: IDENTIFIER
```

And a call is an expression for the function, then for the arguments:
```js
call: "(" expression+ ")"
```

And now we have a complete grammar:
```js
start: expression+

expression: integer
          | string
          | name
          | call

integer: SIGNED_INT
string: ESCAPED_STRING
name: IDENTIFIER
call: "(" expression+ ")"

IDENTIFIER: /(?![0-9])[-+*\/^?!a-zA-Z0-9]+/

%import common.SIGNED_INT
%import common.ESCAPED_STRING

COMMENT: /#.*/
%import common.WS
%ignore COMMENT
%ignore WS
```

You can find all the relevant files in `steps/lisp01`

## 1-3. Testing our grammar

Now let's create a sample program and just parse it.


Let's store the grammar as a separate file. It's pretty convenient,
especially if you have a plugin that highlights the grammar syntax.

First, let's locate and open the grammar file, and then build the
parser.
```python
import lark

parser = lark.Lark.open("grammar.lark", rel_to=__file__)
```

Then, let's load our sample program and parse it, and then we'll
pretty-print the resulting tree.

```py
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
```

You should get something like this:
<details>
  <summary>Syntax tree 1</summary>

```
start
  expression
    call
      expression
        name	function
      expression
        integer	1
      expression
        integer	2
      expression
        integer	3
  expression
    call
      expression
        name	lorem
      expression
        name	ipsum
      expression
        call
          expression
            name	dolor
          expression
            call
              expression
                name	sit
              expression
                name	amet
          expression
            integer	4
      expression
        integer	5
  expression
    call
      expression
        name	my
      expression
        call
          expression
            name	really
          expression
            call
              expression
                name	nested
              expression
                call
                  expression
                    name	function
                  expression
                    call
                      expression
                        name	call
```

</details>

It's so annoying that every tree node has `expression` before it.
We can remove this annoyance by putting `?` before `expression` in
the grammar, and now `expression` will not appear in the tree:

```js
?expression: integer
           | string
           | name
           | call
```

And now it's much nicer:

<details>
  <summary>Syntax tree 2</summary>

```
start
  call
    name	function
    integer	1
    integer	2
    integer	3
  call
    name	lorem
    name	ipsum
    call
      name	dolor
      call
        name	sit
        name	amet
      integer	4
    integer	5
  call
    name	my
    call
      name	really
      call
        name	nested
        call
          name	function
          call
            name	call

```

</details>

## 1-4. Creating runtime representations of our entities

Each virtual machine-based language stores its entities
like integers, strings, objects, functions and so on and performs
operations on them.

What entities will `AlmostLisp` have at runtime?

1. Integer
2. String
3. Name (when evaluated, loads a global name)
4. Function (can be called)
5. Call (when evaluated, performs some call)

To evaluate a call or a name, we will need to give tham a
dictionary that will map names to entities. Let's create the `Entity`
base class.

The `compute_one_step` method will reduce the expression one step.
If an entity is "final", like an Integer, it should return itself.
The `reduce` method will reduce the expression until it's final.

Since we can perform calls, let's also add a `call` method that will
raise an error by default.

```python
class Entity:
    def compute_one_step(self, runtime):
        """Perform one step of computation"""
        return self

    def reduce(self, runtime):
        """Fully reduce an expression"""
        state = self
        while True:
            next_state = state.compute_one_step(runtime)
            if next_state is state:
                return state
            state = next_state

    def call(self, runtime, *args):
        raise TypeError(f"Cannot call {self!r}")
```

_(`{self!r}` instead of `{self}` means that `repr` will be called on
`self` instead of `str`)_

`String`s and `Integer`s are just wrappers around Python objects.
They evaluate to themselves. Let's also add `__str__` and `__repr__`
methods for easier debugging.

```py
class Integer(Entity):
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"Integer({self.value})"


class String(Entity):
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return repr(self.value)

    def __repr__(self):
        return f"String({self.value})"
```

A _Name_ entity will reach to the runtime and grab the value we need.

```python
class Name(Entity):
    def __init__(self, name: str):
        self.name = name

    def compute_one_step(self, runtime):
        return runtime[self.name]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Name({self.name})"
```

For now, we'll only have built-in functions. A built-in function
is a simple wrapper around a built-in function.
`compute_one_step` for `Call`, and we get `reduce` for free.

```py
class Function(Entity):
    def __init__(self, name: str, fn):
        self.name = name
        self.fn = fn

    def call(self, runtime, *args):
        evaluated_args = (arg.reduce(runtime) for arg in args)
        return self.fn(runtime, *evaluated_args)

    def __repr__(self):
        return f"Function({self.name!r}, {self.fn!r})"


class Call(Entity):
    def __init__(self, fn: Entity, *args: Entity):
        self.fn = fn
        self.args = args

    def compute_one_step(self, runtime):
        evaluated_fn = self.fn.reduce(runtime)
        return evaluated_fn.call(runtime, *self.args)
```

The language is pretty useless if there aren't any built-in functions.
So let's add a few.


```python
BUILT_IN_NAMES = {} # name -> Entity

def add(_runtime, a: Integer, b: Integer):
    return Integer(a.value + b.value)
BUILT_IN_NAMES["+"] = Function("+", add)

def multiply(_runtime, a: Integer, b: Integer):
    return Integer(a.value * b.value)
BUILT_IN_NAMES["*"] = Function("*", multiply)
```

By now you're probably bored with writing an assignment every time.
Let's make a decorator (actually a decorator factory) to
simpify the process.

```python
def register(name: str):
    def decorator(fn):
        BUILT_IN_NAMES[name] = Function(name, fn)
        return fn
    return decorator
```

and now it's so much easier to define a new function:

```python
@register("-")
def subtract(_runtime, a: Integer, b: Integer):
    return Integer(a.value - b.value)

@register("^")
def power(_runtime, a: Integer, b: Integer):
    return Integer(a.value ** b.value)
```

If you haven't heard of decorators in Python, check out [this article by Real Python](https://realpython.com/primer-on-python-decorators/).

Let's define a function called `x^2+y^2` that will
return a sum of squares of given integers.
```python
@register("x^2+y^2")
def sum_of_squares(_runtime, x: Integer, y: Integer):
    return Call(
        Name("+"),
        Call(Name("^"), x, Integer(2)),
        Call(Name("^"), y, Integer(2)),
    )
```

## 1-5. Testing our representations

Let's write some tests for `entities.py`. We won't use any
testing framework, so you don't need any previous knowledge for that.

Create `test_entities.py` and paste this setup code:

```py
def assert_equals(a, b):
    """if two values aren't equal, raise an error"""
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}") from None

def run_tests():
    """Run all function whose names start with test_"""
    for name, value in globals().items():
        if name.startswith("test_"):
            print(f"Runing {name}...")
            value()

### tests

def test_passes():
    assert_equals(1, 1)

def test_fails():
    assert_equals(1, 0)

###

run_tests()
```

running the file should give you this output:

```
Runing test_passes...
Runing test_fails...
Traceback (most recent call last):
    ...
AssertionError: 1 != 0
```

In `__init__.py`, remove the `print`-based test and add these lines:
```py
from . import test_entities
```

Now let's replace the stub tests with actual tests.

```py
from . import entities as e
# ... setup code

def test_integers_are_final():
    assert_equals(
        e.Integer(1).reduce({}),
        e.Integer(1)
    )
```

Now simply import the package, like this: `python3 -c "import steps.lisp01"`.
You should get this error:
```py
AssertionError: Integer(1) != Integer(1)
```
This is expected: we didn't define equailty for `Integer`. Let's do that for
`Integer` and `String`:
```py
    def __eq__(self, other):
        if not isinstance(other, Integer):
            return False
        return other.value == self.value

    ...

    def __eq__(self, other):
        if not isinstance(other, String):
            return False
        return other.value == self.value
```

Run the tests again, and there shouldn't be any errors. This means that all
the tests pass. Now let's test variable names.

```py
def test_names_work():
    runtime = {"answer": e.Integer(42)}
    assert_equals(
        e.Name("answer").reduce(runtime),
        e.Integer(42)
    )
```

You can "nest" names: a variable could be a reference to another name.

```py
def test_nested_names_work():
    runtime = {"answer": e.Integer(42),
               "universe": e.Name("answer"),
               "everything": e.Name("universe")}
    assert_equals(
        e.Name("universe").reduce(runtime),
        e.Integer(42)
    )
    assert_equals(
        e.Name("everything").reduce(runtime),
        e.Integer(42)
    )
```

Now let's test our arithmetic functions.

```py
def test_addition():
    runtime = dict(e.BUILT_IN_NAMES)
    assert_equals(
        e.Call(e.Name("+"), e.Integer(2), e.Integer(5)).reduce(runtime),
        e.Integer(7)
    )

def test_subtraction():
    runtime = dict(e.BUILT_IN_NAMES)
    assert_equals(
        e.Call(e.Name("-"), e.Integer(2), e.Integer(5)).reduce(runtime),
        e.Integer(-3)
    )

def test_square_sum():
    runtime = dict(e.BUILT_IN_NAMES)
    assert_equals(
        e.Call(e.Name("x^2+y^2"), e.Integer(2), e.Integer(5)).reduce(runtime),
        e.Integer(29) # 2**2 + 5**2 = 4 + 25 = 29
    )
```
You can write more tests if you want.


## 1-5. Creating the REPL

REPL (read-evaluate-print loop) is a popular tool in many languages, including
Python. Our REPL will read in lines of `AlmostLisp` and output the syntax tree.

Let's create `__main__.py`.

```py
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
```

Now you can run the package as a module: `python3 -m steps.lisp1`.

<details>
  <summary>REPL output</summary>

```bash
$ python3 -m steps.lisp1
```
```clojure
Runing test_integers_are_final...
Runing test_names_work...
Runing test_nested_names_work...
Runing test_addition...
Runing test_subtraction...
Runing test_square_sum...
REPL
|> (1)
start
  call
    integer	1

|> (+ 2 3)
start
  call
    name	+
    integer	2
    integer	3

|> (hello (lorem "ipsum"))
start
  call
    name	hello
    call
      name	lorem
      string	"ipsum"

|> quit
Bye for now!

```

</details>


## 1-6. Connecting the internal representation and the parser

Let's create a new file and call it `transformer.py`. We will use
`lark.Transformer` to convert the raw tree into an _abstract syntax tree_.

If you read the JSON tutorial, you should be familiar with tree transformers.
We will use `lark.v_args(inline=True)` so that our methods will receive the
arguments as `*args`, not as a single container argument.

As we don't need to keep track of any state, we will use static method in place
of normal methods.

```py
import lark
import json
from .entities import (
    Integer, String, Name, Call
)

@lark.v_args(inline=True)
class AlmostLispTransformer(lark.Transformer):
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

    @staticmethod
    def call(fn, *args):
        return Call(fn, *args)
```

Now let's go back to `__init__.py` and make the parser automatically
transform the tree:

```diff
+ from . import transformer
...
- parser = ...
+ parser = lark.Lark.open(
+    "grammar.lark",
+    rel_to=__file__,
+   parser="lalr",
+   transformer=transformer.AlmostLispTransformer()
+ )
```

Now parsing something will produce a tuple of expressions. This breaks our
REPL, so let's fix it now.

```diff
-           tree = parser.parse(command)
-           print(tree.pretty())
+           expressions = parser.parse(command)
+           for expression in expressions:
+               print(expression)
```

This is what you should see:
```clj
REPL
|> (+ 1 2)
Call(+, Integer(1), Integer(2))
```

Now let's create a `runtime` and actually compute the expressions.

#### 1. Create the runtime
```diff
+ from .entities import BUILT_IN_NAMES
...
def lark_repl():
    print("REPL")
+   runtime = dict(BUILT_IN_NAMES)
    ...
-           print(expression)
+           result = expression.reduce(runtime)
+           print(result)
```

This is what you should see now:
```clj
REPL
|> (+ 1 2)
3
```

We're almost done. Instead of printing "Syntax error", let's report
the actual error.

```diff
-       except Exception:
-           print("Syntax error!")
+       except Exception as e:
+           print(e.__class__.__name__, e)
```

Now it's a bit more descriptive:
```clj
|> ()
UnexpectedToken Unexpected token Token(RPAR, ')') at line 1, column 2.
Expected one of:
	* LPAR
	* IDENTIFIER
	* SIGNED_INT
	* ESCAPED_STRING

|> (+ "hello" 42)
TypeError can only concatenate str (not "int") to str
|>
```