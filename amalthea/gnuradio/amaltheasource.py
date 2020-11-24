#!/usr/bin/env python3

import os
import sys
import logging
import time

import usb1

import numpy as np
from gnuradio import gr

VENDOR_ID  = 0x16d0
PRODUCT_ID = 0x0f3b

BULK_ENDPOINT_NUMBER = 1

# Set the size of a transfer.
TRANSFER_SIZE = 16 * 1024

# Size of the host-size "transfer queue" -- this is effectively the number of async transfers we'll
# have scheduled at a given time.
TRANSFER_QUEUE_DEPTH = 16

class AmaltheaSource(gr.sync_block):
    BLOCK_NAME='Amalthea Source'
    OUTPUT_TYPE=np.float32

    def _transfer_completed(self, transfer: usb1.USBTransfer):

        status = transfer.getStatus()

        # If the transfer completed.
        if status in (usb1.TRANSFER_COMPLETED,):
            buf = np.frombuffer(transfer.getBuffer(), dtype=np.int16)
            self.buffer = np.append(self.buffer, buf.astype(float)/32768)
            transfer.submit()

        else:
            # TODO: handle errors
            failed_out = status

    def __init__(self, sample_rate, freq, output_count=1):
        gr.sync_block.__init__(
            self,
            name=self.BLOCK_NAME,
            in_sig=None,
            out_sig=[self.OUTPUT_TYPE]*output_count,
        )

        self.sample_rate  = sample_rate
        self.freq         = freq
        self.output_count = output_count

        self.buffer = np.array([], dtype=self.OUTPUT_TYPE)

        self.context = usb1.USBContext()

        # Grab a reference to our device...
        self.device = self.context.openByVendorIDAndProductID(0x16d0, 0x0f3b)

        # ... and claim its bulk interface.
        self.device.claimInterface(0)

        # LVDS mode
        self.device.controlWrite(usb1.REQUEST_TYPE_VENDOR, 0, 0x16, 0xa, [])

        # Disable AGC
        self.device.controlWrite(usb1.REQUEST_TYPE_VENDOR, 0, 0x0, 0x20B, [])


    def start(self):
        # Submit a set of transfers to perform async comms with.
        self.active_transfers = []
        for _ in range(TRANSFER_QUEUE_DEPTH):

            # Allocate the transfer...
            transfer = self.device.getTransfer()
            transfer.setBulk(0x80 | BULK_ENDPOINT_NUMBER, TRANSFER_SIZE, callback=self._transfer_completed, timeout=1000)

            # ... and store it.
            self.active_transfers.append(transfer)


        # Submit our transfers all at once.
        for transfer in self.active_transfers:
            transfer.submit()

        self.start_rx()
        return True

    def start_rx(self):
        freq_mhz = self.freq / 1e6
        CCF0 = int((freq_mhz - 1500) / 0.025)
        self.write_reg(CCF0 & 0xff, 0x205)
        self.write_reg((CCF0 >> 8) & 0xff, 0x206)
        self.write_reg(0x0, 0x208)

        # 24 -> TXPREP
        self.write_reg(0x3, 0x0203)

        # 24 -> RX
        self.write_reg(0x5, 0x0203)

    def set_freq(self, freq):
        self.freq = freq
        self.start_rx()
        return True

    def work(self, input_items, output_items):
        self.context.handleEvents()

        out = output_items[0]

        sample_count = min(int(len(self.buffer) / self.output_count), len(out))

        if sample_count == 0:
            return 0

        for i in range(self.output_count):
            out = output_items[i]
            out[:sample_count] = self.buffer[i:sample_count*self.output_count:self.output_count]
        self.buffer = self.buffer[sample_count*self.output_count:]
        return sample_count

    def stop(self):
        # Cancel all of our active transfers.
        for transfer in self.active_transfers:
            if transfer.isSubmitted():
                transfer.cancel()
        return True

    def write_reg(self, reg, value):
        self.device.controlWrite(usb1.REQUEST_TYPE_VENDOR, 0, reg, value, [])

