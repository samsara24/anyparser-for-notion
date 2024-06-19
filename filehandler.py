import os
import requests
import json
import sys
from dotenv import load_dotenv
from IPython.display import Image, Markdown
from any_parser import AnyParser
import markdown
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from PIL import Image
import shutil
import time
import re
from concurrent.futures import ThreadPoolExecutor
from utils import split_text, numerical_sort
class FileManager:

    @staticmethod
    def save_images(image_urls, save_dir):
        """
        Save images to local directory

        :param image_urls: List of image URLs
        :param save_dir: Local directory to save images
        """
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for i, url in enumerate(image_urls):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    image_path = os.path.join(save_dir, f'image_{i+1}.png')
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Image saved: {image_path}")
                else:
                    print(f"Failed to download image: {url}")
            except Exception as e:
                print(f"Error downloading image {url}: {e}")

    @staticmethod
    def download_file(urls, save_dir):
        """
        Download files from given URLs and save to local directory

        :param urls: List of file URLs
        :param save_dir: Local directory to save files
        """
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        def download_single_file(url, index):
            response = requests.get(url)
            file_path = os.path.join(save_dir, f"{index}.pdf")
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                    print(f"File downloaded and saved as {file_path}")
            else:
                print(f"Failed to download file from {url}. Status code: {response.status_code}")

        with ThreadPoolExecutor() as executor:
            for index, url in enumerate(urls):
                executor.submit(download_single_file, url, index)


    @staticmethod
    def pdf_to_images(pdf_path, output_folder):
        """
        Convert each page of a PDF file to images and save to specified folder

        :param pdf_path: Path to the PDF file
        :param output_folder: Folder to save the images
        """
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        print("Output folder: " + output_folder)
        
        # Open PDF file
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            # Get PDF page
            page = pdf_document.load_page(page_num)
            # Convert page to pixmap image
            pix = page.get_pixmap()
            # Save pixmap image as PNG file
            file_name = pdf_path.split('/')[-1].split('.')[0] + "page_" + str(page_num + 1) + ".png"
            image_path = os.path.join(output_folder, file_name)
            print("Image path: " + image_path)
            pix.save(image_path)
            print(f"Saved: {image_path}")

    @staticmethod
    def get_all_file_paths(directory):
        """
        Get all file paths from specified directory and its subdirectories

        :param directory: Directory to traverse
        :return: List of all file paths
        """
        file_paths = []

        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

        return sorted(file_paths, key=numerical_sort)

    @staticmethod
    def all_pdf_to_images(directory):
        """
        Convert all PDF files in specified directory and its subdirectories to images

        :param directory: Directory to traverse
        :return: Output folder where images are saved
        """
        file_paths = FileManager.get_all_file_paths(directory)
        for pdf_path in file_paths:
            curr_path = os.getcwd()
            output_folder = os.path.join(curr_path, "pdf_images/")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            FileManager.pdf_to_images(pdf_path, output_folder)
        return output_folder

    @staticmethod
    def clear_folder(folder_path):
        """
        Clear all contents of specified folder

        :param folder_path: Path to the folder to clear
        """
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)
        else:
            os.makedirs(folder_path)
