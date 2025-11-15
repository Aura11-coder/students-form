import os
import requests
from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
from email.utils import parseaddr

# Load .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Brevo configuration
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
TO_EMAIL = os.getenv("TO_EMAIL") or MAIL_DEFAULT_SENDER

# Startup check
if not BREVO_API_KEY or not MAIL_DEFAULT_SENDER:
    raise RuntimeError("BREVO_API_KEY or MAIL_DEFAULT_SENDER not set in .env")

# Email validation
def is_valid_email(email):
    return "@" in parseaddr(email)[1]

@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Collect form data
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "").strip()
        course = request.form.get("course", "").strip()
        year = request.form.get("year", "").strip()
        address = request.form.get("address", "").strip()

        # Validation
        if not full_name or not email or not phone:
            flash("Full Name, Email, and Phone are required.", "warning")
            return redirect(url_for("register"))
        if not is_valid_email(email):
            flash("Invalid email format.", "warning")
            return redirect(url_for("register"))

        # Prepare email content
        subject = "New Student Registration"
        message = f"""
New Student Registration

Full Name: {full_name}
Email: {email}
Phone: {phone}
DOB: {dob}
Gender: {gender}
Course: {course}
Year: {year}
Address: {address}
"""

        # Send email via Brevo
        brevo_url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": BREVO_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "sender": {"name": "Aura Institute", "email": MAIL_DEFAULT_SENDER},
            "to": [{"email": TO_EMAIL}],
            "subject": subject,
            "textContent": message
        }

        try:
            response = requests.post(brevo_url, headers=headers, json=data)
            if response.status_code in (200, 201):
                flash("Registration submitted successfully! Email sent.", "success")
            elif response.status_code == 401:
                flash("Registration saved, but email failed: Unauthorized (check API key).", "warning")
            else:
                flash(f"Registration saved, but email failed ({response.status_code}): {response.text}", "warning")
        except Exception as e:
            flash(f"Registration saved, but email failed: {e}", "warning")

        return redirect(url_for("register"))

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)