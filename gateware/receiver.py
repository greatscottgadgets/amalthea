#!/usr/bin/env python3
# pylint: disable=no-member
#
# This file is part of LUNA.
#

import os
import sys
import logging
import time

import usb1

from nmigen                          import Elaboratable, Module
from usb_protocol.emitters           import DeviceDescriptorCollection

from luna                            import top_level_cli
from luna.gateware.usb.usb2.device   import USBDevice
from luna.gateware.usb.usb2.endpoint import USBStreamInEndpoint


VENDOR_ID  = 0x16d0
PRODUCT_ID = 0x0f3b

BULK_ENDPOINT_NUMBER = 1
MAX_BULK_PACKET_SIZE = 64 if os.getenv('LUNA_FULL_ONLY') else 512

# Set the total amount of data to be used in our speed test.
TEST_DATA_SIZE = 1 * 1024 * 1024
TEST_TRANSFER_SIZE = 16 * 1024

# Size of the host-size "transfer queue" -- this is effectively the number of async transfers we'll
# have scheduled at a given time.
TRANSFER_QUEUE_DEPTH = 16



class USBInSpeedTestDevice(Elaboratable):
    """ Simple device that sends data to the host as fast as hardware can.

    This is paired with the python code below to evaluate LUNA throughput.
    """

    def create_descriptors(self):
        """ Create the descriptors we want to use for our device. """

        descriptors = DeviceDescriptorCollection()

        #
        # We'll add the major components of the descriptors we we want.
        # The collection we build here will be necessary to create a standard endpoint.
        #

        # We'll need a device descriptor...
        with descriptors.DeviceDescriptor() as d:
            d.idVendor           = VENDOR_ID
            d.idProduct          = PRODUCT_ID

            d.iManufacturer      = "LUNA"
            d.iProduct           = "IN speed test"
            d.iSerialNumber      = "no serial"

            d.bNumConfigurations = 1


        # ... and a description of the USB configuration we'll provide.
        with descriptors.ConfigurationDescriptor() as c:

            with c.InterfaceDescriptor() as i:
                i.bInterfaceNumber = 0

                with i.EndpointDescriptor() as e:
                    e.bEndpointAddress = 0x80 | BULK_ENDPOINT_NUMBER
                    e.wMaxPacketSize   = MAX_BULK_PACKET_SIZE


        return descriptors


    def elaborate(self, platform):
        m = Module()

        # Generate our domain clocks/resets.
        m.submodules.car = platform.clock_domain_generator()

        # Create our USB device interface...
        ulpi = platform.request("target_phy")
        m.submodules.usb = usb = USBDevice(bus=ulpi)

        # Add our standard control endpoint to the device.
        descriptors = self.create_descriptors()
        usb.add_standard_control_endpoint(descriptors)

        # Add a stream endpoint to our device.
        stream_ep = USBStreamInEndpoint(
            endpoint_number=BULK_ENDPOINT_NUMBER,
            max_packet_size=MAX_BULK_PACKET_SIZE
        )
        usb.add_endpoint(stream_ep)

        # Send entirely zeroes, as fast as we can.
        m.d.comb += [
            stream_ep.stream.valid    .eq(1),
            stream_ep.stream.payload  .eq(0)
        ]

        # Connect our device as a high speed device by default.
        m.d.comb += [
            usb.connect          .eq(1),
            usb.full_speed_only  .eq(1 if os.getenv('LUNA_FULL_ONLY') else 0),
        ]

        return m


def run_speed_test():
    """ Runs a simple speed test, and reports throughput. """

    total_data_exchanged = 0
    failed_out = False

    _messages = {
        1: "error'd out",
        2: "timed out",
        3: "was prematurely cancelled",
        4: "was stalled",
        5: "lost the device it was connected to",
        6: "sent more data than expected."
    }

    def _should_terminate():
        """ Returns true iff our test should terminate. """
        return (total_data_exchanged > TEST_DATA_SIZE) or failed_out


    def _transfer_completed(transfer: usb1.USBTransfer):
        """ Callback executed when an async transfer completes. """
        nonlocal total_data_exchanged, failed_out

        status = transfer.getStatus()

        # If the transfer completed.
        if status in (usb1.TRANSFER_COMPLETED,):

            # Count the data exchanged in this packet...
            total_data_exchanged += transfer.getActualLength()

            # ... and if we should terminate, abort.
            if _should_terminate():
                return

            # Otherwise, re-submit the transfer.
            transfer.submit()

        else:
            failed_out = status



    with usb1.USBContext() as context:

        # Grab a reference to our device...
        device = context.openByVendorIDAndProductID(0x16d0, 0x0f3b)

        # ... and claim its bulk interface.
        device.claimInterface(0)

        # Submit a set of transfers to perform async comms with.
        active_transfers = []
        for _ in range(TRANSFER_QUEUE_DEPTH):

            # Allocate the transfer...
            transfer = device.getTransfer()
            transfer.setBulk(0x80 | BULK_ENDPOINT_NUMBER, TEST_TRANSFER_SIZE, callback=_transfer_completed, timeout=1000)

            # ... and store it.
            active_transfers.append(transfer)


        # Start our benchmark timer.
        start_time = time.time()

        # Submit our transfers all at once.
        for transfer in active_transfers:
            transfer.submit()

        # Run our transfers until we get enough data.
        while not _should_terminate():
            context.handleEvents()

        # Figure out how long this took us.
        end_time = time.time()
        elapsed = end_time - start_time

        # Cancel all of our active transfers.
        for transfer in active_transfers:
            if transfer.isSubmitted():
                transfer.cancel()

        # If we failed out; indicate it.
        if (failed_out):
            logging.error(f"Test failed because a transfer {_messages[failed_out]}.")
            sys.exit(failed_out)


        bytes_per_second = total_data_exchanged / elapsed
        logging.info(f"Exchanged {total_data_exchanged / 1000000}MB total at {bytes_per_second / 1000000}MB/s.")


if __name__ == "__main__":
    device = top_level_cli(USBInSpeedTestDevice)

    logging.info("Giving the device time to connect...")
    time.sleep(5)

    if device is not None:
        logging.info(f"Starting bulk in speed test.")
        run_speed_test()


