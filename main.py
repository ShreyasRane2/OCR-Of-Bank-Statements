import re
import requests
from io import BytesIO
from PIL import Image, ImageFilter, ImageEnhance
import pandas as pd
import random
import time
from cloudinary import api, config
from easyocr import Reader
import numpy as np
import cohere
import gradio as gr

# Initialize Cohere client
cohere_client = cohere.Client("1H2b8YEfjn9o1TuQR7eLfI24nbxbcLEz5XFuZqU")  # Replace with your API Key

# Initialize the EasyOCR reader for English language
reader = Reader(['en'])

# Cloudinary configuration
config(
    cloud_name="dmwxgv4iv",
    api_key="618415941598468",
    api_secret=" "
)

# Preprocess image to make it more OCR-friendly
def preprocess_image(image):
    try:
        image = image.convert("L")  # Convert to grayscale
        image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
        image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)  # Resize for clarity
        image = ImageEnhance.Contrast(image).enhance(2)  # Enhance contrast
        return image
    except Exception as e:
        raise Exception(f"Error during preprocessing: {str(e)}")

# Fetch images from Cloudinary folder with pagination support
def fetch_images_from_cloudinary(folder_name, num_images):
    try:
        image_urls = []
        next_cursor = None

        while len(image_urls) < num_images:
            response = api.resources(type="upload", prefix=folder_name, max_results=100, next_cursor=next_cursor)
            image_urls.extend([resource['secure_url'] for resource in response['resources']])
            next_cursor = response.get('next_cursor', None)
            if not next_cursor or len(image_urls) >= num_images:
                break
            time.sleep(1)
        
        random.shuffle(image_urls)
        return image_urls[:num_images]
    except Exception as e:
        raise Exception(f"Error fetching images from Cloudinary: {str(e)}")

# Extract relevant information based on document type using Cohere LLM
def extract_relevant_info_with_llm(extracted_text, document_type):
    try:
        # Adjust the LLM prompt based on the document type
        if document_type == "Pay Slip":
            prompt = f"From the following pay slip text, extract only the basic salary or net salary in numeric format: {extracted_text}"
        elif document_type == "Profit Loss Statement":
            prompt = f"Extract only the total expenses in numeric format from the following profit loss statement text: {extracted_text}"
        elif document_type == "Bank Statement":
            prompt = f"From the following bank statement text, extract the ending balance or closing balance in numeric format: {extracted_text}"
        else:
            prompt = f"Extract any numeric financial value related to the document type: {extracted_text}"

        response = cohere_client.generate(
            model="command",
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        generated_text = response.generations[0].text.strip()
        print(f"[DEBUG] LLM Output: {generated_text}")

        # Use regex to ensure only numeric values are returned
        numeric_value = re.search(r"\d+(?:,\d+)*(?:\.\d+)?", generated_text)
        return numeric_value.group(0).replace(',', '') if numeric_value else "Amount not found"
    except Exception as e:
        print(f"Exception during LLM processing: {str(e)}")
        return "Error in LLM processing"

# Perform OCR and extract relevant information
def perform_ocr_from_cloudinary(folder_name, num_images, document_type):
    extracted_data = []
    extracted_values = []
    image_urls = []

    try:
        image_urls = fetch_images_from_cloudinary(folder_name, num_images)

        for url in image_urls:
            try:
                response = requests.get(url)
                image = Image.open(BytesIO(response.content))
                preprocessed_image = preprocess_image(image)
                preprocessed_image_np = np.array(preprocessed_image)
                ocr_result = reader.readtext(preprocessed_image_np)
                extracted_text = " ".join([item[1] for item in ocr_result])
                print(f"[DEBUG] OCR Text for {url}: {extracted_text}")

                # Regular expression to capture relevant financial information
                if document_type == "Pay Slip":
                    salary_match = re.search(r"(basic\s*salary|net\s*salary|gross\s*pay|salary)\s*[:\-]?\s*([₹\d,]+(?:\.\d{2})?)", extracted_text, re.IGNORECASE)
                    relevant_info = salary_match.group(2).replace(',', '') if salary_match else extract_relevant_info_with_llm(extracted_text, document_type)
                elif document_type == "Profit Loss Statement":
                    expense_match = re.search(r"(total\s*expenses|expenses)\s*[:\-]?\s*([₹\d,]+(?:\.\d{2})?)", extracted_text, re.IGNORECASE)
                    relevant_info = expense_match.group(2).replace(',', '') if expense_match else extract_relevant_info_with_llm(extracted_text, document_type)
                elif document_type == "Bank Statement":
                    balance_match = re.search(r"(ending\s*balance|closing\s*balance|available\s*balance)\s*[:\-]?\s*([₹\d,]+(?:\.\d{2})?)", extracted_text, re.IGNORECASE)
                    relevant_info = balance_match.group(2).replace(',', '') if balance_match else extract_relevant_info_with_llm(extracted_text, document_type)
                else:
                    relevant_info = extract_relevant_info_with_llm(extracted_text, document_type)

                extracted_data.append([url.split("/")[-1], document_type, relevant_info])

                try:
                    # Try to convert extracted value to float (if applicable)
                    value = float(relevant_info.replace('₹', '').strip()) if relevant_info and 'Error' not in relevant_info else 0
                    extracted_values.append(value)
                except ValueError:
                    extracted_values.append(0)
            except Exception as e:
                extracted_data.append([url, "Error", str(e)])

    except Exception as e:
        return f"Error during OCR processing: {str(e)}"

    if not extracted_data:
        return "No relevant information found in the provided images."

    df = pd.DataFrame(extracted_data, columns=["Image Name", "Document Type", "Amount"])

    # Calculate statistics (highest, lowest, average value)
    if extracted_values:
        highest_value = max(extracted_values)
        lowest_value = min(extracted_values)
        average_value = np.mean(extracted_values)
        stats_data = [
            ["Highest Value", f"₹{highest_value:,.2f}"],
            ["Lowest Value", f"₹{lowest_value:,.2f}"],
            ["Average Value", f"₹{average_value:,.2f}"]
        ]
        stats_df = pd.DataFrame(stats_data, columns=["Statistic", "Value"])
        return df.to_html(index=False) + stats_df.to_html(index=False), image_urls

    return df.to_html(index=False), image_urls

# Gradio interface function
# Gradio interface function
def gradio_interface(folder_name, num_images, document_type):
    result_table, image_urls = perform_ocr_from_cloudinary(folder_name, num_images, document_type)
    # Display images below the table in a grid layout
    image_html = "".join([f'<div style="display:inline-block; margin: 10px; width:200px; height:200px; border:2px solid #ddd; padding:5px;"><img src="{url}" style="width:100%; height:auto; border-radius:8px;"/></div>' for url in image_urls])
    return result_table + f'<div style="display:flex; flex-wrap:wrap; justify-content:center;">{image_html}</div>'

# Gradio setup with folder name dropdown
iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Dropdown(choices=["Salary", "Profit", "BankStatement"], label="Cloudinary Folder Name"),
        gr.Number(label="Number of Images to Fetch", value=5),
        gr.Dropdown(choices=["Pay Slip", "Profit Loss Statement", "Bank Statement"], label="Document Type")
    ],
    outputs=gr.HTML(label="OCR Output (Tabular)"),
    title="Cloudinary Document OCR",
    description="Fetch images from a Cloudinary folder, process them, and extract relevant information like 'Basic Salary', 'Total Expenses', or 'Ending Balance' from documents."
)

# Launch the Gradio app
if __name__ == "__main__":
    iface.launch()
