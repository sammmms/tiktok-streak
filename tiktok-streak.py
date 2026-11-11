#!/usr/bin/env python3
"""
⚡ TikTok Streak Auto-Saver & Helper Hub
Supports: Windows, macOS, Linux
Interactive Terminal Hub with Grouping, Select All, Auto-Scheduler, and Webhook Notifications.
Modeled after genshin-checkin.
"""

import sys
import os
import json
import time
import shutil
import random
import platform
import argparse
import subprocess
import signal
from datetime import datetime, date, timedelta
from pathlib import Path

def handle_sigint(sig=None, frame=None):
    print("\n\n👋 Operasi dibatalkan oleh pengguna (Keluar). Sampai jumpa!\n")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

OS_NAME = platform.system()  # 'Darwin' (macOS), 'Windows', 'Linux'
APP_NAME = "tiktok-streak"
APP_VERSION = "1.3.0"
HOME_DIR = Path.home()
INSTALL_DIR = HOME_DIR / ".tiktok-streak"
CONFIG_FILE = INSTALL_DIR / "config.json"
STATE_FILE = INSTALL_DIR / "last_run.json"
PROFILE_DIR = INSTALL_DIR / "browser_profile"
LOG_FILE = INSTALL_DIR / "streak.log"
LOGS_DIR = INSTALL_DIR / "logs"
SCRIPT_PATH = Path(__file__).resolve()


def parse_semver(ver: str) -> tuple:
    parts = []
    for x in ver.lstrip("v").split("."):
        if x.isdigit():
            parts.append(int(x))
    return tuple(parts)


def run_with_progress(title: str, worker_fn, timeout: float = 4.0):
    """Executes worker_fn in a daemon thread while rendering an animated progress bar and spinner."""
    import threading
    res = {"done": False, "result": None, "error": None}

    def target():
        try:
            res["result"] = worker_fn()
        except Exception as e:
            res["error"] = e
        finally:
            res["done"] = True

    t = threading.Thread(target=target, daemon=True)
    t.start()

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start_t = time.time()
    i = 0

    while not res["done"] and (time.time() - start_t < timeout):
        elapsed = time.time() - start_t
        pct = min(int((elapsed / timeout) * 100), 99)
        filled = pct // 10
        bar = "█" * filled + "░" * (10 - filled)
        sys.stdout.write(f"\r[*] {title}... {frames[i % len(frames)]} [{bar}] {pct}% ({elapsed:.1f}s)")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1

    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
    return res["result"], res["error"]


def check_for_updates(prompt_if_latest: bool = False):
    """
    Checks latest update from https://wsnsam.my.id/api/updates?app=tiktok-streak
    with fallback to raw.githubusercontent.com/.../version.json.
    Shows animated progress bar and spinner.
    """
    import urllib.request
    import json

    primary_url = f"https://script.wsnsam.my.id/api/updates?app={APP_NAME}"
    fallback_url = f"https://raw.githubusercontent.com/sammmms/{APP_NAME}/main/version.json"

    def fetch_remote():
        for url in [primary_url, fallback_url]:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AutoUpdater)"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        return json.loads(resp.read().decode("utf-8"))
            except Exception:
                continue
        return None

    update_data, _ = run_with_progress("Memeriksa pembaruan terbaru", fetch_remote, timeout=3.5)

    if not update_data or "version" not in update_data:
        print("[*] Memeriksa pembaruan terbaru... [Lewati / Offline]")
        time.sleep(0.2)
        return

    latest_ver = update_data["version"]
    if parse_semver(latest_ver) <= parse_semver(APP_VERSION):
        print(f"[*] Memeriksa pembaruan terbaru... [Versi Terbaru: v{APP_VERSION} ✓]")
        time.sleep(0.3)
        if prompt_if_latest:
            print(f"\n[✓] Anda sudah menggunakan versi terbaru (v{APP_VERSION}).\n")
            import questionary
            questionary.press_any_key_to_continue().ask()
        return

    # Newer version available
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

    print("\n" + "=" * 62)
    print(f"🚀 PEMBARUAN TERSEDIA! (v{APP_VERSION} ➔ v{latest_ver})")
    print(f"📅 Rilis: {update_data.get('release_date', 'Baru')}")
    print("=" * 62)
    print("📋 Catatan Pembaruan (Changelog):")
    for change in update_data.get("changelog", []):
        print(f"  • {change}")
    print("=" * 62 + "\n")

    try:
        import questionary
        action = questionary.select(
            "Apakah Anda ingin memasang pembaruan sekarang?",
            choices=[
                "🚀 Pasang Pembaruan Sekarang (Auto-update in-app)",
                "⏭️  Lewati (Skip untuk sekarang)"
            ]
        ).ask()
    except Exception:
        action = input("Pasang pembaruan sekarang? [Y/n]: ").strip().lower()
        action = "yes" if action in ("", "y", "yes") else "no"

    if action and ("Pasang" in action or action == "yes"):
        print(f"\n⬇️  Mengunduh pembaruan v{latest_ver}...")
        download_url = update_data.get("download_url")
        if not download_url:
            print("[!] URL unduhan tidak tersedia.")
            return

        try:
            req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0 (AutoUpdater)"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                new_code = resp.read().decode("utf-8")

            # Update current script
            with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
                f.write(new_code)
            os.chmod(SCRIPT_PATH, 0o755)

            # Also update target install dir if running from local repo
            target_installed = INSTALL_DIR / "tiktok-streak.py"
            if target_installed.exists() and target_installed != SCRIPT_PATH:
                with open(target_installed, "w", encoding="utf-8") as f:
                    f.write(new_code)
                os.chmod(target_installed, 0o755)

            print(f"✅ Berhasil memperbarui ke versi v{latest_ver}!")
            print("🔄 Memulai ulang aplikasi...")
            time.sleep(1)
            os.execv(sys.executable, [sys.executable, str(SCRIPT_PATH)] + sys.argv[1:])
        except Exception as e:
            print(f"[x] Gagal memasang pembaruan: {e}")
            input("Tekan [ENTER] untuk melanjutkan...")
    else:
        print("[*] Pembaruan dilewati.\n")

DEFAULT_CONFIG = {
    "mode": "all",  # "all" or "groups"
    "default_message": "🔥",
    "messages": {
        "mode": "pool",  # "pool" (acak dari daftar) or "fixed" (selalu pesan tetap)
        "pool": [
            "🔥",
            "Streak 🔥⚡",
            "Selamat {time_greeting} {first_name}! Streak 🔥",
            "Semangat hari {day} ya {first_name}! 🔥",
            "Streak hari ini 🔥✨"
        ],
        "append_random_emoji": False,
        "contact_overrides": {}  # {"contact_name": "Pesan khusus"}
    },
    "safety": {
        "pace": "normal",  # "fast", "normal", "relaxed"
        "safe_hours": {
            "enabled": True,
            "start": 7,
            "end": 23
        }
    },
    "logging": {
        "retention_days": 3  # otomatis simpan up to 3 hari, sisanya dihapus
    },
    "select_all": {
        "enabled": True,
        "message": "🔥",
        "exclude": ["TikTok", "TikTok Rewards", "TikTok Shop", "System Notification"]
    },
    "groups": {
        "Sahabat": {
            "enabled": True,
            "message": "Pagi bro! Streak 🔥⚡",
            "members": []
        },
        "Prioritas": {
            "enabled": True,
            "message": "Semangat harinya ya ❤️🔥",
            "members": []
        },
        "Mutual": {
            "enabled": True,
            "message": "🔥",
            "members": []
        }
    },
    "contacts": [],
    "headless": True,
    "schedule": {
        "hour": 9,
        "minute": 0
    },
    "notifications": {
        "macos": {"enabled": True},
        "telegram": {
            "enabled": False,
            "bot_token": "",
            "chat_id": ""
        },
        "discord": {
            "enabled": False,
            "webhook_url": ""
        }
    }
}


# ==============================================================================
# Configuration & State Management
# ==============================================================================

def ensure_dirs():
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def deep_merge(target: dict, default: dict):
    """Recursively merges default config keys without overwriting existing values."""
    for k, v in default.items():
        if k not in target:
            target[k] = v
        elif isinstance(v, dict) and isinstance(target.get(k), dict):
            deep_merge(target[k], v)


def load_config() -> dict:
    ensure_dirs()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            deep_merge(cfg, DEFAULT_CONFIG)
            return cfg
    except Exception as e:
        print(f"[!] Warning reading config: {e}. Using defaults.")
        return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_success_date": None,
        "last_attempt": None,
        "sent_count": 0,
        "failed_count": 0,
        "last_summary": "Never run"
    }


def save_state(success: bool, sent_count: int, failed_count: int, summary: str):
    state = load_state()
    today_str = str(date.today())
    state["last_attempt"] = datetime.now().isoformat()
    state["sent_count"] = sent_count
    state["failed_count"] = failed_count
    state["last_summary"] = summary
    if success:
        state["last_success_date"] = today_str
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ==============================================================================
# Logging & 3-Day Retention Engine
# ==============================================================================

def clean_expired_logs(retention_days: int = 3):
    """
    Deletes log files and log entries older than retention_days (default: 3 days).
    Keeps only up to 3 days of activity history as requested.
    """
    ensure_dirs()
    cutoff_dt = datetime.now() - timedelta(days=retention_days)

    # 1. Prune daily files in ~/.tiktok-streak/logs/
    for log_path in LOGS_DIR.glob("*.log"):
        name = log_path.stem
        parts = name.split("_")
        if len(parts) >= 2:
            date_part = parts[-1]
            try:
                file_dt = datetime.strptime(date_part, "%Y-%m-%d")
                if file_dt.date() < cutoff_dt.date():
                    log_path.unlink(missing_ok=True)
                    continue
            except ValueError:
                pass

        try:
            mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
            if mtime < cutoff_dt:
                log_path.unlink(missing_ok=True)
        except Exception:
            pass

    # 2. Prune streak.log to retain only lines from the last 3 days
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            kept_lines = []
            for l in lines:
                if l.startswith("[") and len(l) >= 11:
                    date_prefix = l[1:11]
                    try:
                        line_date = datetime.strptime(date_prefix, "%Y-%m-%d").date()
                        if line_date >= cutoff_dt.date():
                            kept_lines.append(l)
                    except ValueError:
                        kept_lines.append(l)
                else:
                    kept_lines.append(l)

            if len(kept_lines) < len(lines):
                with open(LOG_FILE, "w", encoding="utf-8") as f:
                    f.writelines(kept_lines)
        except Exception:
            pass


def log_activity(category: str, message: str, print_to_console: bool = False):
    """
    Structured logging of jobs performed and configuration changes.
    Category: JOB, CONFIG, SYSTEM, ERROR
    Logs to console (if print_to_console), main streak.log, and daily activity file in logs/.
    Automatically enforces 3-day retention policy.
    """
    ensure_dirs()
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")

    cat_upper = category.upper().strip()
    formatted = f"[{timestamp}] [{cat_upper:<6}] {message}"

    if print_to_console:
        print(formatted)

    # Write to main streak.log
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

    # Write to daily file in logs/
    daily_file = LOGS_DIR / f"activity_{date_str}.log"
    try:
        with open(daily_file, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def log_message(msg: str):
    """Backward compatibility wrapper around log_activity."""
    log_activity("JOB", msg, print_to_console=True)


# ==============================================================================
# Message Template Engine & Placeholders
# ==============================================================================

def format_message(template: str, contact_name: str) -> str:
    """
    Replaces placeholders:
    - {name}: Full contact name
    - {first_name}: First word of contact name
    - {time_greeting}: Pagi / Siang / Sore / Malam based on current hour
    - {day}: Senin / Selasa / Rabu / Kamis / Jumat / Sabtu / Minggu
    - {date}: e.g. 10 Nov
    """
    now = datetime.now()
    hour = now.hour
    if 5 <= hour < 11:
        time_greeting = "Pagi"
    elif 11 <= hour < 15:
        time_greeting = "Siang"
    elif 15 <= hour < 18:
        time_greeting = "Sore"
    else:
        time_greeting = "Malam"

    days_id = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    day_name = days_id[now.weekday()]

    months_id = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    date_str = f"{now.day} {months_id[now.month - 1]}"

    first_name = contact_name.split()[0] if contact_name else ""

    text = template.replace("{name}", contact_name)
    text = text.replace("{first_name}", first_name)
    text = text.replace("{time_greeting}", time_greeting)
    text = text.replace("{day}", day_name)
    text = text.replace("{date}", date_str)
    return text


def resolve_message_for_contact(contact_name: str, group_msg: str = None) -> str:
    """
    Determines final text to send for a specific contact:
    1. Per-contact override (if configured in messages.contact_overrides)
    2. Group-specific message (if configured and distinct from default)
    3. Random / Rotated message from message pool (if pool mode active)
    4. Default message fallback
    Applies template variables and optional emoji booster.
    """
    cfg = load_config()
    msg_cfg = cfg.get("messages", {})
    overrides = msg_cfg.get("contact_overrides", {})

    # Priority 1: Contact override
    if contact_name in overrides and overrides[contact_name].strip():
        base_msg = overrides[contact_name].strip()

    # Priority 2: Explicit group message if distinct from generic default
    elif group_msg and group_msg.strip() and group_msg != cfg.get("default_message", "🔥"):
        base_msg = group_msg.strip()

    # Priority 3: Message Pool if pool mode active
    elif msg_cfg.get("mode", "pool") == "pool" and msg_cfg.get("pool"):
        pool = [m for m in msg_cfg["pool"] if m.strip()]
        if pool:
            base_msg = random.choice(pool)
        else:
            base_msg = cfg.get("default_message", "🔥")

    # Priority 4: Group message if provided, else default message
    elif group_msg and group_msg.strip():
        base_msg = group_msg.strip()
    else:
        base_msg = cfg.get("default_message", "🔥")

    # Format placeholders
    final_text = format_message(base_msg, contact_name)

    # Optional Emoji Booster
    if msg_cfg.get("append_random_emoji", False):
        extra_emojis = ["🔥", "⚡", "✨", "💪", "🚀", "🌟"]
        final_text += " " + random.choice(extra_emojis)

    return final_text


# ==============================================================================
# Safety & Delay Helpers
# ==============================================================================

def get_message_delay() -> float:
    """Natural typing jitter between contacts (2.5 - 4.0s)."""
    return random.uniform(2.5, 4.0)


def get_click_delay() -> float:
    return random.uniform(1.5, 2.5)


def is_within_safe_hours() -> tuple:
    """Postpones midnight background runs (01:00 - 06:00) until morning."""
    now_hour = datetime.now().hour
    if 1 <= now_hour < 6:
        return False, "Di luar jam aman pengiriman (01:00 - 06:00)"
    return True, "Within safe hours"


def wait_for_internet(timeout: int = 180, check_interval: int = 3, verbose: bool = False) -> bool:
    """
    Wait for active internet connectivity with DNS resolution.
    Essential on macOS wake-up because launchd fires before Wi-Fi reconnects.
    """
    import socket
    import urllib.request

    start_time = time.time()
    last_logged = 0
    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    step = 0

    while time.time() - start_time < timeout:
        elapsed = time.time() - start_time
        pct = min(int((elapsed / timeout) * 100), 99)
        bar = "█" * (pct // 10) + "░" * (10 - (pct // 10))
        if verbose:
            sys.stdout.write(f"\r[*] Menunggu koneksi internet aktif... {spinner[step % len(spinner)]} [{bar}] {elapsed:.1f}s/{timeout}s")
            sys.stdout.flush()
            step += 1

        try:
            # 1. Quick socket connection to public DNS (Cloudflare / Google)
            s = socket.create_connection(("1.1.1.1", 53), timeout=2)
            s.close()
            # 2. HTTP probe to verify TLS and web routing
            req = urllib.request.Request(
                "https://www.google.com",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status in (200, 204, 301, 302):
                    if verbose:
                        sys.stdout.write(f"\r{' ' * 75}\r[✓] Koneksi internet aktif! ({elapsed:.1f}s)\n")
                        sys.stdout.flush()
                    elif elapsed > 2:
                        log_message(f"Koneksi internet aktif terdeteksi ({elapsed:.1f}s setelah bangun).")
                    return True
        except Exception:
            pass

        if elapsed >= 5 and (elapsed - last_logged >= 15):
            log_message(f"Menunggu koneksi internet aktif ({int(elapsed)}s/{timeout}s)...")
            last_logged = elapsed

        time.sleep(check_interval)

    if verbose:
        sys.stdout.write(f"\r{' ' * 75}\r[!] Gagal terhubung ke internet setelah {timeout} detik.\n")
        sys.stdout.flush()

    log_message(f"Koneksi internet tidak tersedia setelah menunggu {timeout} detik.")
    return False


# ==============================================================================
# Notifications (macOS Native, Telegram, Discord)
# ==============================================================================

def send_telegram_notification(bot_token: str, chat_id: str, title: str, text: str, success: bool) -> tuple:
    """Send HTML notification via Telegram Bot API. Returns (success: bool, message: str)."""
    try:
        import requests
        import html
        icon = "✅" if success else "❌"
        safe_title = html.escape(title)
        safe_text = html.escape(text)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"{icon} <b>{safe_title}</b>\n\n{safe_text}\n\n<i>Waktu: {now_str}</i>"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML"
        }, timeout=10)

        data = resp.json()
        if resp.status_code == 200 and data.get("ok"):
            return True, "Berhasil terkirim ke Telegram!"
        else:
            desc = data.get("description", resp.text)
            return False, f"Telegram API Error ({resp.status_code}): {desc}"
    except Exception as e:
        return False, f"Gagal koneksi Telegram: {e}"


def send_discord_notification(webhook_url: str, title: str, text: str, success: bool) -> tuple:
    """Send Embed notification via Discord Webhook. Returns (success: bool, message: str)."""
    try:
        import requests
        color = 0x2ECC71 if success else 0xE74C3C
        payload = {
            "embeds": [{
                "title": title,
                "description": text,
                "color": color,
                "timestamp": datetime.utcnow().isoformat()
            }]
        }
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code in (200, 204):
            return True, "Berhasil terkirim ke Discord Webhook!"
        else:
            return False, f"Discord Error ({resp.status_code}): {resp.text}"
    except Exception as e:
        return False, f"Gagal koneksi Discord: {e}"


def send_notification(title: str, text: str, success: bool):
    cfg = load_config()
    notifs = cfg.get("notifications", {})

    # 1. macOS native banner (sanitized to avoid AppleScript escaping issues)
    if OS_NAME == "Darwin" and notifs.get("macos", {}).get("enabled", True):
        sound = "default" if success else "Basso"
        clean_title = title.replace('"', '\\"').replace("\n", " ")
        clean_text = text.replace("*", "").replace('"', "'").strip()
        lines = [l.strip() for l in clean_text.splitlines() if l.strip()]
        short_text = " \\n ".join(lines[:3]) if lines else "Status pengiriman streak"
        if len(short_text) > 200:
            short_text = short_text[:197] + "..."
        script = f'display notification "{short_text}" with title "{clean_title}" sound name "{sound}"'
        try:
            subprocess.run(["osascript", "-e", script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # 2. Telegram Bot
    tg = notifs.get("telegram", {})
    if tg.get("enabled") and tg.get("bot_token") and tg.get("chat_id"):
        ok, err = send_telegram_notification(tg["bot_token"], tg["chat_id"], title, text, success)
        if not ok:
            log_message(f"Telegram error: {err}")

    # 3. Discord Webhook
    dc = notifs.get("discord", {})
    if dc.get("enabled") and dc.get("webhook_url"):
        ok, err = send_discord_notification(dc["webhook_url"], title, text, success)
        if not ok:
            log_message(f"Discord error: {err}")


# ==============================================================================
# Auto Scheduler (LaunchAgent / Windows Task / Crontab)
# ==============================================================================

def get_scheduler_status() -> tuple:
    """Returns (is_active: bool, description: str)."""
    cfg = load_config()
    sched = cfg.get("schedule", {"hour": 9, "minute": 0})
    time_str = f"{sched['hour']:02d}:{sched['minute']:02d}"

    if OS_NAME == "Darwin":
        plist_path = HOME_DIR / "Library/LaunchAgents/com.user.tiktokstreak.plist"
        if plist_path.exists():
            # Check if active in launchctl
            res = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
            if "com.user.tiktokstreak" in res.stdout:
                return True, f"Active (macOS LaunchAgent @ {time_str} with Wake-up Catch-up)"
            return True, f"Registered (macOS LaunchAgent @ {time_str})"
        return False, "Not Installed"

    elif OS_NAME == "Windows":
        try:
            res = subprocess.run(["schtasks", "/query", "/tn", "TikTokStreakDaily"], capture_output=True, text=True)
            if res.returncode == 0:
                return True, f"Active (Windows Task Scheduler @ {time_str})"
        except Exception:
            pass
        return False, "Not Installed"

    else:
        # Linux
        try:
            res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if "tiktok-streak" in res.stdout:
                return True, f"Active (Linux Crontab @ {time_str})"
        except Exception:
            pass
        return False, "Not Installed"


def install_scheduler():
    cfg = load_config()
    hour = cfg.get("schedule", {}).get("hour", 9)
    minute = cfg.get("schedule", {}).get("minute", 0)
    time_str = f"{hour:02d}:{minute:02d}"

    # Target executable path
    bin_path = HOME_DIR / ".local/bin/tiktok-streak"
    if not bin_path.exists():
        bin_path = Path(sys.executable).parent / "tiktok-streak"

    if OS_NAME == "Darwin":
        plist_path = HOME_DIR / "Library/LaunchAgents/com.user.tiktokstreak.plist"
        plist_path.parent.mkdir(parents=True, exist_ok=True)

        # Build StartCalendarInterval array: scheduled hour + hourly catch-ups until 23:00
        intervals = []
        for h in range(hour, 24):
            m = minute if h == hour else 0
            intervals.append(f"""        <dict>
            <key>Hour</key>
            <integer>{h}</integer>
            <key>Minute</key>
            <integer>{m}</integer>
        </dict>""")
        intervals_xml = "\n".join(intervals)

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.tiktokstreak</string>
    <key>ProgramArguments</key>
    <array>
        <string>{bin_path}</string>
        <string>--cron</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
{intervals_xml}
    </array>
    <key>StandardOutPath</key>
    <string>{LOG_FILE}</string>
    <key>StandardErrorPath</key>
    <string>{LOG_FILE}</string>
</dict>
</plist>
"""
        with open(plist_path, "w", encoding="utf-8") as f:
            f.write(plist_content)

        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
        subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True)
        print(f"\n[✓] macOS LaunchAgent berhasil dipasang!")
        print(f"    ⏰ Dijadwalkan mulai jam {time_str} pagi.")
        print(f"    ⚡ Fitur Auto-Catchup: Otomatis mengejar pengiriman saat laptop dinyalakan/dibuka kapan saja.")

    elif OS_NAME == "Windows":
        cmd = [
            "schtasks", "/create", "/tn", "TikTokStreakDaily",
            "/tr", f'"{sys.executable}" "{INSTALL_DIR / "tiktok-streak.py"}" --cron',
            "/sc", "daily",
            "/st", time_str,
            "/f"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"\n[✓] Windows Task Scheduler berhasil dibuat pada jam {time_str}!")
        else:
            print(f"[!] Gagal membuat Windows Task: {res.stderr}")

    else:
        # Linux Crontab
        cron_job = f"{minute} {hour} * * * {bin_path} --cron >> {LOG_FILE} 2>&1"
        try:
            curr = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
            lines = [l for l in curr.splitlines() if "tiktok-streak" not in l]
            lines.append(cron_job)
            new_cron = "\n".join(lines) + "\n"
            subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)
            print(f"\n[✓] Crontab berhasil dipasang untuk jam {time_str}!")
        except Exception as e:
            print(f"[!] Gagal mendaftarkan crontab: {e}")


def remove_scheduler():
    if OS_NAME == "Darwin":
        plist_path = HOME_DIR / "Library/LaunchAgents/com.user.tiktokstreak.plist"
        if plist_path.exists():
            subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
            plist_path.unlink(missing_ok=True)
            print("[✓] macOS LaunchAgent berhasil dihapus.")
    elif OS_NAME == "Windows":
        subprocess.run(["schtasks", "/delete", "/tn", "TikTokStreakDaily", "/f"], capture_output=True)
        print("[✓] Windows Task Scheduler berhasil dihapus.")
    else:
        try:
            curr = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
            lines = [l for l in curr.splitlines() if "tiktok-streak" not in l]
            new_cron = "\n".join(lines) + "\n"
            subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)
            print("[✓] Crontab berhasil dihapus.")
        except Exception:
            pass


# ==============================================================================
# TikTok Browser Engine (Playwright)
# ==============================================================================

def check_login_status() -> bool:
    """Checks if valid auth session cookies exist in user data directory (instant SQLite check)."""
    if not PROFILE_DIR.exists():
        return False
    cookie_db = PROFILE_DIR / "Default" / "Cookies"
    if not cookie_db.exists():
        cookie_db = PROFILE_DIR / "Cookies"
    if not cookie_db.exists():
        return False
    try:
        import sqlite3
        conn = sqlite3.connect(f"file:{cookie_db}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM cookies WHERE host_key LIKE '%tiktok.com%' AND "
            "(name LIKE '%session%' OR name LIKE '%sid%' OR name = 'uid_tt' OR name = 'sessionid')"
        )
        rows = cursor.fetchall()
        conn.close()
        return len(rows) > 0
    except Exception:
        # Fallback to profile state check
        storage_state = list(PROFILE_DIR.glob("**/*Cookies*")) + list(PROFILE_DIR.glob("**/*storage*"))
        return len(storage_state) > 0


def launch_browser_context(p, headless: bool = True):
    """
    Launches Playwright persistent context with fallback to Google Chrome
    if the bundled Playwright chromium binary is missing or incompatible.
    """
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    opts = {
        "user_data_dir": str(PROFILE_DIR),
        "headless": headless,
        "viewport": {"width": 1280, "height": 800},
        "args": ["--disable-blink-features=AutomationControlled"]
    }
    try:
        return p.chromium.launch_persistent_context(**opts)
    except Exception as e:
        log_message(f"Chromium default launch gagal ({e}). Fallback ke Google Chrome lokal...")
        opts["channel"] = "chrome"
        return p.chromium.launch_persistent_context(**opts)


def interactive_login():
    """Opens a visible browser window for the user to log in."""
    print("\n" + "=" * 58)
    print("🔑 Login Akun TikTok (Interactive Browser)")
    print("=" * 58)
    print("1. Jendela browser akan terbuka secara otomatis.")
    print("2. Silakan login (bisa scan QR via aplikasi TikTok di HP atau email/password).")
    print("3. Setelah berhasil masuk ke Beranda TikTok, kembali ke sini.")
    print("=" * 58)
    input("\nTekan [ENTER] untuk membuka browser...")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[!] Modul 'playwright' belum terpasang. Jalankan install.sh terlebih dahulu.")
        return

    with sync_playwright() as p:
        context = launch_browser_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.tiktok.com/login", wait_until="networkidle")

        input("\n👉 Jika Anda sudah BERHASIL LOGIN di browser, tekan [ENTER] di terminal ini...")
        context.close()

    print("\n[✓] Sesi login berhasil disimpan di komputer!")


def scan_dm_contacts(verbose: bool = True) -> list:
    """Scans and updates contact list from TikTok Web DM with list scrolling."""
    if verbose:
        print("\n[*] Menghubungkan ke TikTok untuk memindai daftar kontak DM...")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[!] Modul 'playwright' belum terpasang.")
        return []

    cfg = load_config()
    detected_contacts = []

    with sync_playwright() as p:
        try:
            context = launch_browser_context(p, headless=True)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://www.tiktok.com/messages", wait_until="networkidle", timeout=60000)
            time.sleep(4)

            if "login" in page.url:
                if verbose:
                    print("[!] Sesi login kedaluwarsa. Silakan lakukan Login Akun terlebih dahulu.")
                context.close()
                return []

            for _ in range(8):
                items = page.locator('[data-e2e="dm-new-conversation-item"]')
                if items.count() == 0:
                    items = page.locator('div[data-e2e="chat-list-item"], li[class*="chat-item"]')
                count = items.count()

                for i in range(count):
                    it = items.nth(i)
                    nick_el = it.locator('[data-e2e="dm-new-conversation-nickname"]')
                    if nick_el.count() > 0:
                        name = nick_el.inner_text().strip()
                    else:
                        lines = [l.strip() for l in it.inner_text().splitlines() if l.strip()]
                        name = lines[0] if lines else ""

                    if name and name not in detected_contacts:
                        detected_contacts.append(name)

                page.mouse.wheel(0, 450)
                time.sleep(0.3)

            context.close()
        except Exception as e:
            if verbose:
                print(f"[x] Gagal memindai kontak: {e}")

    if detected_contacts:
        cfg["contacts"] = detected_contacts
        save_config(cfg)
        if verbose:
            print(f"\n[✓] Berhasil menemukan {len(detected_contacts)} kontak di DM TikTok:")
            print("-" * 50)
            for idx, name in enumerate(detected_contacts, 1):
                print(f" {idx:2d}. {name}")
            print("-" * 50)
    else:
        if verbose:
            print("[-] Tidak ada percakapan aktif yang terdeteksi.")

    return detected_contacts


def send_message_in_chat(page, message: str, expected_target: str = None) -> bool:
    try:
        # If expected_target is provided, verify active chat header before typing
        if expected_target:
            header_nick = page.locator('[data-e2e="dm-new-chat-nickname"]')
            if header_nick.count() > 0:
                active_name = header_nick.first.inner_text().strip().lower()
                target_clean = expected_target.strip().lower()
                if active_name != target_clean:
                    log_message(f"VERIFIKASI GAGAL: Chat aktif '{active_name}' != target '{target_clean}'. Batal kirim demi keamanan.")
                    return False

        chatbox = page.locator('[data-e2e="dm-new-chatbox"]')
        if chatbox.count() > 0:
            box = chatbox.locator('div[contenteditable="true"]').first
        else:
            box = page.locator('div[contenteditable="true"]').first

        box.wait_for(state="visible", timeout=8000)
        box.click()
        time.sleep(0.5)
        # Use insert_text for smooth Draft.js emoji & unicode typing
        page.keyboard.insert_text(message)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(2)
        return True
    except Exception as e:
        log_message(f"Gagal mengirim pesan di chat: {e}")
        return False


def reset_conversation_list_scroll(page):
    """Resets the scroll position of the conversation sidebar to the top."""
    try:
        first_item = page.locator('[data-e2e="dm-new-conversation-item"]').first
        if first_item.count() > 0:
            parent = first_item.locator('xpath=../..')
            parent.evaluate('e => { e.scrollTop = 0; }')
            time.sleep(0.4)
    except Exception:
        pass


def select_and_open_chat(page, target_name: str, max_scroll_attempts: int = 15) -> bool:
    """
    Reliably selects and opens a DM conversation by scrolling the sidebar,
    clicking the nickname element directly, and verifying that the chat is active.
    """
    target_clean = target_name.strip().lower()

    # Search in two passes: 1) from current position down; 2) from top down if needed
    for phase in range(2):
        for scroll_idx in range(max_scroll_attempts):
            items = page.locator('[data-e2e="dm-new-conversation-item"]')
            count = items.count()

            for i in range(count):
                item = items.nth(i)
                nick_el = item.locator('[data-e2e="dm-new-conversation-nickname"]')
                if nick_el.count() == 0:
                    continue

                current_nick = nick_el.inner_text().strip()
                if current_nick.lower() == target_clean:
                    nick_el.scroll_into_view_if_needed()
                    time.sleep(0.3)

                    # Click nickname directly to trigger React router/state change
                    nick_el.click()
                    time.sleep(1.0)

                    # Verify active selection
                    is_selected = item.get_attribute("aria-selected") == "true"
                    chat_header_nick = page.locator('[data-e2e="dm-new-chat-nickname"]')
                    header_matches = False
                    if chat_header_nick.count() > 0:
                        header_text = chat_header_nick.first.inner_text().strip().lower()
                        if header_text == target_clean:
                            header_matches = True

                    if is_selected or header_matches:
                        return True

                    # Fallback click on outer item
                    item.click()
                    time.sleep(1.0)
                    if item.get_attribute("aria-selected") == "true":
                        return True

            # Scroll down to reveal more virtualized conversation items
            page.mouse.wheel(0, 400)
            time.sleep(0.4)

        if phase == 0:
            reset_conversation_list_scroll(page)
            time.sleep(0.5)

    return False


def run_send_streak(force: bool = False, verbose: bool = True) -> dict:
    """Executes streak sending logic."""
    state = load_state()
    today_str = str(date.today())

    if not force and state.get("last_success_date") == today_str:
        msg = f"Streak untuk hari ini ({today_str}) sudah berhasil dikirim sebelumnya. Lewati."
        if verbose:
            print(f"[*] {msg}")
        return {"success": True, "message": msg, "sent": state.get("sent_count", 0)}

    cfg = load_config()
    mode = cfg.get("mode", "all")
    default_msg = cfg.get("default_message", "🔥")

    log_message("Memulai proses pengiriman streak harian...")

    if not wait_for_internet(timeout=60, check_interval=3, verbose=verbose):
        err = "Koneksi internet tidak tersedia saat pengiriman streak."
        log_message(err)
        return {"success": False, "message": err, "sent": 0, "failed": 1}

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        err = "Modul 'playwright' belum terpasang."
        log_message(err)
        return {"success": False, "message": err}

    success_list = []
    fail_list = []

    with sync_playwright() as p:
        try:
            context = launch_browser_context(p, headless=cfg.get("headless", True))
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://www.tiktok.com/messages", wait_until="networkidle", timeout=60000)
            time.sleep(5)

            if "login" in page.url:
                raise Exception("Sesi login berakhir. Perlu login ulang lewat menu Login.")

            # MODE A: SELECT ALL
            if mode == "all":
                select_all_cfg = cfg.get("select_all", {})
                msg_to_send = select_all_cfg.get("message", default_msg)
                exclude_list = [x.lower() for x in select_all_cfg.get("exclude", [])]

                chat_items = page.locator('[data-e2e="dm-new-conversation-item"]')
                if chat_items.count() == 0:
                    chat_items = page.locator('div[data-e2e="chat-list-item"], li[class*="chat-item"]')

                total = chat_items.count()
                if verbose:
                    print(f"[*] Mode SELECT ALL: Memeriksa {total} kontak chat DM...")

                for i in range(total):
                    item = chat_items.nth(i)
                    nick_el = item.locator('[data-e2e="dm-new-conversation-nickname"]')
                    if nick_el.count() > 0:
                        name = nick_el.inner_text().strip()
                    else:
                        name = item.inner_text().split("\n")[0].strip()

                    if not name or name.lower() in exclude_list:
                        if verbose and name:
                            print(f"  [-] Melewati {name} (ada di daftar blacklist)")
                        continue

                    final_msg = resolve_message_for_contact(name, group_msg=msg_to_send)
                    if verbose:
                        print(f"  [>] Mengirim streak ke {name} ('{final_msg}')...")

                    if nick_el.count() > 0:
                        nick_el.click()
                    else:
                        item.click()
                    time.sleep(get_click_delay())

                    if send_message_in_chat(page, final_msg, expected_target=name):
                        success_list.append(name)
                        log_activity("JOB", f"Streak terkirim ke '{name}' -> '{final_msg}'")
                        if verbose:
                            print(f"      [✓] Terkirim!")
                    else:
                        fail_list.append(name)
                        log_activity("ERROR", f"Gagal kirim pesan ke '{name}'")
                        if verbose:
                            print(f"      [x] Gagal kirim pesan.")
                    time.sleep(get_message_delay())

            # MODE B: GROUPS / LABELING
            else:
                groups = cfg.get("groups", {})
                recipients = {}
                for g_name, g_info in groups.items():
                    if not g_info.get("enabled", True):
                        continue
                    g_msg = g_info.get("message", default_msg)
                    for member in g_info.get("members", []):
                        recipients[member] = g_msg

                if not recipients:
                    raise Exception("Mode Groups aktif, tetapi tidak ada anggota di dalam grup.")

                if verbose:
                    print(f"[*] Mode GROUPS: Memproses {len(recipients)} orang target...")

                for target_name, custom_msg in recipients.items():
                    final_msg = resolve_message_for_contact(target_name, group_msg=custom_msg)
                    if verbose:
                        print(f"  [>] Mencari kontak '{target_name}' (Pesan: '{final_msg}')...")

                    found = select_and_open_chat(page, target_name)
                    if found:
                        time.sleep(get_click_delay())
                        if send_message_in_chat(page, final_msg, expected_target=target_name):
                            success_list.append(f"{target_name} ('{final_msg}')")
                            log_activity("JOB", f"Streak terkirim ke '{target_name}' -> '{final_msg}'")
                            if verbose:
                                print(f"      [✓] Terkirim ({final_msg})!")
                        else:
                            fail_list.append(target_name)
                            log_activity("ERROR", f"Gagal verifikasi/kirim pesan ke '{target_name}'")
                            if verbose:
                                print(f"      [x] Gagal verifikasi atau kirim pesan.")
                    else:
                        fail_list.append(f"{target_name} (Tidak ditemukan / gagal buka chat)")
                        log_activity("ERROR", f"Kontak '{target_name}' tidak ditemukan atau gagal dibuka di chat DM")
                        if verbose:
                            print(f"      [x] Kontak '{target_name}' tidak ditemukan / gagal buka chat.")
                    time.sleep(get_message_delay())

            context.close()
        except Exception as e:
            fail_list.append(f"System Error: {str(e)}")
            log_message(f"Error during streak run: {e}")

    overall_success = len(success_list) > 0 and len(fail_list) == 0
    summary = f"Terkirim: {len(success_list)}, Gagal: {len(fail_list)}"
    save_state(overall_success, len(success_list), len(fail_list), summary)

    # Format notification message
    report = f"📊 *Laporan Pengiriman Streak TikTok:*\n"
    if success_list:
        report += f"\n✅ *Berhasil ({len(success_list)}):*\n- " + "\n- ".join(success_list)
    if fail_list:
        report += f"\n\n❌ *Gagal/Lewat ({len(fail_list)}):*\n- " + "\n- ".join(fail_list)

    send_notification(
        title="TikTok Streak Saver",
        text=report,
        success=overall_success
    )

    log_message(f"Selesai. {summary}")
    return {
        "success": overall_success,
        "message": summary,
        "sent": len(success_list),
        "failed": len(fail_list)
    }


# ==============================================================================
# 100% Interactive Terminal Hub (TUI - Powered by Questionary)
# ==============================================================================

import questionary
from questionary import Choice, Separator


def print_dashboard():
    cfg = load_config()
    state = load_state()
    today_str = str(date.today())
    has_run_today = state.get("last_success_date") == today_str
    is_sched_active, sched_desc = get_scheduler_status()
    is_logged_in = check_login_status()

    if not is_logged_in:
        print("╭" + "─" * 56 + "╮")
        print("│  ⚠️  STATUS AKUN: BELUM LOGIN / SESI TIKTOK KOSONG      │")
        print("│  Bot tidak dapat mengirim streak sebelum Anda login!   │")
        print("│  👉 Pilih opsi [1] di menu untuk login via browser.    │")
        print("╰" + "─" * 56 + "╯\n")

    mode_name = "🌟 Select All" if cfg.get("mode") == "all" else "👥 Groups / Labeling"
    msg_cfg = cfg.get("messages", {})
    msg_mode = "🎲 Pool Acak" if msg_cfg.get("mode", "pool") == "pool" else f"🔒 Fixed ('{cfg.get('default_message', '🔥')}')"
    pace_name = cfg.get("safety", {}).get("pace", "normal").capitalize()
    retention = cfg.get("logging", {}).get("retention_days", 3)

    print("\n" + "=" * 58)
    print("⚡  TikTok Streak Auto-Saver & Helper Hub")
    print("=" * 58)
    print(f"👤 Akun Sesi:      {'🟢 VALID (Aktif)' if is_logged_in else '🔴 Belum Login'}")
    if has_run_today:
        print(f"📅 Status Hari Ini: ✅ Streak Sudah Terkirim ({state.get('sent_count', 0)} kontak)")
    else:
        last_attempt = state.get("last_attempt", "")
        if last_attempt.startswith(today_str) and state.get("failed_count", 0) > 0:
            print(f"📅 Status Hari Ini: ⚠️  Belum Terkirim ({state.get('last_summary', '')})")
            print(f"                   ℹ️  Gagal koneksi saat bangun tidur (Wi-Fi belum tersambung).")
        else:
            print("📅 Status Hari Ini: ⌛ Belum Terkirim Hari Ini")
    print(f"👥 Mode Penerima:   {mode_name}")
    print(f"💬 Konfigurasi:     {msg_mode} | ⚡ Pace: {pace_name}")
    print(f"⏰ Jadwal Auto:     {'🟢' if is_sched_active else '⚪'} {sched_desc}")
    print(f"📁 Log History:     Tersimpan {retention} hari terakhir (Auto-prune)")
    print("=" * 58 + "\n")


def interactive_manage_contacts():
    cfg = load_config()
    contacts = cfg.get("contacts", [])
    if not contacts:
        print("\n[!] Belum ada kontak yang tersimpan. Silakan pilih 'Pindai Kontak' di Menu Utama terlebih dahulu.\n")
        questionary.press_any_key_to_continue("Tekan tombol apa saja untuk kembali...").ask()
        return

    groups = cfg.get("groups", {})
    choices = []
    for c in contacts:
        assigned = [g for g, d in groups.items() if c in d.get("members", [])]
        status_str = f"Grup: {', '.join(assigned)}" if assigned else "Belum ada grup"
        is_checked = len(assigned) > 0
        choices.append(Choice(title=f"{c:<22} ({status_str})", value=c, checked=is_checked))

    print("\n💡 Petunjuk:")
    print(" • [↑ / ↓] Panah keyboard untuk navigasi")
    print(" • [Spasi] untuk centang / batalkan centang")
    print(" • [a] untuk Pilih Semua (Select All) / Batal Semua")
    print(" • [Enter] untuk konfirmasi pilihan Anda\n")

    selected_contacts = questionary.checkbox(
        "Pilih kontak-kontak yang ingin diatur:",
        choices=choices,
        instruction="(Spasi: pilih, a: select all, Enter: konfirmasi)"
    ).ask()

    if not selected_contacts:
        print("\n[*] Tidak ada kontak yang dipilih. Dibatalkan.\n")
        return

    print(f"\n[✓] {len(selected_contacts)} Kontak Terpilih:")
    for sc in selected_contacts[:6]:
        print(f"  • {sc}")
    if len(selected_contacts) > 6:
        print(f"  ... dan {len(selected_contacts) - 6} kontak lainnya.")

    grp_names = list(groups.keys())
    action_choices = [
        Choice(f"📁 Masukkan ke grup '{g_n}'", value=g_n) for g_n in grp_names
    ] + [
        Separator(),
        Choice("➕ Buat Grup Baru", value="__CREATE_GROUP__"),
        Choice("🗑️  Hapus dari Semua Grup (Reset)", value="__RESET__"),
        Choice("🔙 Batal", value="__CANCEL__")
    ]

    chosen_action = questionary.select(
        f"\nPilih tindakan untuk {len(selected_contacts)} kontak ini:",
        choices=action_choices
    ).ask()

    if chosen_action in ("__CANCEL__", None):
        print("[*] Dibatalkan.\n")
        return

    if chosen_action == "__CREATE_GROUP__":
        new_g = questionary.text("Masukkan nama grup baru:").ask()
        if not new_g or not new_g.strip():
            print("[!] Nama grup tidak boleh kosong.\n")
            return
        new_g = new_g.strip()
        new_msg = questionary.text(f"Pesan streak untuk grup '{new_g}':", default="🔥").ask() or "🔥"
        groups[new_g] = {"enabled": True, "message": new_msg, "members": []}
        chosen_action = new_g

    if chosen_action == "__RESET__":
        for g_n in groups:
            groups[g_n]["members"] = [m for m in groups[g_n].get("members", []) if m not in selected_contacts]
        print(f"\n[✓] {len(selected_contacts)} kontak berhasil dihapus dari semua grup.\n")
    else:
        target_members = groups[chosen_action].setdefault("members", [])
        for sc in selected_contacts:
            if sc not in target_members:
                target_members.append(sc)
        print(f"\n[✓] Berhasil memasukkan {len(selected_contacts)} kontak ke grup '{chosen_action}'!\n")

    save_config(cfg)
    questionary.press_any_key_to_continue("Tekan tombol apa saja untuk melanjutkan...").ask()


def menu_manage_groups():
    while True:
        cfg = load_config()
        groups = cfg.get("groups", {})

        print("\n" + "-" * 55)
        print("🏷️  DAFTAR GRUP & PESAN KHUSUS:")
        print("-" * 55)
        for g_name, g_info in groups.items():
            members_str = ", ".join(g_info.get("members", [])) or "Belum ada anggota"
            print(f" • {g_name} ({len(g_info.get('members', []))} anggota):")
            print(f"   Pesan : \"{g_info.get('message')}\"")
            print(f"   Anggota: {members_str}")
        print("-" * 55 + "\n")

        choices = [
            Choice("➕ Tambah Grup Baru", value="add"),
            Choice("✏️  Ubah Pesan Grup", value="edit_msg"),
            Choice("🗑️  Hapus Grup", value="delete"),
            Separator(),
            Choice("🔙 Kembali", value="back")
        ]

        action = questionary.select("Kelola Grup:", choices=choices).ask()
        if action == "back" or not action:
            break

        if action == "add":
            new_g = questionary.text("Nama grup baru:").ask()
            if new_g and new_g.strip():
                new_g = new_g.strip()
                new_msg = questionary.text(f"Pesan untuk grup '{new_g}':", default="🔥").ask() or "🔥"
                groups[new_g] = {"enabled": True, "message": new_msg, "members": []}
                save_config(cfg)
                print(f"[✓] Grup '{new_g}' berhasil dibuat!\n")

        elif action == "edit_msg":
            g_names = list(groups.keys())
            if not g_names:
                print("[!] Tidak ada grup yang tersedia.")
                continue
            target_g = questionary.select("Pilih grup yang ingin diubah pesannya:", choices=g_names).ask()
            if target_g:
                cur_msg = groups[target_g].get("message", "🔥")
                new_msg = questionary.text(f"Pesan baru untuk '{target_g}':", default=cur_msg).ask()
                if new_msg:
                    groups[target_g]["message"] = new_msg
                    save_config(cfg)
                    print(f"[✓] Pesan untuk '{target_g}' berhasil diperbarui!\n")

        elif action == "delete":
            g_names = list(groups.keys())
            if not g_names:
                print("[!] Tidak ada grup yang tersedia.")
                continue
            target_g = questionary.select("Pilih grup yang ingin dihapus:", choices=g_names + ["🔙 Batal"]).ask()
            if target_g and target_g != "🔙 Batal":
                del groups[target_g]
                save_config(cfg)
                print(f"[✓] Grup '{target_g}' telah dihapus.\n")


def menu_manage_exclude():
    while True:
        cfg = load_config()
        excludes = cfg.get("select_all", {}).get("exclude", [])

        print("\n" + "-" * 55)
        print("🚫 DAFTAR BLACKLIST / EXCLUDE (Dilewati di Mode All):")
        print("-" * 55)
        for idx, ex in enumerate(excludes, 1):
            print(f" {idx:2d}. {ex}")
        print("-" * 55 + "\n")

        choices = [
            Choice("➕ Tambah Akun ke Blacklist", value="add"),
            Choice("🗑️  Hapus Akun dari Blacklist (Checklist)", value="remove"),
            Separator(),
            Choice("🔙 Kembali", value="back")
        ]

        action = questionary.select("Kelola Blacklist:", choices=choices).ask()
        if action == "back" or not action:
            break

        if action == "add":
            new_acc = questionary.text("Nama akun yang ingin dilewati/blacklist:").ask()
            if new_acc and new_acc.strip():
                excludes.append(new_acc.strip())
                save_config(cfg)
                print(f"[✓] '{new_acc.strip()}' ditambahkan ke blacklist.\n")

        elif action == "remove":
            if not excludes:
                print("[!] Daftar blacklist masih kosong.")
                continue
            to_remove = questionary.checkbox(
                "Pilih akun yang ingin dihapus dari blacklist:",
                choices=[Choice(title=e, value=e) for e in excludes]
            ).ask()
            if to_remove:
                cfg["select_all"]["exclude"] = [e for e in excludes if e not in to_remove]
                save_config(cfg)
                print(f"[✓] {len(to_remove)} akun berhasil dihapus dari blacklist.\n")


def menu_manage_recipients():
    while True:
        cfg = load_config()
        mode = cfg.get("mode", "all")
        mode_label = "Select All (Semua Kontak)" if mode == "all" else "Groups / Labeling"

        choices = [
            Choice(f"🔄 Ganti Mode Pengiriman (Saat ini: {mode_label})", value="toggle_mode"),
            Choice("📋 Checklist Kontak & Tetapkan Grup (Interactive Multi-select)", value="checklist"),
            Choice("🏷️  Kelola Label Grup", value="groups"),
            Choice("💬 Konfigurasi Pesan & Variasi (Default, Pool Acak & Khusus)", value="messages"),
            Choice("🚫 Kelola Daftar Pengecualian (Blacklist / Exclude)", value="exclude"),
            Choice("👁️  Pratinjau Pesan yang Akan Dikirim (Preview)", value="preview"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select(
            f"👥 Kelola Penerima & Pesan [Mode Aktif: {mode.upper()}]:",
            choices=choices
        ).ask()

        if action == "back" or not action:
            break

        elif action == "toggle_mode":
            cfg["mode"] = "groups" if mode == "all" else "all"
            save_config(cfg)
            log_activity("CONFIG", f"Mode penerima diubah ke: {cfg['mode'].upper()}")
            print(f"\n[✓] Mode pengiriman diubah ke: {cfg['mode'].upper()}\n")

        elif action == "checklist":
            interactive_manage_contacts()

        elif action == "groups":
            menu_manage_groups()

        elif action == "messages":
            menu_manage_messages()

        elif action == "exclude":
            menu_manage_exclude()

        elif action == "preview":
            show_message_preview()


def menu_manage_scheduler():
    while True:
        is_active, desc = get_scheduler_status()
        cfg = load_config()
        sched = cfg.get("schedule", {"hour": 9, "minute": 0})
        time_str = f"{sched['hour']:02d}:{sched['minute']:02d}"

        choices = [
            Choice(f"⏰ Pasang / Aktifkan Jadwal Harian (Jam {time_str} + Auto Catch-up)", value="install"),
            Choice(f"🕒 Ubah Jam Eksekusi (Saat ini: Jam {time_str})", value="change_time"),
            Choice("🗑️  Matikan / Hapus Jadwal", value="remove"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select(
            f"⏰ Pengatur Jadwal Harian [{OS_NAME}] (Status: {'🟢' if is_active else '⚪'} {desc}):",
            choices=choices
        ).ask()

        if action == "back" or not action:
            break

        elif action == "install":
            install_scheduler()
            questionary.press_any_key_to_continue().ask()

        elif action == "change_time":
            new_time = questionary.text(
                "Masukkan jam baru (Format JJ:MM, contoh: 08:30):",
                default=time_str
            ).ask()
            if new_time and ":" in new_time:
                try:
                    h, m = map(int, new_time.split(":", 1))
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        cfg["schedule"] = {"hour": h, "minute": m}
                        save_config(cfg)
                        print(f"\n[✓] Waktu jadwal diubah ke {h:02d}:{m:02d}.")
                        if is_active:
                            install_scheduler()
                    else:
                        print("\n[!] Jam atau menit tidak valid.")
                except ValueError:
                    print("\n[!] Format waktu salah.")
            questionary.press_any_key_to_continue().ask()

        elif action == "remove":
            remove_scheduler()
            questionary.press_any_key_to_continue().ask()


def show_telegram_guide():
    print("\n" + "=" * 62)
    print("📖 Panduan Singkat Integrasi Telegram (Cuma 1 Menit):")
    print("=" * 62)
    print("1. Buka aplikasi Telegram di HP / Laptop kamu.")
    print("2. Cari @BotFather (bot resmi centang biru dari Telegram).")
    print("3. Kirim perintah /newbot dan ikuti instruksi:")
    print("   -> Masukkan nama tampilan bot (misal: 'Streak Helper')")
    print("   -> Masukkan username bot (harus berakhiran 'bot', misal: 'sam_streak_bot')")
    print("   -> BotFather akan memberikan HTTP API Token.")
    print("4. Ambil Chat ID pribadi kamu:")
    print("   -> Cari @userinfobot di Telegram, klik Start.")
    print("   -> Bot tersebut langsung membalas nomor 'Id: 123456789' (Chat ID).")
    print("5. PENTING: Buka bot buatanmu (dari langkah 3) lalu klik tombol START!")
    print("   (Bot Telegram tidak bisa kirim pesan sebelum kamu klik Start).")
    print("=" * 62 + "\n")
    questionary.press_any_key_to_continue().ask()


def menu_telegram_settings():
    while True:
        cfg = load_config()
        tg = cfg.setdefault("notifications", {}).setdefault("telegram", {})
        enabled = tg.get("enabled", False)
        token = tg.get("bot_token", "")
        chat_id = tg.get("chat_id", "")
        masked_token = (token[:6] + "..." + token[-4:]) if len(token) > 10 else (token or "(Belum diisi)")

        print("\n" + "=" * 58)
        print("📱 Pengaturan Telegram Bot:")
        print(f"   Status      : {'🟢 AKTIF' if enabled else '⚪ NONAKTIF'}")
        print(f"   Bot Token   : {masked_token}")
        print(f"   Chat ID     : {chat_id or '(Belum diisi)'}")
        print("=" * 58 + "\n")

        choices = [
            Choice(f"🔄 {'Nonaktifkan' if enabled else 'Aktifkan'} Notifikasi Telegram", value="toggle"),
            Choice("✏️  Atur / Ubah Bot Token & Chat ID", value="edit"),
            Choice("🔔 Tes Kirim Notifikasi ke Telegram Sekarang", value="test"),
            Choice("📖 Panduan Cara Buat Bot & Dapatkan Chat ID", value="guide"),
            Separator(),
            Choice("🔙 Kembali", value="back")
        ]

        action = questionary.select("Pilih Aksi Telegram:", choices=choices).ask()
        if action == "back" or not action:
            break

        elif action == "toggle":
            tg["enabled"] = not enabled
            if tg["enabled"] and (not token or not chat_id):
                print("\n[*] Lengkapi Bot Token dan Chat ID terlebih dahulu:")
                new_token = questionary.text("Masukkan Telegram Bot Token:", default=token).ask()
                new_id = questionary.text("Masukkan Telegram Chat ID:", default=chat_id).ask()
                if new_token:
                    tg["bot_token"] = new_token.strip()
                if new_id:
                    tg["chat_id"] = new_id.strip()
            save_config(cfg)
            log_activity("CONFIG", f"Telegram Bot status diubah ke: {'AKTIF' if tg['enabled'] else 'NONAKTIF'}")
            print(f"\n[✓] Notifikasi Telegram: {'🟢 AKTIF' if tg['enabled'] else '⚪ NONAKTIF'}\n")

        elif action == "edit":
            new_token = questionary.text("Masukkan Telegram Bot Token:", default=token).ask()
            new_id = questionary.text("Masukkan Telegram Chat ID:", default=chat_id).ask()
            if new_token is not None:
                tg["bot_token"] = new_token.strip()
            if new_id is not None:
                tg["chat_id"] = new_id.strip()
            if tg.get("bot_token") and tg.get("chat_id"):
                tg["enabled"] = True
            save_config(cfg)
            log_activity("CONFIG", "Kredensial Telegram Bot diperbarui.")
            print("\n[✓] Konfigurasi Telegram berhasil disimpan!\n")

        elif action == "test":
            if not tg.get("bot_token") or not tg.get("chat_id"):
                print("\n[!] Lengkapi Bot Token dan Chat ID terlebih dahulu di opsi [Edit].\n")
            else:
                print("\n[*] Menghubungi Telegram API...")
                ok, msg = send_telegram_notification(
                    tg["bot_token"],
                    tg["chat_id"],
                    "Tes Notifikasi TikTok Streak",
                    "Halo! Bot TikTok Streak kamu berhasil terhubung ke Telegram 🎉\nNotifikasi streak harian akan masuk ke sini.",
                    success=True
                )
                if ok:
                    print(f"[✓] {msg}\n")
                else:
                    print(f"[!] {msg}")
                    if "chat not found" in msg.lower():
                        print("👉 Tips: Pastikan kamu sudah mencari username bot kamu di Telegram dan klik tombol 'START'!\n")
            questionary.press_any_key_to_continue().ask()

        elif action == "guide":
            show_telegram_guide()


def menu_discord_settings():
    while True:
        cfg = load_config()
        dc = cfg.setdefault("notifications", {}).setdefault("discord", {})
        enabled = dc.get("enabled", False)
        webhook = dc.get("webhook_url", "")
        masked_url = (webhook[:30] + "..." + webhook[-6:]) if len(webhook) > 40 else (webhook or "(Belum diisi)")

        print("\n" + "=" * 58)
        print("💬 Pengaturan Discord Webhook:")
        print(f"   Status      : {'🟢 AKTIF' if enabled else '⚪ NONAKTIF'}")
        print(f"   Webhook URL : {masked_url}")
        print("=" * 58 + "\n")

        choices = [
            Choice(f"🔄 {'Nonaktifkan' if enabled else 'Aktifkan'} Discord Webhook", value="toggle"),
            Choice("✏️  Atur / Ubah Discord Webhook URL", value="edit"),
            Choice("🔔 Tes Kirim Notifikasi ke Discord Sekarang", value="test"),
            Separator(),
            Choice("🔙 Kembali", value="back")
        ]

        action = questionary.select("Pilih Aksi Discord:", choices=choices).ask()
        if action == "back" or not action:
            break

        elif action == "toggle":
            dc["enabled"] = not enabled
            if dc["enabled"] and not webhook:
                new_url = questionary.text("Masukkan Discord Webhook URL:").ask()
                if new_url:
                    dc["webhook_url"] = new_url.strip()
            save_config(cfg)
            log_activity("CONFIG", f"Discord Webhook diubah ke: {'AKTIF' if dc['enabled'] else 'NONAKTIF'}")
            print(f"\n[✓] Discord Webhook: {'🟢 AKTIF' if dc['enabled'] else '⚪ NONAKTIF'}\n")

        elif action == "edit":
            new_url = questionary.text("Masukkan Discord Webhook URL:", default=webhook).ask()
            if new_url is not None:
                dc["webhook_url"] = new_url.strip()
            if dc.get("webhook_url"):
                dc["enabled"] = True
            save_config(cfg)
            log_activity("CONFIG", "Discord Webhook URL diperbarui.")
            print("\n[✓] Discord Webhook berhasil disimpan!\n")

        elif action == "test":
            if not dc.get("webhook_url"):
                print("\n[!] Masukkan Webhook URL terlebih dahulu.\n")
            else:
                print("\n[*] Menghubungi Discord Webhook...")
                ok, msg = send_discord_notification(
                    dc["webhook_url"],
                    "Tes Notifikasi TikTok Streak",
                    "Halo! Webhook Discord kamu berhasil terhubung ke TikTok Streak 🎉",
                    success=True
                )
                if ok:
                    print(f"[✓] {msg}\n")
                else:
                    print(f"[!] {msg}\n")
            questionary.press_any_key_to_continue().ask()


def menu_notifications():
    while True:
        cfg = load_config()
        notifs = cfg.get("notifications", {})
        tg = notifs.get("telegram", {})
        dc = notifs.get("discord", {})

        choices = [
            Choice(f"📱 Telegram Bot: {'🟢 AKTIF' if tg.get('enabled') else '⚪ Nonaktif'}", value="telegram"),
            Choice(f"💬 Discord Webhook: {'🟢 AKTIF' if dc.get('enabled') else '⚪ Nonaktif'}", value="discord"),
            Choice("🔔 Tes Semua Notifikasi Aktif", value="test_all"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select("🔔 Pengaturan Notifikasi ke HP:", choices=choices).ask()
        if action == "back" or not action:
            break

        elif action == "telegram":
            menu_telegram_settings()

        elif action == "discord":
            menu_discord_settings()

        elif action == "test_all":
            print("\n[*] Mengirim notifikasi tes ke semua channel aktif...")
            send_notification("Tes Notifikasi TikTok Streak", "Halo! Notifikasi pengingat streak berhasil terhubung.", success=True)
            print("[✓] Notifikasi tes selesai dikirim!\n")
            questionary.press_any_key_to_continue().ask()


def menu_pool_editor():
    PRESET_TEMPLATES = [
        "🔥",
        "Streak 🔥⚡",
        "Selamat {time_greeting} {first_name}! Streak 🔥",
        "Semangat hari {day} ya {first_name}! 🔥",
        "Streak hari ini {first_name} 🔥✨",
        "Pagi {first_name}! Jangan lupa streak yaa 🔥",
        "Streak {date} 🔥💪"
    ]

    while True:
        cfg = load_config()
        pool = cfg.get("messages", {}).get("pool", [])

        print("\n" + "=" * 58)
        print("📝 Daftar Variasi Pesan Acak (Pool):")
        print("=" * 58)
        if not pool:
            print("  (Daftar pesan masih kosong)")
        else:
            for idx, p in enumerate(pool, 1):
                print(f" {idx:2d}. {p}")
        print("=" * 58 + "\n")

        choices = [
            Choice("➕ Tambah Variasi Pesan Baru", value="add"),
            Choice("📋 Tambah dari Template Preset Populer", value="preset"),
            Choice("✏️  Edit Pesan yang Ada", value="edit"),
            Choice("🗑️  Hapus Pesan dari Pool", value="remove"),
            Separator(),
            Choice("🔙 Selesai / Kembali", value="back")
        ]

        act = questionary.select("Kelola Pool Pesan:", choices=choices).ask()
        if act == "back" or not act:
            break

        if act == "add":
            print("\n💡 Variabel yang didukung:")
            print("  {name}          = Nama lengkap kontak")
            print("  {first_name}    = Nama depan kontak")
            print("  {time_greeting} = Pagi / Siang / Sore / Malam")
            print("  {day}           = Hari (Senin, Selasa, dll)")
            print("  {date}          = Tanggal (contoh: 10 Nov)\n")
            new_text = questionary.text("Tulis template pesan baru:").ask()
            if new_text and new_text.strip():
                pool.append(new_text.strip())
                cfg["messages"]["pool"] = pool
                save_config(cfg)
                log_activity("CONFIG", f"Variasi pesan baru ditambahkan ke pool: '{new_text.strip()}'")
                print(f"[✓] Pesan berhasil ditambahkan ke pool!\n")

        elif act == "preset":
            selected_presets = questionary.checkbox(
                "Pilih template yang ingin dimasukkan ke pool:",
                choices=[Choice(title=p, value=p, checked=(p in pool)) for p in PRESET_TEMPLATES]
            ).ask()
            if selected_presets is not None:
                for sp in selected_presets:
                    if sp not in pool:
                        pool.append(sp)
                cfg["messages"]["pool"] = pool
                save_config(cfg)
                log_activity("CONFIG", f"Pool diperbarui dengan template preset ({len(pool)} pesan)")
                print(f"[✓] Pool berhasil diperbarui ({len(pool)} variasi aktif).\n")

        elif act == "edit":
            if not pool:
                print("[!] Belum ada pesan di dalam pool.\n")
                continue
            item_choices = [Choice(f"{i}. {p}", value=i-1) for i, p in enumerate(pool, 1)]
            item_choices.append(Separator())
            item_choices.append(Choice("🔙 Batal", value="cancel"))
            chosen = questionary.select("Pilih pesan yang ingin diedit:", choices=item_choices).ask()
            if chosen != "cancel" and chosen is not None:
                old_val = pool[chosen]
                new_val = questionary.text("Edit template pesan:", default=old_val).ask()
                if new_val and new_val.strip():
                    pool[chosen] = new_val.strip()
                    cfg["messages"]["pool"] = pool
                    save_config(cfg)
                    log_activity("CONFIG", f"Pesan pool diedit dari '{old_val}' -> '{new_val.strip()}'")
                    print(f"[✓] Pesan nomor {chosen+1} berhasil diperbarui!\n")

        elif act == "remove":
            if not pool:
                print("[!] Belum ada pesan di dalam pool.\n")
                continue
            item_choices = [Choice(f"{i}. {p}", value=p) for i, p in enumerate(pool, 1)]
            to_remove = questionary.checkbox("Pilih pesan yang ingin dihapus:", choices=item_choices).ask()
            if to_remove:
                pool = [p for p in pool if p not in to_remove]
                cfg["messages"]["pool"] = pool
                save_config(cfg)
                log_activity("CONFIG", f"Dihapus {len(to_remove)} pesan dari pool")
                print(f"[✓] {len(to_remove)} pesan berhasil dihapus dari pool.\n")


def menu_contact_overrides():
    while True:
        cfg = load_config()
        contacts = cfg.get("contacts", [])
        overrides = cfg.get("messages", {}).get("overrides", {})

        print("\n" + "=" * 58)
        print("👤 Daftar Pesan Khusus per Kontak:")
        print("=" * 58)
        if not overrides:
            print("  (Belum ada pesan khusus. Semua kontak memakai template default/pool)")
        else:
            for c_name, custom_msg in overrides.items():
                print(f"  • {c_name:<20} -> '{custom_msg}'")
        print("=" * 58 + "\n")

        choices = [
            Choice("➕ Tetapkan Pesan Khusus untuk Kontak", value="add"),
            Choice("🗑️  Hapus Pesan Khusus (Kembalikan ke Default)", value="remove"),
            Separator(),
            Choice("🔙 Selesai / Kembali", value="back")
        ]

        act = questionary.select("Kelola Pesan Khusus Kontak:", choices=choices).ask()
        if act == "back" or not act:
            break

        if act == "add":
            if not contacts:
                print("[!] Belum ada kontak terdeteksi. Silakan Pindai Kontak terlebih dahulu.\n")
                continue
            contact_choices = [Choice(c, value=c) for c in contacts]
            contact_choices.append(Separator())
            contact_choices.append(Choice("🔙 Batal", value="cancel"))
            chosen_contact = questionary.select("Pilih kontak:", choices=contact_choices).ask()
            if chosen_contact and chosen_contact != "cancel":
                current_custom = overrides.get(chosen_contact, "")
                msg_input = questionary.text(
                    f"Tulis pesan khusus untuk '{chosen_contact}':",
                    default=current_custom or "Semangat hari ini {first_name}! Streak 🔥"
                ).ask()
                if msg_input and msg_input.strip():
                    overrides[chosen_contact] = msg_input.strip()
                    cfg["messages"]["overrides"] = overrides
                    save_config(cfg)
                    log_activity("CONFIG", f"Pesan khusus untuk '{chosen_contact}' diatur ke: '{msg_input.strip()}'")
                    print(f"[✓] Pesan khusus untuk '{chosen_contact}' berhasil disimpan!\n")

        elif act == "remove":
            if not overrides:
                print("[!] Tidak ada pesan khusus yang aktif.\n")
                continue
            remove_choices = [Choice(f"{c}: '{m}'", value=c) for c, m in overrides.items()]
            chosen_to_del = questionary.checkbox("Pilih kontak untuk menghapus pesan khususnya:", choices=remove_choices).ask()
            if chosen_to_del:
                for c in chosen_to_del:
                    if c in overrides:
                        del overrides[c]
                cfg["messages"]["overrides"] = overrides
                save_config(cfg)
                log_activity("CONFIG", f"Dihapus pesan khusus untuk {len(chosen_to_del)} kontak")
                print(f"[✓] Pesan khusus berhasil dihapus. Kontak kembali menggunakan template umum.\n")


def show_message_preview():
    cfg = load_config()
    contacts = cfg.get("contacts", [])
    if not contacts:
        contacts = ["Budi Santoso", "Siti Aminah", "David Wijaya"]

    print("\n" + "=" * 65)
    print("👁️  PRATINJAU FORMAT PESAN STREAK (PREVIEW HASIL TEKS)")
    print("=" * 65)
    mode = cfg.get("messages", {}).get("mode", "single")
    print(f" Mode Aktif : {'🎲 Acak dari Pool' if mode == 'pool' else '💬 Satu Pesan Default'}")
    print("-" * 65)

    sample = contacts[:6]
    for c in sample:
        resolved = resolve_message_for_contact(c)
        is_override = c in cfg.get("messages", {}).get("overrides", {})
        badge = " [Pesan Khusus]" if is_override else ""
        print(f"  Kepada: {c:<18}{badge}")
        print(f"  Pesan : '{resolved}'")
        print()
    print("=" * 65 + "\n")
    questionary.press_any_key_to_continue().ask()


def menu_manage_messages():
    while True:
        cfg = load_config()
        msg_cfg = cfg.get("messages", {})
        mode = msg_cfg.get("mode", "single")
        mode_label = "🎲 Variasi Acak (Pool)" if mode == "pool" else "💬 Satu Pesan Default"
        default_msg = cfg.get("default_message", "🔥")
        pool = msg_cfg.get("pool", [])
        overrides = msg_cfg.get("overrides", {})

        choices = [
            Choice(f"🔄 Ganti Mode Pesan (Saat ini: {mode_label})", value="toggle_mode"),
            Choice(f"💬 Ubah Pesan Default (Saat ini: '{default_msg}')", value="default_msg"),
            Choice(f"🎲 Kelola Pool Variasi Acak ({len(pool)} variasi tersimpan)", value="pool"),
            Choice(f"👤 Pesan Khusus per Kontak ({len(overrides)} kontak khusus)", value="overrides"),
            Choice("👁️  Pratinjau Hasil Pesan (Preview)", value="preview"),
            Separator(),
            Choice("🔙 Selesai / Kembali", value="back")
        ]

        act = questionary.select("💬 Konfigurasi Format Pesan Streak:", choices=choices).ask()
        if act == "back" or not act:
            break

        elif act == "toggle_mode":
            new_mode = "pool" if mode == "single" else "single"
            msg_cfg["mode"] = new_mode
            cfg["messages"] = msg_cfg
            save_config(cfg)
            log_activity("CONFIG", f"Mode pesan diubah ke: {new_mode.upper()}")
            print(f"\n[✓] Mode pesan diubah ke: {'Variasi Acak (Pool)' if new_mode == 'pool' else 'Satu Pesan Default'}\n")

        elif act == "default_msg":
            new_def = questionary.text(
                "Masukkan pesan default baru:",
                default=default_msg
            ).ask()
            if new_def:
                cfg["default_message"] = new_def
                save_config(cfg)
                log_activity("CONFIG", f"Pesan default diubah menjadi: '{new_def}'")
                print(f"\n[✓] Pesan default diperbarui menjadi: '{new_def}'\n")

        elif act == "pool":
            menu_pool_editor()

        elif act == "overrides":
            menu_contact_overrides()

        elif act == "preview":
            show_message_preview()


def menu_account():
    while True:
        is_logged_in = check_login_status()
        contacts = load_config().get("contacts", [])
        status_label = "🟢 VALID (Aktif)" if is_logged_in else "🔴 BELUM LOGIN"

        choices = [
            Choice(f"🔍 Pindai Kontak DM dari TikTok (Tersimpan: {len(contacts)} kontak)", value="scan"),
            Choice("🔑 Login / Hubungkan Akun TikTok (Buka Jendela Browser)", value="login"),
            Choice(f"ℹ️  Cek Ulang Status Sesi Login (Status: {status_label})", value="check"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select("🔑 Manajemen Akun & Kontak TikTok:", choices=choices).ask()
        if action == "back" or not action:
            break

        elif action == "scan":
            scan_dm_contacts(verbose=True)
            questionary.press_any_key_to_continue("Tekan tombol apa saja untuk kembali...").ask()

        elif action == "login":
            interactive_login()
            questionary.press_any_key_to_continue("Tekan tombol apa saja untuk kembali...").ask()

        elif action == "check":
            ok, _ = run_with_progress("Memeriksa sesi login TikTok", check_login_status, timeout=2.0)
            print(f"[{'✓' if ok else '!'}] Status Sesi: {'🟢 VALID (Aktif)' if ok else '🔴 KADALUARSA / BELUM LOGIN'}\n")
            questionary.press_any_key_to_continue("Tekan tombol apa saja untuk kembali...").ask()


def display_logs(date_filter: str = None, category_filter: str = None, max_lines: int = 40):
    clean_expired_logs(retention_days=3)
    if not os.path.exists(LOG_DIR):
        print("\n[!] Direktori log belum ditemukan.\n")
        return

    files = sorted([f for f in os.listdir(LOG_DIR) if f.startswith("activity_") and f.endswith(".log")])
    if not files:
        print("\n[!] Belum ada log aktivitas tersimpan.\n")
        return

    all_entries = []
    for f in files:
        d_str = f[len("activity_"):-len(".log")]
        if date_filter and d_str != date_filter:
            continue
        filepath = os.path.join(LOG_DIR, f)
        try:
            with open(filepath, "r", encoding="utf-8") as lf:
                for line in lf:
                    line_s = line.strip()
                    if not line_s:
                        continue
                    if category_filter and f"[{category_filter}]" not in line_s:
                        continue
                    all_entries.append(line_s)
        except Exception:
            pass

    print("\n" + "=" * 70)
    filter_desc = []
    if date_filter:
        filter_desc.append(f"Tanggal: {date_filter}")
    if category_filter:
        filter_desc.append(f"Kategori: {category_filter}")
    f_str = f" ({', '.join(filter_desc)})" if filter_desc else " (Semua Kategori - Max 3 Hari)"
    print(f"📜 RIWAYAT AKTIVITAS & LOG{f_str}:")
    print("=" * 70)

    if not all_entries:
        print("  (Tidak ada catatan log yang cocok dengan filter)")
    else:
        recent = all_entries[-max_lines:]
        for entry in recent:
            print(f"  {entry}")
        if len(all_entries) > max_lines:
            print(f"\n  ... dan {len(all_entries) - max_lines} entri sebelumnya.")

    print("=" * 70 + "\n")


def menu_view_logs():
    while True:
        choices = [
            Choice("📜 Lihat Semua Log (3 Hari Terakhir)", value="all"),
            Choice("🚀 Filter Log Eksekusi Streak (JOB)", value="job"),
            Choice("⚙️  Filter Perubahan Pengaturan (CONFIG)", value="config"),
            Choice("🧹 Bersihkan Log Manual Sekarang", value="clean"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        act = questionary.select("📜 Riwayat Aktivitas & Log (Retensi Otomatis 3 Hari):", choices=choices).ask()
        if act == "back" or not act:
            break

        if act == "all":
            display_logs()
            questionary.press_any_key_to_continue().ask()

        elif act == "job":
            display_logs(category_filter="JOB")
            questionary.press_any_key_to_continue().ask()

        elif act == "config":
            display_logs(category_filter="CONFIG")
            questionary.press_any_key_to_continue().ask()

        elif act == "clean":
            confirm = questionary.confirm("Hapus semua log aktivitas yang tersimpan sekarang?").ask()
            if confirm:
                if os.path.exists(LOG_DIR):
                    for f in os.listdir(LOG_DIR):
                        if f.startswith("activity_") and f.endswith(".log"):
                            try:
                                os.remove(os.path.join(LOG_DIR, f))
                            except Exception:
                                pass
                log_activity("SYSTEM", "Seluruh log aktivitas dibersihkan manual oleh user.")
                print("\n[✓] Seluruh riwayat log berhasil dibersihkan!\n")
            questionary.press_any_key_to_continue().ask()


def interactive_hub():
    while True:
        print_dashboard()
        is_logged_in = check_login_status()

        choices = []
        if not is_logged_in:
            choices.append(Choice("🔑 [WAJIB] LOGIN / HUBUNGKAN AKUN TIKTOK SEKARANG", value="account"))
            choices.append(Choice("🚀 Kirim Streak Sekarang (Run Check-in) [Butuh Login]", value="run"))
        else:
            choices.append(Choice("🚀 Kirim Streak Sekarang (Run Check-in)", value="run"))

        choices.extend([
            Choice("👥 Kelola Penerima & Pesan (Kontak, Grup & Variasi Pesan)", value="recipients"),
            Choice("⏰ Jadwal Otomatis Harian (LaunchAgent @ 09:00 + Wake-up Catch-up)", value="scheduler"),
            Choice("📜 Riwayat Aktivitas & Log (Tersimpan 3 Hari)", value="logs"),
        ])

        if is_logged_in:
            choices.append(Choice("🔑 Akun & Pindai Kontak (Login & Scan DM TikTok)", value="account"))

        choices.extend([
            Choice("🔔 Pengaturan Notifikasi (Telegram / Discord)", value="notifications"),
            Choice("🔄 Cek Pembaruan Aplikasi (Check for Updates)", value="check_update"),
            Separator(),
            Choice("🚪 Keluar", value="exit")
        ])

        action = questionary.select(
            "Pilih Menu:",
            choices=choices,
            use_indicator=True
        ).ask()

        if action in ("exit", None):
            print("\n👋 Sampai jumpa! Streak TikTok Anda aman.\n")
            break

        elif action == "run":
            run_send_streak(force=True, verbose=True)
            questionary.press_any_key_to_continue("Tekan tombol apa saja untuk kembali ke menu...").ask()

        elif action == "recipients":
            menu_manage_recipients()

        elif action == "scheduler":
            menu_manage_scheduler()

        elif action == "logs":
            menu_view_logs()

        elif action == "account":
            menu_account()

        elif action == "notifications":
            menu_notifications()

        elif action == "check_update":
            check_for_updates(prompt_if_latest=True)


def run_cron_job(max_retries: int = 3, retry_delay: int = 40):
    """
    Executes streak sending in unattended background mode with robust wake-up catch-up.
    Waits for network connection if waking up from sleep, and retries on transient errors.
    """
    state = load_state()
    today_str = str(date.today())
    if state.get("last_success_date") == today_str:
        log_activity("SYSTEM", f"Cron check: Streak hari ini ({today_str}) sudah terkirim sebelumnya. Selesai.")
        return

    # Check safe hours before executing
    is_safe, reason = is_within_safe_hours()
    if not is_safe:
        log_activity("SYSTEM", f"Cron ditunda: {reason}. Pengiriman akan dilanjutkan pada jam aman.")
        return

    log_activity("SYSTEM", "Cron dipicu: Memulai proses otomatis...")

    # 1. Wait for active internet connection (crucial for macOS wake-up)
    if not wait_for_internet(timeout=180, check_interval=3, verbose=False):
        log_activity("ERROR", "Cron dibatalkan: Koneksi internet belum tersedia setelah 180 detik.")
        return

    # 2. Retry loop for transient failures
    for attempt in range(1, max_retries + 1):
        log_activity("JOB", f"Menjalankan pengiriman streak (Percobaan {attempt}/{max_retries})...")
        res = run_send_streak(force=False, verbose=False)
        if res.get("success"):
            log_activity("SYSTEM", f"Cron berhasil pada percobaan ke-{attempt}.")
            return

        if attempt < max_retries:
            log_activity("SYSTEM", f"Percobaan ke-{attempt} belum berhasil ({res.get('message')}). Menunggu {retry_delay} detik sebelum mencoba lagi...")
            time.sleep(retry_delay)
            wait_for_internet(timeout=60, check_interval=3, verbose=False)
        else:
            log_activity("ERROR", "Cron selesai: Seluruh percobaan telah habis.")


def main():
    parser = argparse.ArgumentParser(description="⚡ TikTok Streak Auto-Saver & Helper Hub")
    parser.add_argument("--cron", action="store_true", help="Run unattended in background via scheduler")
    parser.add_argument("--force", action="store_true", help="Force send streak even if already sent today")
    parser.add_argument("--login", action="store_true", help="Open visual browser for login")
    parser.add_argument("--scan", action="store_true", help="Scan DM contacts from TikTok")

    args = parser.parse_args()

    if args.cron:
        # Background mode for LaunchAgent / TaskScheduler
        run_cron_job()
    elif args.force:
        wait_for_internet(timeout=15, verbose=True)
        run_send_streak(force=True, verbose=True)
    elif args.login:
        interactive_login()
    elif args.scan:
        wait_for_internet(timeout=15, verbose=True)
        scan_dm_contacts(verbose=True)
    else:
        # Check update on startup
        check_for_updates(prompt_if_latest=False)
        # Default interactive TUI
        interactive_hub()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        handle_sigint()
