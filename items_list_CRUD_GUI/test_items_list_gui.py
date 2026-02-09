import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import fnmatch
import re
import subprocess

# ---------------- Utility Functions ---------------- #

def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}"

def git_fetch():
    fetch_command = "git fetch upstream"
    merge_command = "git merge upstream/main"
    run_shell_command(fetch_command)
    run_shell_command(merge_command)

def expand_fqdn_range(fqdn):
    match = re.search(r'\[(\d+)-(\d+)\]', fqdn)
    if match:
        start, end = int(match.group(1)), int(match.group(2))
        base = fqdn[:match.start()] + "{:0" + str(len(match.group(1))) + "d}" + fqdn[match.end():]
        return [base.format(i) for i in range(start, end + 1)]
    return [fqdn]

# ---------------- Core Functions ---------------- #

def submit_form():
    fqdn_input = fqdn_text.get("1.0", tk.END).strip().split(',')
    comments_raw = comments_text.get("1.0", tk.END)
    comments = re.sub(r'\s+', ' ', comments_raw).strip()

    if not fqdn_input or all(not fqdn.strip() for fqdn in fqdn_input) or not comments:
        show_result("Error: Both hostname and comment are required.")
        return

    expanded_hostnames = []
    for fqdn in fqdn_input:
        expanded_hostnames.extend(expand_fqdn_range(fqdn.strip()))

    existing_hostnames = set()
    new_hostnames = []
    csv_file = "coding_sites_list.csv"

    if os.path.isfile(csv_file):
        try:
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)
                existing_hostnames = {row[0].strip().lower() for row in reader}
        except Exception as e:
            show_result(f"Error reading file: {e}")
            return

    for fqdn in expanded_hostnames:
        if fqdn.lower() not in existing_hostnames:
            new_hostnames.append((fqdn, comments))

    if new_hostnames:
        try:
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if os.path.getsize(csv_file) == 0:
                    writer.writerow(["Hostname", "Comments"])
                writer.writerows(new_hostnames)

            msg = f"Successfully added {len(new_hostnames)} Hostname(s)."
            if existing_hostnames:
                msg += "\n\nAlready listed hosts:\n"
                for fqdn in expanded_hostnames:
                    if fqdn.lower() in existing_hostnames:
                        msg += f"{fqdn}\n"
            show_result(msg)
        except Exception as e:
            show_result(f"Error writing to file: {e}")
    else:
        show_result("No new Hostnames were added. All provided Hostnames already exist.")

def search_fqdn():
    search_pattern = search_text.get("1.0", tk.END).strip().lower()
    csv_file = "coding_sites_list.csv"

    if not search_pattern:
        show_result("Please enter a search pattern.")
        return

    if not os.path.isfile(csv_file):
        show_result("The coding_sites_list.csv file does not exist.")
        return

    matches = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                fqdn = row[0].strip().lower()
                comment = row[1].strip()
                if fnmatch.fnmatch(fqdn, search_pattern):
                    matches.append(f"Hostname: {row[0]}, Comments: {comment}")
        if matches:
            show_result(f"Found {len(matches)} match(es):\n\n" + "\n".join(matches))
        else:
            show_result(f"No matches found for pattern '{search_pattern}'.")
    except Exception as e:
        show_result(f"Error reading file: {e}")

def remove_fqdn():
    search_pattern = search_text.get("1.0", tk.END).strip().lower()
    if not messagebox.askyesno("Confirm Deletion", f"Remove entries matching:\n\n'{search_pattern}'?"):
        return

    csv_file = "coding_sites_list.csv"
    if not search_pattern:
        show_result("Please enter a pattern to remove.")
        return
    if not os.path.isfile(csv_file):
        show_result("The coding_sites_list.csv file does not exist.")
        return

    updated_rows, removed_entries = [], []
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
        if removed_entries:
            show_result(f"Removed {len(removed_entries)} Hostname(s) matching '{search_pattern}'.")
        else:
            show_result(f"No Hostnames matching '{search_pattern}' were found to remove.")
    except Exception as e:
        show_result(f"Error processing file: {e}")

def clear_comments_and_fqdn():
    fqdn_text.delete("1.0", tk.END)
    comments_text.delete("1.0", tk.END)

def clear_search():
    search_text.delete("1.0", tk.END)

def clear_result():
    result_text.config(state='normal')
    result_text.delete("1.0", tk.END)
    result_text.config(state='disabled')

def show_result(message):
    result_text.config(state='normal')
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, message)
    result_text.config(state='disabled')

def on_close():
    commit_and_push()
    root.destroy()

def commit_and_push():
    run_shell_command("git add coding_sites_list.csv")
    run_shell_command("git commit -m 'Updated denied list'")
    run_shell_command("git push")

# ---------------- GUI Setup ---------------- #

root = tk.Tk()
root.title("Denied Hosts List")
root.geometry("800x900")
root.resizable(True, True)
root.protocol("WM_DELETE_WINDOW", on_close)
git_fetch()

style = ttk.Style()
style.configure("Custom.TButton", background="#3498db", foreground="black", padding=6, font=("Helvetica", 9, "bold"))

canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.grid(row=0, column=0, sticky='nsew')
scrollbar.grid(row=0, column=1, sticky='ns')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

main_frame = scrollable_frame

# FQDN Section
fqdn_frame = ttk.LabelFrame(main_frame, text="Add Hostnames", padding=10)
fqdn_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

fqdn_text = tk.Text(fqdn_frame, width=80, height=5, wrap=tk.WORD)
fqdn_text.grid(row=0, column=0, sticky="nsew", pady=5)

comments_text = tk.Text(fqdn_frame, width=80, height=4, wrap=tk.WORD)
comments_text.grid(row=1, column=0, sticky="nsew", pady=5)

btns1 = ttk.Frame(fqdn_frame)
btns1.grid(row=2, column=0, pady=5)
ttk.Button(btns1, text="Submit", command=submit_form, style="Custom.TButton").grid(row=0, column=0, padx=5)
ttk.Button(btns1, text="Clear Fields", command=clear_comments_and_fqdn, style="Custom.TButton").grid(row=0, column=1, padx=5)

# Search Section
search_frame = ttk.LabelFrame(main_frame, text="Search / Remove Hostnames", padding=10)
search_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

search_text = tk.Text(search_frame, width=80, height=3, wrap=tk.WORD)
search_text.grid(row=0, column=0, sticky="nsew", pady=5)

btns2 = ttk.Frame(search_frame)
btns2.grid(row=1, column=0, pady=5)
ttk.Button(btns2, text="Search", command=search_fqdn, style="Custom.TButton").grid(row=0, column=0, padx=5)
ttk.Button(btns2, text="Remove", command=remove_fqdn, style="Custom.TButton").grid(row=0, column=1, padx=5)
ttk.Button(btns2, text="Clear Search", command=clear_search, style="Custom.TButton").grid(row=0, column=2, padx=5)

# Results Section
results_frame = ttk.LabelFrame(main_frame, text="Results", padding=10)
results_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

result_text = tk.Text(results_frame, width=80, height=10, wrap=tk.WORD, state='disabled')
result_text.grid(row=0, column=0, sticky="nsew")

res_scroll = ttk.Scrollbar(results_frame, orient='vertical', command=result_text.yview)
result_text.configure(yscrollcommand=res_scroll.set)
res_scroll.grid(row=0, column=1, sticky='ns')

ttk.Button(results_frame, text="Clear Results", command=clear_result, style="Custom.TButton").grid(row=1, column=0, pady=5)

root.mainloop()
