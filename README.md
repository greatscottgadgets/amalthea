# Amalthea

This repository contains hardware, gateware, and host software sources for Amalthea - an experimental SDR platform.
The main components of the Amalthea hardware are a Lattice ECP5 FPGA, an AT86RF215 radio transceiver, and a Microchip USB3343 USB2.0 PHY (for use with [LUNA](https://luna.readthedocs.io/)).

## Install

 * Clone and install:

```
git clone https://github.com/greatscottgadgets/amalthea
cd amalthea
pip3 install --user --editable '.'
```

 * Add custom block path to `~/.gnuradio/config.conf`:

```
[grc]
local_blocks_path = /path/to/amalthea/amalthea/gnuradio/
```

## Hybrid-SDR

The `amalthea/gnuradio/` directory contains blocks & example flowgraphs for creating mixed FPGA/SDR designs in GNURadio Companion.

### Blocks

 * `hybridsdr.domain.yml` - This defines the `hybridsdr` IO port domain and how connections are made between `hybridsdr` ports.
 * `amalthea_device.block.yml` - This defines the Amalthea Device block, which represents overall device. This block handles gateware elaboration, build, and programming. It will also handle streaming data to/from the host over USB in later versions.
 * `{amalthea_rx,amalthea_demod}.block.yml` - These define some HybridSDR blocks, which represent DSP blocks that run on the FPGA itself. When instantiated, these are added as submodules to the overall Amaranth design.
