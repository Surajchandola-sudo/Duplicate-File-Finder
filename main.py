import os
import hashlib
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def setup_database():
    """Creates the database and table if they don't exist."""
    conn = sqlite3.connect('dff_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SCAN_HISTORY (
            Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Scan_Date TEXT,
            Target_Folder TEXT,
            Total_Files_Deleted INTEGER,
            Space_Freed_MB REAL
        )
    ''')
    conn.commit()
    conn.close()

def log_deletion(folder, files_deleted, space_freed_bytes):
    """Saves deletion history to the SQLite database."""
    space_mb = round(space_freed_bytes / (1024 * 1024), 2)
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('dff_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO SCAN_HISTORY (Scan_Date, Target_Folder, Total_Files_Deleted, Space_Freed_MB)
        VALUES (?, ?, ?, ?)
    ''', (current_date, folder, files_deleted, space_mb))
    conn.commit()
    conn.close()

# ==========================================
# 2. MAIN APPLICATION CLASS
# ==========================================
class DuplicateFileFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate File Finder System - By Suraj Chandola")
        self.root.geometry("850x650")
        self.root.configure(bg="#f0f0f0")

        self.target_folder = tk.StringVar()
        self.duplicate_groups = [] # Will store lists of duplicate file paths
        self.file_sizes = {} # Store file sizes for quick access

        self.setup_ui()
        setup_database()

    def setup_ui(self):
        # Top Frame (Selection)
        top_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        top_frame.pack(fill=tk.X, padx=10)

        tk.Label(top_frame, text="Select Folder to Scan:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Entry(top_frame, textvariable=self.target_folder, width=50, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        tk.Button(top_frame, text="Browse", command=self.browse_folder, bg="#0078D7", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Button(top_frame, text="SCAN", command=self.start_scan, bg="#28A745", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)

        # Middle Frame (Results Treeview)
        mid_frame = tk.Frame(self.root, pady=10)
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Scrollbar for Treeview
        tree_scroll = tk.Scrollbar(mid_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview (Table)
        self.tree = ttk.Treeview(mid_frame, columns=("Group", "File Name", "Size (KB)", "Path"), show="headings", yscrollcommand=tree_scroll.set, selectmode="extended")
        self.tree.heading("Group", text="Group ID")
        self.tree.column("Group", width=70, anchor="center")
        self.tree.heading("File Name", text="File Name")
        self.tree.column("File Name", width=200)
        self.tree.heading("Size (KB)", text="Size (KB)")
        self.tree.column("Size (KB)", width=100, anchor="center")
        self.tree.heading("Path", text="File Path")
        self.tree.column("Path", width=400)
        self.tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree.yview)

        # Bottom Frame (Action)
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        bottom_frame.pack(fill=tk.X, padx=10)

        tk.Label(bottom_frame, text="Hint: Hold 'Ctrl' and click to select multiple unwanted files.", font=("Arial", 10, "italic"), bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Button(bottom_frame, text="DELETE SELECTED FILES", command=self.delete_selected, bg="#DC3545", fg="white", font=("Arial", 12, "bold"), padx=10).pack(side=tk.RIGHT)

    # ==========================================
    # 3. CORE LOGIC & FUNCTIONS
    # ==========================================
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.target_folder.set(folder)

    def get_file_hash(self, filepath):
        """Generates MD5 hash of a file."""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as afile:
                buf = afile.read(65536) # Read in 64kb chunks
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(65536)
            return hasher.hexdigest()
        except Exception:
            return None

    def start_scan(self):
        folder = self.target_folder.get()
        if not folder:
            messagebox.showwarning("Warning", "Please select a folder first!")
            return

        # Security Mechanism: Do not scan Windows core folders
        if "C:/Windows" in folder.replace("\\", "/") or "System32" in folder:
            messagebox.showerror("Security Alert", "Scanning system folders is blocked for safety!")
            return

        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.duplicate_groups.clear()
        self.file_sizes.clear()

        # Step 1: Traverse and group by file size
        size_dict = {}
        for root, dirs, files in os.walk(folder):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    size = os.path.getsize(filepath)
                    self.file_sizes[filepath] = size
                    if size in size_dict:
                        size_dict[size].append(filepath)
                    else:
                        size_dict[size] = [filepath]
                except Exception:
                    pass # Ignore unreadable files

        # Step 2: Compare hashes for files with the exact same size
        hash_dict = {}
        for size, paths in size_dict.items():
            if len(paths) > 1: # Only hash if there are multiple files of the same size
                for path in paths:
                    file_hash = self.get_file_hash(path)
                    if file_hash:
                        if file_hash in hash_dict:
                            hash_dict[file_hash].append(path)
                        else:
                            hash_dict[file_hash] = [path]

        # Step 3: Extract true duplicates and display
        group_id = 1
        for file_hash, paths in hash_dict.items():
            if len(paths) > 1:
                self.duplicate_groups.append(paths)
                for path in paths:
                    filename = os.path.basename(path)
                    size_kb = round(self.file_sizes[path] / 1024, 2)
                    self.tree.insert("", tk.END, values=(f"Group {group_id}", filename, size_kb, path))
                # Insert a blank row to separate groups visually
                self.tree.insert("", tk.END, values=("---", "---", "---", "---"))
                group_id += 1

        if group_id == 1:
            messagebox.showinfo("Result", "No duplicate files found in this folder!")
        else:
            messagebox.showinfo("Result", f"Scan Complete! Found {group_id - 1} groups of duplicate files.")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select files from the list to delete.")
            return

        files_to_delete = []
        for item in selected_items:
            values = self.tree.item(item, "values")
            if values[0] != "---": # Avoid deleting the separator lines
                files_to_delete.append(values[3]) # Path is at index 3

        if not files_to_delete:
            return

        # Confirm Deletion
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(files_to_delete)} selected file(s)?\nThis cannot be undone!")
        
        if confirm:
            deleted_count = 0
            freed_space = 0

            for filepath in files_to_delete:
                try:
                    # Original file safe deletion
                    freed_space += self.file_sizes.get(filepath, 0)
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {filepath}: {e}")

            # Log to Database
            if deleted_count > 0:
                log_deletion(self.target_folder.get(), deleted_count, freed_space)
                freed_mb = round(freed_space / (1024 * 1024), 2)
                messagebox.showinfo("Success", f"Deleted {deleted_count} files.\nSpace Freed: {freed_mb} MB\nLog saved to database.")
                
                # Rescan to refresh the list
                self.start_scan()

# ==========================================
# 4. RUN APPLICATION
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFileFinderApp(root)
    root.mainloop()