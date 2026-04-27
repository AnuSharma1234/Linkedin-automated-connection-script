"""
LinkedIn Auto-Messenger
=======================
Sends a custom message to connections who recently accepted your request.

SETUP:
    pip install selenium webdriver-manager python-dotenv

USAGE:
    1. Copy .env.example to .env and fill in your credentials
    2. Edit MESSAGE_TEMPLATE below with your custom message
    3. Run: python linkedin_auto_message.py

WARNING:
    Automating LinkedIn violates their Terms of Service.
    Use responsibly and at low volume to avoid account restrictions.
"""

import time
import json
import os
import random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

# ─── CONFIG ───────────────────────────────────────────────────────────────────

LINKEDIN_EMAIL    = os.getenv("LINKEDIN_EMAIL", "your@email.com")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "yourpassword")

# Customize your follow-up message here.
# Use {first_name} as a placeholder — it'll be replaced with their actual name.
MESSAGE_TEMPLATE = """Hi {first_name},

Thanks for connecting! I'd love to learn more about what you're working on.

Feel free to reach out anytime — always happy to chat.

Best,
[Your Name]"""

# File to track who has already been messaged (avoids duplicates)
SENT_LOG_FILE = "linkedin_sent.json"

# How many new connections to process per run (keep low to stay safe)
MAX_PER_RUN = 5

# Random delay range between actions (seconds) — mimics human behavior
DELAY_MIN = 2.5
DELAY_MAX = 5.0

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def human_delay(min_s=DELAY_MIN, max_s=DELAY_MAX):
    """Sleep for a random duration to mimic human behavior."""
    time.sleep(random.uniform(min_s, max_s))


def load_sent_log() -> set:
    """Load the set of profile URLs already messaged."""
    if Path(SENT_LOG_FILE).exists():
        with open(SENT_LOG_FILE) as f:
            return set(json.load(f))
    return set()


def save_sent_log(sent: set):
    """Persist the set of messaged profile URLs."""
    with open(SENT_LOG_FILE, "w") as f:
        json.dump(list(sent), f, indent=2)


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ─── BROWSER SETUP ────────────────────────────────────────────────────────────

def create_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Uncomment to run headlessly (no visible browser window):
    # options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    # Mask webdriver fingerprint
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


# ─── LINKEDIN ACTIONS ─────────────────────────────────────────────────────────

def login(driver: webdriver.Chrome):
    log("Logging in to LinkedIn...")
    driver.get("https://www.linkedin.com/login")
    human_delay(2, 3)

    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(LINKEDIN_EMAIL)
    driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    human_delay(3, 5)

    if "feed" in driver.current_url or "checkpoint" not in driver.current_url:
        log("✅ Logged in successfully.")
    else:
        raise RuntimeError("Login failed or security checkpoint triggered. Check manually.")


def get_recent_connections(driver: webdriver.Chrome) -> list[dict]:
    """
    Fetch recently accepted connections from the My Network page.
    Returns list of dicts with 'name' and 'profile_url'.
    """
    log("Fetching recent connections...")
    driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
    human_delay(3, 4)

    wait = WebDriverWait(driver, 15)
    connections = []

    try:
        # Scroll down a bit to load more connections
        driver.execute_script("window.scrollTo(0, 500)")
        human_delay(1, 2)

        cards = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "li.mn-connection-card")
        ))

        for card in cards[:MAX_PER_RUN * 2]:  # fetch extra in case some are already sent
            try:
                anchor = card.find_element(By.CSS_SELECTOR, "a.mn-connection-card__link")
                name_el = card.find_element(By.CSS_SELECTOR, "span.mn-connection-card__name")
                profile_url = anchor.get_attribute("href").split("?")[0]
                full_name = name_el.text.strip()
                first_name = full_name.split()[0]
                connections.append({
                    "name": full_name,
                    "first_name": first_name,
                    "profile_url": profile_url
                })
            except NoSuchElementException:
                continue

    except TimeoutException:
        log("⚠️  Could not load connections list. LinkedIn may have changed its layout.")

    log(f"Found {len(connections)} recent connections.")
    return connections


def send_message(driver: webdriver.Chrome, profile_url: str, first_name: str) -> bool:
    """
    Navigate to a profile and send a message via the Message button.
    Returns True on success, False on failure.
    """
    log(f"Opening profile: {profile_url}")
    driver.get(profile_url)
    human_delay(3, 5)

    wait = WebDriverWait(driver, 10)

    # Look for the Message button on the profile
    try:
        msg_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.pvs-profile-actions__action[aria-label*='Message'], "
                              "button[aria-label*='Message']")
        ))
        msg_btn.click()
        human_delay(2, 3)
    except TimeoutException:
        log(f"  ⚠️  No Message button found for {first_name}. Skipping.")
        return False

    # Type the message
    try:
        msg_box = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.msg-form__contenteditable, div[role='textbox']")
        ))
        msg_box.click()
        human_delay(0.5, 1)

        message = MESSAGE_TEMPLATE.format(first_name=first_name)
        # Type character by character for a more human-like feel
        for char in message:
            msg_box.send_keys(char)
            time.sleep(random.uniform(0.02, 0.07))

        human_delay(1, 2)

        # Send with Enter (or find a Send button)
        try:
            send_btn = driver.find_element(
                By.CSS_SELECTOR, "button.msg-form__send-button, button[type='submit']"
            )
            send_btn.click()
        except NoSuchElementException:
            msg_box.send_keys(Keys.CONTROL + Keys.RETURN)

        human_delay(2, 3)
        log(f"  ✅ Message sent to {first_name}.")
        return True

    except TimeoutException:
        log(f"  ❌ Could not find message input for {first_name}.")
        return False


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    sent_log = load_sent_log()
    driver = create_driver()

    try:
        login(driver)
        connections = get_recent_connections(driver)

        new_connections = [
            c for c in connections if c["profile_url"] not in sent_log
        ]

        if not new_connections:
            log("No new connections to message.")
            return

        log(f"Messaging {min(len(new_connections), MAX_PER_RUN)} new connection(s)...")
        count = 0

        for conn in new_connections:
            if count >= MAX_PER_RUN:
                break

            success = send_message(driver, conn["profile_url"], conn["first_name"])
            if success:
                sent_log.add(conn["profile_url"])
                save_sent_log(sent_log)
                count += 1

            # Longer pause between profiles
            human_delay(4, 8)

        log(f"\nDone. Messaged {count} connection(s) this run.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()