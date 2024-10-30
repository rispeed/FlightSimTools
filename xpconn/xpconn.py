# Class to get dataref values from XPlane Flight Simulator via network.
# License: GPLv3

import json
import socket
import struct
import binascii
from time import sleep
import platform
from lib.XPlaneUDP import *


# function just to do some stuff to create a small delay after updating datarefs from the arduino to the sim
def switch_command(option):
    if option == "N1":
        xp.SendCommand(DATAREF_CMD_N1_PRESS)
        return "N1"
    elif option == "SPEED":
        xp.SendCommand(DATAREF_CMD_SPEED_PRESS)
        return "SPEED"
    elif option == "VNAV":
        xp.SendCommand(DATAREF_CMD_VNAV_PRESS)
        return "VNAV"
    elif option == "LVLCHANGE":
        xp.SendCommand(DATAREF_CMD_LVLCHANGE_PRESS)
        return "LVLCHANGE"
    elif option == "HDGSEL":
        xp.SendCommand(DATAREF_CMD_HDGSEL_PRESS)
        return "HDGSEL"
    elif option == "LNAV":
        xp.SendCommand(DATAREF_CMD_LNAV_PRESS)
        return "LNAV"
    elif option == "VORLOC":
        xp.SendCommand(DATAREF_CMD_VORLOC_PRESS)
        return "VORLOC"
    elif option == "APP":
        xp.SendCommand(DATAREF_CMD_APP_PRESS)
        return "APP"
    elif option == "ALTHLD":
        xp.SendCommand(DATAREF_CMD_ALTHLD_PRESS)
        return "ALTHLD"
    elif option == "VS":
        xp.SendCommand(DATAREF_CMD_VS_PRESS)
        return "VS"
    elif option == "CMDA":
        xp.SendCommand(DATAREF_CMD_CMDA_PRESS)
        return "CMDA"
    elif option == "CMDB":
        xp.SendCommand(DATAREF_CMD_CMDB_PRESS)
        return "CMDB"
    elif option == "CWSA":
        xp.SendCommand(DATAREF_CMD_CWSA_PRESS)
        return "CWSA"
    elif option == "CWSB":
        xp.SendCommand(DATAREF_CMD_CWSB_PRESS)
        return "CWSB"
    elif option == "APDISCON":
        xp.SendCommand(DATAREF_CMD_APDISCON)
        return "APDISCON"
    elif option == "COBTN":
        xp.SendCommand(DATAREF_CMD_COBTNPRESS)
        return "COBTN"
    elif option == "SPEEDINTBTN":
        xp.SendCommand(DATAREF_CMD_SPDINTBTNPRESS)
        return "SPEEDINTBTN"
    elif option == "ALTINTBTN":
        xp.SendCommand(DATAREF_CMD_ALTINTBTNPRESS)
        return "ALTINTBTN"

    else:
        return "Invalid option"


def waitFor(dataref, value):

    for i in range(10):
        values = xp.GetValues()
        print("WAIT")
        sleep(0.0)
        if (values[dataref] == value):
            return

# function to send all our datarefs to the arduino


def SendToArduino(values):
    TSIM_BUTTONLEDS = [
        int(values.get(DATAREF_BTN_N1_LED)),
        int(values.get(DATAREF_BTN_SPEED_LED)),
        int(values.get(DATAREF_BTN_LVLCHANGE_LED)),
        int(values.get(DATAREF_BTN_VNAV_LED)),
        int(values.get(DATAREF_BTN_HDGSEL_LED)),
        int(values.get(DATAREF_BTN_VORLOC_LED)),
        int(values.get(DATAREF_BTN_LNAV_LED)),
        int(values.get(DATAREF_BTN_APP_LED)),
        int(values.get(DATAREF_BTN_ALTHOLD_LED)),
        int(values.get(DATAREF_BTN_VS_LED)),
        int(values.get(DATAREF_BTN_CMDA_LED)),
        int(values.get(DATAREF_BTN_CMDB_LED)),
        int(values.get(DATAREF_BTN_CWSA_LED)),
        int(values.get(DATAREF_BTN_CWSB_LED))
    ]
    packetd = {
        "ISMACH":values[DATAREF_AIRSPEED_IS_MACH],
        "BA":values[DATAREF_BANK_ANGLE_POS],
        "PWR": values[DATAREF_AUTOPILOT_HAS_POWER],
        "1": values[DATAREF_ALT],
        "2": values[DATAREF_HDG],
        "3": values[DATAREF_CAPT_CRS],
        "4": values[DATAREF_IAS],
        "5": values[DATAREF_FO_CRS],
        "6": values[DATAREF_VS],
        "VSDIAL":values[DATAREF_VSDIAL],
        "LEDS": [values[DATAREF_LED_AT], values[DATAREF_LED_CAPTFD], values[DATAREF_LED_FOFD]],
        "FDSIDE": values[DATAREF_FDSIDE],
        "BUTTONLEDS": TSIM_BUTTONLEDS



    }
    packet = str(packetd)
    packet = packet.replace("'", "\"")
    sendpacket = packet+'\n'
    xp.serial1.flushInput()
    xp.serial1.flushOutput()
    cmd = str(sendpacket).encode()
    
    xp.serial1.write(cmd)
    xp.serial1.flushInput()
    xp.serial1.flushOutput()
    print("Sending to arduino")
    print(packet)

    return


# dataref definitions and initial values
DATAREF_ALT = "laminar/B738/autopilot/mcp_alt_dial"
DATAREF_HDG = "laminar/B738/autopilot/mcp_hdg_dial"
DATAREF_CAPT_CRS = "laminar/B738/autopilot/course_pilot"
DATAREF_IAS = "laminar/B738/autopilot/mcp_speed_dial_kts_mach"
DATAREF_FO_CRS = "laminar/B738/autopilot/course_copilot"
DATAREF_VS = "sim/cockpit/autopilot/vertical_velocity"
DATAREF_FDSIDE = "laminar/autopilot/fd_side"
DATAREF_AUTOPILOT_HAS_POWER="sim/cockpit2/autopilot/autopilot_has_power"
DATAREF_VSDIAL="laminar/autopilot/ap_vvi_dial"
# LED DATAREFS
DATAREF_LED_CAPTFD = "laminar/B738/autopilot/pfd_fd_cmd_show"
DATAREF_LED_FOFD = "laminar/B738/autopilot/pfd_fd_cmd_fo_show"
DATAREF_LED_AT = "laminar/B738/autopilot/autothrottle_status1"

# BUTTON LED DATAREFS
DATAREF_BTN_HDGSEL_LED = "laminar/B738/autopilot/hdg_sel_status"
DATAREF_BTN_VNAV_LED = "laminar/B738/autopilot/vnav_status1"
DATAREF_BTN_LNAV_LED = "laminar/B738/autopilot/lnav_status"
DATAREF_BTN_VORLOC_LED = "laminar/B738/autopilot/vorloc_status"
DATAREF_BTN_SPEED_LED = "laminar/B738/autopilot/speed_status1"
DATAREF_BTN_N1_LED = "laminar/B738/autopilot/n1_status"
DATAREF_BTN_LVLCHANGE_LED = "laminar/B738/autopilot/lvl_chg_status"
DATAREF_BTN_APP_LED = "laminar/B738/autopilot/app_status"
DATAREF_BTN_CMDA_LED = "laminar/B738/autopilot/cmd_a_status"
DATAREF_BTN_CMDB_LED = "laminar/B738/autopilot/cmd_b_status"
DATAREF_BTN_CWSA_LED = "laminar/B738/autopilot/cws_a_status"
DATAREF_BTN_CWSB_LED = "laminar/B738/autopilot/cws_b_status"
DATAREF_BTN_VS_LED = "laminar/B738/autopilot/vs_status"
DATAREF_BTN_ALTHOLD_LED = "laminar/B738/autopilot/alt_hld_status"
###################################

# command datarefs
DATAREF_CMD_N1_PRESS = "laminar/B738/autopilot/n1_press"
DATAREF_CMD_SPEED_PRESS = "laminar/B738/autopilot/speed_press"
DATAREF_CMD_VNAV_PRESS = "laminar/B738/autopilot/vnav_press"
DATAREF_CMD_LVLCHANGE_PRESS = "laminar/B738/autopilot/lvl_chg_press"
DATAREF_CMD_HDGSEL_PRESS = "laminar/B738/autopilot/hdg_sel_press"
DATAREF_CMD_LNAV_PRESS = "laminar/B738/autopilot/lnav_press"
DATAREF_CMD_VORLOC_PRESS = "laminar/B738/autopilot/vorloc_press"
DATAREF_CMD_APP_PRESS = "laminar/B738/autopilot/app_press"
DATAREF_CMD_ALTHLD_PRESS = "laminar/B738/autopilot/alt_hld_press"
DATAREF_CMD_VS_PRESS = "laminar/B738/autopilot/vs_press"
DATAREF_CMD_CMDA_PRESS = "laminar/B738/autopilot/cmd_a_press"
DATAREF_CMD_CMDB_PRESS = "laminar/B738/autopilot/cmd_b_press"
DATAREF_CMD_CWSA_PRESS = "laminar/B738/autopilot/cws_a_press"
DATAREF_CMD_CWSB_PRESS = "laminar/B738/autopilot/cws_a_press"

# misc switch datarefs
DATAREF_CMD_APDISCON = "laminar/B738/autopilot/disconnect_toggle"
DATAREF_CMD_COBTNPRESS="laminar/B738/autopilot/change_over_press"
DATAREF_CMD_SPDINTBTNPRESS="laminar/B738/autopilot/spd_interv"
DATAREF_CMD_ALTINTBTNPRESS="laminar/B738/autopilot/alt_interv"


DATAREF_CMD_FDFOTOGGLE   = "laminar/B738/autopilot/flight_director_fo_toggle"
DATAREF_CMD_FDCAPTTOGGLE = "laminar/B738/autopilot/flight_director_toggle"

DATAREF_FDFOPOS = "laminar/B738/autopilot/pfd_fd_cmd_fo"
DATAREF_FDCAPTPOS = "laminar/B738/autopilot/pfd_fd_cmd"

DATAREF_CMD_ATTOGGLE="laminar/B738/autopilot/autothrottle_arm_toggle"
DATAREF_BANK_ANGLE_POS="laminar/B738/rotary/autopilot/bank_angle"

DATAREF_AIRSPEED_IS_MACH="sim/cockpit/autopilot/airspeed_is_mach"
###############################
AIRSPEEDISMACH_VAL = 0
VSDIAL_VAL = 0
BANKANGLE_VAL = 0
AUTOPILOT_HAS_POWER_VAL = 0
CAPT_CRS_VAL = 0
ALT_VAL = 3000
HDG_VAL = 0
IAS_VAL = 100
FO_CRS_VAL = 0
VS_VAL = 0
FDSIDE_VAL = 0

LED_CAPTFD_VAL = 0
LED_FOFD_VAL = 0
LED_AT_VAL = 0

BTN_N1_LED_VAL = 0
BTN_SPEED_LED_VAL = 0
BTN_LVLCHANGE_LED_VAL = 0
BTN_VNAV_LED_VAL = 0
BTN_HDGSEL_LED_VAL = 0
BTN_LNAV_LED_VAL = 0
BTN_VORLOC_LED_VAL = 0
BTN_APP_LED_VAL = 0
BTN_ALTHOLD_LED_VAL = 0
BTN_VS_LED_VAL = 0
BTN_CMDA_LED_VAL = 0
BTN_CMDB_LED_VAL = 0
BTN_CWSA_LED_VAL = 0
BTN_CWSB_LED_VAL = 0

LAST_BUTTON_LEDS = []

lastupdate=0

if __name__ == '__main__':

    xp = XPlaneUdp()
    while True:
        try:
            beacon = xp.FindIp()
            print(beacon)
            print()
            # xp.SendCommand("sim/map/show_current")
            # Subscribe to datarefs
            xp.AddDataRef(DATAREF_ALT, freq=1)
            xp.AddDataRef(DATAREF_HDG, freq=1)
            xp.AddDataRef(DATAREF_CAPT_CRS, freq=1)
            xp.AddDataRef(DATAREF_IAS, freq=1)
            xp.AddDataRef(DATAREF_FO_CRS, freq=1)
            xp.AddDataRef(DATAREF_VS, freq=1)
            xp.AddDataRef(DATAREF_FDSIDE, freq=1)
            xp.AddDataRef(DATAREF_AIRSPEED_IS_MACH,freq=1)
            xp.AddDataRef(DATAREF_VSDIAL,freq=1)
            xp.AddDataRef(DATAREF_AUTOPILOT_HAS_POWER,freq=1)
            xp.AddDataRef(DATAREF_LED_AT, freq=1)
            xp.AddDataRef(DATAREF_LED_CAPTFD, freq=1)
            xp.AddDataRef(DATAREF_LED_FOFD, freq=1)

            # SUBSCRIBE TO BUTTON LEDS
            xp.AddDataRef(DATAREF_BTN_HDGSEL_LED)
            xp.AddDataRef(DATAREF_BTN_VNAV_LED)
            xp.AddDataRef(DATAREF_BTN_LNAV_LED)
            xp.AddDataRef(DATAREF_BTN_VORLOC_LED)
            xp.AddDataRef(DATAREF_BTN_SPEED_LED)
            xp.AddDataRef(DATAREF_BTN_N1_LED)
            xp.AddDataRef(DATAREF_BTN_LVLCHANGE_LED)
            xp.AddDataRef(DATAREF_BTN_APP_LED)
            xp.AddDataRef(DATAREF_BTN_CMDA_LED)
            xp.AddDataRef(DATAREF_BTN_CMDB_LED)
            xp.AddDataRef(DATAREF_BTN_CWSA_LED)
            xp.AddDataRef(DATAREF_BTN_CWSB_LED)
            xp.AddDataRef(DATAREF_BTN_VS_LED)
            xp.AddDataRef(DATAREF_BTN_ALTHOLD_LED)

            xp.AddDataRef(DATAREF_FDFOPOS)
            xp.AddDataRef(DATAREF_FDCAPTPOS)
            xp.AddDataRef(DATAREF_BANK_ANGLE_POS)

            ###

            # Get initial values from sim
            values = xp.GetValues()
            # set our known values to the values from the sim
            AIRSPEEDISMACH_VAL=int(values.get(DATAREF_AIRSPEED_IS_MACH))
            BANKANGLE_VAL = int(values.get(DATAREF_BANK_ANGLE_POS))
            VSDIAL_VAL=int(values.get(DATAREF_VSDIAL))
            AUTOPILOT_HAS_POWER_VAL = int(values.get(DATAREF_AUTOPILOT_HAS_POWER))
            ALT_VAL = int(values.get(DATAREF_ALT))
            HDG_VAL = int(values.get(DATAREF_HDG))
            CAPT_CRS_VAL = int(values.get(DATAREF_CAPT_CRS))
            IAS_VAL = int(values.get(DATAREF_IAS))
            FO_CRS_VAL = int(values.get(DATAREF_FO_CRS))
            VS_VAL = int(values.get(DATAREF_VS))
            FDSIDE_VAL = int(values.get(DATAREF_FDSIDE))

            # Leds
            LED_CAPTFD_VAL = int(values.get(DATAREF_LED_CAPTFD))
            LED_FOFD_VAL = int(values.get(DATAREF_LED_FOFD))
            LED_AT_VAL = int(values.get(DATAREF_LED_AT))

            # button leds

            BTN_N1_LED_VAL = int(values.get(DATAREF_BTN_N1_LED))
            BTN_SPEED_LED_VAL = int(values.get(DATAREF_BTN_SPEED_LED))
            BTN_LVLCHANGE_LED_VAL = int(values.get(DATAREF_BTN_LVLCHANGE_LED))
            BTN_VNAV_LED_VAL = int(values.get(DATAREF_BTN_VNAV_LED))
            BTN_HDGSEL_LED_VAL = int(values.get(DATAREF_BTN_HDGSEL_LED))
            BTN_LNAV_LED_VAL = int(values.get(DATAREF_BTN_LNAV_LED))
            BTN_VORLOC_LED_VAL = int(values.get(DATAREF_BTN_VORLOC_LED))
            BTN_APP_LED_VAL = int(values.get(DATAREF_BTN_APP_LED))
            BTN_ALTHOLD_LED_VAL = int(values.get(DATAREF_BTN_ALTHOLD_LED))
            BTN_VS_LED_VAL = int(values.get(DATAREF_BTN_VS_LED))
            BTN_CMDA_LED_VAL = int(values.get(DATAREF_BTN_CMDA_LED))
            BTN_CMDB_LED_VAL = int(values.get(DATAREF_BTN_CMDB_LED))
            BTN_CWSA_LED_VAL = int(values.get(DATAREF_BTN_CWSA_LED))
            BTN_CWSB_LED_VAL = int(values.get(DATAREF_BTN_CWSB_LED))

            # ---------

            
            SendToArduino(values)
            sleep(3)
            SendToArduino(values)
            sleep(3)

            while True:
                
                try:
                    changesMade = False
                    values = xp.GetValues()
                    SIM_AIRSPEEDISMACH = int(values.get(DATAREF_AIRSPEED_IS_MACH))
                    SIM_VSDIAL = int(values.get(DATAREF_VSDIAL))
                    SIM_APPWR = int(values.get(DATAREF_AUTOPILOT_HAS_POWER))
                    SIM_ALT = int(values.get(DATAREF_ALT))
                    SIM_HDG = int(values.get(DATAREF_HDG))
                    SIM_CAPT_CRS = int(values.get(DATAREF_CAPT_CRS))
                    SIM_IAS = int(values.get(DATAREF_IAS))
                    SIM_FO_CRS = int(values.get(DATAREF_FO_CRS))
                    SIM_VS = int(values.get(DATAREF_VS))
                    SIM_FDSIDE = int(values.get(DATAREF_FDSIDE))

                    SIM_CAPTFDLED = int(values.get(DATAREF_LED_CAPTFD))
                    SIM_FOFDLED = int(values.get(DATAREF_LED_FOFD))
                    SIM_ATARM = int(values.get(DATAREF_LED_AT))

                    SIM_BUTTONLEDS = [
                        int(values.get(DATAREF_BTN_N1_LED)),
                        int(values.get(DATAREF_BTN_SPEED_LED)),
                        int(values.get(DATAREF_BTN_LVLCHANGE_LED)),
                        int(values.get(DATAREF_BTN_VNAV_LED)),
                        int(values.get(DATAREF_BTN_HDGSEL_LED)),
                        int(values.get(DATAREF_BTN_VORLOC_LED)),
                        int(values.get(DATAREF_BTN_LNAV_LED)),
                        int(values.get(DATAREF_BTN_APP_LED)),
                        int(values.get(DATAREF_BTN_ALTHOLD_LED)),
                        int(values.get(DATAREF_BTN_VS_LED)),
                        int(values.get(DATAREF_BTN_CMDA_LED)),
                        int(values.get(DATAREF_BTN_CMDB_LED)),
                        int(values.get(DATAREF_BTN_CWSA_LED)),
                        int(values.get(DATAREF_BTN_CWSB_LED))
                    ]
                    if(SIM_AIRSPEEDISMACH != AIRSPEEDISMACH_VAL):
                        changesMade=True

                    if (SIM_BUTTONLEDS != LAST_BUTTON_LEDS):
                        changesMade = True
                    LAST_BUTTON_LEDS = SIM_BUTTONLEDS

                    if(SIM_VSDIAL != VSDIAL_VAL):
                        VSDIAL_VAL=SIM_VSDIAL
                        changesMade=True
                    if(SIM_APPWR != AUTOPILOT_HAS_POWER_VAL):
                        AUTOPILOT_HAS_POWER_VAL=SIM_APPWR
                        changesMade=True
                    if (SIM_CAPTFDLED != LED_CAPTFD_VAL or SIM_FOFDLED != LED_FOFD_VAL or SIM_ATARM != LED_AT_VAL or SIM_FDSIDE != FDSIDE_VAL):
                        LED_CAPTFD_VAL = SIM_CAPTFDLED
                        LED_FOFD_VAL = SIM_FOFDLED
                        LED_AT_VAL = SIM_ATARM
                        FDSIDE_VAL = SIM_FDSIDE
                        changesMade = True
                    if (SIM_ALT != ALT_VAL or
                        SIM_HDG != HDG_VAL or
                        SIM_CAPT_CRS != CAPT_CRS_VAL or
                        SIM_IAS != IAS_VAL or
                        SIM_FO_CRS != FO_CRS_VAL or
                            SIM_VS != VS_VAL):
                        ALT_VAL = SIM_ALT
                        HDG_VAL = SIM_HDG
                        CAPT_CRS_VAL = SIM_CAPT_CRS
                        IAS_VAL = SIM_IAS
                        FO_CRS_VAL = SIM_FO_CRS
                        VS_VAL = SIM_VS
                        changesMade = True
                    if(changesMade):
                        lastupdate=time.time()
                        SendToArduino(values)
                    now=time.time()
                    if now>(lastupdate+10):
                        lastupdate=time.time()
                        SendToArduino(values)


                    fromArduino = xp.serial1.read_until('\r')
                    text = fromArduino.decode()
                    if (fromArduino):
                        print("From Arduino :", text)
                        lines = text.split("\n")
                        lastline = ""
                        try:
                            lastline = lines[-2]
                        except:
                            lastline = lines[-1]
                        print("Working on ", lastline)
                        try:
                            doc = json.loads(lastline)
                            if "CMD" in doc:
                                mycommand = doc["CMD"]
                                switch_command(mycommand)
                            if "BANKANGLE" in doc:
                                print("Setting bank angle to "+str(doc["BANKANGLE"]))
                                xp.WriteDataRef(DATAREF_BANK_ANGLE_POS,doc["BANKANGLE"])
                            if "ATARM" in doc:
                                    xp.SendCommand(DATAREF_CMD_ATTOGGLE)
                                    SendToArduino(values)
                            if "CAPTFDSTATE" in doc:
                                if (int(values[DATAREF_FDCAPTPOS]) != doc["CAPTFDSTATE"]):
                                    xp.SendCommand(DATAREF_CMD_FDCAPTTOGGLE)
                                    SendToArduino(values)
                            if "FOFDSTATE" in doc:
                                if (int(values[DATAREF_FDFOPOS]) != doc["FOFDSTATE"]):
                                    xp.SendCommand(DATAREF_CMD_FDFOTOGGLE)
                                    SendToArduino(values)
                            
                            if "1" in doc:
                                xp.WriteDataRef(DATAREF_ALT, doc["1"])
                                ALT_VAL = doc["1"]
                                SIM_ALT = doc["1"]
                                waitFor(DATAREF_ALT, ALT_VAL)
                            if "2" in doc:
                                xp.WriteDataRef(DATAREF_HDG, doc["2"])
                                HDG_VAL = doc["2"]
                                SIM_HDG = doc["2"]
                                waitFor(DATAREF_HDG, HDG_VAL)
                            if "3" in doc:
                                xp.WriteDataRef(DATAREF_CAPT_CRS, doc["3"])
                                CAPT_CRS_VAL = doc["3"]
                                SIM_CAPT_CRS = doc["3"]
                                waitFor(DATAREF_CAPT_CRS, CAPT_CRS_VAL)
                            if "4" in doc:
                                xp.WriteDataRef(DATAREF_IAS, doc["4"])
                                IAS_VAL = doc["4"]
                                SIM_IAS = doc["4"]
                                waitFor(DATAREF_IAS, IAS_VAL)
                            if "5" in doc:
                                xp.WriteDataRef(DATAREF_FO_CRS, doc["5"])
                                FO_CRS_VAL = doc["5"]
                                SIM_FO_CRS = doc["5"]
                                waitFor(DATAREF_FO_CRS, FO_CRS_VAL)
                            if "6" in doc:
                                xp.WriteDataRef(DATAREF_VS, doc["6"])
                                VS_VAL = doc["6"]
                                SIM_VS = doc["6"]
                                waitFor(DATAREF_VS, VS_VAL)

                        except ValueError as e:
                            print("valueerror", e, text)
                        except KeyError as e:
                            print("Keyerror", e, text)

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
