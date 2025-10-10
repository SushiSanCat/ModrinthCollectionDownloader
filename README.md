# 🔃 Modrinth Collection Downloader
![Modrinth Collection Downloader Design1](https://github.com/user-attachments/assets/2bd97296-b995-48a8-b71b-1f42ded61661)
Tired of downloading your mods one by one? This Python script is perfect for you!



## Example of what it looks like on usage:
![GIF](https://i.imgur.com/hFvhyWp.gif)
<img width="1919" height="1078" alt="image" src="https://github.com/user-attachments/assets/a04605d6-00f9-48bf-adc7-662d53369c38" />
[🎥Click here to see Example Usage GIF](https://i.imgur.com/hFvhyWp.gif)



A modern Python script to **automatically download and update mods and resource packs** from a [Modrinth](https://modrinth.com) collection, tailored to your chosen Minecraft version and mod loader (e.g., Fabric, Forge, Quilt).

This script streamlines the management of large modpacks by fetching mods directly via Modrinth's API and organizing them locally.

---

## 🚀 Features

- Download all mods from a Modrinth collection in one go
- Filter mods by Minecraft version and mod loader
- Automatically skip or update existing mods
- Multithreaded downloads for faster performance
- Clean, consistent file naming using mod IDs
- Optional resource pack downloading
- Download latest version when no version is specified
- Separate directories for mods and resource packs
- Proper naming for resource packs (using their display names)
- Detailed statistics showing separate counts for mods and resource packs plus aggregated totals
- Convenient batch files for common download scenarios
- Separate log files for mods and resource packs

---

## 📦 Requirements

- Python 3.10 or newer
- Internet connection
- Modrinth Collection ID

---

## 🛠️ Usage

1. Download `modrinth_collection_downloader.py`.
2. Open a terminal and navigate to the script's directory.
3. Run the script with your desired options:
   ```bash
   python modrinth_collection_downloader.py --version 1.21.10 --loader fabric --collection AZubsCAT
   ```
   3. (Optional) you can also use the .bat file to quickly run the script. modify the version, loader and collection ids to your desired values.
   
   To download resource packs in addition to mods:
   ```bash
   python modrinth_collection_downloader.py --version 1.21.10 --loader fabric --collection AZubsCAT --include-resourcepacks
   ```
   
   To download the latest compatible versions (without specifying a version):
   ```bash
   python modrinth_collection_downloader.py --loader fabric --collection AZubsCAT
   ```

4. The script will download all mods from the specified Modrinth collection. 
   - Mods are saved in the `mods` folder
   - Resource packs are saved in the `resourcepacks` folder (when `--include-resourcepacks` is used)

### 📁 Batch Files for Quick Execution

For convenience, three batch files are included to quickly run common download scenarios:

- **[run_download_latest.bat]** - Downloads latest compatible versions without specifying a version
- **[run_download_with_resourcepacks.bat]** - Downloads both mods and resource packs for a specific version
- **[run_download_latest_with_resourcepacks.bat]** - Downloads latest versions of both mods and resource packs

To use these batch files:
1. Edit the file with a text editor
2. Replace `AZubsCAT` with your actual Modrinth collection ID
3. Optionally change the version and loader as needed
4. Double-click the batch file to run it

### 📝 Log Files

The script creates separate log files for mods and resource packs to help you track what was downloaded:

- **Mod logs:** Stored in `modrinth_collection_downloader_logs/` with `downloaded_mods_logs.txt`, `no_version_found_for_mods_logs.txt`, etc.
- **Resource pack logs:** Stored in `modrinth_collection_downloader_logs/` with `downloaded_resourcepacks_logs.txt`, `no_version_found_for_resourcepacks_logs.txt`, etc.

### 💡 Example Configuration

- **Minecraft Version:** `1.21.10` (or any other valid Minecraft version, or omit to download latest)
- **Loader:** `fabric`
- **Collection ID:** `AZubsCAT`

<img width="513" height="171" alt="collection ID" src="https://github.com/user-attachments/assets/632a920a-3e83-4a02-9696-4287f8027743" />

> **Note:** In previous versions of this script, you needed to manually edit the Python file to configure the version, loader, and collection ID. This is no longer necessary as the script now properly supports command-line arguments as the primary method of configuration.

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
python modrinth_collection_downloader.py --version 1.21.10 --loader fabric --collection AZubsCAT
```

### 💡 Additional Arguments

- **API Base URL:** `--api-base-url` - Specify a custom Modrinth API base URL (default: https://api.modrinth.com)
- **Update Mode:** `-u` or `--update` - Download and update existing mods
- **Download Directory:** `-d` or `--directory` - Specify where to download mods (default: "./mods")
- **Include Resource Packs:** `--include-resourcepacks` - Also download resource packs from the collection (saved in ./resourcepacks/)
- **Version (Optional):** `-v` or `--version` - Specify Minecraft version, or omit to download latest compatible versions

---

## ❓ FAQ

<details>
<summary><strong>Where do the mods get downloaded?</strong></summary>

Mods are saved in a folder next to the script, named according to your configuration:
- Mods are saved in the `mods` directory
- Resource packs are saved in the `resourcepacks` directory (when enabled)

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
import argparse
```
- **Command-line argument parsing** for flexible configuration.

---

## 2. 📚 Additional Imports

- `ThreadPoolExecutor`: For parallel downloads.
- `json`: For handling API responses.
- `os`: For file and directory operations.
- `urllib`: For HTTP requests and error handling.

---

## 3. 🏗️ ModrinthClient Class

**Purpose:** Encapsulates all API interactions with Modrinth.

**Methods:**
- `__init__(base_url)`: Sets the base API URL (configurable).
- `get(url)`: Makes a GET request to the Modrinth API and returns JSON data.
- `download_file(url, filename)`: Downloads a file from a URL to a local filename.
- `get_mod_version(mod_id)`: Gets all versions for a mod.
- `get_collection(collection_id)`: Gets details for a collection.
- `get_minecraft_versions()`: Gets list of available Minecraft versions.

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
- **API Base URL** (`--api-base-url`)
- **Include Resource Packs** (`--include-resourcepacks`)

**Validation:** The script validates both loader and version parameters to ensure they meet expected formats.

---

## 6. 📝 Logging Setup

- **Purpose:** Sets up log file names and directory.

```python
LOG_DIR = "modrinth_collection_downloader_logs"
LOG_MODS_DOWNLOADED = "downloaded_mods_logs.txt"
LOG_MODS_UPDATED = "updated_mods_logs.txt"
LOG_MODS_NO_VERSION = "no_version_found_for_mods_logs.txt"
LOG_RPS_DOWNLOADED = "downloaded_resourcepacks_logs.txt"
```

- **Ensures the log directory exists** and appends timestamped log messages to the appropriate log file.
- **Separate logs for mods and resource packs** for better organization.

---

## 7. 📂 Download Directory Setup

- **Purpose:** Ensures the mod download directory exists before downloading mods.
- **Resource Packs:** Creates a separate `resourcepacks` directory when resource packs are included.

---

## 8. 🔍 Existing Mods/Resource Packs Detection

- **Purpose:** Scans the download directories for existing files.
- **Mods:** Extracts mod IDs from filenames for version checking.
- **Resource Packs:** Uses full filenames since resource packs don't have IDs.

---

## 9. ⬇️ Latest Version Fetching

- **Purpose:** Fetches all versions for a mod/resource pack and selects the latest one matching the specified Minecraft version and loader.
- **Enhanced Error Handling:** Improved error handling and data structure validation.
- **Latest Version Support:** When no version is specified, downloads the latest version compatible with the loader.
- **Resource Pack Handling:** More flexible version matching for resource packs since they often don't have specific loaders.
- **Minecraft Version Detection:** Automatically detects the latest Minecraft version for strict compatibility.

---

## 10. 🚚 Downloading/Updating Mods and Resource Packs

**Purpose:** Downloads or updates mods and resource packs:
- Checks if the latest version is already present.
- Downloads the latest version if needed.
- Removes old versions if updating.
- Logs all actions and errors.
- **Atomic Operations:** Uses atomic file operations to prevent corruption during updates.
- **Separate Handling:** Mods and resource packs are handled separately with different naming conventions.
- **Strict Version Compatibility:** Only downloads content that supports the latest Minecraft version when no version is specified.

---

## 11. 🧩 Main Function

**Purpose:** Orchestrates the download/update process:
- Fetches the collection details.
- Gets the list of mods and resource packs in the collection.
- Detects existing mods/resource packs.
- Uses a thread pool to download/update all items in parallel.
- **Resource Pack Support:** Optionally includes resource packs in the download with separate handling.
- **Separate Log Files:** Uses different log files for mods and resource packs.

---

## 12. 📊 Comprehensive Statistics Display

**Purpose:** Shows detailed statistics at the end of the download process:
- Total projects checked (mods + resource packs)
- Separate detailed counts for mods and resource packs:
  - Checked
  - Already exist
  - No version found
  - Newly downloaded
  - Updated
- Aggregated project statistics (totals for all categories)
- Clear, formatted output for easy understanding
- Detailed breakdown helps users understand exactly what was processed

---

## 13. ▶️ Script Entry Point

**Purpose:** Runs the main function, handles unexpected errors, and waits for user input before exiting.
- **User-Friendly Exit:** Script now pauses at the end of both successful runs and error cases, waiting for user input before closing.

---

## 📝 Summary

- **What it does:**  
  Downloads and updates all mods from a specified Modrinth collection for a given Minecraft version and loader, with logging and safe updating.
  Optionally downloads resource packs to a separate directory with proper naming.

- **How to use:**
  1. Run the script with command-line arguments for version, loader, and collection.
  2. Mods are downloaded/updated in the `mods` directory.
  3. Resource packs are downloaded in the `resourcepacks` directory (when enabled).
  4. Logs are saved in the `modrinth_collection_downloader_logs` directory with separate files for mods and resource packs.
  5. Detailed statistics are displayed at the end showing separate counts for mods and resource packs plus aggregated totals.
  6. Convenient batch files are provided for common download scenarios.

---

</details>

<details>
<summary><strong>Is this a virus?</strong></summary>

NO, this script is not a virus. It is open-source and you can read all the code yourself (see `modrinth_collection_downloader.py`). However, always be careful with scripts from the internet. If someone modifies the code with malicious intent, it could become unsafe. If you can read and understand the code, you can verify its safety yourself before running it.

</details>

## 📝 Supported Minecraft Versions

The script supports **any Minecraft version** that is available on Modrinth collections. This includes but is not limited to:

| 1.21.XX+ | 1.20.4 | 1.19.3 | 1.18.1 | 1.17   |
|----------|--------|--------|--------|--------|
| 1.21.10  | 1.20.3 | 1.19.2 | 1.18   | 1.16.5 |
| 1.21.9   | 1.20.2 | 1.19.1 | 1.17.1 | 1.16.4 |
| 1.21.8   | 1.20.1 | 1.19   | 1.16.5 | 1.16.3 |
| 1.21.7   | 1.20   | 1.18.2 | 1.16.2 | 1.16.1 |
| 1.21.6   | 1.19.4 | 1.18   | 1.16   |        |
| 1.21.5   |        |        |        |        |
| 1.21.4   |        |        |        |        |
| 1.21.3   |        |        |        |        |
| 1.21.2   |        |        |        |        |
| 1.21.1   |        |        |        |        |
| 1.21     |        |        |        |        |

> **Note:** The script will work with any Minecraft version that Modrinth supports. The table above shows commonly used versions, but you can specify any valid Minecraft version when running the script. The script validates version formats to ensure they match standard Minecraft version patterns.

## 📝 Supported Loaders

| fabric     | forge      | quilt      |
|------------|------------|------------|
| neoforge   | liteloader | rift       |

(and more, as supported by Modrinth collections)

> **Note:** The script validates loader parameters against a list of commonly supported loaders: forge, fabric, quilt, neoforge, and liteloader.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

---

## 📄 License
This project is licensed under the MIT License.