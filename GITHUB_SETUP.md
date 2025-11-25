# GitHub Actions Setup Guide

## Required Secrets

Go to your repository: https://github.com/chaofiber/ai-news-bot

1. Click on **Settings** (in the repository)
2. Go to **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of these:

### Required Secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `GEMINI_API_KEY` | Your Gemini API key | Get from Google AI Studio |
| `EMAIL_RECIPIENT` | recipient@example.com | Where to send the digest |
| `EMAIL_SENDER` | your-email@gmail.com | Your Gmail address |
| `EMAIL_PASSWORD` | Your 16-char app password | Generate from Google Account settings |
| `SMTP_SERVER` | smtp.gmail.com | Gmail SMTP server |
| `SMTP_PORT` | 587 | Gmail SMTP port |

## Testing the Workflow

### Option 1: Manual Trigger (Recommended for First Test)
1. Go to the **Actions** tab in your repository
2. Select **Daily TechCrunch Digest** workflow
3. Click **Run workflow** → **Run workflow**
4. Watch the workflow execution in real-time

### Option 2: Wait for Scheduled Run
- The workflow runs automatically at 7:00 AM Zurich time daily
- UTC times: 5:00 AM (summer) or 6:00 AM (winter)

## Monitoring

- Check the **Actions** tab to see workflow runs
- Green checkmark = success
- Red X = failure (click to see logs)
- You'll receive emails at the configured recipient address

## Troubleshooting

If the workflow fails:
1. Check the workflow logs in the Actions tab
2. Verify all secrets are correctly set
3. Ensure the Gmail App Password is valid
4. Check that the Gemini API key has not exceeded its quota