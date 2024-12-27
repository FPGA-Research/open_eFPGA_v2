# RTL

These are the Verilog input files.

* [BB](BB): Modules given as black-boxes.
* [Fabric](Fabric): Files related to the fabric itself (e.g. configuration).
* [Tile](Tile): All tiles used in the fabric.
* `defines.v`: Default definitions of values, kept at default version.
* `dummy_modules.v`: Modules needed for compatibility reasons.
* `models_pack.v`: Various modules needed for the fabric implementation.
* `sky130_fd_sc_hd__inv.v`: Sky130 inverter cell definition.
* `uprj_netlists.v`: Further definitions, kept at the default version.
* `user_defines.v`: Definitions for the pin configuration of the caravel pad frame.
> [!IMPORTANT]
> The above is a very important file and has to be adjusted to the desired pin
> configuration that fits the design. If it is not adjusted accordingly, the
> GPIO configuration later has to be changed in the Caravel firmware!
* `user_project_wrapper.v`: The top level design. Instantiates the eFPGA and
connects it to the GPIOs. Also contains the implementation for the wishbone
configuration port.
