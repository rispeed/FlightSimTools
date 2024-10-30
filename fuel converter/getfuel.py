# Class to get dataref values from XPlane Flight Simulator via network.
# License: GPLv3

import json
import socket
import struct
import binascii
from time import sleep
import platform
from lib.XPlaneUDP import *
import sys


DATAREF_FUEL1 = "abus/CL650/ARINC429/FDCU-1/words/FSCU/0/FQTY_MN_L"
DATAREF_FUEL2 = "abus/CL650/ARINC429/FDCU-1/words/FSCU/0/FQTY_MN_R"
DATAREF_FUEL3 = "abus/CL650/ARINC429/FDCU-1/words/FSCU/0/FQTY_AUX"


lastupdate=0

if __name__ == '__main__':

    xp = XPlaneUdp()
    while True:
        try:
            beacon = xp.FindIp()
            
            print("#" + str(beacon))
            
            # xp.SendCommand("sim/map/show_current")
            # Subscribe to datarefs
            xp.AddDataRef(DATAREF_FUEL1, freq=1)
            xp.AddDataRef(DATAREF_FUEL2, freq=1)
            xp.AddDataRef(DATAREF_FUEL3, freq=1)
            
            ###

            # Get initial values from sim
            values = xp.GetValues()
            # set our known values to the values from the sim
            print ("#"+str(values))
            totalFuel=xp.totalFuel
            print("{'fuel':"+str(totalFuel)+"}")
            
            
            
        except XPlaneVersionNotSupported:
            print("XPlane Version not supported.")
            exit(0)
        except XPlaneTimeout:
            print("We found x-plane but having trouble getting data, retrying. ")
            xp.serial1.write("{\"ERROR\":2}\n".encode())
        except XPlaneIpNotFound:
            print("X-Plane not found Retrying")
            xp.serial1.write("{\"ERROR\":2}\n".encode())
        
        exit(0)
            
