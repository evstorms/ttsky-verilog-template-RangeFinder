<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

RangeFinder computes the range (maximum minus minimum) of a stream of 8-bit values.

Operation is controlled by two signals:
- **go** (`uio[0]`): Assert for one cycle to start a new measurement. The value on `data_in` that cycle becomes both the initial maximum and minimum.
- **finish** (`uio[1]`): Assert for one cycle to end the measurement. The computed range (max − min) is latched onto `range`.

While the module is running (between `go` and `finish`), every new `data_in` value is compared against the tracked maximum and minimum, which are updated accordingly.

An **error** flag (`uio[2]`) is raised if any of the following illegal sequences occur:
- `go` is asserted while the module is already running
- `finish` is asserted while the module is not running
- `go` is asserted while the error flag is already set

The error flag is cleared on the next `go` after a reset.

## How to test

1. Assert `rst_n = 0` for several cycles to reset, then de-assert (`rst_n = 1`).
2. Place the first value on `ui_in[7:0]` and assert `uio_in[0]` (go) for one cycle.
3. For each subsequent value, place it on `ui_in[7:0]` while keeping `uio_in[1:0] = 0`.
4. To end the stream, assert `uio_in[1]` (finish) for one cycle.
5. Read the result from `uo_out[7:0]` (range). Check `uio_out[2]` (error) to confirm no error occurred.

**Example:** Streaming the values 10, 20, 5 produces range = 20 − 5 = **15**.

## External hardware

None required.
