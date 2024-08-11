from machine import SoftI2C, Pin, I2C
import time
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM
import math
from ssd1306 import SSD1306_I2C 

def main():
    #oled display setup
    WIDTH = 128
    HEIGHT = 64
    
    OledI2C = I2C(0, scl = Pin(9), sda = Pin(8), freq = 200000)
    OledDisp = SSD1306_I2C(WIDTH, HEIGHT, OledI2C)
    OledDisp.fill(1)

    OledDisp.fill(0)
    
    # I2C software instance
    i2c = SoftI2C(sda=Pin(14), scl=Pin(15), freq=400000)

    # Sensor instance
    sensor = MAX30102(i2c=i2c)

    # Scan I2C bus to ensure that the sensor is connected
    if sensor.i2c_address not in i2c.scan():
        print("Sensor not found.")
        return
    elif not sensor.check_part_id():
        # Check that the targeted sensor is compatible
        print("I2C device ID not corresponding to MAX30102")
        return
    else:
        print("Sensor connected and recognized.")

    # Set up sensor with default configuration
    sensor.setup_sensor()
    sensor.set_sample_rate(3200)
    sensor.set_fifo_average(8)
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

    print("Starting data acquisition from RED & IR registers...")
    
    samples_n = 0  # Number of samples that have been collected



    #stores the calculated bpm
    bpm = 0
    #arrays to store the last x values of ir change and bpm and spO2 so they can be averaged
    irChngStor = [0] * 5
    bpmStor = [0] * 10
    spO2Stor = [0] * 20
    #hold ir values so that we can calculate the change between values
    prev = 0
    curr = 0
    #bool for if we are looking for a peak or not
    lookpeak = True
    #to store when we check a beat and can compare the difference in time to calculate bpm
    millis = time.ticks_ms()
    #store the highest and lowest ir and red values from between each beat, for spo2 calculation
    irHigh = 0
    irLow = 1000000
    redHigh = 0
    redLow = 1000000
    
    while True:
        # The check() method has to be continuously polled, to check if
        # there are new readings into the sensor's FIFO queue. When new
        # readings are available, this function will put them into the storage.
        sensor.check()
        
        # Check if the storage contains available samples
        if sensor.available():
            # Access the storage FIFO and gather the readings (integers)
            red_reading = sensor.pop_red_from_storage()
            ir_reading = sensor.pop_ir_from_storage()
            
            #calculate the change in ir value between last two reads and add it to the list and calculate the average of the last 5
            prev = curr
            curr = ir_reading
            irChngStor.pop(0)
            irChngStor.append(curr - prev)
            avgChng = sum(irChngStor) / 5
            
            #if weve just passed a peak and were looking for a peak calculate bpm
            if avgChng < -5 and lookpeak:
                # calulate bpm as ms per second/ms between beats
                bpm = 60000 / (time.ticks_ms() - millis)
                #reset the time stored for the start of time between this beat and the next
                millis = time.ticks_ms()
                # remove oldest and add newest beat to array for averaging
                bpmStor.pop(0)
                bpmStor.append(bpm)
                
                #print average of the last ten bpm eliminate the high and low values
                bpm = ((sum(bpmStor) - (max(bpmStor) + min(bpmStor))) / (len(bpmStor) - 2))
                print("bpm", bpm)
                PR = bpm
                lookpeak = False
                
                #find spo2
                #remove oldest spO2 value and add newest
                spO2Stor.pop(0)
                spO2Stor.append(calculate_spO2(redHigh, redLow, irHigh, irLow))
                #average the array of stored spO2 values but remove max and min values (possible outliers)
                spO2local = ((sum(spO2Stor) - (max(spO2Stor) + min(spO2Stor))) / (len(spO2Stor) - 2))
                print("spO2", spO2local)
                SPO2 = spO2local
                #reset vals for next beat
                irHigh = 0
                irLow = 100000
                redHigh = 0
                redLow = 100000
                
            #if were not looking for a beat check if we should be looking for a beat
            elif avgChng > 0.5 and not lookpeak:
                lookpeak = True
                
            #see if values are the high or low value in the beat
            if (ir_reading > irHigh):
                irHigh = ir_reading
            if (ir_reading < irLow):
                irLow = ir_reading
            if (red_reading > redHigh):
                redHigh = red_reading
            if (red_reading < redLow):
                redLow = red_reading

def calculate_spO2(redmax, redmin, irmax, irmin):
    RvalNumerator = (redmax - redmin) / redmin
    RvalDenominator = (irmax - irmin) / irmin
    Rval = RvalNumerator / RvalDenominator
    spO2 = 110 - (25 * Rval)
    return spO2

main()