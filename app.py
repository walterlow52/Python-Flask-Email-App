from flask import Flask, render_template, request  # type: ignore[import]
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
try:
    from werkzeug.utils import secure_filename  # type: ignore[import]
except Exception:
    # Fallback implementation of secure_filename if werkzeug is unavailable
    import re
    from unicodedata import normalize

    def secure_filename(filename: str) -> str:
        """A minimal replacement for werkzeug.utils.secure_filename.

        Strips leading/trailing spaces, normalizes unicode, removes unsafe
        characters and ensures the filename is ASCII.
        """
        if not filename:
            return ""
        filename = str(filename).strip().replace("\\", "/")
        filename = filename.split("/")[-1]
        filename = normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")
        # keep alphanumeric, dot, underscore and hyphen
        filename = re.sub(r"[^A-Za-z0-9._-]", "", filename)
        # prevent filenames like .env or empty
        if filename in {"", ".", ".."}:
            return "file"
        return filename

app = Flask(__name__)

print("App file:", os.path.abspath(__file__))
print("Root path:", app.root_path)
print("Template folder:", app.template_folder)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERNAME = "walter.low@unitedsettlement.com"
PASSWORD = "wegs tcjq nhjc aree"

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
