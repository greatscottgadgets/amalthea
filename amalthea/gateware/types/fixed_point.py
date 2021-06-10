from nmigen import Cat, Const, Module, Shape, Signal, Value, tracer
from nmigen.sim import Simulator
import unittest


class FixedPointShape:
    def __init__(self, integer_bits, fraction_bits, signed=True):
        if integer_bits < 0:
            raise ValueError("integer_bits must be >= 0")
        if fraction_bits < 0:
            raise ValueError("fraction_bits must be >= 0")
        if signed and integer_bits < 1:
            raise ValueError("integer_bits must be at least 1 for a signed value")
        self.integer_bits = integer_bits
        self.fraction_bits = fraction_bits
        self.signed = signed

    def signal_shape(self):
        return Shape(len(self), self.signed)

    def value(self, value=None, name=None):
        """Create a FixedPointValue with this shape"""
        return FixedPointValue(self, value=value, name=name)

    def __eq__(self, other):
        return self.integer_bits == other.integer_bits \
            and self.fraction_bits == other.fraction_bits\
            and self.signed == other.signed

    def __len__(self):
        return self.integer_bits + self.fraction_bits

    def __repr__(self):
        return f"Q({self.integer_bits}, {self.fraction_bits}, signed={self.signed})"


def Q(integer_bits, fraction_bits, signed=True):
    return FixedPointShape(integer_bits, fraction_bits, signed)

class FixedPointConst:
    def __init__(self, shape, value):
        self.shape = shape
        self.value = round(value * (2**self.shape.fraction_bits))


class FixedPointValue:
    def __init__(self, shape, value=None, name=None):
        self.shape = shape
        self.name = name or tracer.get_var_name(depth=2, default="FixedPoint")
        if value is None:
            self.value = Signal(shape.signal_shape(), name=self.name)
        elif isinstance(value, Value):
            self.value = value
        elif isinstance(value, (int, float)):
            self.value = Const(FixedPointConst(shape=shape, value=(value)).value)
        else:
            raise TypeError(f"cannot create FixedPointValue from {value}")

    def eq(self, other):
        if isinstance(other, FixedPointValue):
            return [self.value.eq(other.value)]
        elif isinstance(other, Value):
            return [self.value.eq(other)]
        else:
            raise TypeError(f"unsupported {type(other)}")


    def to_float(self):
        """Convert to float (only usable in simulation)"""
        value = (yield self.value)
        return float(value) / (2**self.shape.fraction_bits)

    def reshape(self, new_shape):
        if self.shape == new_shape:
            return self
        integer_diff = new_shape.integer_bits - self.shape.integer_bits
        fraction_diff = new_shape.fraction_bits - self.shape.fraction_bits

        # Extend or reduce fraction bits
        value = self.value.shift_left(fraction_diff)

        if integer_diff > 0:
            # Positive difference, extend integer bits
            # sign-extend if needed
            top_bit = value[-1] if self.shape.signed else 0
            value = Cat(value, [top_bit]*integer_diff)
        elif integer_diff < 0:
            # Negative difference, slice away extra integer bits
            value = value[:integer_diff]

        if new_shape.signed:
            value = value.as_signed()
        return FixedPointValue(new_shape, value)


    def _align(self, other):
        """Align the decimal point in two fixed-point values"""
        fraction_bits = max(self.shape.fraction_bits, other.shape.fraction_bits)
        return (
            self.reshape(Q(self.shape.integer_bits, fraction_bits, self.shape.signed)),
            other.reshape(Q(other.shape.integer_bits, fraction_bits, other.shape.signed)),
        )

    def __add__(self, other):
        self, other = self._align(other)
        integer_bits = max(self.shape.integer_bits, other.shape.integer_bits)+1
        signed = self.shape.signed or other.shape.signed
        new_shape = Q(integer_bits, self.shape.fraction_bits, signed)
        return new_shape.value(self.value + other.value)

    def __sub__(self, other):
        self, other = self._align(other)
        integer_bits = max(self.shape.integer_bits, other.shape.integer_bits)+1
        signed = self.shape.signed or other.shape.signed
        new_shape = Q(integer_bits, self.shape.fraction_bits, signed)
        return new_shape.value(self.value - other.value)

    def __mul__(self, other):
        integer_bits = self.shape.integer_bits + other.shape.integer_bits
        fraction_bits = self.shape.fraction_bits + other.shape.fraction_bits
        signed = self.shape.signed or other.shape.signed
        new_shape = Q(integer_bits, fraction_bits, signed)
        return new_shape.value(self.value * other.value)


class TestFixedPoint(unittest.TestCase):
    def check(self, v, expected):
        m = Module()
        sim = Simulator(m)
        def process():
            self.assertAlmostEqual((yield from v.to_float()), expected, delta=0.01)

        sim.add_process(process)
        sim.run()

    def test_basic(self):
        self.check(Q(8,8).value(0.0), 0.0)
        self.check(Q(8,8).value(1.0), 1.0)
        self.check(Q(8,8).value(-1.0), -1.0)
        self.check(Q(8,8).value(1.5), 1.5)
        self.check(Q(8,8).value(-1.5), -1.5)

    def test_shape_errors(self):
        with self.assertRaises(TypeError):
            Q(8,8).value("test")

        with self.assertRaises(ValueError):
            Q(0,8, signed=True)

    def test_reshape(self):
        self.check(Q(8,8).value(3.14).reshape(Q(8,7)), 3.14)
        self.check(Q(8,8).value(3.14).reshape(Q(9,8)), 3.14)
        self.check(Q(8,8).value(-3.14).reshape(Q(8,7)), -3.14)
        self.check(Q(8,8).value(-3.14).reshape(Q(9,8)), -3.14)
        self.check(Q(8,8).value(3.14).reshape(Q(7,7)), 3.14)
        self.check(Q(8,8).value(3.14).reshape(Q(9,9)), 3.14)
        self.check(Q(8,8).value(-3.14).reshape(Q(7,7)), -3.14)
        self.check(Q(8,8).value(-3.14).reshape(Q(9,9)), -3.14)

    def test_add(self):
        tests = [
            (Q(8,8).value(1.2), Q(8,8).value(3.4), 4.6, Q(9,8)),
            (Q(8,8).value(1.2), Q(8,8).value(-3.4), -2.2, Q(9,8)),
        ]
        for a, b, r, s in tests:
            v = a + b
            self.check(v, r)
            self.assertEqual(v.shape, s)

    def test_add_max(self):
        v = Q(3,0).value(3.0) + Q(3,0).value(3.0)
        self.check(v, 6.0)
        self.assertEqual(v.shape, Q(4,0))

    def test_add_mixed_shapes(self):
        v = Q(8,0).value(3.0) + Q(1,7).value(0.125)
        self.check(v, 3.125)
        self.assertEqual(v.shape, Q(9,7))

    def test_sub(self):
        v = Q(8,8).value(1.2) + Q(8,8).value(-3.4)
        self.check(v, -2.2)
        self.assertEqual(v.shape, Q(9,8))

    def test_mul(self):
        v = Q(8,8).value(1.2) * Q(8,8).value(2)
        self.check(v, 2.4)
        self.assertEqual(v.shape, Q(16,16))

if __name__ == "__main__":
    unittest.main()
