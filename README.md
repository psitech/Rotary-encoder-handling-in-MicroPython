# Rotary encoder handling in MicroPython
Shown is a minimal but rock-stable handling of an EC11 rotary encoder.

Speed improvements can be made by using the function decorators @micropython.native and @micropython.viper.
Run the benchmark to see the speed difference between standard vs native vs viper code.

The code has been tested on a Raspberry Pico 2.
