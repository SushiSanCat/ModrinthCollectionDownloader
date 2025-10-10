@echo off
REM Download latest compatible versions of both mods and resource packs
python ./modrinth_collection_downloader.py --loader fabric --collection AZubsCAT --include-resourcepacks
pause