import os
import requests
import json
import sys
from dotenv import load_dotenv
from IPython.display import Image, Markdown
import markdown
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from utils import split_text, numerical_sort

class NotionHandler:
    # Initialize the NotionHandler with API key and page ID
    def __init__(self, api_key, page_id):
        self.api_key = api_key
        self.page_id = page_id
        # Define headers for Notion API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.blocks = None

    # Add blocks of content to a Notion page
    def add_blocks_to_page(self, blocks):
        url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
        max_blocks = 2000
        # Split blocks into chunks and add each chunk to the page
        for i in range(0, len(blocks), max_blocks):
            chunk = blocks[i:i + max_blocks]
            data = {"children": chunk}
            response = requests.patch(url, headers=self.headers, data=json.dumps(data))
            if response.status_code != 200:
                raise Exception(f"Failed to add blocks: {response.text}")
        return response.json()

    # Add a notice block to the page
    def add_notice_to_page(self):
        url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
        notice_block = {
            "children": [
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Anyparser is working, please wait."
                                }
                            }
                        ],
                        "icon": {
                            "type": "emoji",
                            "emoji": "⚠️"
                        },
                        "color": "yellow_background"
                    }
                }
            ]
        }
        response = requests.patch(url, headers=self.headers, json=notice_block)
        if response.status_code != 200:
            print(f"Error adding notice: {response.text}")
        else:
            print("Notice added to the page.")

    # Retrieve the content of a Notion page
    def get_page_content(self):
        url = f"https://api.notion.com/v1/blocks/{self.page_id}/children?page_size=100"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Error getting page content: {response.text}")
            sys.exit()
        return response.json()

    # Retrieve PDF URLs from the page
    def get_pdfs(self):
        data = self.get_page_content()
        pdf_urls = []
        blocks = data['results'] if len(self.blocks) == 0 else self.blocks
        # Check each block for PDF file type and collect URLs
        for block in blocks:
            if block['type'] == 'file' and block['file']['type'] == 'file':
                if block['file']["name"].endswith('.pdf'):
                    pdf_urls.append(block['file']["file"]['url'])
        return pdf_urls
    def get_completion_notice_count(self):
        url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Error fetching blocks: {response.text}")
            return 0

        data = response.json()
        callout_count = 0
        for block in data.get('results', []):
            if block.get('type') == 'callout' and \
               block['callout']['rich_text'][0]['text']['content'] == "The process has been completed successfully.":
                callout_count += 1

        return callout_count
    def get_blocks_after_last_callout(self):
        url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Error fetching blocks: {response.text}")
            return []

        data = response.json()
        blocks = data.get('results', [])
        
        last_callout_index = -1
        for i, block in enumerate(blocks):
            if block.get('type') == 'callout' and \
               block['callout']['rich_text'][0]['text']['content'] == "The process has been completed successfully.":
                last_callout_index = i
        
        if last_callout_index == -1:
            print("No callout block found.")
            return []

        return blocks[last_callout_index + 1:]
    # Check for a specific keyword in the page and update blocks accordingly
    def check_for_keyword_in_page(self):
        data = self.get_page_content()
        keyword = 'anyparser launch'
        content = "The process has been completed successfully."

        count = 0
        last_block_index = None
        # Count occurrences of the keyword and check for specific content
        for i, block in enumerate(data['results']):
            if block['type'] == 'paragraph' and block['paragraph']['rich_text']:
                if keyword in block['paragraph']['rich_text'][0]['plain_text']:
                    count += 1
        if count > self.get_completion_notice_count():
            self.blocks = self.get_blocks_after_last_callout()
            print(self.blocks)
            return True
        return False

    # Get image blocks to scan in the page
    def get_images_to_scan_in_page(self):
        data = self.get_page_content()

        results = data['results'] if len(self.blocks) == 0 else self.blocks
        image_blocks = []

        # Collect image blocks with specific captions
        for index, block in enumerate(results):
            if block['type'] == 'image':
                if block['image']['caption']:
                    for index_caption, caption in enumerate(block['image']['caption']):
                        if caption['plain_text'] and 'anyparser launch' in caption['plain_text'].split('\n'):
                            image_blocks.append(block['image']['file']['url'])
                            break
            elif block['type'] == 'paragraph' and block['paragraph']['rich_text']:
                if 'anyparser launch' in block['paragraph']['rich_text'][0]['plain_text']:
                    if index > 0 and results[index - 1]['type'] == 'image':
                        image_blocks.append(results[index - 1]['image']['file']['url'])

        return image_blocks

    # Convert HTML content to Notion blocks
    def html_to_notion_blocks(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        blocks = []
        max_length = 2000

        # Convert each HTML element to a Notion block
        for element in soup.children:
            if element.name in ['h1', 'h2', 'p', 'ul', 'strong', 'em']:
                content = element.text.strip()
                chunks = split_text(content, max_length)
                for chunk in chunks:
                    if element.name == 'h1':
                        blocks.append({
                            "object": "block",
                            "type": "heading_1",
                            "heading_1": {
                                "rich_text": [{"type": "text", "text": {"content": chunk}}]
                            }
                        })
                    elif element.name == 'h2':
                        blocks.append({
                            "object": "block",
                            "type": "heading_2",
                            "heading_2": {
                                "rich_text": [{"type": "text", "text": {"content": chunk}}]
                            }
                        })
                    elif element.name == 'p':
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": chunk}}]
                            }
                        })
                    elif element.name == 'ul':
                        for li in element.find_all('li'):
                            li_chunks = split_text(li.text.strip(), max_length)
                            for li_chunk in li_chunks:
                                blocks.append({
                                    "object": "block",
                                    "type": "bulleted_list_item",
                                    "bulleted_list_item": {
                                        "rich_text": [{"type": "text", "text": {"content": li_chunk}}]
                                    }
                                })
                    elif element.name == 'strong':
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": chunk, "annotations": {"bold": True}}}]
                            }
                        })
                    elif element.name == 'em':
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": chunk, "annotations": {"italic": True}}}]
                            }
                        })
        return blocks

    # Send a completion notice to the Notion page
    def send_completion_notice(self):
        url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
        completion_block = {
            "children": [
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "The process has been completed successfully."}
                            }
                        ],
                        "icon": {"type": "emoji", "emoji": "✅"},
                        "color": "green_background"
                    }
                }
            ]
        }
        response = requests.patch(url, headers=self.headers, json=completion_block)
        if response.status_code != 200:
            print(f"Error adding notice: {response.text}")
        else:
            print("Notice added to the page.")