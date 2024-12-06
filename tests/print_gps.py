from machine import UART, Pin
import time
import helpers

# GPS configuration
GPS_TX_PIN = 0   # GPS TX (to Pico RX)
GPS_RX_PIN = 1   # GPS RX (to Pico TX)

gps_uart = UART(0, baudrate=9600, tx=Pin(GPS_TX_PIN), rx=Pin(GPS_RX_PIN))

print("Starting GPS test...")

# Initialize GPS
gps_initialized = helpers.initialize_gps(gps_uart)

if gps_initialized:
    print("GPS initialized. Reading data...")
    while True:
        try:
            if gps_uart.any():
                line = gps_uart.readline().decode('utf-8').strip()
                print(f"GPS Data: {line}")
        except Exception as e:
            print(f"Error reading GPS data: {e}")
            time.sleep(1)  # Avoid spamming errors

else:
    print("Failed to initialize GPS.")

