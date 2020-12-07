import os
import glob
import time
import lcddriver
import max30100

#initializare lcd
display = lcddriver.lcd()

#accesare interfata 1-wire 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#initializare max30100

mx30 = max30100.MAX30100()
mx30.enable_spo2()



#citire date
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

#grade celsius
def read_temp_c():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = int(temp_string) / 1000.0 # TEMP_STRING IS THE SENSOR OUTPUT, MAKE SURE IT'S AN INTEGER TO DO THE MATH
        temp_c = str(round(temp_c, 1)) # ROUND THE RESULT TO 1 PLACE AFTER THE DECIMAL, THEN CONVERT IT TO A STRING
        return temp_c


def read_max30100_hr():
    mx30.read_sensor()
    mx30.ir
    hb = int(mx30.ir / 100)
    print(hb)
    if mx30.ir != mx30.buffer_ir :
        return str(hb)

def read_max30100_spo():
    mx30.read_sensor()
    mx30.ir, mx30.red
    spo2 = 0
    if mx30.ir != 0 and mx30.red != 0 :
        spo2 = 120 - 25*int((mx30.red/5)/(mx30.ir/5))
    else: 
        if mx30.ir == 0 and mx30.red == 0:
            spo2 = 0
    print(spo2)
    if mx30.red != mx30.buffer_red:
        return str(spo2)



while True:
    display.lcd_display_string("Temp: " + read_temp_c() + "C", 1)
    display.lcd_display_string("HR/SPO2: " + read_max30100_hr() + "/" + read_max30100_spo() + "%  ", 2)