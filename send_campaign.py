#!/usr/bin/env python3
"""
SendGrid Email Campaign Script with Resume Capability
Sends promotional emails to customers from CSV with progress tracking
"""

import csv
import os
import time
import random
import json
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, ClickTracking, TrackingSettings

# Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = 'sales@cxsunglassesmx.com'
CSV_FILE = '/Users/luisrico/dev/cx/buenfin/EcomSend_customers_export_1762410755.csv'
HTML_TEMPLATE_FILE = '/Users/luisrico/dev/cx/buenfin/email_template_optimized.html'
PROGRESS_FILE = '/Users/luisrico/dev/cx/buenfin/email_campaign_progress.json'
LOG_FILE = '/Users/luisrico/dev/cx/buenfin/email_campaign_log.txt'

# Timing configuration (in seconds)
MIN_DELAY = 2  # Minimum 2 seconds between emails
MAX_DELAY = 8  # Maximum 8 seconds between emails

def load_html_template():
    """Load the HTML email template"""
    with open(HTML_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def load_progress():
    """Load progress from previous run"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        'last_processed_index': -1,
        'sent_count': 0,
        'failed_count': 0,
        'failed_emails': [],
        'start_time': None,
        'last_run_time': None
    }

def save_progress(progress):
    """Save current progress"""
    progress['last_run_time'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def log_message(message):
    """Log message to both console and file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def send_email(sg_client, to_email, to_name, html_content):
    """Send individual email via SendGrid"""
    try:
        # Personalize the HTML content with customer's first name
        first_name = to_name.split()[0] if to_name else "amigo"
        personalized_html = html_content.replace("{{CUSTOMER_NAME}}", first_name)

        # Create subject line
        subject = "PROMOCIÓN ESPECIAL - $200 de descuento 🕶️"

        # Create the email
        message = Mail(
            from_email=Email(FROM_EMAIL, 'CX Sunglasses'),
            to_emails=To(to_email, to_name),
            subject=subject,
            html_content=Content("text/html", personalized_html)
        )

        # Disable click tracking to preserve original URLs
        message.tracking_settings = TrackingSettings()
        message.tracking_settings.click_tracking = ClickTracking(False, False)

        # Send the email
        response = sg_client.send(message)

        if response.status_code in [200, 201, 202]:
            return True, None
        else:
            return False, f"Status code: {response.status_code}"

    except Exception as e:
        return False, str(e)

def read_customers(csv_file, start_index=0):
    """Read customers from CSV file starting from specific index"""
    customers = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        # Handle BOM if present
        content = f.read()
        if content.startswith('\ufeff'):
            content = content[1:]

        reader = csv.DictReader(content.splitlines())
        for idx, row in enumerate(reader):
            if idx >= start_index:
                customers.append({
                    'index': idx,
                    'email': row['Email address'],
                    'name': row['Customer name'],
                    'phone': row.get('Phone number', ''),
                    'location': row.get('Location', '')
                })

    return customers

def main():
    """Main execution function"""
    # Validate API key
    if not SENDGRID_API_KEY:
        log_message("ERROR: SENDGRID_API_KEY environment variable not set!")
        log_message("Please set it with: export SENDGRID_API_KEY='your-api-key'")
        return

    # Initialize SendGrid client
    sg = SendGridAPIClient(SENDGRID_API_KEY)

    # Load HTML template
    log_message("Loading HTML template...")
    html_template = load_html_template()

    # Load progress
    progress = load_progress()

    if progress['start_time'] is None:
        progress['start_time'] = datetime.now().isoformat()
        log_message("Starting new email campaign...")
    else:
        log_message(f"Resuming campaign from index {progress['last_processed_index'] + 1}")
        log_message(f"Previous stats - Sent: {progress['sent_count']}, Failed: {progress['failed_count']}")

    # Read customers starting from last processed index
    start_index = progress['last_processed_index'] + 1
    customers = read_customers(CSV_FILE, start_index)

    log_message(f"Found {len(customers)} customers to process")

    if len(customers) == 0:
        log_message("Campaign complete! No more customers to process.")
        return

    # Send emails
    for customer in customers:
        try:
            # Send email
            log_message(f"Sending to {customer['name']} ({customer['email']})...")

            success, error = send_email(
                sg,
                customer['email'],
                customer['name'],
                html_template
            )

            if success:
                progress['sent_count'] += 1
                progress['last_processed_index'] = customer['index']
                log_message(f"✓ Sent successfully (Total sent: {progress['sent_count']})")
            else:
                progress['failed_count'] += 1
                progress['failed_emails'].append({
                    'email': customer['email'],
                    'name': customer['name'],
                    'error': error,
                    'timestamp': datetime.now().isoformat()
                })
                log_message(f"✗ Failed: {error}")

            # Save progress after each email
            save_progress(progress)

            # Random delay before next email (natural timing)
            if customer != customers[-1]:  # Don't delay after last email
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                log_message(f"Waiting {delay:.2f} seconds before next email...")
                time.sleep(delay)

        except KeyboardInterrupt:
            log_message("\n\nCampaign interrupted by user. Progress saved.")
            log_message(f"Sent: {progress['sent_count']}, Failed: {progress['failed_count']}")
            save_progress(progress)
            return

        except Exception as e:
            log_message(f"Unexpected error: {str(e)}")
            progress['failed_count'] += 1
            save_progress(progress)
            continue

    # Final summary
    log_message("\n" + "="*60)
    log_message("CAMPAIGN COMPLETE!")
    log_message(f"Total sent: {progress['sent_count']}")
    log_message(f"Total failed: {progress['failed_count']}")
    log_message(f"Start time: {progress['start_time']}")
    log_message(f"End time: {datetime.now().isoformat()}")
    log_message("="*60)

    if progress['failed_emails']:
        log_message(f"\n{len(progress['failed_emails'])} failed emails saved in {PROGRESS_FILE}")

if __name__ == '__main__':
    main()
