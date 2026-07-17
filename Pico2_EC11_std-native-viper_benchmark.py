# https://share.google/aimode/tHiNatZTxMBJ5XHAt

import time
from machine import Pin
import micropython

# Setup global test variables
encoder_count = 0
previous_state = 0b11
pinA = Pin(15, Pin.IN, Pin.PULL_UP)
pinB = Pin(14, Pin.IN, Pin.PULL_UP)

# 1. Standard Python Bytecode
def isr_standard():
    global encoder_count, previous_state
    a_value = pinA.value()
    b_value = pinB.value()
    current_state = (a_value << 1) | b_value                
    if ((previous_state << 2) | current_state) == 0b0111:
        encoder_count += 1
    elif ((previous_state << 2) | current_state) == 0b1011:
        encoder_count -= 1    
    previous_state = current_state

# 2. Native Code Emitter
@micropython.native
def isr_native():
    global encoder_count, previous_state
    a_value = pinA.value()
    b_value = pinB.value()
    current_state = (a_value << 1) | b_value                
    if ((previous_state << 2) | current_state) == 0b0111:
        encoder_count += 1
    elif ((previous_state << 2) | current_state) == 0b1011:
        encoder_count -= 1    
    previous_state = current_state

# 3. Viper Emitter for Pico 2 (RP2350)
# RP2350 GPIO_IN register address is 0x40030004
GPIO_IN_REG = 0x40030004 

@micropython.viper
def isr_viper():
    global encoder_count, previous_state
    
    # Cast the global variable into a local native integer
    prev: int = int(previous_state)
    
    # Extract the 32-bit hardware integer using pointer notation
    reg_val = ptr32(GPIO_IN_REG)
    reg_data: int = reg_val[0]  
    
    # Read GPIO 15 and GPIO 14 on RP2350
    a_value = (reg_data >> 15) & 1  
    b_value = (reg_data >> 14) & 1  
    
    current_state = (a_value << 1) | b_value                
    
    if ((prev << 2) | current_state) == 7:      # 0b0111
        encoder_count = int(encoder_count) + 1  
    elif ((prev << 2) | current_state) == 11:   # 0b1011
        encoder_count = int(encoder_count) - 1  
    
    previous_state = current_state


# --- BENCHMARK EXECUTION RUNNER ---
ITERATIONS = 10000

print("Starting benchmark on Pico 2 (10,000 iterations)...")

# Test Standard
start = time.ticks_us()
for _ in range(ITERATIONS):
    isr_standard()
end = time.ticks_us()
print(f"Standard Python: {time.ticks_diff(end, start)} microseconds")

# Test Native
start = time.ticks_us()
for _ in range(ITERATIONS):
    isr_native()
end = time.ticks_us()
print(f"Native Emitter:  {time.ticks_diff(end, start)} microseconds")

# Test Viper
start = time.ticks_us()
for _ in range(ITERATIONS):
    isr_viper()
end = time.ticks_us()
print(f"Viper Emitter:   {time.ticks_diff(end, start)} microseconds")
