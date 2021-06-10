from nmigen import *
from nmigen import tracer
from nmigen.hdl.mem import *
from nmigen.sim import *
from .fixed_point import FixedPointConst, FixedPointValue, Q

import cmath
import itertools
import unittest

class ComplexConst:
    def __init__(self, shape, value):
        self.shape = shape
        self.real = FixedPointConst(shape, value.real)
        self.imag = FixedPointConst(shape, value.imag)

    def value(self):
        mask = int(2**len(self.real.shape)-1)
        return (self.real.value & mask) | ((self.imag.value & mask) << len(self.real.shape))

class Complex:
    def __init__(self, *, shape=None, value=None, name=None):
        self.shape = shape
        self.name = name or tracer.get_var_name(depth=2, default="Complex")
        if value is None:
            if shape is None:
                raise ValueError(f"must specify `shape` argument")
            self.real = shape.value(name=self.name+'_real')
            self.imag = shape.value(name=self.name+'_imag')
        elif isinstance(value, complex):
            if shape is None:
                raise ValueError(f"must specify `shape` argument for complex value '{value}'")
            self.real = shape.value(value.real, name=self.name+'_real')
            self.imag = shape.value(value.imag, name=self.name+'_imag')
        elif isinstance(value, tuple) and isinstance(value[0], FixedPointValue) and isinstance(value[1], FixedPointValue):
            assert shape is None
            self.real = value[0]
            self.imag = value[1]
            assert self.real.shape == self.imag.shape
            self.shape = self.real.shape
        elif isinstance(value, Value):
            assert len(value) == 2*len(shape)
            l = int(len(value)/2)
            real = value[0:l]
            imag = value[l:]
            if shape.signed:
                real = real.as_signed()
                imag = imag.as_signed()
            self.real = shape.value(real)
            self.imag = shape.value(imag)
            self.shape = shape
        else:
            raise TypeError(f"unsupported value {type(value)}")

    def eq(self, other):
        assert self.shape == other.shape, f"{self.shape} != {other.shape}"
        return [
            self.real.eq(other.real),
            self.imag.eq(other.imag),
        ]

    def reshape(self, shape):
        return Complex(value=(self.real.reshape(shape), self.imag.reshape(shape)))

    def to_complex(self):
        real = (yield from self.real.to_float())
        imag = (yield from self.imag.to_float())
        return complex(real, imag)

    def value(self):
        return Cat(self.real.value, self.imag.value)

    def __add__(self, other):
        real = self.real + other.real
        imag = self.imag + other.imag
        assert real.shape == imag.shape
        return Complex(value=(real, imag))

    def __sub__(self, other):
        real = self.real - other.real
        imag = self.imag - other.imag
        assert real.shape == imag.shape
        return Complex(value=(real, imag))

    def __mul__(self, other):
        real = self.real * other.real - self.imag * other.imag
        imag = self.real * other.imag + self.imag * other.real
        assert real.shape == imag.shape
        return Complex(value=(real, imag))


class TestComplex(unittest.TestCase):
    def check(self, v, expected):
        m = Module()
        sim = Simulator(m)
        def process():
            self.assertAlmostEqual((yield from v.to_complex()), expected, delta=0.01)

        sim.add_process(process)
        sim.run()

    def test_mul(self):
        for a,b,c,d in itertools.permutations([0,1,-1,0.5,-0.5],4):
            c1 = complex(a, b)
            c2 = complex(c, d)
            shape = Q(8,8)
            self.check((Complex(shape=shape, value=c1)*Complex(shape=shape, value=c2)), c1*c2)

if __name__ == "__main__":
    unittest.main()
