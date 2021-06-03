from nmigen import *
from nmigen import tracer
from nmigen.hdl.mem import *
from .fixed_point import FixedPointValue

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
        else:
            raise TypeError(f"unsupported value {type(value)}")


    def eq(self, other):
        return [
            self.real.eq(other.real),
            self.imag.eq(other.imag),
        ]

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
        imag = self.real * other.imag - self.imag * other.real
        assert real.shape == imag.shape
        return Complex(value=(real, imag))
