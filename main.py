import openai
import pdfplumber
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment
api_key = os.getenv('OPENAI_API_KEY')

openai.api_key = api_key

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_data_with_gpt(text,format):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts invoice details."},
            {"role": "user", "content": f"Extract the customer name, address, date, product details (name, quantity, price), and total amount from the following text: {text}.Fill in this format: {format}. Return these details in json format"}
        ]
    )
    return response['choices'][0]['message']['content']

def save_json_to_file(data, file_name):
    # Convert the GPT-extracted string into a dictionary
    json_data = json.loads(data)

    # Save the dictionary to a JSON file
    with open(file_name, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"Data saved to {file_name}")

def remove_backticks_and_json(input_string):
    # Remove backticks and the word 'json'
    result = input_string.replace('```json', '').replace('```', '').strip()
    return result

# Example usage
pdf_path = 'invoice_sample.pdf'
text = extract_text_from_pdf(pdf_path)

format = """{
    "customer_name": "",
    "customer_address": "",
    "date": "18 Jul 2024",
    "product_details": [
        {
            "name": "",
            "quantity": "",
            "price": ""
        }
    ],
    "total_amount": ""
}
"""

# Use GPT to extract and refine the data
gpt_extracted = extract_data_with_gpt(text,format)
gpt_extracted_data = remove_backticks_and_json(gpt_extracted)
#print(gpt_extracted_data)


# Save the GPT-extracted data to a JSON file
save_json_to_file(gpt_extracted_data, 'extracted_data.json')
with open('extracted_data.json', 'r') as json_file:
    data = json.load(json_file)

#print(data)
