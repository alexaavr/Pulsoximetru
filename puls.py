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
        temp_c = int(temp_string) / 1000.0
        temp_c = str(round(temp_c, 1))
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
    #mx30.set_spo_config(100,800)
    mx30.ir, mx30.red
    print(mx30.ir)
    spo2 = 0
    Z = 0
    if mx30.ir != 0 and mx30.red != 0 :
        Z = float((mx30.red/5)/(mx30.ir/5))
        spo2 = 133 - 25*Z 
    else: 
        if mx30.ir == 0 and mx30.red == 0:
            spo2 = 0
    print(spo2)
    if mx30.red != mx30.buffer_red:
        return str(round(spo2,1))

while True:
    if(int(read_max30100_hr()) == 0):
        display.lcd_clear()
        display.lcd_display_string("Please place ", 1)
        display.lcd_display_string("your finger", 2)
    else:
        if(float(read_max30100_spo())< 75):
            display.lcd_clear()
            display.lcd_display_string("Go to", 1)
            display.lcd_display_string("the doctor", 2)
        else:
            if(float(read_max30100_spo())> 100):
                display.lcd_clear
                display.lcd_display_string("System", 1)
                display.lcd_display_string("Error", 2)
            else:
                display.lcd_display_string("Temp: " + read_temp_c() + "C", 1)
                display.lcd_display_string("HR/SPO2:" + read_max30100_hr() + "/" + read_max30100_spo() + "% ", 2)