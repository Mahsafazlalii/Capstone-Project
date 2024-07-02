import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import pandas as pd
import tkinter.ttk as ttk

# Define the path to your CSV file
csv_file_path = r'C:\Users\Ali\Desktop\updated_data.csv'  # Use the absolute path
  
def on_category_selected(value):
    category_var.set(value)
    filter_data()  # Directly call filter_data to apply filter when a category is selected

def load_file():
    try:
        global df
        df = pd.read_csv(csv_file_path)
        df.columns = df.columns.str.strip()  # Strip whitespace from column headers

        categories = ['Animal', 'Earth', 'Fire', 'Ice', 'Land', 'People', 'Plants', 'Water']
        category_var.set('Select a category')
        category_menu['menu'].delete(0, 'end')
        for category in categories:
            category_menu['menu'].add_command(label=category, command=lambda cat=category: on_category_selected(cat))
        status_var.set("File loaded successfully")
    except Exception as e:
        status_var.set(f"An error occurred: {e}")

       

def filter_data():
    global filtered_data
    if 'df' in globals():
        selected_category = category_var.get()
        if selected_category == 'Select a category':
            status_var.set("Please select a valid category.")
            return
        try:
            filtered_data = df[df['Category'].str.contains(selected_category, case=False, na=False)]
            if filtered_data.empty:
                status_var.set("No entries found for this category.")
                text_area.config(state='normal')
                text_area.delete('1.0', tk.END)
                text_area.config(state='disabled')
                return

            links = filtered_data['Link'].dropna()
            text_area.config(state='normal')
            text_area.delete('1.0', tk.END)
            text_area.insert(tk.END, "Links:\n")
            for link in links:
                text_area.insert(tk.END, link + '\n')
            text_area.config(state='disabled')
            status_var.set("Data filtered successfully")
        except KeyError as e:
            status_var.set(f"Column not found: {e}")
        except Exception as e:
            status_var.set(f"An error occurred while filtering: {e}")
    else:
        status_var.set("Data not loaded. Please load a CSV file first.")


def clear_results():
    text_area.config(state='normal')
    text_area.delete('1.0', tk.END)
    text_area.config(state='disabled')
    status_var.set("Results cleared")

def save_filtered_data():
    if 'filtered_data' in globals() and not filtered_data.empty:
        # Select only the required columns and remove duplicates
        columns_to_save = ['Title for Link', 'Link']
        filtered_to_save = filtered_data[columns_to_save].drop_duplicates()
        
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            try:
                filtered_to_save.to_csv(file_path, index=False)
                status_var.set(f"Filtered data saved to {file_path}")
            except Exception as e:
                status_var.set(f"An error occurred while saving the file: {e}")
    else:
        status_var.set("No filtered data to save.")

def set_focus(event=None):
    category_var.set('Select a category')

def search_in_results():
    search_text = search_entry.get().lower()
    if search_text:
        text_area.config(state='normal')
        content = text_area.get("1.0", tk.END).lower()
        text_area.tag_remove("highlight", "1.0", tk.END)
        start_idx = 1.0
        first_occurrence = True
        while True:
            start_idx = text_area.search(search_text, start_idx, tk.END, nocase=1)
            if not start_idx:
                break
            end_idx = f"{start_idx}+{len(search_text)}c"
            text_area.tag_add("highlight", start_idx, end_idx)
            if first_occurrence:
                text_area.see(start_idx)
                first_occurrence = False
            start_idx = end_idx
        text_area.tag_config("highlight", background="yellow")
        status_var.set(f"'{search_text}' found in the results.")
        text_area.config(state='disabled')
    else:
        status_var.set("Please enter text to search.")

class ToolTip(tk.Toplevel):
    def __init__(self, widget, text):
        super().__init__(widget)
        self.widget = widget
        self.text = text
        self.overrideredirect(True)
        self.geometry(f"+{widget.winfo_rootx() + 20}+{widget.winfo_rooty() + 20}")
        label = tk.Label(self, text=self.text, background="yellow", relief=tk.SOLID, borderwidth=1)
        label.pack()

def show_tooltip(event):
    global tooltip
    tooltip = ToolTip(event.widget, "Search for keywords in the displayed links.\nExamples: 'Agriculture', 'geomatics', 'LCC/MapServer'")
    
def hide_tooltip(event):
    global tooltip
    if tooltip:
        tooltip.destroy()

app = tk.Tk()
app.title("Data Filter Hub")  # Change this to the desired title

# Status bar
status_var = tk.StringVar()
status_bar = tk.Label(app, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Frame for filter options
filter_frame = tk.Frame(app, padx=10, pady=10)
filter_frame.pack(fill=tk.X)

filter_label = tk.Label(filter_frame, text="Select filter category:")
filter_label.pack(side=tk.LEFT)

category_var = tk.StringVar(app)
category_menu = tk.OptionMenu(filter_frame, category_var, 'Loading...')
category_menu.pack(side=tk.LEFT, padx=10)

filter_button = tk.Button(filter_frame, text="Filter Data", command=filter_data)
filter_button.pack(side=tk.LEFT, padx=10)

clear_button = tk.Button(filter_frame, text="Clear Results", command=clear_results)
clear_button.pack(side=tk.LEFT, padx=10)

save_button = tk.Button(filter_frame, text="Save Filtered Data", command=save_filtered_data)
save_button.pack(side=tk.LEFT, padx=10)

# Frame for search functionality
search_frame = tk.Frame(app, padx=10, pady=10)
search_frame.pack(fill=tk.X)

search_label = tk.Label(search_frame, text="Search in results:")
search_label.pack(side=tk.LEFT)

search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, padx=5)
search_entry.bind("<Enter>", show_tooltip)
search_entry.bind("<Leave>", hide_tooltip)

search_button = tk.Button(search_frame, text="Search", command=search_in_results)
search_button.pack(side=tk.LEFT, padx=10)

# Instruction label for search
instruction_label = tk.Label(app, text="Enter keywords to search in the filtered links displayed below (e.g., 'Agriculture', 'geomatics', 'LCC/MapServer'):")
instruction_label.pack(padx=10, pady=5)

# Frame for displaying results
results_frame = tk.Frame(app, padx=10, pady=10)
results_frame.pack(fill=tk.BOTH, expand=True)

# Text widget for displaying links
text_area = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15, state='disabled')
text_area.pack(fill=tk.BOTH, expand=True)

# Load the CSV file as soon as the app starts
load_file()

# Bind focus-in event to set focus
app.bind("<FocusIn>", set_focus)

# Set the focus on the entry widget after a slight delay
app.after(100, set_focus)

app.mainloop()

