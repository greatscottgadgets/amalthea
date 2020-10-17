from luna.gateware.stream import StreamInterface
from nmigen import *
from nmigen.lib.fifo import SyncFIFO

class IQStream(StreamInterface):
    def __init__(self, sample_depth=13):
        super().__init__(payload_width=sample_depth*2)
        self.i = self.payload.word_select(0, sample_depth).as_signed()
        self.q = self.payload.word_select(1, sample_depth).as_signed()

class SampleStream(StreamInterface):
    pass

class CombinedStream(StreamInterface):
    pass

class StreamCombiner(Elaboratable):
    def __init__(self, streams, domain="sync", fifo_depth=16):
        self._streams   = streams
        self._domain    = domain
        self._fifo_depth = fifo_depth

        width = sum(len(s.payload) for s in streams)
        self.output = CombinedStream(payload_width=width)

    def elaborate(self, platform):
        m = Module()

        # Create a small FIFO for each stream.
        fifos = []
        for s in self._streams:
            fifo = SyncFIFO(width=len(s.payload), depth=self._fifo_depth)
            m.d.comb += [
                fifo.w_data.eq(s.payload),
                fifo.w_en  .eq(s.valid),
                fifo.r_en  .eq(self.output.valid),

                s.ready    .eq(fifo.w_rdy),
            ]
            fifos.append(fifo)

        m.submodules += fifos

        # If all FIFOs have data ready, output one payload from each.
        payload = Cat(f.r_data for f in fifos)
        valid   = Cat(f.r_rdy  for f in fifos).all()
        m.d.comb += [
            self.output.payload.eq(payload),
            self.output.valid.eq(self.output.ready & valid),
        ]

        return DomainRenamer(self._domain)(m)
