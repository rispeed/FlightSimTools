import tkinter as tk
from tkinter import messagebox
from tkinter import font


#label_font = font.Font(family="Helvetica", size=14, weight="bold")

def update_output():
    try:
        needed_kg = float(entry_needed.get()) if entry_needed.get() else 0
        existing_kg = float(entry_existing.get()) if entry_existing.get() else 0
        density = float(entry_density.get()) if entry_density.get() else 0

        difference = needed_kg - existing_kg
        
        if difference < 0:
            output_label.config(text="You have enough fuel!")
            fuel_label.config(text="")
            return
        
        if fuel_unit.get() == "liters":
            if density > 0:
                fuel_amount = difference / density
            else:
                fuel_amount = 0
        else:  # gallons
            if density_type.get() == "kg/lt":
                density = density * 8.345404  # Convert to lbs/gal
            if density > 0:
                fuel_amount = difference / density
            else:
                fuel_amount = 0
        
        output_label.config(text=f"Difference: {difference:.2f} kg")
        fuel_label.config(text=f"Fuel needed: {fuel_amount:.2f} {fuel_unit.get()}")
    except ValueError:
        output_label.config(text="Invalid input!")
        fuel_label.config(text="")

def set_density():
    if density_type.get() == "kg/lt":
        entry_density.delete(0, tk.END)
        entry_density.insert(0, "0.8")
    else:  # lbs/gal
        entry_density.delete(0, tk.END)
        entry_density.insert(0, "6.7")

# Create the main window

root = tk.Tk()
label_font = font.Font(family="Helvetica", size=12, weight="bold")
root.title("Fuel Calculator")

# Input for kilograms needed

tk.Label(root, text="Kilograms needed:",font=label_font).grid(row=0, column=0)
entry_needed = tk.Entry(root)
entry_needed.grid(row=0, column=1)
entry_needed.bind("<KeyRelease>", lambda e: update_output())  # Update on key release

# Input for kilograms already have
tk.Label(root, text="Kilograms you already have:",font=label_font).grid(row=1, column=0)
entry_existing = tk.Entry(root)
entry_existing.grid(row=1, column=1)
entry_existing.bind("<KeyRelease>", lambda e: update_output())  # Update on key release

# Radio buttons for fuel unit
fuel_unit = tk.StringVar(value="liters")
tk.Label(root, text="Select fuel unit:",font=label_font).grid(row=2, column=0)
tk.Radiobutton(root, text="Liters", variable=fuel_unit, value="liters", command=update_output).grid(row=2, column=1)
tk.Radiobutton(root, text="Gallons", variable=fuel_unit, value="gallons", command=update_output).grid(row=2, column=2)

# Input for fuel density
tk.Label(root, text="Fuel density:",font=label_font).grid(row=3, column=0)
entry_density = tk.Entry(root)
entry_density.grid(row=3, column=1)
entry_density.insert(0, "0.8")  # Set default density value
entry_density.bind("<KeyRelease>", lambda e: update_output())

# Radio buttons for density unit
density_type = tk.StringVar(value="kg/lt")
tk.Label(root, text="Select density unit:",font=label_font).grid(row=4, column=0)
tk.Radiobutton(root, text="kg/L", variable=density_type, value="kg/lt", command=lambda: [set_density(), update_output()]).grid(row=4, column=1)
tk.Radiobutton(root, text="lbs/gal", variable=density_type, value="lbs/gal", command=lambda: [set_density(), update_output()]).grid(row=4, column=2)

# Output labels
output_label = tk.Label(root, text="Difference: 0.00 kg",font=label_font)
output_label.grid(row=5, column=0, columnspan=3)
fuel_label = tk.Label(root, text="Fuel needed: 0.00 liters",font=label_font)
fuel_label.grid(row=6, column=0, columnspan=3)

# Calculate button (optional)
calculate_button = tk.Button(root, text="Calculate", command=update_output,font=label_font)
calculate_button.grid(row=7, column=0, columnspan=3)

# Start the GUI event loop
root.mainloop()
