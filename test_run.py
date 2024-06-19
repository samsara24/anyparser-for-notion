import pytest
import os
import markdown
from run import extract_content_from_image, extract_and_add_from_images
from notion import NotionHandler
from filehandler import FileManager
PAGE_ID = os.getenv("PAGE_ID")
EXAMPLE_API_KEY = os.getenv("CAMBIO_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
expected_content = '''# Introduction to databases

                            ## Database views

                            ## Database templates'''
def test_extract_content_from_image():
    image_path = 'test/test_images/1.png'
    final = extract_content_from_image(image_path)
    print(final)
    assert final.split() == expected_content.split()

def test_extract_content_from_pdf():
    pdf_path = 'test/test_pdf/1.pdf'
    assert extract_content_from_image(pdf_path).split() == expected_content.split()

def test_markdown_to_html():
    markdown_content = '# Heading\n\nSome text'
    expected_html = '<h1>Heading</h1>\n<p>Some text</p>'
    assert markdown.markdown(markdown_content) == expected_html

def test_html_to_notion_blocks():
    notion = NotionHandler(NOTION_API_KEY, PAGE_ID)
    html_content = '<h1>Heading</h1>\n<p>Some text</p>'
    expected_blocks = [{'object': 'block', 'type': 'heading_1', 'heading_1': {'rich_text': [{'type': 'text', 'text': {'content': 'Heading'}}]}}, {'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': 'Some text'}}]}}]
    assert notion.html_to_notion_blocks(html_content) == expected_blocks

def test_clear_directories():
    directories = ['./pdf', './pdf_images', './pic']
    for directory in directories:
        FileManager.clear_folder(directory)
        assert len(os.listdir(directory)) == 0

if __name__ == "__main__":
    pytest.main()
