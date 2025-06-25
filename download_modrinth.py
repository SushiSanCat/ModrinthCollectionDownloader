import sys

MINECRAFT_VERSION = 'EDITYOURVERSIONHERE'  # Your desired Minecraft version (e.g., "1.21.4", "1.21.5", "1.21.6")
LOADER = 'EDITYOURLOADERHERE'  # Your desired mod loader (e.g., "fabric", "forge", "quilt", "neoforge")
COLLECTION_ID = 'EDITYOURCOLLECTIONIDHERE'  # Your collection ID from the URL (e.g., for https://modrinth.com/collection/HO2OnfaY, the ID is HO2OnfaY)

sys.argv = ['download_modrinth.py', '-v', MINECRAFT_VERSION, '-l', LOADER, '-c', COLLECTION_ID]

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from urllib import request, error

# LOG_FILE = 'modrinth_download_log.txt'

class ModrinthClient:

    def __init__(self):
        self.base_url = "https://api.modrinth.com"

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

    def get_mod_version(self, mod_id):
        return self.get(f"/v2/project/{mod_id}/version")

    def get_collection(self, collection_id):
        return self.get(f"/v3/collection/{collection_id}")


modrinth_client = ModrinthClient()


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Download and update mods from a Modrinth collection."
    )
    parser.add_argument(
        "-c",
        "--collection",
        required=True,
        help="ID of the collection to download. Can be obtained from the collection URL (for https://modrinth.com/collection/5OBQuutT collection_id is 5OBQuutT).",
    )
    parser.add_argument(
        "-v", "--version", required=True, help='Minecraft version ("1.20.4", "1.21").'
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
    return parser.parse_args()


args = parse_args()

if args.directory:
    if not os.path.exists(args.directory):
        os.mkdir(args.directory)


def get_existing_mods() -> list[dict]:
    file_names = os.listdir(args.directory)
    mods = []
    for file_name in file_names:
        parts = file_name.split(".")
        if len(parts) < 2:
            print(f"Warning: Skipping file with unexpected name format: {file_name}")
            continue
        mods.append({"id": parts[-2], "filename": file_name})
    return mods


def get_latest_version(mod_id):
    mod_versions_data = modrinth_client.get_mod_version(mod_id)
    if not mod_versions_data:
        print(f"{mod_id} versions not found!")
        return None

    mod_version_to_download = next(
        (
            mod_version
            for mod_version in mod_versions_data
            if args.version in mod_version["game_versions"]
            and args.loader in mod_version["loaders"]
        ),
        None,
    )
    return mod_version_to_download


def download_mod(mod_id, existing_mods=[]):
    try:
        existing_mod = next((mod for mod in existing_mods if mod["id"] == mod_id), None)

        latest_mod = get_latest_version(mod_id)
        if not latest_mod:
            print(f"No version found for {mod_id} with MC_VERSION={args.version} and LOADER={args.loader}")
            return

        file_to_download: dict | None = next(
            (file for file in latest_mod["files"] if file["primary"] == True), None
        )
        if not file_to_download:
            print(f"Couldn't find a file to download for {mod_id}")
            return
        filename: str = file_to_download["filename"]
        filename_parts = filename.split(".")
        filename_parts.insert(-1, mod_id)
        filename_with_id = ".".join(filename_parts)

        if existing_mod and existing_mod["filename"] == filename_with_id:
            print(f"{filename_with_id} latest version already exists.")
            return

        print(("UPDATING: " if existing_mod else "DOWNLOADING: ") +
            f"{file_to_download['filename']} | loaders: {latest_mod['loaders']} | game_versions: {latest_mod['game_versions']}")
        modrinth_client.download_file(
            file_to_download["url"], f"{args.directory}/{filename_with_id}"
        )

        if existing_mod:
            print(f"REMOVING previous version:  {existing_mod['filename']}")
            os.remove(f"{args.directory}/{existing_mod['filename']}")
    except Exception as e:
        print(f"Failed to download {mod_id}: {e}")


def main():
    collection_details = modrinth_client.get_collection(args.collection)
    if not collection_details:
        print(f"Collection id={args.collection} not found")
        return
    mods: str = collection_details["projects"]
    print(f"Mods in collection: {mods}")
    existing_mods = get_existing_mods()

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_mod, mods, [existing_mods] * len(mods))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        input("\nAll tasks finished. Press Enter to exit...")
