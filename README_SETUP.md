# Setting Up Daily Email Digest

## GitHub Secrets Configuration

To enable the daily email digest, you need to configure the following secrets in your GitHub repository:

### Required Secrets

1. **Go to your repository on GitHub**
2. **Navigate to Settings → Secrets and variables → Actions**
3. **Add the following secrets:**

#### 1. `GEMINI_API_KEY` (Required)
- Your Google Gemini API key
- Get it from: https://makersuite.google.com/app/apikey

#### 2. `EMAIL_RECIPIENT` (Required for email)
- The email address that will receive the daily digest
- Example: `your-email@example.com`

#### 3. `EMAIL_SENDER` (Required for email)
- The email address that will send the digest
- For Gmail: `your-sender@gmail.com`

#### 4. `EMAIL_PASSWORD` (Required for email)
- For Gmail: Use an App Password (not your regular password)
- How to create Gmail App Password:
  1. Go to https://myaccount.google.com/security
  2. Enable 2-factor authentication if not already enabled
  3. Search for "App passwords"
  4. Create a new app password for "Mail"
  5. Use this 16-character password as the secret

#### 5. `SMTP_SERVER` (Optional)
- Default: `smtp.gmail.com`
- Change if using a different email provider

#### 6. `SMTP_PORT` (Optional)
- Default: `587`
- Standard port for SMTP with STARTTLS

### Email Provider Settings

#### Gmail
```
SMTP_SERVER: smtp.gmail.com
SMTP_PORT: 587
EMAIL_PASSWORD: (Use App Password)
```

#### Outlook/Hotmail
```
SMTP_SERVER: smtp-mail.outlook.com
SMTP_PORT: 587
EMAIL_PASSWORD: (Your password)
```

#### Yahoo
```
SMTP_SERVER: smtp.mail.yahoo.com
SMTP_PORT: 587
EMAIL_PASSWORD: (Use App Password)
```

## Testing the Workflow

### Manual Trigger
1. Go to Actions tab in your GitHub repository
2. Select "Daily TechCrunch Digest" workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow" button

### Schedule
The workflow runs automatically every day at:
- **7:00 AM Zurich time** (adjusted for daylight saving)
- You can modify the schedule in `.github/workflows/daily_digest.yml`

## Customizing Interests

Edit `config/interests_config.json` to customize what articles are relevant to you:

```json
{
  "interests": [
    {
      "topic": "your_topic",
      "keywords": ["keyword1", "keyword2"],
      "priority": "high"
    }
  ]
}
```

## Email Preview

The digest email includes:
- 📊 Statistics (total relevant posts, high priority count)
- 🔥 High priority articles with summaries
- 📝 Key points from each article
- 🔗 Direct links to full articles
- 🎯 Relevance scores and matched topics

## Troubleshooting

### Email not sending
1. Check GitHub Actions logs for errors
2. Verify all secrets are set correctly
3. For Gmail, ensure "Less secure app access" or App Password is configured
4. Check spam folder for the digest emails

### No relevant posts found
1. Review your interests configuration
2. Consider broadening keywords
3. Check if TechCrunch has posts in your interest areas

### Gemini API errors
1. Verify your API key is valid
2. Check API quota limits
3. The script will continue without summaries if API fails