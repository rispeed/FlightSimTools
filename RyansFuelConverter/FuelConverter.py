import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import json
import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
import math

# Function to read SimBrief username from config file
def read_simbrief_username():
    try:
        with open('config.txt', 'r') as file:
            return file.readline().strip()
    except FileNotFoundError:
        return 'rgralinski'  # Default username if config file is not found

# Function to write SimBrief username to config file
def write_simbrief_username(username):
    with open('config.txt', 'w') as file:
        file.write(username)

# Read SimBrief username from config file
simbrief_username = read_simbrief_username()

def fetch_simbrief_block_fuel(username):
    try:
        response = requests.get(f'https://www.simbrief.com/api/xml.fetcher.php?username={username}')
        response.raise_for_status()
        root = ET.fromstring(response.content)
        ramp_fuel = root.find('.//fuel/plan_ramp').text
        rounded_fuel = math.ceil(int(ramp_fuel) / 100) * 100
        return rounded_fuel
    except Exception as e:
        print(f"Error fetching SimBrief block fuel: {e}", file=sys.stderr)
        return -1  # Default value if fetching fails

def fuel_on_board():
    return 0

def fuel_required():
    return fetch_simbrief_block_fuel(simbrief_username)

def update_density():
    if density_unit.get() == "kg/lt":
        density_var.set(0.8)  # Default density for kg/lt
    else:
        density_var.set(6.7)  # Default density for lbs/gal
    update_difference()

def update_difference():
    try:
        fob = float(fuel_on_board_var.get())
        fr = float(fuel_required_var.get())
        density = float(density_var.get())
        unit = unit_var.get()
        
        difference = fr - fob
        if unit == "KG":
            difference_kg = difference
            difference_lbs = difference * 2.20462
        else:
            difference_lbs = difference
            difference_kg = difference / 2.20462
        
        if output_unit.get() == "liters":
            output_value = difference_kg / density
        else:
            output_value = difference_lbs / density
        
        difference_label.config(text=f"Difference: {difference:.2f} {unit}")
        
        if difference < 0:
            output_label.config(text=f"You have enough fuel: {-output_value:.2f} {output_unit.get()}", fg="green")
        else:
            output_label.config(text=f"Required fuel: {output_value:.2f} {output_unit.get()}", fg="red")
        
        # Update progress bar
        progress = min(max(fob / fr * 100, 0), 100) if fr > 0 else 0
        progress_bar['value'] = progress
    except ValueError:
        pass

def update_fuel_on_board():
    script_path = 'getFuel.py'
    if not os.path.exists(script_path):
        print(f"Error: {script_path} does not exist", file=sys.stderr)
        return

    while True:
        try:
            process = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                line = process.stdout.readline()
                if line:
                    print(f"Output from getFuel.py: {line}", end='')  # Print the output line to the main script's console
                    if line.startswith('#'):
                        continue
                    try:
                        data = json.loads(line)
                        fuel_on_board_value = data.get("fuelOnBoard", 0)
                        fuel_on_board_var.set(fuel_on_board_value)
                        update_difference()
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}", file=sys.stderr)
                        continue
                if process.poll() is not None:
                    break
            stderr = process.stderr.read()
            if stderr:
                print(f"Error output from getFuel.py: {stderr}", file=sys.stderr)
        except Exception as e:
            print(f"Error running {script_path}: {e}", file=sys.stderr)
        
        time.sleep(1)  # Wait for 1 second before running the script again

def start_fuel_on_board_thread():
    fuel_thread = threading.Thread(target=update_fuel_on_board, name="FuelOnBoardThread", daemon=True)
    fuel_thread.start()

def save_config():
    global simbrief_username
    simbrief_username = simbrief_username_var.get()
    write_simbrief_username(simbrief_username)
    fuel_required_var.set(fuel_required())

root = tk.Tk()
root.title("Fuel Calculator")
root.geometry("600x600")

font_large = ("Arial", 16)
font_red = ("Arial", 16, "bold")
font_green = ("Arial", 16, "bold")

style = ttk.Style()
style.configure("TRadiobutton", font=font_large)
style.configure("TLabelFrame.Label", font=font_large)

fuel_on_board_var = tk.StringVar(value=fuel_on_board())
fuel_required_var = tk.StringVar(value=fuel_required())
density_var = tk.StringVar(value=0.8)
unit_var = tk.StringVar(value="KG")
density_unit = tk.StringVar(value="kg/lt")
output_unit = tk.StringVar(value="liters")
simbrief_username_var = tk.StringVar(value=simbrief_username)

# Config section
config_frame = ttk.LabelFrame(root, text="Config")
config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

tk.Label(config_frame, text="SimBrief Username:", font=font_large).grid(row=0, column=0, sticky="e", padx=10, pady=10)
tk.Entry(config_frame, textvariable=simbrief_username_var, font=font_large).grid(row=0, column=1, padx=10, pady=10)
tk.Button(config_frame, text="Save", command=save_config, font=font_large).grid(row=0, column=2, padx=10, pady=10)

# Aircraft section
aircraft_frame = ttk.LabelFrame(root, text="Aircraft")
aircraft_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

tk.Label(aircraft_frame, text="Fuel On Board:", font=font_large).grid(row=0, column=0, sticky="e", padx=10, pady=10)
tk.Entry(aircraft_frame, textvariable=fuel_on_board_var, font=font_large).grid(row=0, column=1, padx=10, pady=10)

tk.Label(aircraft_frame, text="Fuel Required:", font=font_large).grid(row=1, column=0, sticky="e", padx=10, pady=10)
tk.Entry(aircraft_frame, textvariable=fuel_required_var, font=font_large).grid(row=1, column=1, padx=10, pady=10)

tk.Label(aircraft_frame, text="Unit:", font=font_large).grid(row=2, column=0, sticky="e", padx=10, pady=10)
ttk.Radiobutton(aircraft_frame, text="KG", variable=unit_var, value="KG", command=update_difference).grid(row=2, column=1, sticky="w", padx=10, pady=10)
ttk.Radiobutton(aircraft_frame, text="LBS", variable=unit_var, value="LBS", command=update_difference).grid(row=2, column=2, sticky="w", padx=10, pady=10)

# Refuel section
refuel_frame = ttk.LabelFrame(root, text="Refuel")
refuel_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

tk.Label(refuel_frame, text="Density:", font=font_large).grid(row=0, column=0, sticky="e", padx=10, pady=10)
tk.Entry(refuel_frame, textvariable=density_var, font=font_large).grid(row=0, column=1, padx=10, pady=10)

tk.Label(refuel_frame, text="Density Unit:", font=font_large).grid(row=1, column=0, sticky="e", padx=10, pady=10)
ttk.Radiobutton(refuel_frame, text="kg/lt", variable=density_unit, value="kg/lt", command=update_density).grid(row=1, column=1, sticky="w", padx=10, pady=10)
ttk.Radiobutton(refuel_frame, text="lbs/gal", variable=density_unit, value="lbs/gal", command=update_density).grid(row=1, column=2, sticky="w", padx=10, pady=10)

difference_label = tk.Label(refuel_frame, text="Difference: 0.00 KG", font=font_large)
difference_label.grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=10)

tk.Label(refuel_frame, text="Output Unit:", font=font_large).grid(row=3, column=0, sticky="e", padx=10, pady=10)
ttk.Radiobutton(refuel_frame, text="liters", variable=output_unit, value="liters", command=update_difference).grid(row=3, column=1, sticky="w", padx=10, pady=10)
ttk.Radiobutton(refuel_frame, text="gallons", variable=output_unit, value="gallons", command=update_difference).grid(row=3, column=2, sticky="w", padx=10, pady=10)

output_label = tk.Label(refuel_frame, text="Required fuel: 0.00 liters", font=font_red, fg="red")
output_label.grid(row=4, column=0, columnspan=3, sticky="w", padx=10, pady=10)

progress_bar = ttk.Progressbar(refuel_frame, orient="horizontal", length=580, mode="determinate")
progress_bar.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

fuel_on_board_var.trace_add("write", lambda *args: update_difference())
fuel_required_var.trace_add("write", lambda *args: update_difference())
density_var.trace_add("write", lambda *args: update_difference())

# Perform initial calculation
update_difference()

# Start the fuel on board thread
start_fuel_on_board_thread()

root.mainloop()