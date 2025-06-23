# 🔃 Modrinth Collection Downloader

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
2. Open a terminal and navigate to the script's directory.
3. Run the script:
   ```bash
   python download_modrinth.py
   ```
4. The script will download all mods from the specified Modrinth collection. Downloaded mods will be saved in a folder located alongside `download_modrinth.py`.

### 💡 Default Configuration

By default, the script is set to:
- **Minecraft Version:** `1.21.6`
- **Loader:** `fabric`
- **Collection ID:** `HO2OnfaY`

You can modify these defaults in the script or via command-line arguments (if supported).

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

```bash
python download_modrinth.py
