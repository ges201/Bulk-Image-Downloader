# Bulk-Image-Downloader
This Python script allows users to download images from Bing image search based on a list of keywords. It offers options for image format, quality, and naming conventions.

## Features
- Search and download images from Bing
- Specify desired image format (any, jpg, or png with transparency)
- Set minimum image quality
- Choose between keyword-based or sequential naming for downloaded images
- Colorized console output for better readability
- Validation of downloaded images
- Detailed final report

## Requirements
- Python 3.x
- Required libraries:
  - requests
  - beautifulsoup4
  - Pillow
  - colorama

## Installation
1. Download the script.
   pip install requests beautifulsoup4 Pillow colorama
   
2. Install the required libraries:
   pip install requests beautifulsoup4 Pillow colorama

## Usage
1. Run the script.
2. Follow the prompts to:
   - Choose the desired image format
   - Set the minimum image quality
   - Select the naming format for downloaded images
   - Enter a comma-separated list of keywords
The script will create a folder named 'DownloadedImages' on your Desktop and save the images there.

## Notes
- The script respects Bing's robots.txt and includes delays between requests to avoid overloading the server.
- Image download attempts are limited to prevent excessive requests for difficult-to-find images.
- The script provides a summary report at the end, including successful downloads and failed keywords.
