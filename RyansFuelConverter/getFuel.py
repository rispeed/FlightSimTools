#!/usr/bin/env python

# Class to get dataref values from XPlane Flight Simulator via network.
# License: GPLv3

import json
import socket
import struct
import binascii
from time import sleep
import platform
from lib.XPlaneUDP import *





DATAREF_FUEL1 = "abus/CL650/ARINC429/FDCU-1/words/FSCU/0/FQTY_MN_L"
DATAREF_FUEL2 = "abus/CL650/ARINC429/FDCU-1/words/FSCU/0/FQTY_MN_R"
DATAREF_FUEL3 = "abus/CL650/ARINC429/FDCU-1/words/FSCU/0/FQTY_AUX"
DATAREF_FUEL4 = "abus/CL650/ARINC429/FDCU-1/words/FSCU/0/FQTY_TAIL"

lastupdate=0

if __name__ == '__main__':

    xp = XPlaneUdp()
    while True:
        try:
            beacon = xp.FindIp()
            
            print("#" + str(beacon))
            xp.AddDataRef(DATAREF_FUEL1, freq=1)
            xp.AddDataRef(DATAREF_FUEL2, freq=1)
            xp.AddDataRef(DATAREF_FUEL3, freq=1)
            xp.AddDataRef(DATAREF_FUEL4, freq=1)
            
            values = xp.GetValues()
           # print (values)
            

            while True:
                
                try:
                    values = xp.GetValues()
                    FUEL1=values[DATAREF_FUEL1]
                    FUEL2=values[DATAREF_FUEL2]
                    FUEL3=values[DATAREF_FUEL3]
                    FUEL4=values[DATAREF_FUEL4]
                    total=FUEL1+FUEL2+FUEL3+FUEL4
                    print("{\"fuelOnBoard\":"+str(total)+"}")
                    exit(0)
                except XPlaneTimeout:
                    print("#XPlane Timeout")
                    break

        except XPlaneVersionNotSupported:
            print("#XPlane Version not supported.")
            exit(0)
        except XPlaneTimeout:
            print("#We found x-plane but having trouble getting data, retrying. ")
            sleep(1)
        except XPlaneIpNotFound:
            print("#X-Plane not found Retrying")
            sleep(1)
