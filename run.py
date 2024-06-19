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
from notion import NotionHandler
from filehandler import FileManager

load_dotenv(override=True)
PAGE_ID = os.getenv("PAGE_ID")
EXAMPLE_API_KEY = os.getenv("CAMBIO_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")



def extract_content_from_image(image_path):
    """Extract content from an image and convert it to Markdown.
    
    Args:
        image_path (str): The path to the image file.
    
    Returns:
        str: The extracted content in Markdown format.
    """
    op = AnyParser(EXAMPLE_API_KEY)
    content_result = op.extract(image_path)
    markdown_content = "".join(content + "\n" for content in content_result)
    return markdown_content

def extract_and_add_from_images(images_folder, notion):
    """Extract content from images and add it to Notion.
    
    Args:
        images_folder (str): The folder containing image files.
        notion (NotionHandler): An instance of NotionHandler to interact with Notion.
    """
    file_paths = FileManager.get_all_file_paths(images_folder)
    for image_path in file_paths:
        markdown_content = extract_content_from_image(image_path)
        html_content = markdown.markdown(markdown_content)
        notion_blocks = notion.html_to_notion_blocks(html_content)
        notion.add_blocks_to_page(notion_blocks)

def process_images(notion):
    """Process images by extracting content and adding it to Notion.
    
    Args:
        notion (NotionHandler): An instance of NotionHandler to interact with Notion.
    """
    save_dir = "./pic/"
    image_blocks = notion.get_images_to_scan_in_page()
    if not image_blocks:
        return
    FileManager.save_images(image_blocks, save_dir)
    extract_and_add_from_images(save_dir, notion)

def process_pdf(notion):
    """Process PDFs by converting them to images, extracting content, and adding it to Notion.
    
    Args:
        notion (NotionHandler): An instance of NotionHandler to interact with Notion.
    """
    pdf_urls = notion.get_pdfs()
    if not pdf_urls:
        return
    curr_path = os.getcwd()
    save_folder = "./pdf/"
    FileManager.download_file(pdf_urls, save_folder)
    output_folder = "./pdf_images/"
    FileManager.all_pdf_to_images(save_folder)
    extract_and_add_from_images(output_folder, notion)

def clear_directories(directories):
    """Clear specified directories.
    
    Args:
        directories (list): A list of directory paths to be cleared.
    """
    for directory in directories:
        FileManager.clear_folder(directory)

def main():
    """Main function to orchestrate the processing of images and PDFs."""
    notion = NotionHandler(NOTION_API_KEY, PAGE_ID)
    directories_to_clear = [r"./pdf", r"./pdf_images", r"./pic"]
    clear_directories(directories_to_clear)
    
    while not notion.check_for_keyword_in_page():
        time.sleep(3)
    
    notion.add_notice_to_page()
    process_pdf(notion)
    process_images(notion)
    notion.send_completion_notice()

if __name__ == "__main__":
    while True:
        main()
