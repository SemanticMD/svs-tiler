# svs-tiler
Instructions and code for tiling pathology image (svs) files

## Overview
We will be using libvips (https://github.com/jcupitt/libvips) for processing the .svs image files. All instructions were tested on Ubuntu 14.04.

### Install vips dependencies
sudo apt-get install libvips-tools
sudo apt-get install libvips --no-install-recommends
#### patch to fix broken libopenjpeg2 library
sudo dpkg -i libopenjpeg2_1.3+dfsg-4.6ubuntu2_amd64.deb

### Example usage
vips dzsave output_files_dir_name svs_image_name.svs --background 0 --centre --layout dz

### TODO
Update /examples folder with more examples of usage (e.g. with TCGA data)