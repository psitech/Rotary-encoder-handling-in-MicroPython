# https://share.google/aimode/mPEkxpuOHKbSfo4Fb
# Rotary encoder pin A & B states:
# CW   CCW 
# 11   11   detent
# 10   01
# 00   00
# 01   10
# 11   11   detent

from machine import Pin
import micropython

# Initialize states
encoder_count = 0
previous_state = 0b1111  

pinA = Pin(15, Pin.IN, Pin.PULL_UP)
pinB = Pin(14, Pin.IN, Pin.PULL_UP)

get_A = pinA.value
get_B = pinB.value

# Viper compiles directly to Cortex-M33 machine instructions
@micropython.viper
def encoder_isr(pin):
    global encoder_count, previous_state
    
    # current_state becomes: [prev_A, prev_B, curr_A, curr_B]
    current_state = ((int(previous_state) << 2) & 0x0F) | (int(get_A()) << 1) | int(get_B())
    print("{:04b}".format(current_state))
    
    # Evaluate transitions using ultra-fast native integer logic
    if current_state == 0b0111:       # CW transition, from 01 to 11
        encoder_count = int(encoder_count) + 1
    elif current_state == 0b1011:     # CCW transition, from 10 to 11
        encoder_count = int(encoder_count) - 1
    previous_state = current_state

# Bind interrupts to the fast Viper handler
pinA.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_isr)
pinB.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_isr)

# Main loop remains slow/non-blocking
last_printed_count = 0
while True:
    current_count = encoder_count
    if current_count != last_printed_count:
        print("Count:", current_count)
        last_printed_count = current_count
