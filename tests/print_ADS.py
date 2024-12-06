from machine import Pin, SPI
import time
import helpers

sampling_rate = 3750  # Hz

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


#configure other
sample_mode = Pin(6, Pin.IN)
mode = sample_mode.value()

stop = Pin(7, Pin.IN)

file_n = 0

if ads_initialized:
    try:
        while stop.value() == 0:
            if mode==0: # read one component mag only                   
                helpers.read_and_print_1(drdy, ads_spi, ads_cs, stop)

            if mode==1: # read 2 components
                helpers.read_and_print_2(drdy, ads_spi, ads_cs, stop)

        print("Program terminated by stop.")

    except KeyboardInterrupt:
        print("Program terminated by computer control.")
        
    finally:
        helpers.close_sd()
        print('end')