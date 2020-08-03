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


class Integer(Entity):
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, Integer):
            return False
        return other.value == self.value

    def __repr__(self):
        return f"Integer({self.value})"


class String(Entity):
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return repr(self.value)

    def __eq__(self, other):
        if not isinstance(other, String):
            return False
        return other.value == self.value

    def __repr__(self):
        return f"String({self.value})"


class Name(Entity):
    def __init__(self, name: str):
        self.name = name

    def compute_one_step(self, runtime):
        return runtime[self.name]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Name({self.name})"


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

    def __repr__(self):
        return f"Call({self.fn}, {', '.join(map(repr, self.args))})"


BUILT_IN_NAMES = {}

def register(name: str):
    def decorator(fn):
        BUILT_IN_NAMES[name] = Function(name, fn)
        return fn
    return decorator

@register("+")
def add(_runtime, a: Integer, b: Integer):
    return Integer(a.value + b.value)

@register("*")
def multiply(_runtime, a: Integer, b: Integer):
    return Integer(a.value * b.value)

@register("-")
def subtract(_runtime, a: Integer, b: Integer):
    return Integer(a.value - b.value)

@register("^")
def power(_runtime, a: Integer, b: Integer):
    return Integer(a.value ** b.value)

@register("x^2+y^2")
def sum_of_squares(_runtime, x: Integer, y: Integer):
    return Call(
        Name("+"),
        Call(Name("^"), x, Integer(2)),
        Call(Name("^"), y, Integer(2)),
    )