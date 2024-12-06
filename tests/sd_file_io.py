from machine import Pin, SPI
import helpers

# SD card configuration
SD_CS_PIN = 13
SD_SCLK_PIN = 10  # Serial Clock (SCLK)
SD_MISO_PIN = 12  # Data Out (MISO)
SD_MOSI_PIN = 11  # Data In (MOSI)

sd_spi = SPI(1, baudrate=4000000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB,
             sck=Pin(SD_SCLK_PIN), mosi=Pin(SD_MOSI_PIN), miso=Pin(SD_MISO_PIN))
sd_cs = Pin(SD_CS_PIN, Pin.OUT)

print("Starting SD card test...")

# Initialize the SD card
sdcard, sd_initialized = helpers.initialize_sd(sd_spi, sd_cs)

if not sd_initialized:
    print("Failed to initialize SD card. Exiting test.")
else:
    try:
        # File name
        file_name = "test_read_write.txt"

        # Write test data to the SD card
        print("Writing data to SD card...")
        test_data = [
            "Line 1: MicroPython SD card test.",
            "Line 2: Testing write and read functionality.",
            "Line 3: If you see this, it works correctly!"
        ]
        helpers.write(test_data, file_name)
        print(f"Data written to {file_name}.")

        # Read data back from the SD card
        print("Reading data back from SD card...")
        full_path = "/sd/" + file_name
        with open(full_path, 'r') as file:
            for line in file:
                print(f"Read: {line.strip()}")

    except Exception as e:
        print(f"Error during SD card test: {e}")

    finally:
        # Unmount the SD card
        helpers.close_sd()
        print("SD card test completed.")
