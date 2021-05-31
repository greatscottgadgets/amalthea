from nmigen import *

class Complex(Record):
    def __init__(self, sample_width):
        self.sample_width = sample_width
        super().__init__([
            ('real', signed(sample_width)),
            ('imag', signed(sample_width)),
        ])


    def eq(self, other):
        return [
            self.real.eq(other.real),
            self.imag.eq(other.imag),
        ]

    def __add__(self, other):
        width = max(self.sample_width, other.sample_width) + 1
        result = Complex(width)
        result.real = self.real + other.real
        result.imag = self.imag + other.imag
        return result

    def __sub__(self, other):
        width = max(self.sample_width, other.sample_width) + 1
        result = Complex(width)
        result.real = self.real - other.real
        result.imag = self.imag - other.imag
        return result

    def __mul__(self, other):
        width = self.sample_width + other.sample_width
        result = Complex(width)
        result.real = self.real * other.real - self.imag * other.imag
        result.imag = self.real * other.imag - self.imag * other.real
        return result
