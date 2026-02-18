# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer

# Pin mapping:
#   ui_in[7:0]  = data_in
#   uio_in[0]   = go
#   uio_in[1]   = finish
#   uo_out[7:0] = range
#   uio_out[2]  = error

def get_error(dut):
    return (int(dut.uio_out.value) >> 2) & 1

def get_range(dut):
    return int(dut.uo_out.value)

def set_inputs(dut, data_in=0, go=0, finish=0):
    dut.ui_in.value = data_in
    dut.uio_in.value = (finish << 1) | go

async def tick(dut):
    """Advance one clock cycle: wait for rising edge, then settle 1ns."""
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset (active-low)
    dut.ena.value = 1
    set_inputs(dut, 0, 0, 0)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await Timer(1, units="ns")

    # ------------------------------------------------------------------
    # Test 1: Simple sequence 0x7F, 0x80, 0x81, 0x7E --> range = 3
    # Matches reference TB: 7FFF, 8000, 8001, 7FFE with WIDTH=16
    # ------------------------------------------------------------------
    dut._log.info("Test 1: sequence 0x7F,0x80,0x81,0x7E -> expect range=3")

    # Two idle cycles before go (matches reference TB)
    set_inputs(dut, 0x7F, 0, 0)
    await tick(dut)
    await tick(dut)

    # go=1, data_in=0x7F (initial high and low)
    set_inputs(dut, 0x7F, go=1)
    await tick(dut)

    # data_in=0x80, go=0
    set_inputs(dut, 0x80, go=0)
    await tick(dut)

    # data_in=0x81
    set_inputs(dut, 0x81)
    await tick(dut)

    # data_in=0x7E
    set_inputs(dut, 0x7E)
    await tick(dut)

    # data_in=0x7F (within bounds, doesn't change range)
    set_inputs(dut, 0x7F)
    await tick(dut)

    # finish=1; range latches on this posedge
    set_inputs(dut, 0x7F, finish=1)
    await tick(dut)
    set_inputs(dut, 0, 0, 0)

    assert get_range(dut) == 3, f"Expected range=3, got {get_range(dut)}"
    assert get_error(dut) == 0, "Expected error=0"
    dut._log.info("PASS: range=3, no error")

    await tick(dut)

    # ------------------------------------------------------------------
    # Test 2: Error - go and finish asserted simultaneously
    # ------------------------------------------------------------------
    dut._log.info("Test 2: go+finish simultaneously -> error=1")

    set_inputs(dut, 0, go=1, finish=1)
    await tick(dut)
    set_inputs(dut, 0, 0, 0)

    assert get_error(dut) == 1, "Expected error=1 (go+finish simultaneously)"
    dut._log.info("PASS: error=1 on go+finish")

    await tick(dut)

    # ------------------------------------------------------------------
    # Test 3: Error - finish before go
    # ------------------------------------------------------------------
    dut._log.info("Test 3: finish before go -> error=1")

    await tick(dut)
    await tick(dut)

    set_inputs(dut, 0, finish=1)
    await tick(dut)
    set_inputs(dut, 0, 0, 0)

    assert get_error(dut) == 1, "Expected error=1 (finish without go)"
    dut._log.info("PASS: error=1 on finish without go")

    # ------------------------------------------------------------------
    # Test 4: Error persists until go
    # ------------------------------------------------------------------
    dut._log.info("Test 4: error persists")

    await tick(dut)
    assert get_error(dut) == 1, "Expected error still=1"

    await tick(dut)
    assert get_error(dut) == 1, "Expected error still=1 after extra cycle"
    dut._log.info("PASS: error persists")

    # ------------------------------------------------------------------
    # Test 5: reset clears error; then widest range 0x01,0x00,0xFF -> 0xFF
    # ------------------------------------------------------------------
    dut._log.info("Test 5: reset clears error, then range=0xFF")

    dut.rst_n.value = 0
    await tick(dut)
    dut.rst_n.value = 1
    await Timer(1, units="ns")

    assert get_error(dut) == 0, "Expected error=0 after reset"
    dut._log.info("PASS: error cleared by reset")

    # go with data_in=0x01
    set_inputs(dut, 0x01, go=1)
    await tick(dut)

    # data_in=0x00 (new low)
    set_inputs(dut, 0x00, go=0)
    await tick(dut)

    # data_in=0xFF (new high)
    set_inputs(dut, 0xFF)
    await tick(dut)

    # finish; range = high_q - low_q = 0xFF - 0x00 = 0xFF
    set_inputs(dut, 0x00, finish=1)
    await tick(dut)
    set_inputs(dut, 0, 0, 0)

    assert get_range(dut) == 0xFF, f"Expected range=0xFF, got {hex(get_range(dut))}"
    assert get_error(dut) == 0, "Expected error=0"
    dut._log.info("PASS: range=0xFF, no error")

    await tick(dut)
    await tick(dut)
    dut._log.info("All tests passed")
