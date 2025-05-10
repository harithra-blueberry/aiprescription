import pandas as pd
from fuzzywuzzy import process
from twilio.rest import Client
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas 
from io import BytesIO

# Load the dataset
try:
    dataset = pd.read_csv("D:\\AI Prescription\\medicine_dataset.csv")
except FileNotFoundError:
    print("Error: Dataset not found. Please check the file path.")
    exit()

# Function to get medicine details using fuzzy matching
def get_medicine_details(medicine_name, dataset, threshold=70):
    # Convert the input medicine name to lowercase
    medicine_name_lower = medicine_name.lower()
    
    # Add a lowercase version of the medicine names from the dataset for easier matching
    dataset['Name_lower'] = dataset['Name'].str.lower()
    
    # Fuzzy matching to find the best match for the input medicine name
    best_match, score = process.extractOne(medicine_name_lower, dataset['Name_lower'].tolist())
    
    if score >= threshold:  # If the match score is above the threshold
        # Fetch the details of the matched medicine
        details = dataset[dataset['Name_lower'] == best_match]
        
        output = ""
        for index, row in details.iterrows():
            output += f"Medicine Name: {row['Name']}\n"
            output += f"Category: {row['Category']}\n"
            output += f"Dosage Form: {row['Dosage Form']}\n"
            output += f"Strength: {row['Strength']}\n"
            output += f"Manufacturer: {row['Manufacturer']}\n"
            output += f"Indication: {row['Indication']}\n"
            output += f"Classification: {row['Classification']}\n"
            output += "-"*40 + "\n"  # Separator line for each entry
        return output
    else:
        return f"Medicine '{medicine_name}' not found in the dataset."

# Function to generate a PDF with the medicine details in memory
def generate_pdf_in_memory(content):
    # Create a BytesIO buffer to hold the PDF data
    buffer = BytesIO()
    
    # Create a canvas to generate the PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Split content into lines and write to the PDF
    lines = content.split('\n')
    y = height - 50  # Start from the top
    
    for line in lines:
        c.drawString(30, y, line)
        y -= 15  # Move down the page
        if y < 50:
            c.showPage()  # Add a new page if we run out of space
            y = height - 50
    
    c.save()  # Save the PDF content to the buffer
    
    # Get the PDF data from the buffer
    buffer.seek(0)  # Reset the buffer position to the beginning
    return buffer

# Function to send the PDF via WhatsApp using Twilio
def send_whatsapp_pdf(pdf_buffer, to_whatsapp_number):
    # Your Twilio account credentials
    account_sid = 'AC9e6ce7928dbfd8c43d7b3f314b04f971'  # Replace with your Twilio Account SID
    auth_token = '350e44bd66845bb04e8179c4419c08f5'    # Replace with your Twilio Auth Token

    client = Client(account_sid, auth_token)

    from_whatsapp_number = 'whatsapp:+14155238886'  # Twilio sandbox number for WhatsApp
    to_whatsapp_number = f'whatsapp:{to_whatsapp_number}'  # Recipient's WhatsApp number

    # In this case, you'd need to host the PDF somewhere publicly accessible
    # Example: Upload to cloud storage like AWS S3 or any web server
    # For this example, it is assumed that PDF is uploaded to a public URL
    
    # Simulating a file upload and URL generation
    media_url = 'http://your-domain.com/path_to_generated_pdf'

    # Send the PDF file as a media message
    message = client.messages.create(
        media_url=[media_url],
        from_=from_whatsapp_number,
        to=to_whatsapp_number
    )

    print(f"PDF sent to {to_whatsapp_number}: {message.sid}")

# Input from the user
medicine_name = input("Enter the medicine name: ")
whatsapp_number = input("Enter the WhatsApp number (e.g., +1234567890): ")

# Fetch the medicine details
medicine_details = get_medicine_details(medicine_name, dataset)

# Print the details locally
print(medicine_details)

# Generate PDF in memory if details are found
if medicine_details:
    pdf_buffer = generate_pdf_in_memory(medicine_details)
    send_whatsapp_pdf(pdf_buffer, whatsapp_number)
else:
    print("No valid medicine details to send.")
