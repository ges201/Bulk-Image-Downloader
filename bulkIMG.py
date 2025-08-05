import os
import requests
from bs4 import BeautifulSoup
import time
import random
import json
from PIL import Image
from colorama import init, Fore, Style
import io
import re

# Initialize colorama
init(autoreset=True)

# Increase the size limit for large images
Image.MAX_IMAGE_PIXELS = None


def has_transparency(img):
    if img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True
    return False


def check_image_quality(img, min_quality):
    width, height = img.size
    total_pixels = width * height
    if min_quality == 0:
        return True
    elif min_quality == 1:  # Medium quality
        return total_pixels >= 480000  # 800x600
    elif min_quality == 2:  # High quality
        return total_pixels >= 2073600  # 1920x1080
    return False


def download_image(url, folder_path, filename, desired_format, min_quality):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            try:
                img = Image.open(io.BytesIO(response.content))

                # Verify the quality
                if not check_image_quality(img, min_quality):
                    print(f"{Fore.YELLOW}Image quality too low: {filename}")
                    return False

                if desired_format == 0:
                    # Save the image in its original format
                    file_path = os.path.join(
                        folder_path, f"{filename}.{img.format.lower()}"
                    )
                    img.save(file_path)
                elif desired_format == 1:
                    # Download only if it is already in JPG format
                    if img.format.lower() != "jpeg":
                        print(f"{Fore.YELLOW}Not a JPG image: {filename}")
                        return False
                    file_path = os.path.join(folder_path, f"{filename}.jpg")
                    img.save(file_path)
                elif desired_format == 2:
                    # Check if it is a PNG with a transparent background
                    if img.format != "PNG" or not has_transparency(img):
                        print(
                            f"{Fore.YELLOW}Not a PNG with transparent background: {filename}"
                        )
                        return False
                    file_path = os.path.join(folder_path, f"{filename}.png")
                    img.save(file_path)
                elif desired_format == 3:
                    # Download any format except PNG
                    if img.format.lower() == "png":
                        print(f"{Fore.YELLOW}PNG image not allowed: {filename}")
                        return False
                    file_path = os.path.join(
                        folder_path, f"{filename}.{img.format.lower()}"
                    )
                    img.save(file_path)

                # Verify the integrity of the saved image
                try:
                    with Image.open(file_path) as check_img:
                        check_img.verify()
                    print(
                        f"{Fore.GREEN}Image saved and validated successfully: {os.path.basename(file_path)}"
                    )
                    return True
                except Exception:
                    print(
                        f"{Fore.RED}Image validation failed: {os.path.basename(file_path)}"
                    )
                    os.remove(file_path)
                    return False

            except Exception as e:
                print(f"{Fore.RED}Error processing image for {filename}: {str(e)}")
                return False
        else:
            print(
                f"{Fore.RED}Error downloading image for: {filename}. Status code: {response.status_code}"
            )
            return False
    except Exception as e:
        print(f"{Fore.RED}Error during image download for {filename}: {str(e)}")
        return False


def get_bing_images(query, num_images=50):
    url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2&first=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    image_urls = []
    for a in soup.find_all("a", class_="iusc"):
        m = a.get("m")
        if m:
            try:
                m_json = json.loads(m)
                if "murl" in m_json:
                    image_urls.append(m_json["murl"])
                    if len(image_urls) == num_images:
                        break
            except json.JSONDecodeError:
                continue

    return image_urls


def clean_keyword(keyword):
    # Removes potentially problematic characters
    return re.sub(r"[^\w\s-]", "", keyword).strip()


def main():
    try:
        desired_format = int(
            input(
                f"{Fore.CYAN}Enter the desired format (0 = any, 1 = jpg, 2 = png with transparency, 3 = any except png): {Style.RESET_ALL}"
            )
        )
        while desired_format not in [0, 1, 2, 3]:
            desired_format = int(
                input(
                    f"{Fore.RED}Invalid format. Enter 0 (any), 1 (jpg), 2 (png with transparency), or 3 (any except png): {Style.RESET_ALL}"
                )
            )

        min_quality = int(
            input(
                f"{Fore.CYAN}Enter minimum image quality (0 = any, 1 = medium, 2 = high): {Style.RESET_ALL}"
            )
        )
        while min_quality not in [0, 1, 2]:
            min_quality = int(
                input(
                    f"{Fore.RED}Invalid quality. Enter 0 (any), 1 (medium) or 2 (high): {Style.RESET_ALL}"
                )
            )

        naming_choice = int(
            input(
                f"{Fore.CYAN}Choose naming format (1 = keyword_number, 2 = sequential number): {Style.RESET_ALL}"
            )
        )
        while naming_choice not in [1, 2]:
            naming_choice = int(
                input(
                    f"{Fore.RED}Invalid choice. Enter 1 (keyword_number) or 2 (sequential number): {Style.RESET_ALL}"
                )
            )

        words = input(
            f"{Fore.CYAN}Enter a list of words separated by commas: {Style.RESET_ALL}"
        ).split(",")
        words = [clean_keyword(word.strip()) for word in words]

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        folder_name = "DownloadedImages"
        folder_path = os.path.join(desktop_path, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        total_downloaded = 0
        failed_keywords = []

        for word in words:
            if not word:  # Skip empty keywords
                continue
            print(
                f"\n{Fore.BLUE}Searching images for: {Fore.CYAN}{word}{Style.RESET_ALL}"
            )
            image_urls = get_bing_images(word)

            success = False
            for i, image_url in enumerate(image_urls):
                if naming_choice == 1:
                    filename = f"{word}_{i + 1}"
                else:
                    filename = f"{total_downloaded + 1}"
                if download_image(
                    image_url, folder_path, filename, desired_format, min_quality
                ):
                    success = True
                    total_downloaded += 1
                    break
                else:
                    print(
                        f"{Fore.YELLOW}Failed attempt for {filename}. Trying next image.{Style.RESET_ALL}"
                    )
                time.sleep(random.uniform(1, 2))

            if not success:
                failed_keywords.append(word)
                format_name = (
                    "any"
                    if desired_format == 0
                    else (
                        "jpg"
                        if desired_format == 1
                        else (
                            "png with transparency"
                            if desired_format == 2
                            else "any except png"
                        )
                    )
                )
                quality_name = (
                    "any"
                    if min_quality == 0
                    else ("medium" if min_quality == 1 else "high")
                )
                print(
                    f"{Fore.RED}Unable to download any valid image in {format_name} format with {quality_name} quality for: {word}{Style.RESET_ALL}"
                )

            time.sleep(random.uniform(2, 4))

        print(f"\n{Fore.GREEN}{Style.BRIGHT}Final Report:{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}Images successfully downloaded: {Fore.GREEN}{total_downloaded}{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}Keywords without valid images: {Fore.RED}{len(failed_keywords)}{Style.RESET_ALL}"
        )
        if failed_keywords:
            print(
                f"{Fore.RED}Failed keywords: {', '.join(failed_keywords)}{Style.RESET_ALL}"
            )
        print(
            f"{Fore.CYAN}Total keywords processed: {Fore.BLUE}{len(words)}{Style.RESET_ALL}"
        )

    except Exception as e:
        print(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")

    input(f"{Fore.YELLOW}Press Enter to close the program...{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
