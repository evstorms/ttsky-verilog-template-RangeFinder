/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire [7:0] range;
  wire       error;

  RangeFinder #(.WIDTH(8)) rf (
    .data_in (ui_in),
    .clock   (clk),
    .reset   (~rst_n),
    .go      (uio_in[0]),
    .finish  (uio_in[1]),
    .range   (range),
    .error   (error)
  );

  // range on dedicated outputs; error on uio[2] (output direction)
  assign uo_out  = range;
  assign uio_out = {5'b0, error, 2'b0};  // bit 2 = error
  assign uio_oe  = 8'b00000100;           // uio[2] is output, rest are inputs

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in[7:2], 1'b0};

endmodule
