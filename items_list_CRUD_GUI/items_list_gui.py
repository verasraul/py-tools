#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox 
import csv
import os
import fnmatch
import re
import subprocess

def run_shell_command(command):
    """Run shell commands and capture output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}"

def git_fetch():
    """Fetch changes from the upstream repo and merge them into the local main branch."""
    fetch_command = "git fetch upstream"
    merge_command = "git merge upstream/main"
    fetch_result = run_shell_command(fetch_command)
    merge_result = run_shell_command(merge_command)
    print(fetch_result)  # Optionally display the fetch result in the GUI or log it.
    print(merge_result)

def expand_fqdn_range(fqdn):
    """Expand range patterns into a list of names."""
    match = re.search(r'\[(\d+)-(\d+)\]', fqdn)
    if match:
        start, end = int(match.group(1)), int(match.group(2))
        base = fqdn[:match.start()] + "{:0" + str(len(match.group(1))) + "d}" + fqdn[match.end():]
        return [base.format(i) for i in range(start, end + 1)]
    else:
        return [fqdn]

def submit_form():
    """Submit Hostnames and comments to csv file."""
    fqdn_input = fqdn_text.get("1.0", tk.END).strip().split(',')
    comments_raw = comments_text.get("1.0", tk.END)
    comments = re.sub(r'\s+', ' ', comments_raw).strip()

    if not fqdn_input or all(not fqdn.strip() for fqdn in fqdn_input) or not comments:
        result_text.config(state='normal')
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Error: Both hostname and comment are required.")
        result_text.config(state='disabled')
        return
    
    # Expand Hostnames with ranges
    expanded_hostnames = []
    for fqdn in fqdn_input:
        expanded_hostnames.extend(expand_fqdn_range(fqdn.strip()))

    existing_hostnames = set()
    new_hostnames = []
    csv_file = "coding_sites_list.csv"
    
    # Check if the Hostnames already exist in the file
    if os.path.isfile(csv_file):
        try:
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header
                existing_hostnames = {row[0].strip().lower() for row in reader}
        except Exception as e:
            result_text.config(state='normal')
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, f"Error reading file: {e}")
            result_text.config(state='disabled')
            return

    # Separate new and existing Hostnames
    for fqdn in expanded_hostnames:
        if fqdn.lower() in existing_hostnames:
            continue
        else:
            new_hostnames.append((fqdn, comments))
    
    if new_hostnames:
        try:
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if os.path.getsize(csv_file) == 0:  # File is empty, write headers
                    writer.writerow(["Hostname", "Comments"])
                writer.writerows(new_hostnames)
            
            result_text.config(state='normal')
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, f"Successfully added {len(new_hostnames)} Hostname(s) to coding_sites_list.csv.")
            
            # List the existing Hostnames
            if existing_hostnames:
                result_text.insert(tk.END, "\n\nThe following hosts are already listed:\n")
                for fqdn in expanded_hostnames:
                    if fqdn.lower() in existing_hostnames:
                        result_text.insert(tk.END, f"{fqdn}\n")
            
            result_text.config(state='disabled')
        except Exception as e:
            result_text.config(state='normal')
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, f"Error writing to file: {e}")
            result_text.config(state='disabled')
    else:
        result_text.config(state='normal')
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "No new Hostnames were added. All provided Hostnames already exist.")
        result_text.config(state='disabled')

def search_fqdn():
    """Search for Hostnames with wildcard."""
    search_pattern = search_text.get("1.0", tk.END).strip().lower()
    csv_file = "coding_sites_list.csv"
    
    if search_pattern:
        if os.path.isfile(csv_file):
            matches = []
            try:
                with open(csv_file, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader, None)  # Skip header
                    for row in reader:
                        fqdn = row[0].strip().lower()
                        comment = row[1].strip()
                        if fnmatch.fnmatch(fqdn, search_pattern):
                            matches.append(f"Hostname: {row[0]}, Comments: {comment}")
                
                result_text.config(state='normal')
                result_text.delete("1.0", tk.END)
                if matches:
                    result_text.insert(tk.END, f"Found {len(matches)} match(es):\n\n")
                    result_text.insert(tk.END, "\n".join(matches))
                else:
                    result_text.insert(tk.END, f"No matches found for pattern '{search_pattern}'.")
                result_text.config(state='disabled')
            except Exception as e:
                result_text.config(state='normal')
                result_text.delete("1.0", tk.END)
                result_text.insert(tk.END, f"Error reading file: {e}")
                result_text.config(state='disabled')
        else:
            result_text.config(state='normal')
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, "The coding_sites_list.csv file does not exist.")
            result_text.config(state='disabled')
    else:
        result_text.config(state='normal')
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Please enter a search pattern.")
        result_text.config(state='disabled')

def remove_fqdn():
    """Remove Hostnames with wildcard."""
    search_pattern = search_text.get("1.0", tk.END).strip().lower()
    if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove entries matching:\n\n'{search_pattern}'?"):
        return
    
    csv_file = "coding_sites_list.csv"
    
    if search_pattern:
        if os.path.isfile(csv_file):
            updated_rows = []
            removed_entries = []
            try:
                with open(csv_file, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    headers = next(reader, None)
                    for row in reader:
                        fqdn = row[0].strip().lower()
                        if fnmatch.fnmatch(fqdn, search_pattern):
                            removed_entries.append(row)
                        else:
                            updated_rows.append(row)
                
                with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    if headers:
                        writer.writerow(headers)
                    writer.writerows(updated_rows)
                
                result_text.config(state='normal')
                result_text.delete("1.0", tk.END)
                if removed_entries:
                    result_text.insert(tk.END, f"Removed {len(removed_entries)} Hostname(s) matching '{search_pattern}'.")
                else:
                    result_text.insert(tk.END, f"No Hostnames matching '{search_pattern}' were found to remove.")
                result_text.config(state='disabled')
            except Exception as e:
                result_text.config(state='normal')
                result_text.delete("1.0", tk.END)
                result_text.insert(tk.END, f"Error processing file: {e}")
                result_text.config(state='disabled')
        else:
            result_text.config(state='normal')
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, "The coding_sites_list.csv file does not exist.")
            result_text.config(state='disabled')
    else:
        result_text.config(state='normal')
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Please enter a pattern to remove.")
        result_text.config(state='disabled')

def clear_comments_and_fqdn():
    """Clear both Hostname and Comments text fields."""
    fqdn_text.delete("1.0", tk.END)
    comments_text.delete("1.0", tk.END)

def clear_search():
    """Clear the Search text field."""
    search_text.delete("1.0", tk.END)

def clear_result():
    """Clear the Result text field."""
    result_text.config(state='normal')
    result_text.delete("1.0", tk.END)
    result_text.config(state='disabled')

def on_close():
    """Actions to perform when the GUI is closed."""
    commit_and_push()
    root.destroy()

def commit_and_push():
    """Commit and push the changes to the Git repository."""
    add_command = "git add coding_sites_list.csv"
    commit_command = "git commit -m 'Updated denied list'"
    push_command = "git push"
    add_result = run_shell_command(add_command)
    commit_result = run_shell_command(commit_command)
    push_result = run_shell_command(push_command)
    # Display any errors encountered during the git commit/push operations
    print(add_result)
    print(commit_result)
    print(push_result)

# # ...GUI Setup...
# root = tk.Tk()
# root.title("Denied Hosts List")
# # root.geometry("800x1000")
# root.resizable(True, True)

# # Initialize and pull changes at startup
# git_fetch()

# # Bind the close event to the on_close function
# root.protocol("WM_DELETE_WINDOW", on_close)

# # Style Configuration
# # style = tk.Style()
# # style.configure('TButton', font=('Helvetica', 10))
# # style.configure('TLabel', foreground='green', font=('Helvetica', 12))
# # style.configure('TFrame', foreground='green', padding=10)
# # style.configure('main_frame', background='#fff')

# # Main Frame
# main_frame = ttk.Frame(root)
# main_frame.pack(fill=tk.BOTH, expand=True)

# # Hostname Input Section
# fqdn_frame = ttk.LabelFrame(main_frame, text="Add Hostnames")
# fqdn_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# fqdn_label = ttk.Label(fqdn_frame, text="Enter Hostname(s) (comma-separated):")
# #fqdn_label.pack(anchor=tk.W, pady=(5, 0))
# fqdn_label.grid(row=0, column=0, sticky='w', padx=5, pady=2)

# fqdn_text = tk.Text(fqdn_frame, width=80, height=3, wrap=tk.WORD)
# #fqdn_text.pack(pady=5)
# fqdn_text.grid(row=0, column=1, padx=5, pady=2)

# comments_label = ttk.Label(fqdn_frame, text="Comments:")
# # comments_label.pack(anchor=tk.W, pady=(5, 0))
# comments_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)

# comments_text = tk.Text(fqdn_frame, width=80, height=3, wrap=tk.WORD)
# # comments_text.pack(pady=5)
# comments_text.grid(row=1, column=1, padx=5, pady=2)

# clear_add_button = ttk.Button(fqdn_frame, text="Clear Fields", command=clear_comments_and_fqdn)
# clear_add_button.pack(side=tk.LEFT, padx=5, pady=5)

# submit_button = ttk.Button(fqdn_frame, text="Submit", command=submit_form, highlightbackground='#00a8ff')
# submit_button.pack(side=tk.RIGHT, padx=5, pady=5)

# # Search and Remove Section
# search_frame = tk.LabelFrame(main_frame, relief='flat', text="Search / Remove Hostnames", bg='#0097e6', foreground='black')
# search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# search_label = tk.Label(search_frame, text="Search Pattern (supports wildcards '*', '?'):", bg='#0097e6', foreground='black')
# search_label.pack(anchor=tk.W, pady=(5, 0))

# search_text = tk.Text(search_frame, width=80, height=2, wrap=tk.WORD)
# search_text.pack(pady=5)

# search_buttons_frame = tk.Frame(search_frame, bg='#0097e6')
# search_buttons_frame.pack(fill=tk.X, pady=5)

# search_button = tk.Button(search_buttons_frame, text="Search", command=search_fqdn, highlightbackground='#0097e6')
# search_button.pack(side=tk.LEFT, padx=5)

# remove_button = tk.Button(search_buttons_frame, text="Remove", command=remove_fqdn, highlightbackground='#0097e6')
# remove_button.pack(side=tk.LEFT, padx=5)

# clear_search_button = tk.Button(search_buttons_frame, text="Clear Search", command=clear_search, highlightbackground='#0097e6')
# clear_search_button.pack(side=tk.LEFT, padx=5)

# # Result Section
# result_frame = tk.LabelFrame(main_frame, relief='flat', text="Results", bg='#487eb0', foreground='white')
# result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# result_text = tk.Text(result_frame, width=80, height=10, wrap=tk.WORD, state='disabled')
# result_text.pack(pady=5)

# clear_result_button = tk.Button(result_frame, text="Clear Results", command=clear_result, highlightbackground='#487eb0')
# clear_result_button.pack(side=tk.RIGHT, padx=5, pady=5)

# # Start the main event loop
# root.mainloop()

# Apply full working scrollable layout to the canvas code
# GUI Setup with scrollable frame
root = tk.Tk()
root.title("Denied Hosts List")
root.geometry("760x1050")
root.resizable(True, True)
git_fetch()
root.protocol("WM_DELETE_WINDOW", on_close)

# Create canvas + scrollbar to make main area scrollable
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.grid(row=0, column=0, sticky='nsew')
scrollbar.grid(row=0, column=1, sticky='ns')

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# main_frame = ttk.Frame(root, padding=10)
# main_frame.grid(row=0, column=0, sticky='nsew')
main_frame = scrollable_frame

for i in range(3):
    main_frame.columnconfigure(i, weight=1)
for r in [1, 3, 6, 10]:
    main_frame.rowconfigure(r, weight=0)

# FQDN Input
ttk.Label(main_frame, text="Enter Hostname(s) (comma-separated):").grid(row=0, column=0, sticky='w')
# fqdn_text = tk.Text(main_frame, height=9, wrap=tk.WORD)
# fqdn_text.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=5)
fqdn_container = ttk.Frame(main_frame)
fqdn_container.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=5, padx=(10, 0))
fqdn_text = tk.Text(fqdn_container, width=100, wrap=tk.WORD)
fqdn_text.pack(fill='both', expand=True)

ttk.Label(main_frame, text="Comments:").grid(row=2, column=0, sticky='w')
# comments_text = tk.Text(main_frame, height=9, wrap=tk.WORD)
# comments_text.grid(row=3, column=0, columnspan=2, sticky='nsew', pady=5)
comments_container = ttk.Frame(main_frame)
comments_container.grid(row=3, column=0, columnspan=2, sticky='nsew', pady=5, padx=(10, 0))
comments_text = tk.Text(comments_container, height=6, width=80, wrap=tk.WORD)
comments_text.pack(fill='both', expand=True)

# ttk.Button(main_frame, text="Submit", command=submit_form).grid(row=4, column=0, sticky='e', pady=5)
# ttk.Button(main_frame, text="Clear Fields", command=clear_comments_and_fqdn).grid(row=4, column=1, sticky='w', pady=5)
submit_button_container = ttk.Frame(main_frame)
submit_button_container.grid(row=4, column=0, columnspan=2, pady=5)

ttk.Button(submit_button_container, text="Submit", command=submit_form).pack(side="left", padx=5)
ttk.Button(submit_button_container, text="Clear Fields", command=clear_comments_and_fqdn).pack(side="left", padx=5)


# Search Section
ttk.Label(main_frame, text="Search Pattern (supports wildcards '*', '?'):").grid(row=5, column=0, sticky='w')
# search_text = tk.Text(main_frame, height=3, wrap=tk.WORD)
# search_text.grid(row=6, column=0, columnspan=2, sticky='ew', pady=5)
search_container = ttk.Frame(main_frame)
search_container.grid(row=6, column=0, columnspan=2, sticky='nsew', pady=5, padx=(10, 0))
search_text = tk.Text(search_container, height=4, width=80, wrap=tk.WORD)
search_text.pack(fill='both', expand=True)


# Add a placeholder frame to contain the buttons
button_container = ttk.Frame(main_frame)
button_container.grid(row=7, column=0, columnspan=2, pady=5)

ttk.Button(button_container, text="Search", command=search_fqdn).pack(side="left", padx=5)
ttk.Button(button_container, text="Remove", command=remove_fqdn).pack(side="left", padx=5)
ttk.Button(button_container, text="Clear Search", command=clear_search).pack(side="left", padx=5)

# Results Section
ttk.Label(main_frame, text="Results:").grid(row=9, column=0, sticky='w')
# result_text = tk.Text(main_frame, height=10, wrap=tk.WORD, state='disabled')
# result_text.grid(row=10, column=0, columnspan=2, sticky='nsew', pady=5)
results_container = ttk.Frame(main_frame)
results_container.grid(row=10, column=0, columnspan=2, sticky='nsew', pady=5, padx=(10, 0))
result_text = tk.Text(results_container, width=100, wrap=tk.WORD, state='disabled')
result_text.pack(side='left', fill='both', expand=True)

# Attach scrollbar
results_scrollbar = ttk.Scrollbar(results_container, orient='vertical', command=result_text.yview)
result_text.configure(yscrollcommand=results_scrollbar.set)
results_scrollbar.pack(side='right', fill='y')
# scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=result_text.yview)
# result_text.configure(yscrollcommand=scrollbar.set)
# scrollbar.grid(row=10, column=2, sticky='ns')

ttk.Button(main_frame, text="Clear Results", command=clear_result).grid(row=11, column=0, columnspan=2, pady=5)

root.mainloop()
