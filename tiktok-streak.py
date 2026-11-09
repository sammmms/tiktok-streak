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
import platform
import argparse
import subprocess
from datetime import datetime, date
from pathlib import Path

OS_NAME = platform.system()  # 'Darwin' (macOS), 'Windows', 'Linux'
APP_NAME = "tiktok-streak"
APP_VERSION = "1.2.0"
HOME_DIR = Path.home()
INSTALL_DIR = HOME_DIR / ".tiktok-streak"
CONFIG_FILE = INSTALL_DIR / "config.json"
STATE_FILE = INSTALL_DIR / "last_run.json"
PROFILE_DIR = INSTALL_DIR / "browser_profile"
LOG_FILE = INSTALL_DIR / "streak.log"
SCRIPT_PATH = Path(__file__).resolve()


def parse_semver(ver: str) -> tuple:
    parts = []
    for x in ver.lstrip("v").split("."):
        if x.isdigit():
            parts.append(int(x))
    return tuple(parts)


def check_for_updates(prompt_if_latest: bool = False):
    """
    Checks latest update from https://wsnsam.my.id/api/updates?app=tiktok-streak
    with fallback to raw.githubusercontent.com/.../version.json.
    Prompts user with changelog and performs in-place in-app updates.
    """
    import urllib.request
    import json
    import time

    sys.stdout.write("[*] Memeriksa pembaruan terbaru... ")
    sys.stdout.flush()

    primary_url = f"https://wsnsam.my.id/api/updates?app={APP_NAME}"
    fallback_url = f"https://raw.githubusercontent.com/sammmms/{APP_NAME}/main/version.json"

    update_data = None
    for url in [primary_url, fallback_url]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AutoUpdater)"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    update_data = json.loads(resp.read().decode("utf-8"))
                    break
        except Exception:
            continue

    if not update_data or "version" not in update_data:
        sys.stdout.write("\r[*] Memeriksa pembaruan terbaru... [Lewati / Offline]\n")
        sys.stdout.flush()
        time.sleep(0.3)
        return

    latest_ver = update_data["version"]
    if parse_semver(latest_ver) <= parse_semver(APP_VERSION):
        sys.stdout.write(f"\r[*] Memeriksa pembaruan terbaru... [Versi Terbaru: v{APP_VERSION} ✓]\n")
        sys.stdout.flush()
        time.sleep(0.4)
        if prompt_if_latest:
            print(f"\n[✓] Anda sudah menggunakan versi terbaru (v{APP_VERSION}).\n")
            import questionary
            questionary.press_any_key_to_continue().ask()
        return

    # Newer version available
    sys.stdout.write("\r" + " " * 60 + "\r")
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


def load_config() -> dict:
    ensure_dirs()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            # merge any missing keys from DEFAULT_CONFIG
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
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


def log_message(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


# ==============================================================================
# Notifications (macOS Native, Telegram, Discord)
# ==============================================================================

def send_notification(title: str, text: str, success: bool):
    cfg = load_config()
    notifs = cfg.get("notifications", {})

    # 1. macOS native banner
    if OS_NAME == "Darwin" and notifs.get("macos", {}).get("enabled", True):
        sound = "default" if success else "Basso"
        script = f'display notification "{text}" with title "{title}" sound name "{sound}"'
        try:
            subprocess.run(["osascript", "-e", script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # 2. Telegram Bot
    tg = notifs.get("telegram", {})
    if tg.get("enabled") and tg.get("bot_token") and tg.get("chat_id"):
        try:
            import requests
            icon = "✅" if success else "❌"
            msg = f"{icon} *{title}*\n\n{text}\n\n_Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
            requests.post(
                f"https://api.telegram.org/bot{tg['bot_token']}/sendMessage",
                json={"chat_id": tg["chat_id"], "text": msg, "parse_mode": "Markdown"},
                timeout=10
            )
        except Exception as e:
            log_message(f"Telegram notification error: {e}")

    # 3. Discord Webhook
    dc = notifs.get("discord", {})
    if dc.get("enabled") and dc.get("webhook_url"):
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
            requests.post(dc["webhook_url"], json=payload, timeout=10)
        except Exception as e:
            log_message(f"Discord notification error: {e}")


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
    <dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>
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
        print(f"    ⏰ Dijadwalkan setiap jam {time_str} pagi.")
        print(f"    ⚡ Fitur Auto-Catchup: Jika laptop tidur/mati jam {time_str}, script otomatis jalan saat dinyalakan.")

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
    """Check if browser profile directory has cookies/storage state."""
    if not PROFILE_DIR.exists():
        return False
    # Check if Default or Storage directories exist inside profile
    storage_state = list(PROFILE_DIR.glob("**/*Cookies*")) + list(PROFILE_DIR.glob("**/*storage*"))
    return len(storage_state) > 0


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
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.tiktok.com/login", wait_until="networkidle")

        input("\n👉 Jika Anda sudah BERHASIL LOGIN di browser, tekan [ENTER] di terminal ini...")
        context.close()

    print("\n[✓] Sesi login berhasil disimpan di komputer!")


def scan_dm_contacts(verbose: bool = True) -> list:
    """Scans and updates contact list from TikTok Web DM."""
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
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True,
                viewport={"width": 1280, "height": 800},
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://www.tiktok.com/messages", wait_until="networkidle", timeout=60000)
            time.sleep(5)

            if "login" in page.url:
                if verbose:
                    print("[!] Sesi login kedaluwarsa. Silakan lakukan Login Akun terlebih dahulu.")
                context.close()
                return []

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


def send_message_in_chat(page, message: str) -> bool:
    try:
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
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=cfg.get("headless", True),
                viewport={"width": 1280, "height": 800},
                args=["--disable-blink-features=AutomationControlled"]
            )
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

                    if verbose:
                        print(f"  [>] Mengirim streak ke {name}...")
                    item.click()
                    time.sleep(2)
                    if send_message_in_chat(page, msg_to_send):
                        success_list.append(name)
                        if verbose:
                            print(f"      [✓] Terkirim!")
                    else:
                        fail_list.append(name)
                        if verbose:
                            print(f"      [x] Gagal kirim pesan.")
                    time.sleep(1)

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
                    if verbose:
                        print(f"  [>] Mencari kontak '{target_name}'...")

                    # Search by nickname or text in conversation item
                    target_locator = page.locator(f'[data-e2e="dm-new-conversation-item"]:has([data-e2e="dm-new-conversation-nickname"]:text-is("{target_name}"))')
                    if target_locator.count() == 0:
                        target_locator = page.locator(f'[data-e2e="dm-new-conversation-item"]:has-text("{target_name}"), div[data-e2e="chat-list-item"]:has-text("{target_name}")')

                    found = False
                    if target_locator.count() > 0:
                        target_locator.first.click()
                        found = True
                    else:
                        # Try search box
                        search_box = page.locator('input[placeholder*="Search"], input[type="search"]')
                        if search_box.count() > 0:
                            search_box.first.fill(target_name)
                            time.sleep(2)
                            result = page.locator(f'[data-e2e="dm-new-conversation-item"]:has-text("{target_name}"), li:has-text("{target_name}")')
                            if result.count() > 0:
                                result.first.click()
                                found = True
                            search_box.first.fill("")

                    if found:
                        time.sleep(2)
                        if send_message_in_chat(page, custom_msg):
                            success_list.append(f"{target_name} ('{custom_msg}')")
                            if verbose:
                                print(f"      [✓] Terkirim ({custom_msg})!")
                        else:
                            fail_list.append(target_name)
                    else:
                        fail_list.append(f"{target_name} (Tidak ditemukan)")
                        if verbose:
                            print(f"      [x] Kontak '{target_name}' tidak ditemukan.")
                    time.sleep(1)

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
# Interactive Terminal Hub (TUI)
# ==============================================================================

def print_dashboard():
    cfg = load_config()
    state = load_state()
    today_str = str(date.today())
    has_run_today = state.get("last_success_date") == today_str
    is_sched_active, sched_desc = get_scheduler_status()
    is_logged_in = check_login_status()

    mode_name = "🌟 Select All" if cfg.get("mode") == "all" else "👥 Groups / Labeling"
    
    print("\n" + "=" * 58)
    print("⚡  TikTok Streak Auto-Saver & Helper Hub")
    print("=" * 58)
    print(f"👤 Akun Sesi:      {'🟢 VALID (Aktif)' if is_logged_in else '🔴 Belum Login'}")
    print(f"📅 Status Hari Ini: {'✅ Streak Sudah Terkirim' if has_run_today else '⏳ Belum Terkirim Hari Ini'}")
    print(f"👥 Mode Penerima:   {mode_name}")
    print(f"⏰ Jadwal Auto:     {'🟢' if is_sched_active else '⚪'} {sched_desc}")
    print("=" * 58)
    print(" [1] 🚀 Kirim Streak Sekarang (Run Check-in)")
    print(" [2] 👥 Kelola Penerima & Grup (Select All / Checklist)")
    print(" [3] 🔍 Pindai Kontak DM dari TikTok (Auto-detect)")
    print(" [4] ⏰ Pasang / Atur Jadwal Harian (Catch-up saat laptop nyala)")
    print(" [5] 🔑 Login / Hubungkan Akun TikTok (Browser Window)")
    print(" [6] 🔔 Pengaturan Notifikasi (Telegram / Discord)")
    print(" [0] 🚪 Keluar")
    print("=" * 58)


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

    mode_name = "🌟 Select All" if cfg.get("mode") == "all" else "👥 Groups / Labeling"

    print("\n" + "=" * 58)
    print("⚡  TikTok Streak Auto-Saver & Helper Hub")
    print("=" * 58)
    print(f"👤 Akun Sesi:      {'🟢 VALID (Aktif)' if is_logged_in else '🔴 Belum Login'}")
    print(f"📅 Status Hari Ini: {'✅ Streak Sudah Terkirim' if has_run_today else '⏳ Belum Terkirim Hari Ini'}")
    print(f"👥 Mode Penerima:   {mode_name}")
    print(f"⏰ Jadwal Auto:     {'🟢' if is_sched_active else '⚪'} {sched_desc}")
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
        mode_label = "Select All" if mode == "all" else "Groups / Labeling"
        default_msg = cfg.get("default_message", "🔥")

        choices = [
            Choice(f"🔄 Ganti Mode (Saat ini: {mode_label})", value="toggle_mode"),
            Choice("📋 Checklist Kontak & Tetapkan Grup (Interactive Multi-select)", value="checklist"),
            Choice("🏷️  Kelola Label Grup & Pesan Khusus", value="groups"),
            Choice("🚫 Kelola Daftar Pengecualian (Blacklist / Exclude)", value="exclude"),
            Choice(f"💬 Ubah Pesan Default (Saat ini: '{default_msg}')", value="default_msg"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select(
            f"👥 Kelola Penerima & Grup [Mode Aktif: {mode.upper()}]:",
            choices=choices
        ).ask()

        if action == "back" or not action:
            break

        elif action == "toggle_mode":
            cfg["mode"] = "groups" if mode == "all" else "all"
            save_config(cfg)
            print(f"\n[✓] Mode pengiriman diubah ke: {cfg['mode'].upper()}\n")

        elif action == "checklist":
            interactive_manage_contacts()

        elif action == "groups":
            menu_manage_groups()

        elif action == "exclude":
            menu_manage_exclude()

        elif action == "default_msg":
            new_def = questionary.text(
                "Masukkan pesan default baru:",
                default=default_msg
            ).ask()
            if new_def:
                cfg["default_message"] = new_def
                save_config(cfg)
                print(f"\n[✓] Pesan default diperbarui menjadi: '{new_def}'\n")


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


def menu_notifications():
    while True:
        cfg = load_config()
        notifs = cfg.get("notifications", {})
        tg = notifs.get("telegram", {})
        dc = notifs.get("discord", {})

        choices = [
            Choice(f"📱 Telegram Bot: {'🟢 AKTIF' if tg.get('enabled') else '⚪ Nonaktif'}", value="toggle_tg"),
            Choice(f"💬 Discord Webhook: {'🟢 AKTIF' if dc.get('enabled') else '⚪ Nonaktif'}", value="toggle_dc"),
            Choice("🔔 Tes Kirim Notifikasi Sekarang", value="test_notif"),
            Separator(),
            Choice("🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select("🔔 Pengaturan Notifikasi ke HP:", choices=choices).ask()
        if action == "back" or not action:
            break

        if action == "toggle_tg":
            tg["enabled"] = not tg.get("enabled", False)
            if tg["enabled"] and not tg.get("bot_token"):
                tg["bot_token"] = questionary.text("Masukkan Telegram Bot Token:").ask()
                tg["chat_id"] = questionary.text("Masukkan Telegram Chat ID:").ask()
            save_config(cfg)
            print(f"\n[✓] Telegram Bot sekarang: {'AKTIF' if tg['enabled'] else 'NONAKTIF'}\n")

        elif action == "toggle_dc":
            dc["enabled"] = not dc.get("enabled", False)
            if dc["enabled"] and not dc.get("webhook_url"):
                dc["webhook_url"] = questionary.text("Masukkan Discord Webhook URL:").ask()
            save_config(cfg)
            print(f"\n[✓] Discord Webhook sekarang: {'AKTIF' if dc['enabled'] else 'NONAKTIF'}\n")

        elif action == "test_notif":
            print("\n[*] Mengirim notifikasi tes...")
            send_notification("Tes Notifikasi TikTok Streak", "Halo! Notifikasi pengingat streak berhasil terhubung.", success=True)
            print("[✓] Notifikasi tes dikirim!\n")
            questionary.press_any_key_to_continue().ask()


def interactive_hub():
    while True:
        print_dashboard()

        choices = [
            Choice("🚀 Kirim Streak Sekarang (Run Check-in)", value="run"),
            Choice("👥 Kelola Penerima & Grup (Select All / Checklist)", value="recipients"),
            Choice("🔍 Pindai Kontak DM dari TikTok (Auto-detect)", value="scan"),
            Choice("⏰ Pasang / Atur Jadwal Harian (Catch-up saat laptop nyala)", value="scheduler"),
            Choice("🔑 Login / Hubungkan Akun TikTok (Browser Window)", value="login"),
            Choice("🔔 Pengaturan Notifikasi (Telegram / Discord)", value="notifications"),
            Choice("🔄 Cek Pembaruan Aplikasi (Check for Updates)", value="check_update"),
            Separator(),
            Choice("🚪 Keluar", value="exit")
        ]

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

        elif action == "scan":
            scan_dm_contacts(verbose=True)
            questionary.press_any_key_to_continue("Tekan tombol apa saja untuk kembali ke menu...").ask()

        elif action == "scheduler":
            menu_manage_scheduler()

        elif action == "login":
            interactive_login()
            questionary.press_any_key_to_continue("Tekan tombol apa saja untuk kembali ke menu...").ask()

        elif action == "notifications":
            menu_notifications()

        elif action == "check_update":
            check_for_updates(prompt_if_latest=True)


# ==============================================================================
# CLI Entry Point
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="⚡ TikTok Streak Auto-Saver & Helper Hub")
    parser.add_argument("--cron", action="store_true", help="Run unattended in background via scheduler")
    parser.add_argument("--force", action="store_true", help="Force send streak even if already sent today")
    parser.add_argument("--login", action="store_true", help="Open visual browser for login")
    parser.add_argument("--scan", action="store_true", help="Scan DM contacts from TikTok")

    args = parser.parse_args()

    if args.cron:
        # Background mode for LaunchAgent / TaskScheduler
        run_send_streak(force=False, verbose=False)
    elif args.force:
        run_send_streak(force=True, verbose=True)
    elif args.login:
        interactive_login()
    elif args.scan:
        scan_dm_contacts(verbose=True)
    else:
        # Check update on startup
        check_for_updates(prompt_if_latest=False)
        # Default interactive TUI
        interactive_hub()


if __name__ == "__main__":
    main()
