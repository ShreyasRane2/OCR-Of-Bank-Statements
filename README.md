OCR-Of-Bank-Statements

A Python-based application that integrates OCR and NLP technologies to extract relevant financial information from images stored in specific Cloudinary folders. 
The application preprocesses images, performs OCR using EasyOCR, and refines the extracted data with Cohere's NLP API. Results are presented in a user-friendly interface powered by Gradio.

Features

Cloudinary Integration: Fetch images from designated folders in your Cloudinary account (Salary, Profit, Bank Statements, etc.).
OCR Processing: Preprocess and analyze document images using EasyOCR for text extraction.
LLM Integration: Refine extracted text and extract specific financial data using Cohere's language model.
Financial Insights: Automatically extract key financial metrics like Basic Salary, Total Expenses, and Closing Balance.
User Interface: Interact with the application using a Gradio-based UI, which displays results in tables and includes image previews.

Getting Started
Prerequisites
Ensure the following are installed and configured:

Python 3.7 or higher
Cloudinary Python SDK (pip install cloudinary)
Cohere Python SDK (pip install cohere)
EasyOCR (pip install easyocr)
Gradio (pip install gradio)
Pillow (pip install pillow)
Numpy (pip install numpy)
Pandas (pip install pandas)
Requests (pip install requests)

Setup

Clone the repository:
git clone https://github.com/yourusername/Cloudinary-Document-OCR.git
cd Cloudinary-Document-OCR

Install dependencies:

pip install -r requirements.txt
Configure Cloudinary: Update the Cloudinary credentials in the script:

config(
    cloud_name="your-cloud-name",
    api_key="your-api-key",
    api_secret="your-api-secret"
)
Configure Cohere: Replace the Cohere API key in the script:

cohere_client = cohere.Client("your-cohere-api-key")

Usage
Running the Application
1) Launch the Gradio interface:
python main.py

2) Open the Gradio app in your web browser and configure the following:

Cloudinary Folder Name: Choose one of the following folders:
Salary: Contains pay slip images.
Profit: Contains profit and loss statements.
Bank Statements: Contains bank statement images.

Document Type: Select the type of document being processed:
Pay Slip
Profit and Loss Statement
Bank Statement

Number of Images: Enter the number of images to fetch from the selected folder.

3) View results:

Extracted financial metrics like Basic Salary, Total Expenses, and Closing Balance.
Statistical insights (Highest Value, Lowest Value, Average Value).
Processed image previews.

Example Output
Here’s an example of the results displayed by the application:

Extracted Metrics:
Pay Slip: Basic Salary, Total Earnings
Profit and Loss Statement: Total Revenue, Net Profit
Bank Statement: Closing Balance, Deposits

Statistical Insights:
Highest and lowest values for the selected financial metric.
Average value calculated across all images.

Image Previews:
Shows the processed document alongside extracted text.

License
This project is licensed under the MIT License. See the LICENSE file for details.

