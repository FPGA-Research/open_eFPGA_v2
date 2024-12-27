# Scripts

This contains scripts that were useful when creating the design. They are not
optimized and might not work perfectly. Make sure not to overwrite any of your
files with these.

* `copy_macro_files`: Copies all macro files from the build directory of each
macro to the macro input directory of the top level design. 
* `manipulate_macro_cfg.py`: Manipulate the macro positions in various ways.
This still lacks a proper CLI for better usability. Could be deprecated if
FABulous and OpenLane are integrated tighter together in the future.
* `update_verilator_directives.py`: Adds Verilator directives to turn the linter
  off for specific warnings in the files specified in `TILE_NAMES`.
