import tkinter as tk
from tkinter import ttk
import requests
import xml.etree.ElementTree as ET
import os
import math
import subprocess
import json

# Constants
SIMBRIEF_API_URL = "https://www.simbrief.com/api/xml.fetcher.php?username={}"
SIMBRIEF_USERNAME = "rgralinski"
OUT_DIR = "out"

# Ensure the output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# Default fuel densities
DENSITY_KG_L = 0.8  # kg/l
DENSITY_LBS_GAL = 6.7  # lbs/gal

# Function to fetch initial fuel on board from the local script
def fetch_initial_fuel():
    try:
        result = subprocess.run(['python', 'getfuel.py'], capture_output=True, text=True)
        output = result.stdout
        print("Output from getfuel.py:", output)
        
        # Extract JSON part from the output
        json_output = None
        for line in output.splitlines():
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