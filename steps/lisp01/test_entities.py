from . import entities as e

def assert_equals(a, b):
    """if two values aren't equal, raise an error"""
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")

def run_tests():
    """Run all function whose names start with test_"""
    for name, value in globals().items():
        if name.startswith("test_"):
            print(f"Runing {name}...")
            value()

### tests

def test_integers_are_final():
    assert_equals(
        e.Integer(1).reduce({}),
        e.Integer(1)
    )

def test_names_work():
    runtime = {"answer": e.Integer(42)}
    assert_equals(
        e.Name("answer").reduce(runtime),
        e.Integer(42)
    )

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

###

run_tests()