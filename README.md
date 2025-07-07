# 🔃 Modrinth Collection Downloader
![Modrinth Collection Downloader Design1](https://github.com/user-attachments/assets/2bd97296-b995-48a8-b71b-1f42ded61661)
Tired of downloading your mods one by one? This Python script is perfect for you!



## Example of what it looks like on usage:
<img src="https://github.com/user-attachments/assets/d613c07d-44f5-47f2-88a8-342d282cd096" alt="image" width="750"/>



A modern Python script to **automatically download and update mods** from a [Modrinth](https://modrinth.com) collection, tailored to your chosen Minecraft version and mod loader (e.g., Fabric, Forge, Quilt).

This script streamlines the management of large modpacks by fetching mods directly via Modrinth's API and organizing them locally.

---

## 🚀 Features

- Download all mods from a Modrinth collection in one go
- Filter mods by Minecraft version and mod loader
- Automatically skip or update existing mods
- Multithreaded downloads for faster performance
- Clean, consistent file naming using mod IDs

---

## 📦 Requirements

- Python 3.10 or newer
- Internet connection
- Modrinth Collection ID

---

## 🛠️ Usage

1. Download `modrinth_collection_downloader.py`.
2. Open the file `modrinth_collection_downloader.py` as text editor
3. Modify the Minecraft version, loader, and collection ID to your desired options.
4. Open a terminal and navigate to the script's directory.
5. Run the script:
   ```bash
   python modrinth_collection_downloader.py
   ```
6. The script will download all mods from the specified Modrinth collection. Downloaded mods will be saved in a folder located alongside `modrinth_collection_downloader.py`.

### 💡 Example Configuration

- **Minecraft Version:** `1.21.7`
- **Loader:** `fabric`
- **Collection ID:** `HO2OnfaY`

You can modify these in the script or via command-line arguments (if supported).
![Screenshot 2025-06-24 115159](https://github.com/user-attachments/assets/4c7ad3f9-2737-4274-bc59-a44db5195566)

---

## 💡 Best Usage for this Python Script

For the most seamless experience, you can place `modrinth_collection_downloader.py` directly into your Minecraft directory folder, typically located at:

```
C:\Users\YOURNAME\AppData\Roaming\.minecraft\
```

**Why do this?**
- Whenever you run the script from this location, it will automatically download and update your mods right where Minecraft expects them.
- The script will also delete old versions of mods to prevent conflicts, so you don't have to manually update or clean up mods one by one!
- This keeps your mod folder always up-to-date with your chosen Modrinth collection.

**Tip:** Replace `YOURNAME` with your actual Windows username.

---

## 📖 Example

```bash
python modrinth_collection_downloader.py --version 1.21.6 --loader fabric --collection HO2OnfaY
```

---

## ❓ FAQ

<details>
<summary><strong>Where do the mods get downloaded?</strong></summary>

Mods are saved in a folder next to the script, named according to your configuration.

</details>

<details>
<summary><strong>Can I use this for Forge or Quilt?</strong></summary>

Yes! Just set the loader to `forge` or `quilt` and more!

</details>

<details>
<summary><strong>What does the code in <code>modrinth_collection_downloader.py</code> do?</strong></summary>

# 📦 Script Explanation: `modrinth_collection_downloader.py`

This script automates downloading and updating Minecraft mods from a Modrinth collection, supporting version and loader selection, logging, and safe updating.

---

## 1. 🛠️ Imports and Constants

```python
import sys
import datetime
```
- **Standard Python modules** for system operations and date/time handling.

```python
MINECRAFT_VERSION = 'EDITYOURVERSIONHERE'
LOADER = 'EDITYOURLOADERHERE'
COLLECTION_ID = 'EDITYOURCOLLECTIONIDHERE'
```
- **Constants**: Placeholders for Minecraft version, mod loader, and Modrinth collection ID.  
  _Edit these values or use command-line arguments._

```python
sys.argv = ['modrinth_collection_downloader.py', '-v', MINECRAFT_VERSION, '-l', LOADER, '-c', COLLECTION_ID]
```
- **Default Arguments**: Allows the script to run with default values if not called from the command line.

---

## 2. 📚 Additional Imports

- `argparse`: For parsing command-line arguments.
- `ThreadPoolExecutor`: For parallel downloads.
- `json`: For handling API responses.
- `os`: For file and directory operations.
- `urllib`: For HTTP requests and error handling.

---

## 3. 🏗️ ModrinthClient Class

**Purpose:** Encapsulates all API interactions with Modrinth.

**Methods:**
- `__init__`: Sets the base API URL.
- `get(url)`: Makes a GET request to the Modrinth API and returns JSON data.
- `download_file(url, filename)`: Downloads a file from a URL to a local filename.
- `get_mod_version(mod_id)`: Gets all versions for a mod.
- `get_collection(collection_id)`: Gets details for a collection.

---

## 4. 🌐 Global Client Instance

- **Purpose:** Creates a single client instance for use throughout the script.

---

## 5. ⚙️ Argument Parsing

**Purpose:** Defines and parses command-line arguments for:
- **Collection ID** (`-c`)
- **Minecraft version** (`-v`)
- **Loader** (`-l`)
- **Download directory** (`-d`)
- **Update mode** (`-u`)

---

## 6. 📝 Logging Setup

- **Purpose:** Sets up log file names and directory.

```python
LOG_DIR = "modrinth_collection_downloader_logs"
LOG_DOWNLOADED = "downloaded_mods_logs.txt"
LOG_UPDATED = "updated_mods_logs.txt"
LOG_NO_VERSION = "no_version_found_for_mods_logs.txt"
```

- **Ensures the log directory exists** and appends timestamped log messages to the appropriate log file.

---

## 7. 📂 Download Directory Setup

- **Purpose:** Ensures the mod download directory exists before downloading mods.

---

## 8. 🔍 Existing Mods Detection

- **Purpose:** Scans the download directory for existing mod files, extracting mod IDs from filenames.

---

## 9. ⬇️ Latest Version Fetching

- **Purpose:** Fetches all versions for a mod and selects the latest one matching the specified Minecraft version and loader.

---

## 10. 🚚 Downloading/Updating Mods

**Purpose:** Downloads or updates a mod:
- Checks if the latest version is already present.
- Downloads the latest version if needed.
- Removes old versions if updating.
- Logs all actions and errors.

---

## 11. 🧩 Main Function

**Purpose:** Orchestrates the download/update process:
- Fetches the collection details.
- Gets the list of mods in the collection.
- Detects existing mods.
- Uses a thread pool to download/update all mods in parallel.

---

## 12. ▶️ Script Entry Point

**Purpose:** Runs the main function, handles unexpected errors, and waits for user input before exiting.

---

## 📝 Summary

- **What it does:**  
  Downloads and updates all mods from a specified Modrinth collection for a given Minecraft version and loader, with logging and safe updating.

- **How to use:**
  1. Edit the constants at the top or use command-line arguments.
  2. Run the script.
  3. Mods are downloaded/updated in the specified directory.
  4. Logs are saved in the `modrinth_collection_downloader_logs` directory.

---

</details>

<details>
<summary><strong>Is this a virus?</strong></summary>

NO, this script is not a virus. It is open-source and you can read all the code yourself (see `modrinth_collection_downloader.py`). However, always be careful with scripts from the internet. If someone modifies the code with malicious intent, it could become unsafe. If you can read and understand the code, you can verify its safety yourself before running it.

</details>

## 📝 Supported Minecraft Versions

| 1.21.7   | 1.20.4 | 1.19.3 | 1.18.1 | 1.17   |
|----------|--------|--------|--------|--------|
| 1.21.6   | 1.20.3 | 1.19.2 | 1.18   | 1.16.5 |
| 1.21.5   | 1.20.2 | 1.19.1 | 1.17.1 | 1.16.4 |
| 1.21.4   | 1.20.1 | 1.19   | 1.16.5 | 1.16.3 |
| 1.21.3   | 1.20   | 1.18.2 | 1.16.2 | 1.16.1 |
| 1.21.2   | 1.19.4 | 1.18   | 1.16   |        |
| 1.21.1   |        |        |        |        |
| 1.21     |        |        |        |        |

(and more, as supported by Modrinth collections)

## 📝 Supported Loaders

| fabric     | forge      | quilt      |
|------------|------------|------------|
| neoforge   | liteloader | rift       |

(and more, as supported by Modrinth collections)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

---

## 📄 License
This project is licensed under the MIT License.
