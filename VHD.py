import minimalmodbus
import serial.tools.list_ports as plist
import serial
import time

Port = 'COM3'
SlaveId = 9
Bdrate = 9600
Parity=serial.PARITY_NONE
Stopbit=1
Timeout=0.5

instrument = minimalmodbus.Instrument(Port, SlaveId)
instrument.serial.baudrate = Bdrate
instrument.serial.bytesize = 8
instrument.serial.parity = Parity
instrument.serial.stopbits = Stopbit
instrument.serial.timeout = Timeout
instrument.mode = minimalmodbus.MODE_RTU
instrument.clear_buffers_before_each_transaction = True
instrument.close_port_after_each_call = True
instrument.debug =False

def read_frequency():
    try:
        frequencyread = instrument.read_register(8450, number_of_decimals=2, functioncode=3, signed=False)
    except IOError:
        print("Failed to read from instrument")
    return frequencyread

def write_frequency():
    try:
        frequency = float(input("Enter the frequency: "))
        frequency = frequency*100
        frequencywrite = instrument.write_register(8193,  frequency , number_of_decimals=0, functioncode=16, signed=False) 
    except IOError:
        print("Failed to write into the instrument")

def run():
    try:
        run = instrument.write_register(8192, 18 , number_of_decimals=0, functioncode=16, signed=False)
    except IOError:
        print("Failed to run the instrument")
        
def stop():
    try:
        run = instrument.write_register(8192, 1 , number_of_decimals=0, functioncode=16, signed=False)
    except IOError:
        print("Failed to run the instrument")
        
def read_status():
    try:
        time.sleep(7.5)
        statusread = instrument.read_register(8449, number_of_decimals=0, functioncode=3, signed=False)
        status = bin(statusread)
        status = str(status[-2:])

        if (status == '00'):
            finalstatus = 'The Motor is at stop'
        if (status == '11'):
            finalstatus = 'The Motor is at run'
        if (status == '01'):
            finalstatus = 'Motor is in ramp stop'
        if (status == '10'):
            finalstatus = 'Motor is in standby'
    except:
        print("Cannot determine the status")
        
    return finalstatus
