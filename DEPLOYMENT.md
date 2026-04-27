# LinkedIn Auto-Messenger — Deployment Guide

## Prerequisites

Before deploying anywhere, make sure you have:

- Python 3.10+
- The script file: `linkedin_auto_message.py`
- A `.env` file with your credentials:
  ```
  LINKEDIN_EMAIL=your@email.com
  LINKEDIN_PASSWORD=yourpassword
  ```

---

## Option 1: Run Locally (simplest)

Best if you just want to run it manually or on a schedule while your laptop is on.

### Setup

```bash
# Install dependencies
pip install selenium webdriver-manager python-dotenv

# Run the script
python linkedin_auto_message.py
```

A Chrome window will open and run automatically. Keep your laptop awake while it runs.

### Schedule it (optional)

**Mac/Linux — using cron:**
```bash
crontab -e
# Add this line to run daily at 10am:
0 10 * * * cd /path/to/linkedin_bot && python3 linkedin_auto_message.py
```

**Windows — using Task Scheduler:**
1. Open Task Scheduler → Create Basic Task
2. Set trigger to Daily at your preferred time
3. Set action to: `python C:\path\to\linkedin_auto_message.py`

---

## Option 2: GitHub Actions (free, recommended)

No server needed. GitHub runs the script on a schedule for free.

### Steps

**1. Create a private GitHub repository** and push your script to it.
> ⚠️ Make sure the repo is **private** so your script isn't publicly visible.

**2. Add your credentials as GitHub Secrets:**
- Go to your repo → Settings → Secrets and variables → Actions
- Add two secrets:
  - `LINKEDIN_EMAIL` → your LinkedIn email
  - `LINKEDIN_PASSWORD` → your LinkedIn password

**3. Enable headless mode in the script:**

Open `linkedin_auto_message.py` and uncomment this line inside `create_driver()`:
```python
options.add_argument("--headless=new")
```

**4. Create the workflow file:**

Create the file `.github/workflows/run.yml` in your repo with this content:

```yaml
name: LinkedIn Auto Message

on:
  schedule:
    - cron: '0 10 * * *'  # Runs daily at 10am UTC
  workflow_dispatch:        # Allows manual trigger from GitHub UI

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Chrome
        run: sudo apt-get install -y google-chrome-stable

      - name: Install Python dependencies
        run: pip install selenium webdriver-manager python-dotenv

      - name: Run script
        env:
          LINKEDIN_EMAIL: ${{ secrets.LINKEDIN_EMAIL }}
          LINKEDIN_PASSWORD: ${{ secrets.LINKEDIN_PASSWORD }}
        run: python linkedin_auto_message.py
```

**5. Push and verify:**
- Push the workflow file to GitHub
- Go to Actions tab in your repo to see it run
- You can also trigger it manually via the "Run workflow" button

### Saving the sent log between runs

By default, `linkedin_sent.json` is not persisted between GitHub Actions runs. To avoid re-messaging people, commit and push the log file back after each run. Add these steps at the end of your workflow:

```yaml
      - name: Save sent log
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add linkedin_sent.json
          git diff --staged --quiet || git commit -m "Update sent log"
          git push
```

---

## Option 3: DigitalOcean Droplet ($4–6/mo)

Best if you want full control and need the script available around the clock.

### Steps

**1. Create a Droplet:**
- Go to [digitalocean.com](https://digitalocean.com) → Create Droplet
- Choose **Ubuntu 22.04**, the **Basic $4/mo** plan
- Add your SSH key during setup

**2. SSH into your server:**
```bash
ssh root@your_droplet_ip
```

**3. Install dependencies:**
```bash
sudo apt update && sudo apt upgrade -y

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# Install Python deps
pip3 install selenium webdriver-manager python-dotenv
```

**4. Upload your files:**

From your local machine:
```bash
scp linkedin_auto_message.py root@your_droplet_ip:/root/linkedin_bot/
scp .env root@your_droplet_ip:/root/linkedin_bot/
```

**5. Enable headless mode in the script:**

Open `linkedin_auto_message.py` and uncomment:
```python
options.add_argument("--headless=new")
```

**6. Test it manually:**
```bash
cd /root/linkedin_bot
python3 linkedin_auto_message.py
```

**7. Schedule with cron:**
```bash
crontab -e
# Run daily at 10am UTC
0 10 * * * cd /root/linkedin_bot && python3 linkedin_auto_message.py >> /root/linkedin_bot/run.log 2>&1
```

Logs will be saved to `run.log` so you can check what happened.

---

## Option 4: AWS EC2 (free tier eligible)

Same approach as DigitalOcean but using AWS.

**1. Launch an EC2 instance:**
- Go to AWS Console → EC2 → Launch Instance
- Choose **Ubuntu 22.04**, instance type **t2.micro** (free tier)
- Create or select a key pair for SSH access
- Allow SSH (port 22) in the security group

**2. SSH in:**
```bash
ssh -i your-key.pem ubuntu@your_ec2_public_ip
```

**3. Follow the same steps as DigitalOcean** from step 3 onwards, replacing `root` with `ubuntu` in paths.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `pip not found` | Use `pip3` instead |
| `python not found` | Use `python3` instead |
| Chrome won't launch on server | Make sure `--headless=new` is uncommented |
| Login stuck at CAPTCHA (local only) | Solve it manually in the browser window |
| Message button not found | LinkedIn changed their HTML — update the CSS selector in `send_message()` |
| Sent log not persisting (GitHub Actions) | Add the "Save sent log" step to your workflow |
| Account restricted | Reduce `MAX_PER_RUN` and add longer delays |

---

## Security Tips

- Never commit your `.env` file to GitHub — add it to `.gitignore`
- Always use GitHub Secrets or environment variables for credentials on servers
- Keep `MAX_PER_RUN` low (5–10/day) to avoid LinkedIn bot detection