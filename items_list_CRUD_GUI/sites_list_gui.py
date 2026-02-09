import tkinter as tk
import csv
import os
import fnmatch
import re
import subprocess

### Dependency Inversion & Single Responsibility: Command Execution ###
def execute_command(command: str) -> str:
    """Executes a shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

### Single Responsibility: File Handling ###
def write_to_csv(file_name, data):
    """Writes data to a CSV file and handles file operations."""
    try:
        with open(file_name, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if os.path.getsize(file_name) == 0:
                writer.writerow(["FQDN", "Comments"])  # Write header if file is empty
            writer.writerows(data)
        return True, len(data)
    except Exception as e:
        return False, f"Error writing to file: {e}"

def read_from_csv(file_name):
    """Reads data from a CSV file."""
    try:
        with open(file_name, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            return list(reader)
    except Exception as e:
        return False, f"Error reading file: {e}"

### Single Responsibility: FQDN Expansion ###
def expand_fqdn_range(fqdn: str):
    """Expand FQDN patterns like varnish[09-11].voice.prod.co."""
    match = re.search(r'\[(\d+)-(\d+)\]', fqdn)
    if match:
        start, end = int(match.group(1)), int(match.group(2))
        base = fqdn[:match.start()] + "{:0" + str(len(match.group(1))) + "d}" + fqdn[match.end():]
        return [base.format(i) for i in range(start, end + 1)]
    else:
        return [fqdn]

### Open/Closed Principle: Git Operations ###
def commit_and_push_changes():
    """Commit and push changes to the Git repository."""
    commands = [
        "git add coding_sites_list.csv",
        "git commit -m 'Updated coding_sites_list.csv with new FQDN entries'",
        "git push"
    ]
    for command in commands:
        result = execute_command(command)
        if "Error" in result:
            print(result)
            return False, result
    return True, "Git operations completed successfully."

### Single Responsibility: FQDN Management ###
def submit_fqdns(fqdns, comments, file_name="coding_sites_list.csv"):
    """Submits expanded FQDNs to the CSV file."""
    expanded_fqdns = []
    for fqdn in fqdns:
        expanded_fqdns.extend(expand_fqdn_range(fqdn.strip()))

    file_data = read_from_csv(file_name)
    if not file_data:
        return False, "Error reading file."

    existing_fqdns = {row[0].strip().lower() for row in file_data[1:]}  # Skip header
    new_fqdns = [(fqdn, comments) for fqdn in expanded_fqdns if fqdn.lower() not in existing_fqdns]

    if new_fqdns:
        success, result = write_to_csv(file_name, new_fqdns)
        if success:
            return True, new_fqdns
        else:
            return False, result
    return False, "All FQDNs already exist."

def search_fqdn(pattern, file_name="coding_sites_list.csv"):
    """Search for FQDNs in the file using a pattern."""
    file_data = read_from_csv(file_name)
    if not file_data:
        return False, "Error reading file."

    matches = [f"FQDN: {row[0]}, Comments: {row[1]}" for row in file_data[1:] if fnmatch.fnmatch(row[0].strip().lower(), pattern)]
    if matches:
        return True, matches
    else:
        return False, "No matches found."

def remove_fqdn(pattern, file_name="coding_sites_list.csv"):
    """Remove FQDNs from the file using a pattern."""
    file_data = read_from_csv(file_name)
    if not file_data:
        return False, "Error reading file."

    updated_rows = [file_data[0]]  # Keep header
    removed_entries = []
    for row in file_data[1:]:
        fqdn = row[0].strip().lower()
        if fnmatch.fnmatch(fqdn, pattern):
            removed_entries.append(row)
        else:
            updated_rows.append(row)

    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

    if removed_entries:
        return True, removed_entries
    return False, "No FQDNs matched the pattern."

### GUI Integration ###

def submit_fqdns_gui():
    """Handles FQDN submission through the GUI."""
    fqdns = fqdn_text.get("1.0", tk.END).strip().split(',')
    comments = comments_text.get("1.0", tk.END).strip()
    success, result = submit_fqdns(fqdns, comments)
    update_result(success, result)

def search_fqdn_gui():
    """Handles FQDN search through the GUI."""
    pattern = search_text.get("1.0", tk.END).strip().lower()
    success, result = search_fqdn(pattern)
    update_result(success, result)

def remove_fqdn_gui():
    """Handles FQDN removal through the GUI."""
    pattern = search_text.get("1.0", tk.END).strip().lower()
    success, result = remove_fqdn(pattern)
    update_result(success, result)

def update_result(success, result):
    """Update the result box in the GUI."""
    result_text.config(state='normal')
    result_text.delete("1.0", tk.END)
    if success:
        if isinstance(result, list):
            result_text.insert(tk.END, "\n".join(result))
        else:
            result_text.insert(tk.END, result)
    else:
        result_text.insert(tk.END, result)
    result_text.config(state='disabled')

def clear_result():
    """Clear the result text field."""
    result_text.config(state='normal')
    result_text.delete("1.0", tk.END)
    result_text.config(state='disabled')

def on_close():
    """Handles GUI closing and Git operations."""
    commit_and_push_changes()
    root.destroy()

### GUI Setup ###

root = tk.Tk()
root.title("Denied FQDN Manager")
root.geometry("700x700")
root.resizable(False, False)

# Main Frame
main_frame = tk.Frame(root, bg='red')
main_frame.pack(fill=tk.BOTH, expand=True)

# FQDN Input Section
fqdn_frame = tk.LabelFrame(main_frame, text="Add FQDNs", bg='light gray')
fqdn_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

fqdn_text = tk.Text(fqdn_frame, width=80, height=3, wrap=tk.WORD)
fqdn_text.pack(pady=5)

comments_text = tk.Text(fqdn_frame, width=80, height=3, wrap=tk.WORD)
comments_text.pack(pady=5)

tk.Button(fqdn_frame, text="Submit", command=submit_fqdns_gui).pack(side=tk.RIGHT, padx=5, pady=5)

# Search Section
search_frame = tk.LabelFrame(main_frame, text="Search / Remove FQDNs", bg='light gray')
search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

search_text = tk.Text(search_frame, width=80, height=2, wrap=tk.WORD)
search_text.pack(pady=5)

tk.Button(search_frame, text="Search", command=search_fqdn_gui).pack(side=tk.LEFT, padx=5)
tk.Button(search_frame, text="Remove", command=remove_fqdn_gui).pack(side=tk.LEFT, padx=5)

# Result Section
result_frame = tk.LabelFrame(main_frame, text="Result", bg='light gray')
result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

result_text = tk.Text(result_frame, width=80, height=10, wrap=tk.WORD, state='normal')
result_text.pack(pady=5)

tk.Button(result_frame, text="Clear Result", command=clear_result).pack(side=tk.RIGHT, padx=5, pady=5)

# Close Event
root.protocol("WM_DELETE_WINDOW", on_close)

# Start the main event loop
root.mainloop()
