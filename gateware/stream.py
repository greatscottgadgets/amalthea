from luna.gateware.stream import StreamInterface

class IQStream(StreamInterface):
    def __init__(self, sample_depth=13):
        super().__init__(payload_width=sample_depth*2)
        self.i = self.payload.word_select(0, sample_depth).as_signed()
        self.q = self.payload.word_select(1, sample_depth).as_signed()
