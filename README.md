# Duplicate File Finder System v1.0

A lightweight, high-performance, and secure local storage optimization desktop utility built using Python 3.12, Tkinter, and SQLite3. The system scans deeply nested directories, identifies exact duplicate files using cryptographic MD5 checksums, and provides a safe, interactive interface for permanent data reclamation.

## 🚀 Key Features
* **Dual-Layer Filtration Engine:** Optimizes scanning speed by first grouping files by physical byte-size, then performing cryptographic verification only on matching sizes.
* **Cryptographic Accuracy:** Uses the MD5 algorithm to read internal binary streams in 64KB chunks, eliminating false positives and preventing memory overload on massive files (>2GB).
* **Interactive UI Grid:** Renders results dynamically in a multi-column Tkinter Treeview grid with specific checkboxes for precise user-controlled deletion.
* **Failsafe Security:** Implements strict read-only modes during scans, wraps file I/O operations in privilege exception blocks, and forces double-verification prompts before execution.
* **Persistent History Logging:** Automatically commits cumulative session metrics (freed storage, timestamp, target path) into a serverless SQLite backend audit trail.

## 📁 Repository Structure
* `main.py` - Core source code containing the standalone OOP implementation (GUI, Engine, and DB modules).
* `Duplicate_File_Finder.exe` - Pre-compiled, production-ready executable application for instant testing on Windows.
* `dff_history.db` - Localized storage instance for historical logging schemas.

## ⚙️ Installation & Usage

### Method 1: Instant Execution (For Examiners)
1. Navigate to the repository root.
2. Download and double-click on `Duplicate_File_Finder.exe`.
3. No external Python dependencies or installations are required.

### Method 2: Running from Source
If you wish to audit or execute the source code directly, ensure you have Python 3.10+ installed:
```bash
# Run the application
python main.py
