
#helpers.py

import time
import uos
import struct
from sdcard import SDCard
from machine import SPI, Pin, UART

##### time #####
# High-precision time in in seconds (machine time)
def get_time():
    return time.ticks_us()


##### GPS ####
# finctions and code to interact with NEO-6M gps

def initialize_gps(uart):
    try:
        print("Initializing NEO-6M")
        # Configure GPS to output only RMC sentences at 1 Hz
        uart.write(b"$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29\r\n")
        uart.write(b"$PMTK220,1000*1F\r\n")  # Set update rate to 1Hz
        time.sleep(1) # Give GPS time to configure

        # Wait for a valid RMC sentence and extract coordinates and time
        while True:
            if uart.any():
                line = uart.readline().decode('utf-8')
                if line.startswith('$GNRMC') or line.startswith('$GPRMC'):  # RMC sentence
                    data = line.split(',')
                    if data[2] == 'A':  # 'A' means data is valid
                        print("GPS initialized")
                        latitude = parse_coordinate(data[3], data[4])
                        longitude = parse_coordinate(data[5], data[6])
                        timestamp = data[1]
                        print(f"Latitude: {latitude}, Longitude: {longitude}, Time (UTC): {timestamp}")
                        return True
    except Exception as e:
        print("Error during GPS initialization:", e)
        return False

def parse_coordinate(coord, direction):
    """Convert NMEA format to decimal degrees."""
    if not coord or not direction:
        return None
    degrees = float(coord[:2]) if direction in ['N', 'S'] else float(coord[:3])
    minutes = float(coord[2:]) if direction in ['N', 'S'] else float(coord[3:])
    decimal = degrees + minutes / 60
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

##### SD #####
#functions and helpers to interact with adafruit sd

def initialize_sd(spi, cs):

    try:
        print ("Initializing SD board") 
        # Create SDCard instance
        sd = SDCard(spi, cs)
                
        # Mount filesystem
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, "/sd")
        print("SD card mounted.")
        return sd, True
    
    except Exception as e:
        print(f"Error mounting SD card: {e}")
        return None, False

def close_sd():
    try:
        uos.umount("/sd")
        print("SD card unmounted successfully.")
    except Exception as e:
        print(f"Error unmounting SD card: {e}")

def create_new_file(file_name):
    try:
        base_path = '/sd/'
        prefix = 0
        
        # Find the first available filename with a prefix
        while True:
            full_path = base_path + f"{prefix}_{file_name}"
            try:
                uos.stat(full_path)  # Check if the file exists
                prefix += 1  # Increment prefix if file exists
            except OSError:
                break  # File does not exist, so it's available
        
        # Create or truncate the file
        with open(full_path, 'w') as file:
            pass  # Create the file or truncate it if it exists
        
        print(f"New file created: {full_path}")
        return f"{prefix}_{file_name}"
    
    except Exception as e:
        print(f"Error creating new file: {e}")
        return None

def write(data_block, file_name):
    try:
        full_path = '/sd/' + file_name  # Ensure the file is on the SD card
        with open(full_path, 'a') as file:  # Open file in append mode
            for entry in data_block:
                file.write(f"{entry}\n")
            #file.flush()  # Flush the file buffer
            #uos.sync()    # Sync the filesystem
    except Exception as e:
        print(f"Error writing to SD card: {e}")

def write_binary(data_block, file_name):
    try:
        full_path = '/sd/' + file_name
        with open(full_path, 'ab') as file:  # Append binary mode
            file.write(data_block)
    except Exception as e:
        print(f"Error writing to SD card: {e}")


##### ADS #####
# code and functions for operating the TI ads1256 EMM board

# ADS1256 Commands based on documentation
WAKEUP = 0xFF
RDATA = 0x01
RDATAC = 0x03
SDATAC = 0x0F
RREG = 0x10
WREG = 0x50
SELFCAL = 0xF0
SELFOCAL = 0xF1
SELFGCAL = 0xF2
SYSOCAL = 0xF3
SYSGCAL = 0xF4
SYNC = 0xFC
STANDBY = 0xFD
RESET = 0xFE
CONFIG_DIF1 = (WREG | 0x01, 0x00, (0x00 << 4) | 0x01)  # AIN0 = positive, AIN1 = negative
CONFIG_DIF2 = (WREG | 0x01, 0x00, (0x02 << 4) | 0x03)  # AIN2 = positive, AIN3 = negative
CONFIG_DIF3 = (WREG | 0x01, 0x00, (0x04 << 4) | 0x05)  # AIN4 = positive, AIN5 = negative
CONFIG_DIF4 = (WREG | 0x01, 0x00, (0x06 << 4) | 0x07)  # AIN6 = positive, AIN7 = negative


def send_command(spi, cs, command): 
    cs.value(0)
    if isinstance(command, tuple):
        spi.write(bytearray(command))
    else:
        spi.write(bytearray([command]))
    #cs.value(1)

def set_data_rate(spi, cs, sps):
    # Map of SPS to DRATE register values
    sps_to_drate = {
        30000: 0xF0,
        15000: 0xE0,
        7500:  0xD0,
        3750:  0xC0,
        2000:  0xB0,
        1000:  0xA0,
        500:   0x90,
        100:   0x80,
        60:    0x70,
        50:    0x60,
        30:    0x50,
        25:    0x40,
        15:    0x30,
        10:    0x20,
        5:     0x10,
        2.5:   0x00,
    }
    
    # Find the corresponding DRATE hex value
    if sps in sps_to_drate:
        drate_value = sps_to_drate[sps]
    else:
        raise ValueError(f"Invalid SPS value: {sps}. Supported values are: {list(sps_to_drate.keys())}")

    # Write to the DRATE register (register 0x03)
    send_command(spi, cs, WREG | 0x03)  # Start writing to the DRATE register
    send_command(spi, cs, 0x00)         # Write 1 byte
    send_command(spi, cs, drate_value)  # Write the desired data rate value

    print(f"Data rate set to {sps} SPS (DRATE value: {hex(drate_value)})")

def read_data_rate(spi, cs):
    send_command(spi, cs, RREG | 0x03)  # Read from DRATE register
    send_command(spi, cs, 0x00)         # Read 1 byte
    drate_value = spi.read(1)[0]
    print(f"Current Data Rate Register Value: {hex(drate_value)}")
    return drate_value

def initialize_ads1256(spi, cs, drdy, sps):
    try:
        print("Initializing ADS1256")
        send_command(spi, cs, RESET)
        time.sleep(0.1)
        send_command(spi, cs, SELFCAL)
        time.sleep(0.1)

        set_data_rate(spi, cs, sps)
        time.sleep(0.1)
        drate = read_data_rate(spi, cs)
        time.sleep(0.1)

        send_command(spi, cs, SDATAC)
        time.sleep(0.1)
        send_command(spi, cs, SYNC)
        time.sleep(0.1)
        send_command(spi, cs, WAKEUP)
        time.sleep(0.1)
        send_command(spi, cs, CONFIG_DIF1) # iitialize to read diff 1
        time.sleep(0.1)
        send_command(spi, cs, RDATAC)

        # Check if the DRDY pin is responding
        while drdy.value() == 1:
            pass
        print("DRDY = 0")
        return True
    except Exception as e:
        print("Error during ADS1256 initialization:", e)
        return False

def read_and_print_1(drdy, spi, cs, stop):  # For reading 2 component to serial using RDATA in SDATAC mode
    # Ensure we are not in continuous read mode
    send_command(spi, cs, SDATAC)
    # Set MUX to channel pair AIN0-AIN1
    send_command(spi, cs, CONFIG_DIF1)   # Set channel

    # Issue RDATA command and discard the first sample (stale)
    cs.value(0)
    spi.write(bytearray([RDATA]))
    raw_data = spi.read(3)
    cs.value(1)

    while stop.value() == 0:
        try:
            # Wait for DRDY to indicate data ready
            while drdy.value() == 1:
                pass
            sample_time_x = get_time()
            cs.value(0)
            spi.write(bytearray([RDATA]))
            raw_data = spi.read(3)
            cs.value(1)

            result_x = (raw_data[0] << 16) | (raw_data[1] << 8) | raw_data[2]
            if result_x & 0x800000:
                result_x -= 0x1000000

            # Print the results
            print(f"{result_x},{sample_time_x}")

        except Exception as e:
            print(f"Error sampling data: {e}")
            continue

    # Cleanup: ensure SDATAC mode at the end
    send_command(spi, cs, SDATAC)

def read_and_print_2(drdy, spi, cs, stop):  # For reading 2 component to serial using RDATA in SDATAC mode
    # Ensure we are not in continuous read mode
    send_command(spi, cs, SDATAC)

    while stop.value() == 0:
        try:
            # ---- READ FROM CHANNEL 1 (CONFIG_DIF1) ----
            # Set MUX to channel pair AIN0-AIN1
            send_command(spi, cs, SDATAC)        # Ensure not in RDATAC
            send_command(spi, cs, CONFIG_DIF4)   # Set channel
            # Wait for DRDY to indicate data ready
            while drdy.value() == 1:
                pass
            # Issue RDATA command and discard the first sample (stale)
            cs.value(0)
            spi.write(bytearray([RDATA]))
            raw_data = spi.read(3)
            cs.value(1)

            # Wait for next DRDY for a stable sample
            while drdy.value() == 1:
                pass
            sample_time_x = get_time()
            cs.value(0)
            spi.write(bytearray([RDATA]))
            raw_data = spi.read(3)
            cs.value(1)

            result_x = (raw_data[0] << 16) | (raw_data[1] << 8) | raw_data[2]
            if result_x & 0x800000:
                result_x -= 0x1000000

            # ---- READ FROM CHANNEL 2 (CONFIG_DIF4) ----
            send_command(spi, cs, SDATAC)
            send_command(spi, cs, CONFIG_DIF4)  # Set to channel AIN6-AIN7
            # Wait for DRDY
            while drdy.value() == 1:
                pass
            # Discard first sample
            cs.value(0)
            spi.write(bytearray([RDATA]))
            raw_data = spi.read(3)
            cs.value(1)

            # Wait for next DRDY
            while drdy.value() == 1:
                pass
            sample_time_y = get_time()
            cs.value(0)
            spi.write(bytearray([RDATA]))
            raw_data = spi.read(3)
            cs.value(1)

            result_y = (raw_data[0] << 16) | (raw_data[1] << 8) | raw_data[2]
            if result_y & 0x800000:
                result_y -= 0x1000000

            # Print the results
            print(f"{result_x},{sample_time_x},{result_y},{sample_time_y}")

        except Exception as e:
            print(f"Error sampling data: {e}")
            continue

    # Cleanup: ensure SDATAC mode at the end
    send_command(spi, cs, SDATAC)


def sample_data_1(file_size, pps, drdy, spi, cs, file_name):  # Single component (fast, explicit RDATA)
    send_command(spi, cs, SDATAC)  # Ensure not in RDATAC mode
    send_command(spi, cs, CONFIG_DIF4)  # Initialize channel AIN0-AIN1

    full_path = '/sd/' + file_name

    with open(full_path, 'ab') as file:  # Append binary mode
        for _ in range(file_size):
            try:
                # Wait for DRDY to signal data is ready
                while drdy.value() == 1:
                    pass

                # Send RDATA command and read 3 bytes
                cs.value(0)
                spi.write(bytearray([RDATA]))
                raw_data = spi.read(3)
                cs.value(1)

                # Convert raw 24-bit data to signed integer
                result = (raw_data[0] << 16) | (raw_data[1] << 8) | raw_data[2]
                if result & 0x800000:  # Handle negative values
                    result -= 0x1000000

                # Get timestamp and add PPS flag
                sample_time = int(get_time() & 0x7FFFFFFF)
                pps_flag = 1 if pps.value() else 0
                combined_time = (pps_flag << 31) | sample_time  # Set MSB as PPS flag

                # Pack data: [raw_data (3 bytes), combined_time (4 bytes)]
                packed_data = struct.pack('<3sI', raw_data, combined_time)
                file.write(packed_data)

            except Exception as e:
                print(f"Error sampling data: {e}")
                continue

    send_command(spi, cs, SDATAC)  # Ensure cleanup to SDATAC mode


def sample_data_2(file_size, pps, drdy, spi, cs, file_name):  # Two components (explicit RDATA)
    send_command(spi, cs, SDATAC)  # Ensure not in RDATAC mode

    full_path = '/sd/' + file_name

    with open(full_path, 'ab') as file:  # Append binary mode
        for _ in range(file_size):
            try:
                # ---- READ CHANNEL 1 (CONFIG_DIF1) ----
                send_command(spi, cs, CONFIG_DIF1)  # Set channel AIN0-AIN1
                while drdy.value() == 1:  # Wait for DRDY signal
                    pass

                cs.value(0)
                spi.write(bytearray([RDATA]))
                raw_data_x = spi.read(3)
                cs.value(1)

                result_x = (raw_data_x[0] << 16) | (raw_data_x[1] << 8) | raw_data_x[2]
                if result_x & 0x800000:  # Handle negative values
                    result_x -= 0x1000000

                sample_time_x = int(get_time() & 0x7FFFFFFF)
                pps_flag = 1 if pps.value() else 0
                combined_time_x = (pps_flag << 31) | sample_time_x

                # ---- READ CHANNEL 2 (CONFIG_DIF4) ----
                send_command(spi, cs, CONFIG_DIF4)  # Set channel AIN6-AIN7
                while drdy.value() == 1:  # Wait for DRDY signal
                    pass

                cs.value(0)
                spi.write(bytearray([RDATA]))
                raw_data_y = spi.read(3)
                cs.value(1)

                result_y = (raw_data_y[0] << 16) | (raw_data_y[1] << 8) | raw_data_y[2]
                if result_y & 0x800000:  # Handle negative values
                    result_y -= 0x1000000

                sample_time_y = int(get_time() & 0x7FFFFFFF)
                combined_time_y = (pps_flag << 31) | sample_time_y

                # Pack data: [raw_data_x (3 bytes), combined_time_x (4 bytes), raw_data_y (3 bytes), combined_time_y (4 bytes)]
                packed_data = struct.pack('<3sI3sI', raw_data_x, combined_time_x, raw_data_y, combined_time_y)
                file.write(packed_data)

            except Exception as e:
                print(f"Error sampling data: {e}")
                continue

    send_command(spi, cs, SDATAC)  # Ensure cleanup to SDATAC mode


    #### OTHER ####

def write_metadata(gps_initialized, file_name):
    try:
        full_path = '/sd/' + file_name

        # Default metadata values
        latitude = "N/A"
        longitude = "N/A"
        timestamp = "N/A"

        if gps_initialized:
            # Attempt to fetch GPS data
            uart = UART(1, baudrate=9600, tx=17, rx=16, timeout=500)  # Adjust UART pins and settings as needed
            uart.init(baudrate=9600, tx=17, rx=16, timeout=500)
            start_time = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), start_time) < 1000:  # Allow up to 1 second to get valid GPS data
                if uart.any():
                    line = uart.readline().decode('utf-8')
                    if line.startswith('$GNRMC') or line.startswith('$GPRMC'):
                        data = line.split(',')
                        if data[2] == 'A':  # Valid GPS data
                            latitude = parse_coordinate(data[3], data[4])
                            longitude = parse_coordinate(data[5], data[6])
                            timestamp = data[1]
                            break

        # Write metadata to the file
        with open(full_path, 'a') as file:
            file.write(f"GPS Latitude: {latitude}\n")
            file.write(f"GPS Longitude: {longitude}\n")
            file.write(f"GPS Timestamp (UTC): {timestamp}\n")
            file.write(f"Pico Time (us): {get_time()}\n")
            file.write(f"Data:\n")

    except Exception as e:
        print(f"Error writing metadata: {e}")

##### XBEE ######
# Send data to XBee
def send_xbee_data(data, xbee_uart):
    xbee_uart.write(data)
    print(f"Sent to XBee: {data}")

# Receive data from XBee
def receive_xbee_data(xbee_uart):
    if xbee_uart.any():
        data = xbee_uart.read()  # Read data from UART
        print(f"Received from XBee: {data}")
        return data
    return None