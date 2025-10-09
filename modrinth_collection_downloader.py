import sys
import datetime
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from urllib import request, error

# Statistics tracking variables
stats = {
    'total_checked': 0,
    'total_updated': 0,
    'total_already_exist': 0,
    'total_no_version': 0,
    'total_downloaded': 0
}

class ModrinthClient:

    def __init__(self, base_url="https://api.modrinth.com"):
        self.base_url = base_url

    def get(self, url):
        try:
            with request.urlopen(self.base_url + url) as response:
                return json.loads(response.read())
        except error.URLError as e:
            print(f"Network error: {e}")
            return None

    def download_file(self, url, filename):
        try:
            request.urlretrieve(url, filename)
        except error.URLError as e:
            print(f"Failed to download file: {e}")
            raise  # Re-raise the exception so caller can handle it properly

    def get_mod_version(self, mod_id):
        return self.get(f"/v2/project/{mod_id}/version")

    def get_collection(self, collection_id):
        return self.get(f"/v3/collection/{collection_id}")


# Global Modrinth client instance
modrinth_client = ModrinthClient()


def validate_loader(loader):
    """Validate that the loader is supported by Modrinth."""
    # Commonly supported loaders - in practice, this could be fetched from the API
    supported_loaders = ["forge", "fabric", "quilt", "neoforge", "liteloader"]
    return loader.lower() in supported_loaders


def validate_version(version):
    """Validate that the version follows a standard Minecraft version format."""
    # Basic validation for Minecraft version format (e.g., 1.20.4, 1.21, etc.)
    import re
    return bool(re.match(r"^\d+\.\d+(\.\d+)?(-rc\d+|-pre\d+)?$", version))


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Download and update mods from a Modrinth collection.",
        epilog="Example: python modrinth_collection_downloader.py --version 1.21.6 --loader fabric --collection HO2OnfaY"
    )
    parser.add_argument(
        "-c",
        "--collection",
        required=True,
        help="ID of the collection to download. Can be obtained from the collection URL (for https://modrinth.com/collection/5OBQuutT collection_id is 5OBQuutT).",
    )
    parser.add_argument(
        "-v", "--version", required=True, help='Minecraft version (e.g., "1.20.4", "1.21"). Supports any valid Minecraft version.'
    )
    parser.add_argument(
        "-l",
        "--loader",
        required=True,
        help='Loader to use ("fabric", "forge", "quilt" etc).',
    )
    parser.add_argument(
        "-d",
        "--directory",
        default="./mods",
        help='Directory to download mods to. Default: "mods"',
    )
    parser.add_argument(
        "-u",
        "--update",
        default=False,
        action="store_true",
        help="Download and update existing mods. Default: false",
    )
    parser.add_argument(
        "--api-base-url",
        default="https://api.modrinth.com",
        help="Base URL for the Modrinth API. Default: https://api.modrinth.com",
    )
    
    args = parser.parse_args()
    
    # Validate loader
    if not validate_loader(args.loader):
        parser.error(f"Unsupported loader: {args.loader}. Supported loaders include: forge, fabric, quilt, neoforge, liteloader")
    
    # Validate version
    if not validate_version(args.version):
        parser.error(f"Invalid version format: {args.version}. Expected format: X.Y or X.Y.Z (e.g., 1.20.4, 1.21)")
    
    return args


def setup_logging():
    """Set up logging directory and files."""
    # Logging setup
    LOG_DIR = "modrinth_collection_downloader_logs"
    LOG_DOWNLOADED = "downloaded_mods_logs.txt"
    LOG_UPDATED = "updated_mods_logs.txt"
    LOG_NO_VERSION = "no_version_found_for_mods_logs.txt"
    LOG_ALREADY_EXISTS = "already_existing_mods_logs.txt"

    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    return LOG_DIR, LOG_DOWNLOADED, LOG_UPDATED, LOG_NO_VERSION, LOG_ALREADY_EXISTS


def log_event(log_dir, filename, message):
    log_path = os.path.join(log_dir, filename)
    # Count existing entries
    entry_count = 0
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                # Count lines that start with a number and a dot, e.g., '1. ['
                if line.strip().startswith(f"{entry_count + 1}. [") or (entry_count == 0 and line.strip().startswith("1. [")):
                    entry_count += 1
                elif line.strip() and line.strip()[0].isdigit() and ". [" in line:
                    entry_count += 1
    entry_count += 1  # For the new entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{entry_count}. [{timestamp}]\n{message}\n\n")


def get_existing_mods(directory) -> list[dict]:
    file_names = os.listdir(directory)
    mods = []
    for file_name in file_names:
        parts = file_name.split(".")
        if len(parts) < 2:
            print(f"Warning: Skipping file with unexpected name format: {file_name}")
            continue
        mods.append({"id": parts[-2], "filename": file_name})
    return mods


def get_latest_version(mod_id, version, loader):
    try:
        mod_versions_data = modrinth_client.get_mod_version(mod_id)
        if not mod_versions_data:
            print(f"{mod_id} versions not found!")
            return None

        # Validate data structure before processing
        if not isinstance(mod_versions_data, list):
            print(f"Unexpected data structure for {mod_id} versions")
            return None

        mod_version_to_download = next(
            (
                mod_version
                for mod_version in mod_versions_data
                if isinstance(mod_version, dict) and 
                   "game_versions" in mod_version and 
                   "loaders" in mod_version and
                   version in mod_version["game_versions"] and
                   loader in mod_version["loaders"]
            ),
            None,
        )
        return mod_version_to_download
    except Exception as e:
        print(f"Error processing versions for {mod_id}: {e}")
        return None


def download_mod(mod_id, existing_mods, version, loader, directory, log_dir, log_files):
    try:
        stats['total_checked'] += 1
        existing_mod = next((mod for mod in existing_mods if mod["id"] == mod_id), None)

        latest_mod = get_latest_version(mod_id, version, loader)
        if not latest_mod:
            # Try to get the mod name for better error reporting
            mod_details = modrinth_client.get(f"/v2/project/{mod_id}")
            mod_name = mod_details["title"] if mod_details and "title" in mod_details else "Unknown"
            log_message = (
                f"❌ NO VERSION FOUND FOR:\n"
                f"🔹 MOD_NAME: {mod_name}\n"
                f"🆔 MOD_ID: {mod_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}"
            )
            print(f"\n{log_message}\n")
            log_event(log_dir, log_files['no_version'], log_message)
            stats['total_no_version'] += 1
            return

        file_to_download: dict | None = next(
            (file for file in latest_mod["files"] if file["primary"] == True), None
        )
        if not file_to_download:
            print(f"Couldn't find a file to download for {mod_id}")
            print()
            # Log this error
            mod_details = modrinth_client.get(f"/v2/project/{mod_id}")
            mod_name = mod_details["title"] if mod_details and "title" in mod_details else mod_id
            log_message = (
                f"❌ NO DOWNLOADABLE FILE FOUND FOR:\n"
                f"🔹 MOD_NAME: {mod_name}\n"
                f"🆔 MOD_ID: {mod_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}"
            )
            log_event(log_dir, log_files['no_version'], log_message)
            stats['total_no_version'] += 1
            return
        filename: str = file_to_download["filename"]
        filename_parts = filename.split(".")
        filename_parts.insert(-1, mod_id)
        filename_with_id = ".".join(filename_parts)

        if existing_mod and existing_mod["filename"] == filename_with_id:
            print(f"{filename_with_id} LATEST VERSION ALREADY EXISTS. ⏩")
            print()
            # Log already existing mod
            mod_details = modrinth_client.get(f"/v2/project/{mod_id}")
            mod_name = mod_details["title"] if mod_details and "title" in mod_details else mod_id
            log_message = (
                f"⏩ ALREADY EXISTS (UPDATED):\n"
                f"🔹 MOD_NAME: {mod_name}\n"
                f"🆔 MOD_ID: {mod_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}\n"
                f"📄 FILE: {filename_with_id}"
            )
            log_event(log_dir, log_files['already_exists'], log_message)
            stats['total_already_exist'] += 1
            return

        print(("💹 UPDATING: " if existing_mod else "✅ DOWNLOADING: ") +
            f"{file_to_download['filename']} | loaders: {latest_mod['loaders']} | game_versions: {latest_mod['game_versions']}")
        print()
        temp_filename = f"{directory}/{filename_with_id}.tmp"
        final_filename = f"{directory}/{filename_with_id}"
        
        try:
            modrinth_client.download_file(
                file_to_download["url"], temp_filename
            )
        except Exception as e:
            print(f"Failed to download {mod_id}: {e}")
            # Clean up partially downloaded file if it exists
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            return
        
        # Atomically replace the existing file if updating
        if existing_mod:
            print(f"🚫 REMOVING PREVIOUS VERSION:  {existing_mod['filename']}")
            print()
            existing_file_path = f"{directory}/{existing_mod['filename']}"
            # Rename temp file to final name, replacing existing file atomically
            os.replace(temp_filename, final_filename)
            # Remove the old file
            os.remove(existing_file_path)
            
            mod_details = modrinth_client.get(f"/v2/project/{mod_id}")
            mod_name = mod_details["title"] if mod_details and "title" in mod_details else mod_id
            log_message = (
                f"💹 UPDATED MOD:\n"
                f"🔹 MOD_NAME: {mod_name}\n"
                f"🆔 MOD_ID: {mod_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}\n"
                f"📄 NEW_FILE: {filename_with_id}"
            )
            log_event(log_dir, log_files['updated'], log_message)
            stats['total_updated'] += 1
        else:
            # For new downloads, just rename the temp file
            os.replace(temp_filename, final_filename)
            
            # Log first time download
            mod_details = modrinth_client.get(f"/v2/project/{mod_id}")
            mod_name = mod_details["title"] if mod_details and "title" in mod_details else mod_id
            log_message = (
                f"✅ DOWNLOADED MOD:\n"
                f"🔹 MOD_NAME: {mod_name}\n"
                f"🆔 MOD_ID: {mod_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}\n"
                f"📄 FILE: {filename_with_id}"
            )
            log_event(log_dir, log_files['downloaded'], log_message)
            stats['total_downloaded'] += 1
    except Exception as e:
        print(f"Failed to download {mod_id}: {e}")


def display_final_statistics():
    """Display final statistics after all tasks are completed."""
    print("\n" + "="*60)
    print("📊 FINAL STATISTICS")
    print("="*60)
    print(f"🔍 Total mods checked: {stats['total_checked']}")
    print(f"💹 Total mods updated: {stats['total_updated']}")
    print(f"⏩ Total mods already exist: {stats['total_already_exist']}")
    print(f"❌ Total mods with no version found: {stats['total_no_version']}")
    print(f"✅ Total mods newly downloaded: {stats['total_downloaded']}")
    print("="*60)


def main(args):
    # Set up logging
    log_dir, log_downloaded, log_updated, log_no_version, log_already_exists = setup_logging()
    log_files = {
        'downloaded': log_downloaded,
        'updated': log_updated,
        'no_version': log_no_version,
        'already_exists': log_already_exists
    }

    # Initialize Modrinth client with the specified base URL
    global modrinth_client
    modrinth_client = ModrinthClient(base_url=args.api_base_url)

    # Ensure download directory exists
    if not os.path.exists(args.directory):
        os.mkdir(args.directory)

    collection_details = modrinth_client.get_collection(args.collection)
    if not collection_details:
        error_message = f"Collection id={args.collection} not found"
        print(error_message)
        # Log this error
        log_event(log_dir, log_files['no_version'], f"❌ COLLECTION NOT FOUND:\n{error_message}")
        return
    mods: str = collection_details["projects"]
    print(f"Mods in collection: {mods}")
    print(f"📦 Total mods to check: {len(mods)}")
    print()
    existing_mods = get_existing_mods(args.directory)

    with ThreadPoolExecutor(max_workers=5) as executor:
        # Pass all required arguments to download_mod function
        from functools import partial
        download_func = partial(
            download_mod,
            existing_mods=existing_mods,
            version=args.version,
            loader=args.loader,
            directory=args.directory,
            log_dir=log_dir,
            log_files=log_files
        )
        executor.map(download_func, mods)
    
    # Display final statistics
    display_final_statistics()
    
    # Pause at the end of a successful run
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        # Parse arguments normally
        args = parse_args()
        main(args)
    except SystemExit as e:
        # Check if this is a help request (exit code 0) or argument error (exit code 2)
        if e.code == 0:
            # Help was requested, let it exit normally
            sys.exit(0)
        else:
            # Arguments are missing, show custom instructions
            print("\nTo use this script, run it with the required arguments:")
            print("Example: python modrinth_collection_downloader.py --version 1.21.6 --loader fabric --collection HO2OnfaY")
            print("\nFor more information, use: python modrinth_collection_downloader.py --help")
            input("\nPress Enter to exit...")
            sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
