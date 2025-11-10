#!/usr/bin/env python3
"""
Test script to send a single email
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, ClickTracking, TrackingSettings

# Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = 'sales@cxsunglassesmx.com'
HTML_TEMPLATE_FILE = '/Users/luisrico/dev/cx/buenfin/email_template_optimized.html'

# Test recipient
TEST_EMAIL = 'luiscarlosricoalmada@gmail.com'
TEST_NAME = 'Luis Carlos Rico Almada'

def load_html_template():
    """Load the HTML email template"""
    with open(HTML_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def send_test_email():
    """Send a test email"""
    if not SENDGRID_API_KEY:
        print("ERROR: SENDGRID_API_KEY environment variable not set!")
        return

    # Initialize SendGrid client
    sg = SendGridAPIClient(SENDGRID_API_KEY)

    # Load and personalize HTML template
    html_content = load_html_template()
    first_name = TEST_NAME.split()[0] if TEST_NAME else "amigo"
    personalized_html = html_content.replace("{{CUSTOMER_NAME}}", first_name)

    print(f"Sending test email to: {TEST_EMAIL}")
    print(f"Personalized with name: {first_name}")

    # Create subject line
    subject = "PROMOCIÓN ESPECIAL - $200 de descuento 🕶️"

    # Create the email
    message = Mail(
        from_email=Email(FROM_EMAIL, 'CX Sunglasses'),
        to_emails=To(TEST_EMAIL, TEST_NAME),
        subject=subject,
        html_content=Content("text/html", personalized_html)
    )

    # Disable click tracking to preserve original URLs
    message.tracking_settings = TrackingSettings()
    message.tracking_settings.click_tracking = ClickTracking(False, False)

    # Send the email
    try:
        response = sg.send(message)
        if response.status_code in [200, 201, 202]:
            print(f"✓ Test email sent successfully! Status: {response.status_code}")
            print(f"Check your inbox at: {TEST_EMAIL}")
        else:
            print(f"✗ Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

if __name__ == '__main__':
    send_test_email()
