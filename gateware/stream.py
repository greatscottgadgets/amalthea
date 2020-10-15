from luna.gateware.stream import StreamInterface

class IQStream(StreamInterface):
    def __init__(self):
        super().__init__(payload_width=13*2)
        self.i = self.payload[:13].as_signed()
        self.q = self.payload[13:].as_signed()
