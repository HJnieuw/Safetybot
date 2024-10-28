import tkinter as tk
import subprocess

def import_bim():
    """Placeholder function for the Import BIM button."""
    print("Import BIM button clicked (no action defined).")

def start_scripts():
    """Function to start the start.py script."""
    subprocess.Popen(["python", "/Users/tombo/Documents/CORE/Safetybot/S.I.M.O.H./modules/start.py"])

# Set up the main Tkinter window
root = tk.Tk()
root.title("S.I.M.O.H. Control Panel")
root.geometry("300x150")

# Create and place the Import BIM button
import_button = tk.Button(root, text="Import BIM", command=import_bim, width=20, height=2)
import_button.pack(pady=10)

# Create and place the Start button
start_button = tk.Button(root, text="Start", command=start_scripts, width=20, height=2)
start_button.pack(pady=10)

# Run the Tkinter main loop
root.mainloop()
