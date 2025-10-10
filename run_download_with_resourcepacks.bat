@echo off
REM Download both mods and resource packs from a collection
python ./modrinth_collection_downloader.py --version 1.21.10 --loader fabric --collection AZubsCAT --include-resourcepacks
pause