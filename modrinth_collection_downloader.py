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
    'total_mods_checked': 0,
    'total_resourcepacks_checked': 0,
    'total_updated': 0,
    'total_mods_updated': 0,
    'total_resourcepacks_updated': 0,
    'total_already_exist': 0,
    'total_mods_already_exist': 0,
    'total_resourcepacks_already_exist': 0,
    'total_no_version': 0,
    'total_mods_no_version': 0,
    'total_resourcepacks_no_version': 0,
    'total_downloaded': 0,
    'total_mods_downloaded': 0,
    'total_resourcepacks_downloaded': 0
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

    def get_minecraft_versions(self):
        """Get list of available Minecraft versions from Modrinth API."""
        try:
            with request.urlopen(self.base_url + "/v2/tag/game_version") as response:
                versions = json.loads(response.read())
                # Filter for release versions only (not snapshots or betas)
                release_versions = [v for v in versions if v.get("version_type") == "release"]
                # Sort by semantic versioning (newest first)
                release_versions.sort(key=lambda x: [int(i) if i.isdigit() else 0 for i in x["version"].split(".")], reverse=True)
                return [v["version"] for v in release_versions]
        except Exception as e:
            print(f"Error getting Minecraft versions: {e}")
            return None

# Global Modrinth client instance
modrinth_client = ModrinthClient()

# Global variable to cache the latest Minecraft version
_latest_minecraft_version = None

def get_latest_minecraft_version():
    """Get the latest Minecraft version from Modrinth API."""
    global _latest_minecraft_version
    if _latest_minecraft_version:
        return _latest_minecraft_version
    
    versions = modrinth_client.get_minecraft_versions()
    if versions:
        _latest_minecraft_version = versions[0]  # First one is the newest
        return _latest_minecraft_version
    return None


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
        description="Download and update mods and optionally resource packs from a Modrinth collection.",
        epilog="Example: python modrinth_collection_downloader.py --version 1.21.6 --loader fabric --collection HO2OnfaY"
    )
    parser.add_argument(
        "-c",
        "--collection",
        required=True,
        help="ID of the collection to download. Can be obtained from the collection URL (for https://modrinth.com/collection/5OBQuutT collection_id is 5OBQuutT).",
    )
    parser.add_argument(
        "-v", "--version", required=False, help='Minecraft version (e.g., "1.20.4", "1.21"). Supports any valid Minecraft version. If not provided, will download latest compatible version.'
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
    parser.add_argument(
        "--include-resourcepacks",
        default=False,
        action="store_true",
        help="Include resource packs in the download. Default: false",
    )
    
    args = parser.parse_args()
    
    # Validate loader
    if not validate_loader(args.loader):
        parser.error(f"Unsupported loader: {args.loader}. Supported loaders include: forge, fabric, quilt, neoforge, liteloader")
    
    # Validate version if provided
    if args.version and not validate_version(args.version):
        parser.error(f"Invalid version format: {args.version}. Expected format: X.Y or X.Y.Z (e.g., 1.20.4, 1.21)")
    
    return args


def setup_logging():
    """Set up logging directory and files."""
    # Logging setup
    LOG_DIR = "modrinth_collection_downloader_logs"
    # Mod log files
    LOG_MODS_DOWNLOADED = "downloaded_mods_logs.txt"
    LOG_MODS_UPDATED = "updated_mods_logs.txt"
    LOG_MODS_NO_VERSION = "no_version_found_for_mods_logs.txt"
    LOG_MODS_ALREADY_EXISTS = "already_existing_mods_logs.txt"
    
    # Resource pack log files
    LOG_RPS_DOWNLOADED = "downloaded_resourcepacks_logs.txt"
    LOG_RPS_UPDATED = "updated_resourcepacks_logs.txt"
    LOG_RPS_NO_VERSION = "no_version_found_for_resourcepacks_logs.txt"
    LOG_RPS_ALREADY_EXISTS = "already_existing_resourcepacks_logs.txt"

    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    return LOG_DIR, LOG_MODS_DOWNLOADED, LOG_MODS_UPDATED, LOG_MODS_NO_VERSION, LOG_MODS_ALREADY_EXISTS, LOG_RPS_DOWNLOADED, LOG_RPS_UPDATED, LOG_RPS_NO_VERSION, LOG_RPS_ALREADY_EXISTS


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
    """Get existing mods from the mods directory."""
    if not os.path.exists(directory):
        return []
    file_names = os.listdir(directory)
    mods = []
    for file_name in file_names:
        parts = file_name.split(".")
        if len(parts) < 2:
            print(f"Warning: Skipping file with unexpected name format: {file_name}")
            continue
        mods.append({"id": parts[-2], "filename": file_name})
    return mods


def get_existing_resourcepacks(directory) -> list[dict]:
    """Get existing resource packs from the resourcepacks directory."""
    if not os.path.exists(directory):
        return []
    file_names = os.listdir(directory)
    resourcepacks = []
    for file_name in file_names:
        # For resource packs, we don't have IDs in the filename, so we use the full filename
        resourcepacks.append({"filename": file_name})
    return resourcepacks


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

        # If no version specified, get the latest version that supports the loader AND the latest Minecraft version
        if not version:
            # Get the latest Minecraft version
            latest_mc_version = get_latest_minecraft_version()
            if not latest_mc_version:
                print(f"Could not determine latest Minecraft version for {mod_id}")
                return None
            
            # Find versions that support both the loader and the latest Minecraft version
            compatible_versions = [
                mod_version
                for mod_version in mod_versions_data
                if isinstance(mod_version, dict) and 
                   "game_versions" in mod_version and 
                   "loaders" in mod_version and
                   latest_mc_version in mod_version["game_versions"] and
                   loader.lower() in [l.lower() for l in mod_version["loaders"]]
            ]
            
            # If no exact match, try to find versions that support the latest Minecraft version (ignoring loader for some cases)
            if not compatible_versions:
                compatible_versions = [
                    mod_version
                    for mod_version in mod_versions_data
                    if isinstance(mod_version, dict) and 
                       "game_versions" in mod_version and 
                       latest_mc_version in mod_version["game_versions"]
                ]
            
            # If still no match, try to find the latest version that supports the loader
            if not compatible_versions:
                compatible_versions = [
                    mod_version
                    for mod_version in mod_versions_data
                    if isinstance(mod_version, dict) and 
                       "loaders" in mod_version and
                       loader.lower() in [l.lower() for l in mod_version["loaders"]]
                ]
            
            # Return the first (most recent) compatible version, or None if none found
            return compatible_versions[0] if compatible_versions else None
        else:
            # Filter by specific version and loader
            mod_version_to_download = next(
                (
                    mod_version
                    for mod_version in mod_versions_data
                    if isinstance(mod_version, dict) and 
                       "game_versions" in mod_version and 
                       "loaders" in mod_version and
                       version in mod_version["game_versions"] and
                       loader.lower() in [l.lower() for l in mod_version["loaders"]]
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
        stats['total_mods_checked'] += 1

        existing_mod = next((mod for mod in existing_mods if mod["id"] == mod_id), None)

        latest_mod = get_latest_version(mod_id, version, loader)
        if not latest_mod:
            # Try to get the mod name for better error reporting
            mod_details = modrinth_client.get(f"/v2/project/{mod_id}")
            mod_name = mod_details["title"] if mod_details and "title" in mod_details else "Unknown"
            log_message = (
                f"❌ NO VERSION FOUND FOR MOD:\n"
                f"🔹 MOD_NAME: {mod_name}\n"
                f"🆔 MOD_ID: {mod_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}"
            )
            print(f"\n{log_message}\n")
            log_event(log_dir, log_files['no_version'], log_message)
            stats['total_no_version'] += 1
            stats['total_mods_no_version'] += 1
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
                f"❌ NO DOWNLOADABLE FILE FOUND FOR MOD:\n"
                f"🔹 MOD_NAME: {mod_name}\n"
                f"🆔 MOD_ID: {mod_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}"
            )
            log_event(log_dir, log_files['no_version'], log_message)
            stats['total_no_version'] += 1
            stats['total_mods_no_version'] += 1
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
                f"⏩ MOD ALREADY EXISTS (UPDATED):\n"
                f"🔹 MOD_NAME: {mod_name}\n"
                f"🆔 MOD_ID: {mod_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}\n"
                f"📄 FILE: {filename_with_id}"
            )
            log_event(log_dir, log_files['already_exists'], log_message)
            stats['total_already_exist'] += 1
            stats['total_mods_already_exist'] += 1
            return

        print(("💹 UPDATING MOD: " if existing_mod else "✅ DOWNLOADING MOD: ") +
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
            stats['total_mods_updated'] += 1
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
            stats['total_mods_downloaded'] += 1
    except Exception as e:
        print(f"Failed to download {mod_id}: {e}")


def download_resourcepack(rp_id, existing_resourcepacks, version, loader, directory, log_dir, log_files):
    """Download a resource pack to the resourcepacks directory."""
    try:
        stats['total_checked'] += 1
        stats['total_resourcepacks_checked'] += 1
        
        # Get resource pack details
        rp_details = modrinth_client.get(f"/v2/project/{rp_id}")
        if not rp_details:
            print(f"Failed to get details for resource pack {rp_id}")
            stats['total_no_version'] += 1
            stats['total_resourcepacks_no_version'] += 1
            return
            
        rp_name = rp_details.get("title", rp_id)
        rp_type = rp_details.get("project_type", "unknown")
        
        # Verify it's a resource pack
        if rp_type != "resourcepack":
            print(f"Project {rp_id} is not a resource pack, skipping...")
            stats['total_no_version'] += 1
            stats['total_resourcepacks_no_version'] += 1
            return
            
        # Get versions
        rp_versions_data = modrinth_client.get_mod_version(rp_id)
        if not rp_versions_data:
            log_message = (
                f"❌ NO VERSION FOUND FOR RESOURCE PACK:\n"
                f"🔹 RP_NAME: {rp_name}\n"
                f"🆔 RP_ID: {rp_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}"
            )
            print(f"\n{log_message}\n")
            log_event(log_dir, log_files['no_version'], log_message)
            stats['total_no_version'] += 1
            stats['total_resourcepacks_no_version'] += 1
            return

        # Validate data structure before processing
        if not isinstance(rp_versions_data, list):
            print(f"Unexpected data structure for {rp_id} versions")
            stats['total_no_version'] += 1
            stats['total_resourcepacks_no_version'] += 1
            return

        # Find the appropriate version
        rp_version_to_download = None
        
        # For resource packs, when no version is specified, check for the latest Minecraft version support
        if not version:
            # Get the latest Minecraft version
            latest_mc_version = get_latest_minecraft_version()
            if not latest_mc_version:
                print(f"Could not determine latest Minecraft version for resource pack {rp_id}")
                stats['total_no_version'] += 1
                stats['total_resourcepacks_no_version'] += 1
                return
            
            # Find versions that support the latest Minecraft version
            compatible_versions = [
                rp_version
                for rp_version in rp_versions_data
                if isinstance(rp_version, dict) and 
                   "game_versions" in rp_version and 
                   latest_mc_version in rp_version["game_versions"]
            ]
            
            # Return the first (most recent) compatible version, or None if none found
            rp_version_to_download = compatible_versions[0] if compatible_versions else None
        else:
            # Filter by specific version or get the latest if no exact match
            rp_version_to_download = next(
                (
                    rp_version
                    for rp_version in rp_versions_data
                    if isinstance(rp_version, dict) and 
                       "game_versions" in rp_version and 
                       version in rp_version["game_versions"]
                ),
                rp_versions_data[0] if rp_versions_data else None  # Fall back to latest
            )
            
        if not rp_version_to_download:
            log_message = (
                f"❌ NO COMPATIBLE VERSION FOUND FOR RESOURCE PACK:\n"
                f"🔹 RP_NAME: {rp_name}\n"
                f"🆔 RP_ID: {rp_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}"
            )
            print(f"\n{log_message}\n")
            log_event(log_dir, log_files['no_version'], log_message)
            stats['total_no_version'] += 1
            stats['total_resourcepacks_no_version'] += 1
            return

        file_to_download: dict | None = next(
            (file for file in rp_version_to_download["files"] if file["primary"] == True), None
        )
        # If no primary file, just take the first file
        if not file_to_download and rp_version_to_download["files"]:
            file_to_download = rp_version_to_download["files"][0]
            
        if not file_to_download:
            print(f"Couldn't find a file to download for resource pack {rp_id}")
            log_message = (
                f"❌ NO DOWNLOADABLE FILE FOUND FOR RESOURCE PACK:\n"
                f"🔹 RP_NAME: {rp_name}\n"
                f"🆔 RP_ID: {rp_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"🛠️ LOADER: {loader.upper()}"
            )
            log_event(log_dir, log_files['no_version'], log_message)
            stats['total_no_version'] += 1
            stats['total_resourcepacks_no_version'] += 1
            return
            
        filename: str = file_to_download["filename"]
        
        # Check if this resource pack already exists
        existing_rp = next((rp for rp in existing_resourcepacks if rp["filename"] == filename), None)
        
        if existing_rp:
            print(f"{filename} LATEST VERSION ALREADY EXISTS. ⏩")
            print()
            log_message = (
                f"⏩ RESOURCE PACK ALREADY EXISTS:\n"
                f"🔹 RP_NAME: {rp_name}\n"
                f"🆔 RP_ID: {rp_id}\n"
                f"🎮 MC_VERSION: {version}\n"
                f"📄 FILE: {filename}"
            )
            log_event(log_dir, log_files['already_exists'], log_message)
            stats['total_already_exist'] += 1
            stats['total_resourcepacks_already_exist'] += 1
            return

        print(f"✅ DOWNLOADING RESOURCE PACK: {filename}")
        print()
        temp_filename = f"{directory}/{filename}.tmp"
        final_filename = f"{directory}/{filename}"
        
        try:
            modrinth_client.download_file(
                file_to_download["url"], temp_filename
            )
        except Exception as e:
            print(f"Failed to download resource pack {rp_id}: {e}")
            # Clean up partially downloaded file if it exists
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            return
        
        # For new downloads, just rename the temp file
        os.replace(temp_filename, final_filename)
        
        # Log first time download
        log_message = (
            f"✅ DOWNLOADED RESOURCE PACK:\n"
            f"🔹 RP_NAME: {rp_name}\n"
            f"🆔 RP_ID: {rp_id}\n"
            f"🎮 MC_VERSION: {version}\n"
            f"📄 FILE: {filename}"
        )
        log_event(log_dir, log_files['downloaded'], log_message)
        stats['total_downloaded'] += 1
        stats['total_resourcepacks_downloaded'] += 1
    except Exception as e:
        print(f"Failed to download resource pack {rp_id}: {e}")


def display_final_statistics():
    """Display final statistics after all tasks are completed."""
    print("\n" + "="*60)
    print("📊 FINAL STATISTICS")
    print("="*60)
    print(f"🔍 Total projects checked: {stats['total_checked']}")
    print(f"📈 Total mods checked: {stats['total_mods_checked']}")
    print(f"   ⏩ Mods already exist: {stats['total_mods_already_exist']}")
    print(f"   ❌ Mods with no version found: {stats['total_mods_no_version']}")
    print(f"   ✅ Mods newly downloaded: {stats['total_mods_downloaded']}")
    print(f"   💹 Mods updated: {stats['total_mods_updated']}")
    print(f"📊 Total resource packs checked: {stats['total_resourcepacks_checked']}")
    print(f"   ⏩ Resource packs already exist: {stats['total_resourcepacks_already_exist']}")
    print(f"   ❌ Resource packs with no version found: {stats['total_resourcepacks_no_version']}")
    print(f"   ✅ Resource packs newly downloaded: {stats['total_resourcepacks_downloaded']}")
    print(f"   💹 Resource packs updated: {stats['total_resourcepacks_updated']}")
    print()
    print("📈 AGGREGATED PROJECT STATISTICS:")
    print(f"   ⏩ Total projects already exist: {stats['total_already_exist']}")
    print(f"   ❌ Total projects with no version found: {stats['total_no_version']}")
    print(f"   ✅ Total projects newly downloaded: {stats['total_downloaded']}")
    print(f"   💹 Total projects updated: {stats['total_updated']}")
    print("="*60)


def main(args):
    # Set up logging
    log_dir, log_mods_downloaded, log_mods_updated, log_mods_no_version, log_mods_already_exists, log_rps_downloaded, log_rps_updated, log_rps_no_version, log_rps_already_exists = setup_logging()
    
    # Create log files dictionaries for mods and resource packs
    mod_log_files = {
        'downloaded': log_mods_downloaded,
        'updated': log_mods_updated,
        'no_version': log_mods_no_version,
        'already_exists': log_mods_already_exists
    }
    
    rp_log_files = {
        'downloaded': log_rps_downloaded,
        'updated': log_rps_updated,
        'no_version': log_rps_no_version,
        'already_exists': log_rps_already_exists
    }

    # Initialize Modrinth client with the specified base URL
    global modrinth_client
    modrinth_client = ModrinthClient(base_url=args.api_base_url)

    # Ensure mods download directory exists
    if not os.path.exists(args.directory):
        os.mkdir(args.directory)

    # Ensure resourcepacks download directory exists if needed
    resourcepacks_directory = "./resourcepacks"
    if args.include_resourcepacks:
        if not os.path.exists(resourcepacks_directory):
            os.mkdir(resourcepacks_directory)

    collection_details = modrinth_client.get_collection(args.collection)
    if not collection_details:
        error_message = f"Collection id={args.collection} not found"
        print(error_message)
        # Log this error to mod logs
        log_event(log_dir, log_mods_no_version, f"❌ COLLECTION NOT FOUND:\n{error_message}")
        return
    
    # Get all projects from the collection
    all_projects = collection_details["projects"]
    
    # Separate mods and resource packs
    mods_to_download = []
    resourcepacks_to_download = []
    
    if args.include_resourcepacks:
        # Separate projects by type
        for project_id in all_projects:
            project_details = modrinth_client.get(f"/v2/project/{project_id}")
            if project_details and project_details.get("project_type") == "resourcepack":
                resourcepacks_to_download.append(project_id)
            else:
                # Treat as mod (including unknown types)
                mods_to_download.append(project_id)
        project_type_text = f"mods ({len(mods_to_download)}) and resource packs ({len(resourcepacks_to_download)})"
    else:
        # Only mods
        mods_to_download = all_projects
        project_type_text = f"mods ({len(mods_to_download)})"
    
    print(f"Projects in collection: {project_type_text}")
    print(f"📦 Total projects to check: {len(mods_to_download) + len(resourcepacks_to_download)}")
    print()
    
    # Get existing mods
    existing_mods = get_existing_mods(args.directory)
    
    # Download mods
    if mods_to_download:
        print(f"📥 Downloading {len(mods_to_download)} mods...")
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
                log_files=mod_log_files
            )
            executor.map(download_func, mods_to_download)
    
    # Download resource packs if requested
    if args.include_resourcepacks and resourcepacks_to_download:
        print(f"\n📥 Downloading {len(resourcepacks_to_download)} resource packs...")
        existing_resourcepacks = get_existing_resourcepacks(resourcepacks_directory)
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Pass all required arguments to download_resourcepack function
            from functools import partial
            download_rp_func = partial(
                download_resourcepack,
                existing_resourcepacks=existing_resourcepacks,
                version=args.version,
                loader=args.loader,
                directory=resourcepacks_directory,
                log_dir=log_dir,
                log_files=rp_log_files
            )
            executor.map(download_rp_func, resourcepacks_to_download)
    
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
