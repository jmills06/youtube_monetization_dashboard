# YouTube Monetization Dashboard

Auto-updating YouTube monetization dashboard for The Everyday Ham Podcast.

## Quick Setup

### 1. Upload These Files to GitHub

Create a new repository named: `youtube_monetization_dashboard`

Upload all files from this folder, keeping the `.github/workflows/` folder structure.

### 2. Add GitHub Secrets

Go to: Settings → Secrets and variables → Actions

Add two secrets:

**GOOGLE_CREDENTIALS**
- Paste your entire `credentials.json` content

**GOOGLE_TOKEN**  
- Run: `base64 token.pickle`
- Paste the output

### 3. Test the Workflow

- Go to Actions tab
- Click "Update YouTube Monetization Data"
- Click "Run workflow"
- Wait ~2 minutes
- Check that `youtube_monetization.json` is created

### 4. Deploy Dashboard

Copy `youtube_monetization_dakboard.html` to DakBoard.

Update the `DATA_URL` on line 240 to:
```javascript
const DATA_URL = 'https://raw.githubusercontent.com/jmills06/youtube_monetization_dashboard/main/youtube_monetization.json';
```

## Files Included

- `fetch_youtube_monetization.py` - Fetches revenue data from YouTube API
- `youtube_monetization_dakboard.html` - Dashboard display
- `youtube_monetization_sample.json` - Sample data for testing
- `requirements.txt` - Python dependencies
- `.gitignore` - Protects sensitive files
- `.github/workflows/update-monetization.yml` - Daily automation

## That's It!

The dashboard will auto-update daily at 7 AM UTC.

## Need Help?

- No revenue data? You need Content Owner access from YouTube
- Workflow fails? Check your secrets are correct
- Dashboard blank? Verify the DATA_URL points to your repository

---

**Everyday Ham Podcast** 🐷📊
