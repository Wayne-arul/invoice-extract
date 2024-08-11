from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
from werkzeug.utils import secure_filename
from main import extract_text_from_pdf, extract_data_with_gpt, remove_backticks_and_json, save_json_to_file

app = Flask(__name__)

# This folder will store uploaded PDFs
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Here we are checking if a file is uploaded
        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']

        # If user does not select a file then return accordingly
        if file.filename == '':
            return 'No selected file'

        if file:
            # Saving the uploaded file to our uploads folder
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Extracting the text from the given pdf file
            text = extract_text_from_pdf(filepath)
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
            }"""
            gpt_extracted = extract_data_with_gpt(text, format)

            # Removing the backticks and 'json' from given text
            gpt_extracted_data = remove_backticks_and_json(gpt_extracted)

            # Saving our data to a json file
            save_json_to_file(gpt_extracted_data, 'extracted_data.json')

            # Redirecting our page to /invoice
            return redirect(url_for('display_invoice'))

    return render_template('index.html')


@app.route('/invoice')
def display_invoice():
    # Load the extracted data from the JSON file
    with open('extracted_data.json', 'r') as json_file:
        invoice_data = json.load(json_file)

    return render_template('invoice.html', data=invoice_data)


if __name__ == '__main__':
    app.run(debug=True)
