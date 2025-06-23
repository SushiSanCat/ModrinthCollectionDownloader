# 🔃 Modrinth Collection Downloader

A modern Python script to **automatically download and update mods** from a [Modrinth](https://modrinth.com) collection based on your chosen Minecraft version and mod loader (e.g. Fabric, Forge, Quilt).

This script simplifies managing large modpacks by pulling mods directly using Modrinth's API and organizing them locally.

---

## 🚀 Features

- Download all mods from a Modrinth collection
- Filter by Minecraft version and mod loader
- Automatically skip or update existing mods
- Multithreaded downloads for speed
- Clean file naming with mod IDs
- Lightweight, no external dependencies

---

## 📦 Requirements

- Python 3.10 or newer
- Internet connection
- Collection ID from Modrinth

---

## 🛠️ How to Use

### 💡 Default Behavior

By default, the script is pre-configured to use:
- Minecraft Version: `1.21.6`
- Loader: `fabric`
- Collection ID: `HO2OnfaY`

You can just run the script locally:

```bash
python download_modrinth.py
