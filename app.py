from flask import Flask, render_template, request
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERNAME = "walter.low@unitedsettlement.com"
PASSWORD = "YOUR_APP_PASSWORD"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():

    client_name = request.form["client_name"]
    creditor_name = request.form["creditor_name"]
    ssn = request.form["ssn"]
    dob = request.form["dob"]
    account_number = request.form["account_number"]
    recipients = request.form["recipients"].split(",")

    file = request.files["attachment"]

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    subject = f"{creditor_name} vs {client_name}"

    body = f"""
Good Morning/Afternoon,

Please find attached the completed POA form and let me know what settlement offers are available for this account.

Name: {client_name}

SSN: {ssn}

DOB: {dob}

Kindly confirm receipt of this email and the attached document. 

If any additional information is required, please let me know. 

Thank you for your attention to this matter. 

Best Regards, 
Walter Low
"""

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(USERNAME, PASSWORD)

    for recipient in recipients:

        msg = MIMEMultipart()

        msg["From"] = USERNAME
        msg["To"] = recipient.strip()
        msg["Subject"] = subject

        msg.attach(MIMEText(body))

        with open(filepath, "rb") as attachment:

            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{filename}"'
        )

        msg.attach(part)

        server.sendmail(USERNAME, recipient.strip(), msg.as_string())

    server.quit()

    os.remove(filepath)

    return "Emails Sent Successfully!"

if __name__ == "__main__":
    app.run(debug=True)
