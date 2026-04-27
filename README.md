# 🤝 LinkedIn Auto-Messenger

Automatically send a custom follow-up message to new LinkedIn connections the moment they accept your request — without keeping your laptop open.

---

## ✨ Features

- Detects newly accepted connection requests
- Sends a personalized message using `{first_name}` placeholder
- Tracks who has been messaged to avoid duplicates
- Human-like typing and random delays to avoid detection
- Runs headlessly on any cloud server or GitHub Actions

---

## 📁 Project Structure

```
Linkedin-automated-connection-script/
├── main.py   # Main script
├── .env                       # Your credentials (never commit this)
├── .env.example               # Credentials template
├── linkedin_sent.json         # Auto-generated log of messaged profiles
├── README.md                  # You are here
└── DEPLOYMENT.md              # Full deployment guide
```

---

## ⚡ Quick Start

**1. Clone or download this repo**

```bash
git clone https://github.com/AnuSharma1234/Linkedin-automated-connection-script.git
cd Linkedin-automated-connection-script
```

**2. Install dependencies**

```bash
pip install selenium webdriver-manager python-dotenv
```

**3. Set up your credentials**

```bash
cp .env.example .env
```

Edit `.env` with your LinkedIn login:
```
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=yourpassword
```

**4. Customize your message**

Open `linkedin_auto_message.py` and edit `MESSAGE_TEMPLATE`:

```python
MESSAGE_TEMPLATE = """Hi {first_name},

Thanks for connecting! I'd love to learn more about what you're working on.

Best,
[Your Name]"""
```

**5. Run it**

```bash
python linkedin_auto_message.py
```

A Chrome window will open and handle everything automatically.

---

## ⚙️ Configuration

All key settings are at the top of `linkedin_auto_message.py`:

| Variable | Default | Description |
|---|---|---|
| `MESSAGE_TEMPLATE` | See script | Message to send. Use `{first_name}` for personalization |
| `MAX_PER_RUN` | `5` | Max connections to message per run |
| `DELAY_MIN` | `2.5` | Minimum seconds between actions |
| `DELAY_MAX` | `5.0` | Maximum seconds between actions |
| `SENT_LOG_FILE` | `linkedin_sent.json` | File tracking already-messaged profiles |

---

## 🚀 Deployment

Don't want to keep your laptop open? See **[DEPLOYMENT.md](DEPLOYMENT.md)** for full instructions on:

- ⏱️ Local scheduling with cron / Task Scheduler
- 🐙 **GitHub Actions** (free, recommended)
- 🌊 DigitalOcean Droplet ($4–6/mo)
- ☁️ AWS EC2 (free tier eligible)

---

## ⚠️ Disclaimer

Automating LinkedIn activity violates their [Terms of Service](https://www.linkedin.com/legal/user-agreement). Using this tool may result in your account being restricted or banned. Use responsibly:

- Keep `MAX_PER_RUN` low (5–10 per day)
- Do not use for mass spam or unsolicited commercial outreach
- You are solely responsible for how you use this tool

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| Script can't find Message button | LinkedIn updated their HTML — update CSS selectors in `send_message()` |
| Login stuck at CAPTCHA | Solve it manually in the browser window, script will continue |
| `pip` / `python` not found | Try `pip3` / `python3` instead |
| Chrome won't launch on server | Uncomment `--headless=new` in `create_driver()` |
| Same person messaged twice | Check `linkedin_sent.json` exists and isn't being reset |

---

## 📄 License

MIT — use freely, modify as needed.