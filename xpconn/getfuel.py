# Class to get dataref values from XPlane Flight Simulator via network.
# License: GPLv3

import json
import socket
import struct
import binascii
from time import sleep
import platform
from lib.XPlaneUDP import *



DATAREF_FUEL = "sim/flightmodel/weight/m_fuel_total"


lastupdate=0

if __name__ == '__main__':

    xp = XPlaneUdp()
    while True:
        try:
            beacon = xp.FindIp()
            
            print("#" + str(beacon))
            
            # xp.SendCommand("sim/map/show_current")
            # Subscribe to datarefs
            xp.AddDataRef(DATAREF_FUEL, freq=1)
            
            ###

            # Get initial values from sim
            values = xp.GetValues()
            # set our known values to the values from the sim
            print (values)
            FUEL_VAL = int(values.get(DATAREF_FUEL))
            

            while True:
                
                try:
                    changesMade = False
                    values = xp.GetValues()
                    SIM_FUEL = int(values.get(DATAREF_FUEL))
                    print(values)
                  

                except XPlaneTimeout:
                    print("XPlane Timeout")
                    break

        except XPlaneVersionNotSupported:
            print("XPlane Version not supported.")
            exit(0)
        except XPlaneTimeout:
            print("We found x-plane but having trouble getting data, retrying. ")
            xp.serial1.write("{\"ERROR\":2}\n".encode())
            sleep(1)
        except XPlaneIpNotFound:
            print("X-Plane not found Retrying")
            xp.serial1.write("{\"ERROR\":2}\n".encode())
            sleep(1)
