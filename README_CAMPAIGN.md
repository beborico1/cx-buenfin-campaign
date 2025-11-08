# Email Campaign Script - Instructions

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your SendGrid API Key:**
   ```bash
   export SENDGRID_API_KEY='your-sendgrid-api-key-here'
   ```

3. **Verify your files are in place:**
   - `email_template_optimized.html` - Email template
   - `EcomSend_customers_export_1762410755.csv` - Customer list
   - `send_campaign.py` - Main script

## Running the Campaign

### Start the campaign:
```bash
python3 send_campaign.py
```

### Resume after interruption:
Simply run the same command again. The script automatically resumes from where it left off:
```bash
python3 send_campaign.py
```

## Features

✓ **Resume Capability** - Stops and resumes exactly where it left off
✓ **Progress Tracking** - Saves progress after each email
✓ **Natural Timing** - Random delays (2-8 seconds) between emails
✓ **Detailed Logging** - All actions logged to `email_campaign_log.txt`
✓ **Error Handling** - Failed emails tracked in `email_campaign_progress.json`

## Files Generated

- `email_campaign_progress.json` - Current progress and failed emails
- `email_campaign_log.txt` - Detailed log of all operations

## Monitoring Progress

Watch the log file in real-time:
```bash
tail -f email_campaign_log.txt
```

## Testing First

**IMPORTANT:** Test with a small batch first!

Edit `send_campaign.py` and modify the `read_customers` function to limit the number:
```python
# Add this after line that creates customers list:
customers = customers[:5]  # Test with only 5 emails first
```

## Campaign Statistics

The script tracks:
- Total emails sent
- Total failures
- Failed email addresses with error messages
- Campaign start/end times
- Last processed customer index

## Stopping the Campaign

Press `Ctrl+C` to stop safely. Progress is automatically saved.

## SendGrid Rate Limits

Current configuration:
- 2-8 seconds between emails (natural timing)
- Approximately 7-30 emails per minute
- ~24,570 emails will take 13-41 hours to complete

**Note:** Adjust `MIN_DELAY` and `MAX_DELAY` in the script if needed based on your SendGrid plan limits.

## Troubleshooting

### "SENDGRID_API_KEY not set"
Run: `export SENDGRID_API_KEY='your-key'`

### Want to start over?
Delete `email_campaign_progress.json` to reset progress

### Check failed emails?
Look in `email_campaign_progress.json` under "failed_emails"
