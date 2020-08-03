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
characters, but cannot start with a digit.

```js
IDENTIFIER: /(?![0-9])[-+*\/^?!a-zA-Z0-9]+/
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
