import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import json
import subprocess

SPREAD_GEN_SCRIPT = 'spread_gen.py'

class MentorSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Mentor Scheduler')
        
        # Mentor Management Section
        tk.Button(self.root, text="Add/Edit Mentor Info", command=self.edit_mentor_info).grid(row=0, columnspan=2)
        
        # Schedule Name
        tk.Label(self.root, text="Schedule Name:").grid(row=1, column=0)
        self.schedule_name_entry = tk.Entry(self.root)
        self.schedule_name_entry.grid(row=1, column=1)
        
        # Year
        tk.Label(self.root, text="Year:").grid(row=2, column=0)
        self.year_entry = tk.Entry(self.root)
        self.year_entry.grid(row=2, column=1)
        
        # Month Dropdown Menu
        tk.Label(self.root, text="Month:").grid(row=3, column=0)
        self.months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        self.month_var = tk.StringVar()
        self.month_dropdown = ttk.Combobox(self.root, textvariable=self.month_var, values=self.months, state="readonly")
        self.month_dropdown.grid(row=3, column=1)
        
        # Generate Button
        tk.Button(self.root, text="Generate Schedule", command=self.generate_schedule).grid(row=4, columnspan=2)

    def edit_mentor_info(self):
        # Open the JSON file and read the mentor information
        with open('mentor_db.json', 'r') as file:
            self.mentor_data = json.load(file)
        
        self.mentor_names = ["New Mentor"] + list(self.mentor_data['mentor_info'].keys())
        
        # Create a new window for editing mentor information
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Mentor Information")

        # Dropdown menu to select an existing mentor to edit
        tk.Label(self.edit_window, text="Select Mentor:").grid(row=0, column=0)
        self.selected_mentor_var = tk.StringVar(self.edit_window)
        self.selected_mentor_var.set(self.mentor_names[0])  # Set to 'New Mentor'
        self.mentor_dropdown = ttk.Combobox(self.edit_window, textvariable=self.selected_mentor_var, values=self.mentor_names, state="readonly")
        self.mentor_dropdown.grid(row=0, column=1)
        self.mentor_dropdown.bind('<<ComboboxSelected>>', self.load_mentor_info)

        # Entry fields for mentor information
        self.name_entry = self.create_label_entry("Name:", 1)
        self.weekdays_entry = self.create_label_entry("Weekdays unavailable (comma separated):", 2)
        self.hard_dates_entry = self.create_label_entry("Dates unavailable (comma separated):", 3)
        self.hours_wanted_entry = self.create_label_entry("Hours Wanted:", 4)
        self.soft_dates_entry = self.create_label_entry("Soft Dates (comma separated):", 5)

        # Save button to save edited information or add a new mentor
        self.save_button = tk.Button(self.edit_window, text="Save", command=self.save_mentor_info)
        self.save_button.grid(row=6, column=1)

    def create_label_entry(self, label_text, row):
        tk.Label(self.edit_window, text=label_text).grid(row=row, column=0)
        entry = tk.Entry(self.edit_window)
        entry.grid(row=row, column=1)
        return entry

    def load_mentor_info(self, event):
        # Load the selected mentor's information into the entry fields for editing
        selected_mentor_name = self.selected_mentor_var.get()
        if selected_mentor_name == "New Mentor":
            self.name_entry.delete(0, tk.END)
            self.weekdays_entry.delete(0, tk.END)
            self.hard_dates_entry.delete(0, tk.END)
            self.hours_wanted_entry.delete(0, tk.END)
            self.soft_dates_entry.delete(0, tk.END)
        else:
            mentor_info = self.mentor_data['mentor_info'][selected_mentor_name]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, selected_mentor_name)
            self.weekdays_entry.delete(0, tk.END)
            self.weekdays_entry.insert(0, ','.join(mentor_info.get('weekdays', [])))
            self.hard_dates_entry.delete(0, tk.END)
            self.hard_dates_entry.insert(0, ','.join(map(str, mentor_info.get('hard_dates', []))))
            self.hours_wanted_entry.delete(0, tk.END)
            self.hours_wanted_entry.insert(0, mentor_info.get('hours_wanted', ''))
            self.soft_dates_entry.delete(0, tk.END)
            self.soft_dates_entry.insert(0, ','.join(map(str, mentor_info.get('soft_dates', []))))

    def save_mentor_info(self):
        # Logic to save the edited information back to the JSON file
        name = self.name_entry.get()
        weekdays = self.weekdays_entry.get().split(',')
        hard_dates = list(map(int, self.hard_dates_entry.get().split(',')))
        hours_wanted = int(self.hours_wanted_entry.get())
        soft_dates = list(map(int, self.soft_dates_entry.get().split(',')))

        if not name:
            messagebox.showerror("Error", "The name field cannot be empty.")
            return

        # Replace or add the mentor information
        self.mentor_data['mentor_info'][name] = {
            "weekdays": weekdays,
            "hard_dates": hard_dates,
            "hours_wanted": hours_wanted,
            "soft_dates": soft_dates
        }

        # Save the updated mentor data back to the JSON file
        with open('mentor_db.json', 'w') as file:
            json.dump(self.mentor_data, file, indent=4)

        messagebox.showinfo("Success", "Mentor information saved successfully.")
        self.edit_window.destroy()

    def generate_schedule(self):
        schedule_name = self.schedule_name_entry.get()
        year = self.year_entry.get()
        month = str(self.months.index(self.month_var.get()) + 1)  # Convert month name to month number
        pay_period_length = '15'  # Hardcoded to always be 15
        
        # Call spread_gen.py with subprocess
        try:
            subprocess.run(['python', SPREAD_GEN_SCRIPT, schedule_name, year, month, pay_period_length], check=True)
            messagebox.showinfo("Success", "Schedule generated successfully.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", "Failed to generate schedule.")

def main():
    root = tk.Tk()
    app = MentorSchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
