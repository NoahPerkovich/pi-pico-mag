from machine import UART, Pin
import time
import helpers

# XBee configuration
XBEE_TX_PIN = 4  # XBee TX -> Pico UART1 RX
XBEE_RX_PIN = 5  # XBee RX -> Pico UART1 TX

xbee_uart = UART(1, baudrate=9600, tx=Pin(XBEE_TX_PIN), rx=Pin(XBEE_RX_PIN))

print("Starting XBee test...")

try:
    # Test sending data
    test_message = "Hello from Pico XBee!"
    print(f"Sending: {test_message}")
    helpers.send_xbee_data(test_message + "\r\n", xbee_uart)

    # Wait a moment to ensure the message is sent
    time.sleep(1)

    # Test receiving data
    print("Listening for incoming messages...")
    while True:
        received_data = helpers.receive_xbee_data(xbee_uart)
        if received_data:
            print(f"Received: {received_data.decode('utf-8').strip()}")

except Exception as e:
    print(f"Error during XBee test: {e}")
