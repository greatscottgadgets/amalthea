from nmigen import *
from nmigen.back import cxxrtl

import cmath
import math

from .stream import IQStream


class IQ:
    def __init__(self, sample_depth):
        self.i = Signal(signed(sample_depth))
        self.q = Signal(signed(sample_depth))

class CORDICDemod(Elaboratable):
    def __init__(self, sample_depth, iterations=9):
        self._iterations = iterations
        self.input         = IQStream(sample_depth)
        self.amplitude     = Signal(sample_depth)
        self.frequency     = Signal(signed(sample_depth))
        self.phase         = Signal(signed(sample_depth))
        self._sample_depth = sample_depth

        # Make the intermediate stages 1-bit wider to account for CORDIC gain.
        self.stages = [IQ(self._sample_depth+1)             for i in range(self._iterations)]
        self.phases = [Signal(signed(self._sample_depth)) for i in range(self._iterations)]

    def cordic_table(self):
        cordic_angles = []
        cordic_gain = 1.0
        for l in range(self._iterations):
            k = pow(2, -l)
            vec = complex(1, k)
            phase_rads = cmath.phase(vec)
            cordic_angles.append(round(phase_rads * pow(2, self._sample_depth-1) / math.pi))
            cordic_gain *= abs(vec)
        return cordic_angles, cordic_gain

    def elaborate(self, platform):
        m = Module()

        stages = self.stages
        phases = self.phases

        cordic_angles, cordic_gain = self.cordic_table()

        # First stage, special case for 90 degrees
        negative_phase = self.input.q[-1]
        with m.If(negative_phase):
            # Rotate +90 and set the initial phase estimate to -90
            m.d.sync += [
                stages[0].i.eq(-self.input.q),
                stages[0].q.eq( self.input.i),
                phases[0].eq( pow(2, self._sample_depth-2))
            ]
        with m.Else():
            # Rotate -90 and set the initial phase estimate to +90
            m.d.sync += [
                stages[0].i.eq( self.input.q),
                stages[0].q.eq(-self.input.i),
                phases[0].eq(-pow(2, self._sample_depth-2))
            ]

        # Remaining stages, rotate towards 1+0j by successively smaller angles
        for i in range(self._iterations-1):
            lhs = stages[i+1]
            rhs = stages[i]
            negative_phase = rhs.q[-1]
            with m.If(negative_phase):
                # Rotate positive towards 1+0j, subtract from phase estimate
                m.d.sync += [
                    lhs.i.eq(rhs.i - (rhs.q >> i)),
                    lhs.q.eq(rhs.q + (rhs.i >> i)),
                    phases[i+1].eq(phases[i] - cordic_angles[i]),
                ]
            with m.Else():
                # Rotate negative towards 1+0j, add to phase estimate
                m.d.sync += [
                    lhs.i.eq(rhs.i + (rhs.q >> i)),
                    lhs.q.eq(rhs.q - (rhs.i >> i)),
                    phases[i+1].eq(phases[i] + cordic_angles[i]),
                ]

        def divide(sig, divisor, bits=16):
            width = len(sig)

            # Calculate the equivalent multiplier (in ~fixed-point).
            multiplier_fp = round(2**bits / divisor)

            # Multiply, then shift back down.
            result = (sig * multiplier_fp).shift_right(bits)

            # and return the result truncated to the original width.
            return result[:width]

        # After the sample has been rotated fully the imaginary part is ~0, so we can take the real part as the vector magnitude.
        # The CORDIC algorithm applies some gain, so we divide that back out here.
        ampl = divide(stages[-1].i.as_unsigned(), cordic_gain)

        prev_phase = Signal(signed(self._sample_depth))
        m.d.sync += [
            prev_phase    .eq(phases[-1]),
            self.amplitude.eq(ampl),
            self.frequency.eq(phases[-1] - prev_phase),
            self.phase    .eq(phases[-1]),
        ]

        return m


if __name__ == "__main__":
    m = Module()

    input_i = Signal(signed(16))
    input_q = Signal(signed(16))
    freq    = Signal(signed(16))
    demod   = CORDICDemod(16)
    m.submodules += demod

    blink = Signal()
    m.d.sync += blink.eq(blink + 1)

    m.d.comb += [
        demod.input.i.eq(input_i),
        demod.input.q.eq(input_q),
        freq.eq(demod.frequency),
    ]

    output = cxxrtl.convert(m, ports=(input_i, input_q, freq, blink))
    with open('lib/rtl.cpp', 'w') as f:
        f.write(output)
