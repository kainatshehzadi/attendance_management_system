import csv
import os
from datetime import date
import smtplib  #its a python standerd module to send the email using simple mail transfer protocol 
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("D:/K.KA/sedule_management/app/.env")
# CSV generation function: updates or adds records
def generate_attendance_csv(file_path, attendance_records):
    fieldnames = ['date', 'status', 'marked_by']
    existing_data = {}

    # Load existing data if the file exists
    if os.path.exists(file_path):
        with open(file_path, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_data[row['date']] = row

    # Overwrite or add new rows
    for record in attendance_records:
        record_date = record['date']
        existing_data[record_date] = {
            'date': record_date,
            'status': record['status'],
            'marked_by': record['marked_by']
        }

    # Write updated CSV
    with open(file_path, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(existing_data.values(), key=lambda x: x['date']):
            writer.writerow(row)

# Email sending function using Gmail SMTP
def send_csv_to_email_sync(to_email: str, file_path: str):
    EMAIL_USER = os.getenv("EMAIL_USER")         # Sender
    EMAIL_PASS = os.getenv("EMAIL_PASS")       # App password
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT",587)) #Port 587 is the standard for secure email sending using TLS encryption

    if not EMAIL_USER or not EMAIL_PASS:
        raise Exception("Missing email credentials in environment variables.")

    msg = EmailMessage()
    msg['Subject'] = "Your Attendance Report"
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content("Attached is your latest attendance CSV report.")

    with open(file_path, 'rb') as f:
        file_data = f.read()
        filename = os.path.basename(file_path)
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=filename)

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

