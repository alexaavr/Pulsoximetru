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

#citire date senzor temperatura
def read_temp_raw():
    f = open(device_file, 'r')    #deschidem fisierul in care se afla datele de la senzor
    lines = f.readlines()         #citim cele 2 linii
    f.close()                     #inchidem fisier
    return lines                  #returnam liniile citite

#grade celsius conversie
def read_temp_c():
    lines = read_temp_raw()                   #ne folosim de liniile citite din fisier
    while lines[0].strip()[-3:] != 'YES':     #daca prima linie nu se termina in 'YES'
        time.sleep(0.2)                       #nu facem nimic
        lines = read_temp_raw()               #trecem la linia urmatoare      
    equals_pos = lines[1].find('t=')          #pozitia se initializeaza cu locul unde s-a gasit 't=' 
    if equals_pos != -1:                      #cat timp s-a gasit 
        temp_string = lines[1][equals_pos+2:] #folosim partea din dreapta 't='
        temp_c = int(temp_string) / 1000.0    #o transformam in numar intreg
        temp_c = str(round(temp_c, 1))        #o rotunjim cu o zecimala
        return temp_c                         #o returnam


#detectia pulsului
def read_max30100_hr():
    mx30.read_sensor()
    mx30.ir
    hb = int(mx30.ir / 100)         #convertire in valoare normala intreaga 
    #hb = 151                       #test puls mare
    #hb = 49                        #test puls mic
    print("HB= " + str(hb))
    if mx30.ir != mx30.buffer_ir :
        return str(hb)

#detectie SPO2
def read_max30100_spo():
    mx30.read_sensor()
    mx30.ir, mx30.red
    spo2 = 0
    Z = 0
    #calcul saturatie
    if mx30.ir != 0 and mx30.red != 0 :
        Z = float(mx30.red/5)/float(mx30.ir/5)
        spo2 =131 - 25*Z      #ecuatie liniara
    else: 
        if mx30.ir == 0 and mx30.red == 0:
            spo2 = 0    
    print("RED= " + str(mx30.red))   
    print("IR= " + str(mx30.ir))    
    print("Z= " + str(Z))        
    print("SPO2= " + str(spo2))
    if mx30.red != mx30.buffer_red:
        return str(round(spo2,1))

while True:
    #eroare de saturatie >100 sau mai mica decat 0
    if float(read_max30100_spo())> 100 or float(read_max30100_spo())<0:
        display.lcd_display_string("  System Error   ", 1)
        display.lcd_display_string("SPO2 error->Wait", 2)
    else:
        #sh error
        if int(read_max30100_hr())<0:
            display.lcd_display_string("  System Error   ", 1)
            display.lcd_display_string(" HB error->Wait ", 2)
        else:
            #temp mai mica de 30 se asteapta citirea            
            if float(read_temp_c()) <30:
                display.lcd_display_string("Wait Temp detect", 1)
            else: 
                #se afiseaza temperatura
                display.lcd_display_string("Temp: " + read_temp_c() + " C    ", 1)
                #puls sau saturatie 0 se afiseaza mesaj
            if int(read_max30100_hr()) == 0:
                display.lcd_display_string("Place finger    ", 2)
            else:
                #daca pulsul este mai mare ca 110 exista o problema de sanatate
                if int(read_max30100_hr()) > 110:
                    display.lcd_display_string("Need a doctor   ", 2)
                    time.sleep(5)
                    display.lcd_display_string("HR: " + read_max30100_hr() + " ->high ", 2)
                    time.sleep(5)
                else:
                    #daca pulsul este mai mic ca 50 exista o problema de sanatate
                    if int(read_max30100_hr()) > 0  and int(read_max30100_hr()) < 50:
                        display.lcd_display_string("Need a doctor   ", 2)
                        time.sleep(5)
                        display.lcd_display_string("HR: " + read_max30100_hr() + " ->low   ", 2)
                        time.sleep(5)
                    else:
                        #daca saturatai este intre 0 si 75 atunci este o problema de sanatate
                        if float(read_max30100_spo()) > 0 and float(read_max30100_spo())< 75:
                            display.lcd_display_string("Need a doctor   ", 2)
                            time.sleep(5)
                            display.lcd_display_string("SPO2: " + read_max30100_spo() + " ->low   ", 2)
                            time.sleep(5)
                        else:
                            #daca totuleste in parametrii
                            display.lcd_display_string("HR/SPO:" + read_max30100_hr() + "/" + read_max30100_spo() + "% ", 2)