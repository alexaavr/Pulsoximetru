import time
import max30100

# creating an instance of the MAX30100 class
mx30 = max30100.MAX30100()

# enable Sp02 reading
mx30.enable_spo2()

while 1:
    # perform a sensor read
    mx30.read_sensor()

    # after the sensor read, there are now values in the .ir and .red parameters
    mx30.ir, mx30.red

    # set the heartbeat
    hb = int(mx30.ir/100.0)

    # compute the pulse modulation ratio and the oxygen saturation
    if mx30.ir != 0:
        R = int((mx30.red/5)/(mx30.ir/5))
        spo2 = 120 -25*R

    # print values
    print(mx30.red)
    print(mx30.ir)
    if mx30.ir != mx30.buffer_ir :
        print("Pulse:",hb)
    if mx30.red != mx30.buffer_red:
        print("SPO2:",spo2)

    time.sleep(2)