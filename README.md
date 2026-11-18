# Photo Cull

Review thumbnails from a local photo shoot and export the names you mark for retouching.

Install Pillow (python3 -m pip install Pillow) and run python3 companion/serve.py /path/to/photos. Set bridge to http://127.0.0.1:8770/reading in the emulator. Turn to browse, click to toggle selection and Start to export busybar-selection.txt in the folder. Selections persist in a separate hidden JSON file. Supported images include JPEG, PNG, TIFF, BMP and WebP. For hardware, use --bind with your computer's LAN address on a trusted local network and use that address in the URL.

## Run locally

From this folder, run `~/.busy-emulator/bin/busy-emulator dev --once` with BUSY Bar Emulator open. Back exits.

![BUSY Bar front display](screenshots/front-1.png)
