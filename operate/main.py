from machine import Pin, SPI, UART
import time
import helpers

sampling_rate = 15000  # Hz
file_size = 30000 # num samples
project = 'nogps'

time.sleep(0.5)

# ADS configuration
ads_cs = Pin(17, Pin.OUT)
drdy = Pin(20, Pin.IN)
MISO_PIN = 16     # Data Out (DOUT / MISO)
MOSI_PIN = 19     # Data In (DIN / MOSI)
SCLK_PIN = 18     # Serial Clock (SCLK)

ads_spi = SPI(0, baudrate=1000000, polarity=0, phase=1, sck=Pin(SCLK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))
ads_initialized = helpers.initialize_ads1256(ads_spi, ads_cs, drdy, sampling_rate)
time.sleep(0.5)

#GPS configuration
gps_on = Pin(3, Pin.IN)
pps = Pin(2, Pin.IN)
GPS_TX_PIN = 0   # GPS TX (to Pico RX)
GPS_RX_PIN = 1   # GPS RX (to Pico TX)
gps_uart = UART(0, baudrate=9600, tx=Pin(GPS_TX_PIN), rx=Pin(GPS_RX_PIN))
pps_led = Pin(14, Pin.OUT)
if gps_on.value() == 1:
    gps_initialized = helpers.initialize_gps(gps_uart)
else:
    print("not using gps")
    gps_initialized = False
time.sleep(0.5)

# SD card configuration
sd_cs = Pin(13, Pin.OUT)
SD_SCLK_PIN = 10  # Serial Clock (SCLK)
SD_MISO_PIN = 12   # Data Out (MISO)
SD_MOSI_PIN = 11  # Data In (MOSI)
sd_spi = SPI(1, baudrate=4000000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB,
             sck=Pin(SD_SCLK_PIN), mosi=Pin(SD_MOSI_PIN), miso=Pin(SD_MISO_PIN))
sdcard, sd_initialized = helpers.initialize_sd(sd_spi, sd_cs)
time.sleep(0.5)

'''
# XBee Configuration
XBEE_TX_PIN = 4  # XBee TX -> Pico UART1 RX
XBEE_RX_PIN = 5  # XBee RX -> Pico UART1 TX
xbee_uart = UART(1, baudrate=9600, tx=Pin(XBEE_TX_PIN), rx=Pin(XBEE_RX_PIN))
'''

#configure other
sample_mode = Pin(6, Pin.IN)
mode = sample_mode.value()

stop = Pin(7, Pin.IN)

file_n = 0

if ads_initialized and sd_initialized:
    try:
        while stop.value() == 0:
            file_n += 1
            if mode==0: # read one component mag only
                print(f"measuring 1 component {file_size} samples")
                file_name = helpers.create_new_file(f"{project}_x_{file_n}.bin")
                helpers.write_metadata(gps_initialized, file_name)                    
                helpers.sample_data_1(file_size, pps, drdy, ads_spi, ads_cs, file_name)
                #send_data = file_name + ',' + str(helpers.get_time())
                #helpers.send_xbee_data(send_data, xbee_uart)
                #helpers.sample_data( drdy, ads_spi, ads_cs, stop)

            if mode==1: # read 2 components
                print(f"measuring 2 component {file_size} samples")
                file_name = helpers.create_new_file(f"{project}_xy_{file_n}.bin")
                helpers.write_metadata(gps_initialized, file_name)
                #helpers.sample_data_2(file_size, pps, drdy, ads_spi, ads_cs, file_name)
                #send_data = f"{file_name}, {helpers.get_time()}"
                #helpers.send_xbee_data(send_data, xbee_uart)
            
        print("Program terminated by stop.")

    except KeyboardInterrupt:
        print("Program terminated by computer control.")
        
    finally:
        helpers.close_sd()
        print('end')