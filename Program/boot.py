# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)

import gc
gc.collect()

import network
import time

# Disable AP
ap = network.WLAN(network.AP_IF)
ap.active(False)

# Start Web Shell
import webrepl
webrepl.start()

# ~ import main
