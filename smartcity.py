import sys
from flask import Flask, request
import time
import paho.mqtt.client as mqtt
import time as ts
import random
import datetime
import json
import logging
import requests
from logging.handlers import RotatingFileHandler
import minimalmodbus
import serial

logging.basicConfig(filename="sc.log", format='%(asctime)s %(message)s', filemode='a+')
logger=logging.getLogger()
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s %(message)s')
filename = 'sc.log'
handler = RotatingFileHandler(filename, mode='a+', maxBytes=100*1024*1024, backupCount=1, encoding=None, delay=0)
handler.setFormatter(log_formatter)
handler.setLevel(logging.INFO)
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

ENDPOINT = '34.93.19.183'

def sendData(data,deviceID,deviceKey,deviceType,deviceName,cellName):
    try:
        mqttc2=mqtt.Client()
        mqttc2.username_pw_set(username=deviceID,password=deviceKey)
        mqttc2.connect_async(ENDPOINT,1883,10)
        mqttc2.loop_start()
        ts.sleep(5)
        messageval= json.dumps(data)
        logger.debug("Sending Data: %s"%messageval)
        print("Sending Data: %s"%messageval)
        
        if(deviceType == "mains"):
            if(cellName==""):
                channel="channels/02a55eeb-cc77-4114-825e-21f3db901c17/messages/main/"
                (result,mid)= mqttc2.publish(channel,messageval,0)
            else:
                channel="channels/02a55eeb-cc77-4114-825e-21f3db901c17/messages/main/{0}".format(cellName)
                (result,mid)= mqttc2.publish(channel,messageval,0)

        if(deviceType == "smart-water"):
            channel="channels/02a55eeb-cc77-4114-825e-21f3db901c17/messages/water/"
            (result,mid)= mqttc2.publish(channel,messageval,0)
            print(result,mid)
            print("sent data: %s"%messageval)
            logger.debug("sent data: %s"%messageval)

        mqttc2.loop_stop()
        mqttc2.disconnect()


    except KeyboardInterrupt:
            ser.write("stop" + "\r\n")
    except Exception as e:
            print('Exception occured while sending data')
            logger.error(e,exc_info=True)

def constructJsonForSmartMeter(areaType,deviceType,serviceType,zone,customerId,deviceID,deviceName,deviceUnit,deviceValue):
    data = {}
    data['siteid']='3041e48e-bd24-4865-b83b-4a4a827e92e9:'
    data['n']=deviceName
    data['u']=deviceUnit
    data['v']=float(deviceValue)
    data['areatype']=areaType
    data['devicetype']=deviceType
    data['servicetype']=serviceType
    data['zone']=zone
    data['cid']=customerId
    data['thingid']='94aa299b-c4ff-4ee8-9382-ad178c10d9be'
    data =[data]
    return data

def constructJsonForSmartWater(devicetype,deviceid,devicename,deviceunit,devicevalue):
    data = {}
    data['siteid']='3041e48e-bd24-4865-b83b-4a4a827e92e9:'
    data['n']=devicename
    data['u']=deviceunit
    data['v']=float(devicevalue)
    data['devicetype']=devicetype
    data['thingid']='1e943720-94d5-46fd-81d7-cf40735913dc'
    data=[data]
    return data

def flowmeterdata_read():

    Port = '/dev/ttyUSB0'
    FlowId = 1
    Bdrate = 9600
    Parity = serial.PARITY_NONE
    Stopbit = 1
    Timeout = 0.5
    instrument1 = minimalmodbus.Instrument(Port, FlowId)
    instrument1.serial.baudrate = Bdrate
    instrument1.serial.bytesize = 8
    instrument1.serial.parity = Parity
    instrument1.serial.stopbits = Stopbit
    instrument1.serial.timeout = Timeout
    instrument1.mode = minimalmodbus.MODE_RTU
    instrument1.clear_buffers_before_each_transaction = True
    instrument1.close_port_after_each_call = True
    instrument1.debug = True
    print(instrument1)

    try:
        flowrate = instrument1.read_float(0, functioncode=3, number_of_registers=2, byteorder=0)
        print("flowrate is: ",flowrate)
        volumecons = instrument1.read_float(2, functioncode=3, number_of_registers=2, byteorder=0)
        print("volume consumption is: ", volumecons)
        
    except IOError:
        print("Failed to read from instrument")
        time.sleep(1)
        flowmeterdata_read()
        
    return [flowrate, volumecons]

def powermeterdata_read():

    Port1='/dev/ttyUSB0'
    Bdrate1=19200
    Parity1= serial.PARITY_EVEN
    Timeout1=1
    Stopbit1 = 1
    PowerId = 99
    instrument2 = minimalmodbus.Instrument(Port1, PowerId)
    instrument2.serial.baudrate = Bdrate1
    instrument2.serial.bytesize = 8
    instrument2.serial.parity = Parity1
    instrument2.serial.stopbits = Stopbit1
    instrument2.serial.timeout = 5
    instrument2.mode = minimalmodbus.MODE_RTU
    instrument2.clear_buffers_before_each_transaction = True
    instrument2.close_port_after_each_call = True
    instrument2.debug = True
    print(instrument2)

    try:
        voltage1 = instrument2.read_float(3027, functioncode=3, number_of_registers=2, byteorder=0)
        print("voltage of phase 1 is:", voltage1)
        voltage2 = instrument2.read_float(3029, functioncode=3, number_of_registers=2, byteorder=0)
        print("voltage of phase 2 is:", voltage2)
        voltage3 = instrument2.read_float(3031, functioncode=3, number_of_registers=2, byteorder=0)
        print("voltage of phase 3 is:", voltage3)

        current1 = instrument2.read_float(2999, functioncode=3, number_of_registers=2, byteorder=0)
        print("current of phase 1 is:", current1)
        current2 = instrument2.read_float(3001, functioncode=3, number_of_registers=2, byteorder=0)
        print("current of phase 2 is:", current2)
        current3 = instrument2.read_float(3003, functioncode=3, number_of_registers=2, byteorder=0)
        print("current of phase 3 is:", current3)

        power1 = instrument2.read_float(3053, functioncode=3, number_of_registers=2, byteorder=0)
        print("power of phase 1 is:", power1)
        power2 = instrument2.read_float(3055, functioncode=3, number_of_registers=2, byteorder=0)
        print("power of phase 2 is:", power2)
        power3 = instrument2.read_float(3057, functioncode=3, number_of_registers=2, byteorder=0)
        print("power of phase 3 is:", power3)

        pf_val1 = instrument2.read_float(3077, functioncode=3, number_of_registers=2, byteorder=0)
        if(pf_val1 > 1):
            Pf1 = 2 - pf_val1
        pf_val2 = instrument2.read_float(3079, functioncode=3, number_of_registers=2, byteorder=0)
        if(pf_val2 > 1):
            Pf2 = 2 - pf_val2
        pf_val3 = instrument2.read_float(3081, functioncode=3, number_of_registers=2, byteorder=0)
        if(pf_val3 > 1):
            Pf3 = 2 - pf_val3

        print("power factor of phase 1 is:", Pf1)
        print("power factor of phase 2 is:", Pf2)
        print("power factor of phase 3 is:", Pf3)
        
    return [["dummy"],[voltage1, current1, power1, Pf1], [voltage2, current2, power2, Pf2], [voltage3, current3, power3, Pf3]]
    except IOError:
        print("Failed to read from instrument")
        time.sleep(1)
        powermeterdata_read()

def powermeterdata_write():
    with open('smart.json') as f:
        temp=json.load(f)
        
    temp1= temp
    logger.debug('AFTER GETTING RESPONSE FOR THING LIST:'+json.dumps(temp1))
    for i in range(0,temp1["total"]):
        if((temp1["things"][i]["metadata"]["siteid"]) == "3041e48e-bd24-4865-b83b-4a4a827e92e9"):
            deviceType = (temp1["things"][i]["metadata"]["devicetype"])
            deviceID = temp1["things"][i]["id"];
            print("device id is:",deviceID)
            deviceName = temp1["things"][i]["name"];
            deviceKey = temp1["things"][i]["key"];
            areaType = temp1["things"][i]["metadata"]["areatype"]
            zone = temp1["things"][i]["metadata"]["zone"]
            serviceType = temp1["things"][i]["metadata"]["servicetype"]
            customerId = temp1["things"][i]["metadata"]["cid"]

            mainsvaluelist = powermeterdata_read()
            mainsParameterList=[['mains-voltage','V'],['mains-current','A'],['mains-power','kW'],['mains-pfactor','units']]

            if(deviceType == "smart-meter")&(deviceName == "mains-1"):
                jsonMains=[]
                for i in range(1,4):
                    jsonMains=[]
                    for k in range(0,4):
                        deviceName=mainsParameterList[k][0]
                        deviceUnit=mainsParameterList[k][1]
                        deviceValue=mainsvaluelist[i][k]
                        deviceID=str(deviceID)
                        jsonMains.append(constructJsonForSmartMeter(areaType,deviceType,serviceType,zone,customerId,deviceID,deviceName,deviceUnit,deviceValue))
                    cellName="p"+str(i)
                    sendData(jsonMains,deviceID,deviceKey,deviceType,deviceName,cellName)


def flowmeterdata_write():

    waterParameterList = [['total-volume-consumption', 'CubicMeter'],['flow-rate','CubicMeterPerMinute']]
    watervaluelist = flowmeterdata_read()
    devicetype="smart-water"
    deviceid="1e943720-94d5-46fd-81d7-cf40735913dc"
    devicekey="c1d74242-d12a-4c5e-94b2-0ee93b3a3005"

    for k in range(0,2):
        jsonMains=[]
        devicename=waterParameterList[k][0]
        deviceunit=waterParameterList[k][1]
        devicevalue=watervaluelist[k]
        jsonMains=constructJsonForSmartWater(devicetype,deviceid,devicename,deviceunit,devicevalue)
        cellname="Total"
        sendData(jsonMains,deviceid,devicekey,devicetype,devicename,cellname)

flowmeterdata_write()
powermeterdata_write()
