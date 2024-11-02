import tkinter as tk
from tkinter import ttk

def fuel_on_board():
    return 0

def fuel_required():
    return 1000

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
        output_label.config(text=f"Output: {output_value:.2f} {output_unit.get()}")
    except ValueError:
        pass

root = tk.Tk()
root.title("Fuel Calculator")
root.geometry("400x300")

font_large = ("Arial", 14)

fuel_on_board_var = tk.StringVar(value=fuel_on_board())
fuel_required_var = tk.StringVar(value=fuel_required())
density_var = tk.StringVar(value=0.8)
unit_var = tk.StringVar(value="KG")
density_unit = tk.StringVar(value="kg/lt")
output_unit = tk.StringVar(value="liters")

tk.Label(root, text="Fuel On Board:", font=font_large).grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=fuel_on_board_var, font=font_large).grid(row=0, column=1)

tk.Label(root, text="Fuel Required:", font=font_large).grid(row=1, column=0, sticky="w")
tk.Entry(root, textvariable=fuel_required_var, font=font_large).grid(row=1, column=1)

tk.Label(root, text="Unit:", font=font_large).grid(row=2, column=0, sticky="w")
ttk.Radiobutton(root, text="KG", variable=unit_var, value="KG", command=update_difference).grid(row=2, column=1, sticky="w")
ttk.Radiobutton(root, text="LBS", variable=unit_var, value="LBS", command=update_difference).grid(row=2, column=2, sticky="w")

tk.Label(root, text="Density:", font=font_large).grid(row=3, column=0, sticky="w")
tk.Entry(root, textvariable=density_var, font=font_large).grid(row=3, column=1)

tk.Label(root, text="Density Unit:", font=font_large).grid(row=4, column=0, sticky="w")
ttk.Radiobutton(root, text="kg/lt", variable=density_unit, value="kg/lt", command=update_density).grid(row=4, column=1, sticky="w")
ttk.Radiobutton(root, text="lbs/gal", variable=density_unit, value="lbs/gal", command=update_density).grid(row=4, column=2, sticky="w")

difference_label = tk.Label(root, text="Difference: 0.00 KG", font=font_large)
difference_label.grid(row=5, column=0, columnspan=2, sticky="w")

tk.Label(root, text="Output Unit:", font=font_large).grid(row=6, column=0, sticky="w")
ttk.Radiobutton(root, text="liters", variable=output_unit, value="liters", command=update_difference).grid(row=6, column=1, sticky="w")
ttk.Radiobutton(root, text="gallons", variable=output_unit, value="gallons", command=update_difference).grid(row=6, column=2, sticky="w")

output_label = tk.Label(root, text="Output: 0.00 liters", font=font_large)
output_label.grid(row=7, column=0, columnspan=2, sticky="w")

fuel_on_board_var.trace_add("write", lambda *args: update_difference())
fuel_required_var.trace_add("write", lambda *args: update_difference())
density_var.trace_add("write", lambda *args: update_difference())

# Perform initial calculation
update_difference()

root.mainloop()