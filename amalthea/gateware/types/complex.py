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
        imag = self.real * other.imag - self.imag * other.real
        assert real.shape == imag.shape
        return Complex(value=(real, imag))
