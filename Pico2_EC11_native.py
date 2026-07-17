# Rotary encoder pin A & B states:
# CW   CCW 
# 11   11   detent
# 10   01
# 00   00
# 01   10
# 11   11   detent

from machine import Pin
import micropython

# Global variables
encoder_count = 0
previous_state = 0b11     # both pins HIGH
last_printed_count = 0

# Configure pins with pull-up resistors
pinA = Pin(15, Pin.IN, Pin.PULL_UP)
pinB = Pin(14, Pin.IN, Pin.PULL_UP)

# Use .native instead of .viper for compatibility with globals/pins
@micropython.native
def encoder_isr(pin):
    global encoder_count, previous_state
    
    a_value = pinA.value()
    b_value = pinB.value()
    
    current_state = (a_value << 1) | b_value                

    if ((previous_state << 2) | current_state) == 0b0111:     # 01 > 11 is CW
        encoder_count += 1
    elif ((previous_state << 2) | current_state) == 0b1011:   # 10 > 11 is CCW
        encoder_count -= 1    
        
    print(a_value, b_value, "{:02b}".format(previous_state), "{:02b}".format(current_state))
        
    previous_state = current_state

# Interrupt on rising & falling edge
pinA.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_isr)
pinB.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_isr)

while True:
    state = machine.disable_irq()    # disable interrupts to ensure a atomic data copy
    current_count = encoder_count
    machine.enable_irq(state)        # re-enable interrupts
    
    if current_count != last_printed_count:
        print("Count:", current_count)
        last_printed_count = current_count
