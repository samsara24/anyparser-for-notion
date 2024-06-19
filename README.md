
# AnyParser for Notion

## Background
AnyParser is a Python SDK developed using CambioML's proprietary large language models (LLMs). It extracts text and structured data, like tables and forms, from documents without needing any configuration or templates. AnyParser enhances traditional OCR by also identifying relationships and structures within the documents.

We need to create a connector that allows Notion users to directly use the `anyparse.extract()` function within a Notion page to convert a PDF or an image to markdown text.

## Features
- **Direct Integration**: Seamlessly integrates with Notion, allowing users to utilize the powerful extraction capabilities of AnyParser directly within their Notion pages.
- **Easy Conversion**: Extracts text and structured data from PDFs or images and converts it to markdown format.
- **User-Friendly**: Designed to be easy to use for Notion users, with minimal setup and configuration required.

## Installation
1. Clone the repository:
   \`\`\`bash
   git clone git clone https://github.com/samsara24/anyparser-for-notion.git
   \`\`\`
2. Install the required dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

## Usage
1. **NOTION API Key and Page ID**: Ensure you have your Notion API key and the page ID where you want to use the connector.
2. **AnyParser API Key**:Ensure you have your AnyParser API key from CambioML.
3. **Add env**: Add a notice to the Notion page indicating the start of the process.
   \`\`\`bash
   CAMBIO_API_KEY="17b……XXXX"
   PAGE_ID = ''
   NOTION_API_KEY = 'secret_……XXXX'
   \`\`\`
4. **Add file**: Add a pdf file or a pic in the notion page and write "anyparser launch" to parse

5. **Run**: Just run the project.
   \`\`\`bash
   python run.py
   \`\`\`
6. **More Information**: To learn more about how to use this tool, see the demo_3min.mp4

## Testing
- Due to time constraints, I could only design a few unit tests in test_run.py.
- For additional usability testing, please download this project and try to identify more issues.
- Please report any issues you find to help improve this tool.Welcome and embrace.

## Contributing
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Push to your branch.
5. Submit a pull request.

## Acknowledgements
- Thanks to CambioML for developing the AnyParser SDK.

## Contact
For any inquiries or issues, please contact [sobremesachen@163.com](mailto:sobremesachen@163.com).
