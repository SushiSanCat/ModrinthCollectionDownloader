# 🔃 Modrinth Collection Downloader

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

1. Download `download_modrinth.py`.
2. Open the file `download_modrinth.py` as text editor
3. Modify the Minecraft version, loader, and collection ID to your desired options.
4. Open a terminal and navigate to the script's directory.
5. Run the script:
   ```bash
   python download_modrinth.py
   ```
6. The script will download all mods from the specified Modrinth collection. Downloaded mods will be saved in a folder located alongside `download_modrinth.py`.

### 💡 Default Configuration

By default, the script is set to:
- **Minecraft Version:** `1.21.6`
- **Loader:** `fabric`
- **Collection ID:** `HO2OnfaY`

You can modify these defaults in the script or via command-line arguments (if supported).
![Screenshot 2025-06-24 115159](https://github.com/user-attachments/assets/4c7ad3f9-2737-4274-bc59-a44db5195566)

---

## 💡 Best Usage for this Python Script

For the most seamless experience, you can place `download_modrinth.py` directly into your Minecraft directory folder, typically located at:

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
python download_modrinth.py --version 1.21.6 --loader fabric --collection HO2OnfaY
```

---

## ❓ FAQ

**Q:** Where do the mods get downloaded?  
**A:** Mods are saved in a folder next to the script, named according to your configuration.

**Q:** Can I use this for Forge or Quilt?  
**A:** Yes! Just set the loader to `forge` or `quilt` and more!

**Q:** What does the code in `download_modrinth.py` do?  
**A:**
- The script is designed to download and update all mods from a Modrinth collection for a specific Minecraft version and mod loader.
- **Configuration:** At the top, you can set default values for Minecraft version, loader, and collection ID. These can also be provided as command-line arguments.
- **Argument Parsing:** The script uses `argparse` to handle command-line arguments for collection ID, Minecraft version, loader, download directory, and whether to update existing mods.
- **Modrinth API Client:** The `ModrinthClient` class handles API requests to Modrinth for collection and mod version data, and downloads mod files.
- **Directory Setup:** If the target download directory does not exist, it is created automatically.
- **Existing Mods:** The script checks which mods are already downloaded in the directory to avoid unnecessary downloads (unless updating is requested).
- **Version Filtering:** For each mod in the collection, it finds the latest version that matches the specified Minecraft version and loader.
- **Download Logic:** Mods are downloaded with filenames that include their mod ID for clarity. If a mod is updated, the old version is removed.
- **Multithreading:** Downloads are performed in parallel using a thread pool for faster performance.
- **User Prompt:** After all downloads are complete, the script waits for the user to press Enter before exiting.

**Q:** Is this a virus?  
**A:** NO, this script is not a virus. It is open-source and you can read all the code yourself (see `download_modrinth.py`). However, always be careful with scripts from the internet. If someone modifies the code with malicious intent, it could become unsafe. If you can read and understand the code, you can verify its safety yourself before running it.

## 📝 Supported Minecraft Versions

| 1.21.6   | 1.20.4 | 1.19.3 | 1.18.1 | 1.17   |
|----------|--------|--------|--------|--------|
| 1.21.5   | 1.20.3 | 1.19.2 | 1.18   | 1.16.5 |
| 1.21.4   | 1.20.2 | 1.19.1 | 1.17.1 | 1.16.4 |
| 1.21.3   | 1.20.1 | 1.19   | 1.16.5 | 1.16.3 |
| 1.21.2   | 1.20   | 1.18.2 | 1.16.2 | 1.16.1 |
| 1.21.1   | 1.19.4 | 1.18   | 1.16   |        |
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
