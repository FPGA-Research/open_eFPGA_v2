# OpenLane

This contains files used in the OpenLane flow. Most directories are macros for
the fabric tiles. Exceptions to this are [eFPGA_Config](eFPGA_Config) which
contains the logic used for configuring the fabric and
[user_project_wrapper](user_project_wrapper) which contains the top level
design.

Each directory consists of the following:

* `src`: The Verilog sources files.
* `.sdc` file: The design constraints for the design.
* `config.json`: The design configuration for the design.
* `gate_map.v`: Implementations of different small modules.
* `pin_order.cfg`: The pin order configuration which defines the locations of the
pins in the design.

The top level design also contains the following:
* `fixed_dont_change`: Configurations that must not be changed.
* `macro`: `gds`, `lef` and `lib` files for all macros.
* `vsrc`: Definitions for the power nets.
* `macro_placement.cfg`: The locations of the macros used in the top level design.
* `pdn_cfg.tcl`: A tcl script which defines the Power Distribution Network (PDN),
kindly provided by efabless.
