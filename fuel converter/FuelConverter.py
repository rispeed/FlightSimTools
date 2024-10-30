import tkinter as tk
from tkinter import ttk
import requests
import xml.etree.ElementTree as ET
import os
import math
import subprocess
import json

import json
import socket
import struct
import binascii
from time import sleep
import platform

import sys
import socket
import struct
import binascii
from time import sleep
import platform
import time



class XPlaneIpNotFound(Exception):
  args="Could not find any running XPlane instance in network."

class XPlaneTimeout(Exception):
  args="XPlane timeout."

class XPlaneVersionNotSupported(Exception):
  args="XPlane version not supported."


class XPlaneUdp:

  '''
  Get data from XPlane via network.
  Use a class to implement RAI Pattern for the UDP socket. 
  '''
  
  #constants
  MCAST_GRP = "239.255.1.1"
  MCAST_PORT = 49707 # (MCAST_PORT was 49000 for XPlane10)
  
  
  
  
  def __init__(self):
    
    # Open a UDP Socket to receive on Port 49000
    
    print("#Opening UDP Port for XP port")
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.settimeout(3.0)
    # list of requested datarefs with index number
    self.datarefidx = 0
    self.datarefs = {} # key = idx, value = dataref
    # values from xplane
    self.BeaconData = {}
    self.xplaneValues = {}
    self.defaultFreq = 1
    self.totalFuel= 0

  def __del__(self):
    for i in range(len(self.datarefs)):
      self.AddDataRef(next(iter(self.datarefs.values())), freq=0)
    self.socket.close()
    
    
    
  def SendCommand(self,dataref):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3.0)

    msg = 'CMND\x00'                                  # Sending a command (with terminating null byte)
    msg += dataref                     # the command to send
    msg = msg.encode('utf-8')                         # convert from unicode to utf-8 encoded string
    
    self.socket.sendto(msg, (self.BeaconData["IP"], self.BeaconData["Port"]))
    
  def WriteDataRef(self,dataref,value,vtype='float'):
    '''
    Write Dataref to XPlane
    DREF0+(4byte byte value)+dref_path+0+spaces to complete the whole message to 509 bytes
    DREF0+(4byte byte value of 1)+ sim/cockpit/switches/anti_ice_surf_heat_left+0+spaces to complete to 509 bytes
    '''
    self.xplaneValues[dataref]=value
    cmd = b"DREF\x00"
    dataref  =dataref+'\x00'
    string = dataref.ljust(500).encode()
    message = "".encode()
    if vtype == "float":
      message = struct.pack("<5sf500s", cmd,value,string)
    elif vtype == "int":
      message = struct.pack("<5si500s", cmd, value, string)
    elif vtype == "bool":
      message = struct.pack("<5sI500s", cmd, int(value), string)

    assert(len(message)==509)
    self.socket.sendto(message, (self.BeaconData["IP"], self.BeaconData["Port"]))

  def AddDataRef(self, dataref, freq = None):

    '''
    Configure XPlane to send the dataref with a certain frequency.
    You can disable a dataref by setting freq to 0. 
    '''

    idx = -9999

    if freq == None:
      freq = self.defaultFreq

    if dataref in self.datarefs.values():
      idx = list(self.datarefs.keys())[list(self.datarefs.values()).index(dataref)]
      if freq == 0:
        if dataref in self.xplaneValues.keys():
          del self.xplaneValues[dataref]
        del self.datarefs[idx]
    else:
      idx = self.datarefidx
      self.datarefs[self.datarefidx] = dataref
      self.datarefidx += 1
    
    cmd = b"RREF\x00"
    string = dataref.encode()
    message = struct.pack("<5sii400s", cmd, freq, idx, string)
    assert(len(message)==413)
    self.socket.sendto(message, (self.BeaconData["IP"], self.BeaconData["Port"]))
    if (self.datarefidx%100 == 0):
      sleep(0)

  def GetValues(self):
    try:
      # Receive packet
      data, addr = self.socket.recvfrom(1472) # maximum bytes of an RREF answer X-Plane will send (Ethernet MTU - IP hdr - UDP hdr)
      # Decode Packet
      retvalues = {}
      # * Read the Header "RREFO".
      header=data[0:5]
      if(header!=b"RREF,"): # (was b"RREFO" for XPlane10)
        print("#Unknown packet: ", binascii.hexlify(data))
      else:
        # * We get 8 bytes for every dataref sent:
        #   An integer for idx and the float value. 
        values =data[5:]
        lenvalue = 8
        self.totalFuel = 0 
        numvalues = int(len(values)/lenvalue)
        for i in range(0,numvalues):
          singledata = data[(5+lenvalue*i):(5+lenvalue*(i+1))]
          (idx,value) = struct.unpack("<if", singledata)
          if idx in self.datarefs.keys():
            # convert -0.0 values to positive 0.0 
            if value < 0.0 and value > -0.001 :
              value = 0.0
            retvalues[self.datarefs[idx]] = round(value)
            self.totalFuel+=retvalues[self.datarefs[idx]]
      self.xplaneValues.update(retvalues)
    except:
      #print("ERROR GETTING VALUES HOLD TIGHT")
      raise XPlaneTimeout
    return self.xplaneValues

  def FindIp(self):

      '''
      Find the IP of XPlane Host in Network.
      It takes the first one it can find. 
      '''
    
      self.BeaconData = {}
      
      # open socket for multicast group. 
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      if platform.system() == "Windows":
        sock.bind(('', self.MCAST_PORT))
      else:
        sock.bind((self.MCAST_GRP, self.MCAST_PORT))
      mreq = struct.pack("=4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)
      sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
      sock.settimeout(3.0)
      
      # receive data
      try:   
        packet, sender = sock.recvfrom(1472)
        print("#XPlane Beacon: ", packet.hex())

        # decode data
        # * Header
        header = packet[0:5]
        if header != b"BECN\x00":
          print("#Unknown packet from "+sender[0])
          print(str(len(packet)) + " bytes")
          print(packet)
          print(binascii.hexlify(packet))
          
        else:
          # * Data
          data = packet[5:21]
          # struct becn_struct
          # {
          # 	uchar beacon_major_version;		// 1 at the time of X-Plane 10.40
          # 	uchar beacon_minor_version;		// 1 at the time of X-Plane 10.40
          # 	xint application_host_id;			// 1 for X-Plane, 2 for PlaneMaker
          # 	xint version_number;			// 104014 for X-Plane 10.40b14
          # 	uint role;						// 1 for master, 2 for extern visual, 3 for IOS
          # 	ushort port;					// port number X-Plane is listening on
          # 	xchr	computer_name[strDIM];		// the hostname of the computer 
          # };
          beacon_major_version = 0
          beacon_minor_version = 0
          application_host_id = 0
          xplane_version_number = 0
          role = 0
          port = 0
          (
            beacon_major_version,  # 1 at the time of X-Plane 10.40
            beacon_minor_version,  # 1 at the time of X-Plane 10.40
            application_host_id,   # 1 for X-Plane, 2 for PlaneMaker
            xplane_version_number, # 104014 for X-Plane 10.40b14
            role,                  # 1 for master, 2 for extern visual, 3 for IOS
            port,                  # port number X-Plane is listening on
            ) = struct.unpack("<BBiiIH", data)
          hostname = packet[21:-1] # the hostname of the computer
          hostname = hostname[0:hostname.find(0)]
          if beacon_major_version == 1 \
              and beacon_minor_version <= 2 \
              and application_host_id == 1:
              self.BeaconData["IP"] = sender[0]
              self.BeaconData["Port"] = port
              self.BeaconData["hostname"] = hostname.decode()
              self.BeaconData["XPlaneVersion"] = xplane_version_number
              self.BeaconData["role"] = role
              print("#XPlane Beacon Version: {}.{}.{}".format(beacon_major_version, beacon_minor_version, application_host_id))
          else:
            print("#XPlane Beacon Version not supported: {}.{}.{}".format(beacon_major_version, beacon_minor_version, application_host_id))
            raise XPlaneVersionNotSupported()

      except socket.timeout:
        print("#XPlane IP not found.")
        raise XPlaneIpNotFound()
      finally:
        sock.close()
        

      return self.BeaconData




DATAREF_FUEL1 = "abus/CL650/ARINC429/FDCU-1/words/FSCU/0/FQTY_MN_L"
DATAREF_FUEL2 = "abus/CL650/ARINC429/FDCU-1/words/FSCU/0/FQTY_MN_R"
DATAREF_FUEL3 = "abus/CL650/ARINC429/FDCU-1/words/FSCU/0/FQTY_AUX"











# Constants
SIMBRIEF_API_URL = "https://www.simbrief.com/api/xml.fetcher.php?username={}"
SIMBRIEF_USERNAME = "rgralinski"
OUT_DIR = "out"

# Ensure the output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# Default fuel densities
DENSITY_KG_L = 0.8  # kg/l
DENSITY_LBS_GAL = 6.7  # lbs/gal



def get_fuel_from_xplane():

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
            return("{'fuel':"+str(totalFuel)+"}")
            
            
            
        except XPlaneVersionNotSupported:
            print("XPlane Version not supported.")
            exit(0)
        except XPlaneTimeout:
            print("We found x-plane but having trouble getting data, retrying. ")
            xp.serial1.write("{\"ERROR\":2}\n".encode())
        except XPlaneIpNotFound:
            print("X-Plane not found Retrying")
            xp.serial1.write("{\"ERROR\":2}\n".encode())


# Function to fetch initial fuel on board from the local script
def fetch_initial_fuel():
    try:
        #result = subprocess.run(['python', 'getfuel.py'], capture_output=True, text=True)
        #output = result.stdout
        #print("Output from getfuel.py:", output)
        result = get_fuel_from_xplane()
        
        # Extract JSON part from the output
        json_output = None
        for line in result.splitlines():
            if line.startswith('{'):
                json_output = line
                break
        
        if json_output:
            # Replace single quotes with double quotes
            json_output = json_output.replace("'", '"')
            data = json.loads(json_output)
            fuel_on_board_kg = data.get('fuel', 0)
            # Round up and remove decimal places
            fuel_on_board_kg = math.ceil(fuel_on_board_kg)
            return fuel_on_board_kg
        else:
            return 0
    except Exception as e:
        print("Error running getfuel.py:", e)
        return 0

# Function to fetch block fuel from the initial SimBrief XML response
def fetch_fuel_required(simbrief_username):
    response = requests.get(SIMBRIEF_API_URL.format(simbrief_username))
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content)
            block_fuel = float(root.find('fuel/plan_ramp').text)
            unit = root.find('params/units').text.lower()
            # Save the XML content to a file
            with open(os.path.join(OUT_DIR, 'recent_flight_plan.xml'), 'wb') as file:
                file.write(response.content)
            # Round up to the nearest hundred
            block_fuel = math.ceil(block_fuel / 100) * 100
            return block_fuel, unit
        except (ET.ParseError, AttributeError, ValueError) as e:
            print("Error parsing SimBrief XML:", e)
            return 0.0, 'kg'
    return 0.0, 'kg'

# Function to calculate the difference and update the GUI
def calculate_difference():
    try:
        fuel_required = float(fuel_required_var.get())
        fuel_on_board = float(fuel_on_board_var.get())
        density = DENSITY_KG_L if density_unit_var.get() == 'KG/l' else DENSITY_LBS_GAL
        fuel_unit = fuel_unit_var.get()
        fuel_required_unit = fuel_required_unit_var.get()
        
        # Convert fuel required to the appropriate unit
        if fuel_required_unit == 'lbs':
            fuel_required = fuel_required * 2.20462
        
        difference = fuel_required - fuel_on_board
        amount_needed = difference / density if fuel_unit == 'liters' else difference * density
        
        # Update the labels
        difference_var.set(f"{difference:.2f} {fuel_required_unit.upper()}")
        amount_needed_var.set(f"{amount_needed:.2f} {fuel_unit.capitalize()}")
    except ValueError:
        difference_var.set("Error")
        amount_needed_var.set("Error")

# Function to update the GUI in real-time
def update_gui(*args):
    calculate_difference()

# Initialize the GUI
root = tk.Tk()
root.title("X-Plane Fuel Calculator")

# Variables
fuel_required_var = tk.StringVar()
fuel_on_board_var = tk.StringVar()
fuel_unit_var = tk.StringVar()
density_unit_var = tk.StringVar()
fuel_required_unit_var = tk.StringVar()
difference_var = tk.StringVar()
amount_needed_var = tk.StringVar()

# Fetch initial values
fuel_required, default_unit = fetch_fuel_required(SIMBRIEF_USERNAME)
fuel_on_board = fetch_initial_fuel()  # Fetch initial fuel on board from the local script

fuel_required_var.set(fuel_required)
fuel_on_board_var.set(fuel_on_board)

# Set default units based on SimBrief unit
if default_unit in ['kg', 'kgs']:
    fuel_unit_var.set('liters')
    density_unit_var.set('KG/l')
    fuel_required_unit_var.set('kg')
else:
    fuel_unit_var.set('gallons')
    density_unit_var.set('lbs/gal')
    fuel_required_unit_var.set('lbs')

# Layout
ttk.Label(root, text="Fuel Required:").grid(column=0, row=0, padx=10, pady=5)
ttk.Entry(root, textvariable=fuel_required_var).grid(column=1, row=0, padx=10, pady=5)
ttk.Radiobutton(root, text="KG", variable=fuel_required_unit_var, value='kg').grid(column=2, row=0, padx=10, pady=5)
ttk.Radiobutton(root, text="LBS", variable=fuel_required_unit_var, value='lbs').grid(column=3, row=0, padx=10, pady=5)

ttk.Label(root, text="Fuel On Board:").grid(column=0, row=1, padx=10, pady=5)
ttk.Entry(root, textvariable=fuel_on_board_var).grid(column=1, row=1, padx=10, pady=5)

ttk.Label(root, text="Fuel Unit:").grid(column=0, row=2, padx=10, pady=5)
ttk.Radiobutton(root, text="Liters", variable=fuel_unit_var, value='liters').grid(column=1, row=2, padx=10, pady=5)
ttk.Radiobutton(root, text="Gallons", variable=fuel_unit_var, value='gallons').grid(column=2, row=2, padx=10, pady=5)

ttk.Label(root, text="Density Unit:").grid(column=0, row=3, padx=10, pady=5)
ttk.Radiobutton(root, text="KG/l", variable=density_unit_var, value='KG/l').grid(column=1, row=3, padx=10, pady=5)
ttk.Radiobutton(root, text="lbs/gal", variable=density_unit_var, value='lbs/gal').grid(column=2, row=3, padx=10, pady=5)

ttk.Label(root, text="Difference:").grid(column=0, row=4, padx=10, pady=5)
ttk.Label(root, textvariable=difference_var).grid(column=1, row=4, padx=10, pady=5)

ttk.Label(root, text="Amount Needed:").grid(column=0, row=5, padx=10, pady=5)
ttk.Label(root, textvariable=amount_needed_var).grid(column=1, row=5, padx=10, pady=5)

# Trace variables for real-time updates
fuel_required_var.trace_add('write', update_gui)
fuel_on_board_var.trace_add('write', update_gui)
fuel_unit_var.trace_add('write', update_gui)
density_unit_var.trace_add('write', update_gui)
fuel_required_unit_var.trace_add('write', update_gui)

# Perform initial calculation
calculate_difference()

# Start the GUI event loop
root.mainloop()