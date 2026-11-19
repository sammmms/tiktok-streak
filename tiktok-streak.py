#!/usr/bin/env python3
"""
⚡ TikTok Streak Auto-Saver & Helper Hub
Supports: Windows, macOS, Linux
Interactive Terminal Hub with Grouping, Select All, Auto-Scheduler, and Webhook Notifications.
Modeled after genshin-checkin.
Bilingual Support: English (Default) & Bahasa Indonesia
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
import re
from datetime import datetime, date, timedelta
from pathlib import Path

OS_NAME = platform.system()  # 'Darwin' (macOS), 'Windows', 'Linux'
APP_NAME = "tiktok-streak"
APP_VERSION = "1.4.4"
HOME_DIR = Path.home()
INSTALL_DIR = HOME_DIR / ".tiktok-streak"
CONFIG_FILE = INSTALL_DIR / "config.json"
STATE_FILE = INSTALL_DIR / "last_run.json"
PROFILE_DIR = INSTALL_DIR / "browser_profile"
LOG_FILE = INSTALL_DIR / "streak.log"
LOGS_DIR = INSTALL_DIR / "logs"
LOG_DIR = LOGS_DIR  # Alias for compatibility
SCRIPT_PATH = Path(__file__).resolve()

# ==============================================================================
# Internationalization (i18n): EN (Default) & ID
# ==============================================================================

DEFAULT_LANG = "en"
CURRENT_LANG = "en"

TRANSLATIONS = {
    "en": {
        "sigint_exit": "\n\n👋 Operation cancelled by user (Exit). Goodbye!\n",
        "checking_updates": "Checking for latest updates",
        "update_offline": "[*] Checking for updates... [Skip / Offline]",
        "update_latest": "[*] Checking for updates... [Latest Version: v{ver} ✓]",
        "update_already_latest": "\n[✓] You are already on the latest version (v{ver}).\n",
        "press_key_continue": "Press any key to continue...",
        "press_key_return": "Press any key to return to menu...",
        "update_available": "🚀 UPDATE AVAILABLE! (v{current} ➔ v{latest})",
        "release_date": "📅 Release: {date}",
        "changelog": "📋 Changelog:",
        "update_prompt": "Would you like to install the update now?",
        "update_opt_install": "🚀 Install Update Now (Auto-update in-app)",
        "update_opt_skip": "⏭️  Skip for now",
        "update_downloading": "\n⬇️  Downloading update v{ver}...",
        "update_no_url": "[!] Download URL not available.",
        "update_success": "✅ Successfully updated to version v{ver}!",
        "restarting_app": "🔄 Restarting application...",
        "update_failed": "[x] Failed to install update: {err}",
        "update_skipped": "[*] Update skipped.\n",
        "wait_internet": "Checking internet connection",
        "internet_connected": "Internet connection: [Connected ✓] ({elapsed:.1f}s)",
        "internet_failed": "Failed to connect to internet after {timeout} seconds.",
        "cron_internet_failed": "Cron cancelled: Internet connection not available after 180s.",
        "cron_safe_hours": "Cron postponed: Outside safe hours ({reason}). Sending will resume during safe hours.",
        "cron_already_sent": "Cron check: Streak today ({date}) already sent previously. Done.",
        "cron_triggered": "Cron triggered: Starting automatic process...",
        "cron_attempt": "Running streak dispatch (Attempt {attempt}/{max_attempts})...",
        "cron_success": "Cron succeeded on attempt {attempt}.",
        "cron_retry": "Attempt {attempt} failed ({msg}). Retrying in {delay}s...",
        "cron_exhausted": "Cron finished: All retry attempts exhausted.",
        "sched_macos_active": "macOS LaunchAgent (Active)",
        "sched_macos_loaded": "macOS LaunchAgent (Loaded)",
        "sched_win_active": "Windows Task Scheduler (Active)",
        "sched_linux_active": "Linux Crontab (Active)",
        "sched_not_configured": "Not Configured",
        "sched_unsupported": "Unsupported OS",
        "sched_installed_mac": "[✓] Daily schedule registered once per day at {time} via macOS LaunchAgent!",
        "sched_installed_win": "[✓] Windows Task Scheduler registered successfully at {time}.",
        "sched_installed_linux": "[✓] Linux Crontab registered successfully at {time}.",
        "sched_removed_mac": "[✓] macOS LaunchAgent removed.",
        "sched_removed_win": "[✓] Windows Task Scheduler removed.",
        "sched_removed_linux": "[✓] Linux Crontab removed.",
        "dash_title": "⚡  TikTok Streak Auto-Saver & Helper Hub",
        "dash_account_status": "👤 Account Session: ",
        "dash_status_valid": "🟢 VALID (Active)",
        "dash_status_unauthed": "🔴 Not Logged In",
        "dash_today_status": "📅 Today's Status : ",
        "dash_today_sent": "✅ Streak Sent Today ({count} contacts)",
        "dash_today_pending": "⌛ Not Sent Today",
        "dash_today_failed": "⚠️  Not Sent ({summary})",
        "dash_today_failed_hint": "                   ℹ️  Connection failed during wake-up (Wi-Fi not connected).",
        "dash_recipient_mode": "👥 Recipient Mode : ",
        "dash_config": "💬 Configuration  : ",
        "dash_sched": "⏰ Auto Schedule  : ",
        "dash_logs": "📁 Log History    : Stored for the last {days} days (Auto-prune)",
        "dash_warn_unauthed_title": "⚠️  ACCOUNT STATUS: NOT LOGGED IN / EMPTY SESSION",
        "dash_warn_unauthed_desc1": "Bot cannot send streaks before you log in!",
        "dash_warn_unauthed_desc2": "👉 Choose option [1] in the menu to log in via browser.",
        "dash_mode_all": "🌟 Select All",
        "dash_mode_groups": "👥 Groups / Labeling",
        "dash_msg_mode_pool": "🎲 Random Pool",
        "dash_msg_mode_fixed": "🔒 Fixed ('{msg}')",
        "menu_select": "Select Menu:",
        "menu_opt_login_req": "🔑 [REQUIRED] LOGIN / CONNECT TIKTOK ACCOUNT NOW",
        "menu_opt_run_need_login": "🚀 Send Streak Now (Run Check-in) [Login Required]",
        "menu_opt_run": "🚀 Send Streak Now (Run Check-in)",
        "menu_opt_recipients": "👥 Manage Recipients & Messages (Contacts, Groups & Variations)",
        "menu_opt_speed": "⚡ Dispatch Speed & Safety (Pace & Browser Mode)",
        "menu_opt_scheduler": "⏰ Daily Auto Schedule (LaunchAgent @ {time} + Wake-up Catch-up)",
        "menu_opt_logs": "📜 Activity History & Logs (Last 3 Days)",
        "menu_opt_account": "🔑 Account & Scan Contacts (Login & Scan DM)",
        "menu_opt_notifications": "🔔 Notification Settings (Telegram / Discord)",
        "menu_opt_check_update": "🔄 Check for Updates",
        "menu_opt_lang": "🌐 Language / Bahasa (Current: {current})",
        "menu_opt_exit": "🚪 Exit",
        "goodbye": "\n👋 Goodbye! Your TikTok streak is safe.\n",
        "lang_menu_title": "🌐 Select Language / Pilih Bahasa:",
        "lang_opt_en": "🇬🇧 English (Default)",
        "lang_opt_id": "🇮🇩 Bahasa Indonesia",
        "lang_opt_back": "🔙 Back / Kembali",
        "lang_changed": "\n[✓] Language changed to: {lang}\n",
        "current_lang_label": "Current",
        "login_title": "🔑 Login to TikTok Account (Interactive Browser)",
        "login_step_1": "1. A browser window will open automatically.",
        "login_step_2": "2. Please log in (QR scan via TikTok mobile app or email/password).",
        "login_step_3": "3. Once on your TikTok Home / Feed, return to this terminal.",
        "login_press_enter": "\nPress [ENTER] to open browser...",
        "login_wait_confirm": "\n👉 Once you have LOGGED IN in the browser, press [ENTER] here...",
        "login_saved": "\n[✓] Login session saved on your computer!",
        "login_playwright_missing": "[!] Playwright module not installed. Run install.sh first.",
        "scan_connecting": "\n[*] Connecting to TikTok to scan DM contact list...",
        "scan_expired": "[!] Login session expired. Please log in first.",
        "scan_found": "\n[✓] Successfully found {count} contacts in TikTok DM:",
        "scan_none": "[-] No active conversations detected in DM.",
        "scan_failed": "[x] Failed to scan contacts: {err}",
        "streak_starting": "Starting daily streak dispatch process...",
        "streak_already_sent_log": "Streak for today ({date}) already sent previously. Skipping.",
        "streak_internet_fail": "Internet connection not available during streak sending.",
        "streak_verif_fail": "VERIFICATION FAILED: Active chat '{active}' != target '{target}'. Aborted for safety.",
        "streak_select_all_checking": "[*] Mode SELECT ALL: Checking {total} DM contacts...",
        "streak_skip_blacklist": "  [-] Skipping {name} (in blacklist)",
        "streak_sending_to": "  [>] Sending streak to {name} ('{msg}')...",
        "streak_sent_ok": "      [✓] Sent!",
        "streak_send_fail": "      [x] Failed to send message.",
        "streak_groups_processing": "[*] Mode GROUPS: Processing {count} target recipients...",
        "streak_groups_empty": "Mode Groups is active, but there are no members in any group.",
        "streak_finding_contact": "  [>] Finding contact '{name}' (Message: '{msg}')...",
        "streak_contact_not_found": "      [x] Contact '{name}' not found / failed to open chat.",
        "streak_finished": "Finished. {summary}",
        "streak_report_title": "📊 *TikTok Streak Dispatch Report:*",
        "streak_report_success": "✅ *Success ({count}):*",
        "streak_report_failed": "❌ *Failed/Skipped ({count}):*",
        "recip_menu_title": "👥 Manage Recipients & Messages [Active Mode: {mode}]:",
        "recip_toggle_mode": "🔄 Switch Mode (Current: {mode})",
        "recip_checklist": "📋 Contact Checklist & Assign Groups (Multi-select)",
        "recip_groups": "🏷️  Manage Group Labels",
        "recip_messages": "💬 Message Configuration & Variations (Default, Pool & Custom)",
        "recip_exclude": "🚫 Manage Exclude / Blacklist",
        "recip_preview": "👁️  Preview Messages to be Sent",
        "recip_back": "🔙 Back to Main Menu",
        "recip_mode_changed": "\n[✓] Recipient mode changed to: {mode}\n",
        "sched_menu_title": "⏰ Daily Schedule Manager [{os}] (Status: {icon} {desc}):",
        "sched_opt_install": "⏰ Enable / Install Daily Schedule (Runs at {time} + Auto Catch-up)",
        "sched_opt_change_time": "🕒 Change Run Time (Current: {time})",
        "sched_opt_remove": "🗑️  Disable / Remove Schedule",
        "sched_prompt_new_time": "Enter new time (Format HH:MM, e.g. 08:30):",
        "sched_time_changed": "\n[✓] Schedule time changed to {time}.",
        "sched_time_invalid": "\n[!] Invalid time format.",
        "notif_menu_title": "🔔 Notification Settings:",
        "notif_telegram": "📱 Telegram Bot: {status}",
        "notif_discord": "💬 Discord Webhook: {status}",
        "notif_test_all": "🔔 Test All Active Notifications",
        "notif_back": "🔙 Back to Main Menu",
        "notif_test_sending": "\n[*] Sending test notification to all active channels...",
        "notif_test_done": "[✓] Test notifications dispatched!\n",
        "status_active_upper": "🟢 ACTIVE",
        "status_inactive_upper": "⚪ INACTIVE",
        "account_menu_title": "🔑 TikTok Account & Contact Management:",
        "account_opt_scan": "🔍 Scan DM Contacts from TikTok (Saved: {count} contacts)",
        "account_opt_login": "🔑 Login / Connect TikTok Account (Open Browser)",
        "account_opt_check": "ℹ️  Re-check Session Status (Status: {status})",
        "account_opt_back": "🔙 Back to Main Menu",
        "logs_menu_title": "📜 Activity History & Logs (3-Day Retention):",
        "logs_opt_all": "📜 View All Logs (Last 3 Days)",
        "logs_opt_job": "🚀 Filter Streak Execution Logs (JOB)",
        "logs_opt_config": "⚙️  Filter Configuration Changes (CONFIG)",
        "logs_opt_clean": "🧹 Clear Logs Manually Now",
        "logs_opt_back": "🔙 Back to Main Menu",
        "logs_clean_confirm": "Delete all stored activity logs now?",
        "logs_cleaned": "\n[✓] All activity logs cleared successfully!\n",
        "pool_menu_title": "📝 Random Message Variations (Pool):",
        "pool_empty": "  (Message pool is empty)",
        "pool_opt_add": "➕ Add New Message Variation",
        "pool_opt_preset": "📋 Add from Popular Presets",
        "pool_opt_edit": "✏️  Edit Existing Message",
        "pool_opt_remove": "🗑️  Remove Message from Pool",
        "pool_opt_back": "🔙 Done / Return",
        "pool_add_hint": "\n💡 Supported placeholders:\n  {name}          = Full contact name\n  {first_name}    = First name\n  {time_greeting} = Morning / Afternoon / Evening\n  {day}           = Day name (Monday, etc.)\n  {date}          = Date (e.g. 10 Nov)\n",
        "pool_prompt_new": "Enter new message template:",
        "pool_added": "[✓] Message successfully added to pool!\n",
        "pool_preset_prompt": "Select templates to add to pool:",
        "pool_updated": "[✓] Message pool updated!\n",
        "pool_edit_prompt": "Select message to edit:",
        "pool_remove_prompt": "Select messages to remove:",
        "overrides_title": "👤 Custom Messages per Contact:",
        "overrides_empty": "  (No custom messages. All contacts use default/pool template)",
        "overrides_opt_add": "➕ Set Custom Message for Contact",
        "overrides_opt_remove": "🗑️  Remove Custom Message (Reset to Default)",
        "overrides_opt_back": "🔙 Done / Return",
        "preview_title": "👁️  STREAK MESSAGE FORMAT PREVIEW (OUTPUT RESULT)",
        "preview_mode": " Active Mode : {mode}",
        "preview_to": "  To     : {name}{badge}",
        "preview_msg": "  Message: '{msg}'",
        "groups_title": "🏷️  GROUP LIST & CUSTOM MESSAGES:",
        "groups_opt_add": "➕ Add New Group",
        "groups_opt_edit": "✏️  Edit Group Message",
        "groups_opt_delete": "🗑️  Delete Group",
        "groups_opt_back": "🔙 Return",
        "exclude_title": "🚫 BLACKLIST / EXCLUDE LIST (Skipped in All Mode):",
        "exclude_opt_add": "➕ Add Account to Blacklist",
        "exclude_opt_remove": "🗑️  Remove Account from Blacklist",
        "exclude_opt_back": "🔙 Return",
    },
    "id": {
        "sigint_exit": "\n\n👋 Operasi dibatalkan oleh pengguna (Keluar). Sampai jumpa!\n",
        "checking_updates": "Memeriksa pembaruan terbaru",
        "update_offline": "[*] Memeriksa pembaruan terbaru... [Lewati / Offline]",
        "update_latest": "[*] Memeriksa pembaruan terbaru... [Versi Terbaru: v{ver} ✓]",
        "update_already_latest": "\n[✓] Anda sudah menggunakan versi terbaru (v{ver}).\n",
        "press_key_continue": "Tekan tombol apa saja untuk melanjutkan...",
        "press_key_return": "Tekan tombol apa saja untuk kembali ke menu...",
        "update_available": "🚀 PEMBARUAN TERSEDIA! (v{current} ➔ v{latest})",
        "release_date": "📅 Rilis: {date}",
        "changelog": "📋 Catatan Pembaruan (Changelog):",
        "update_prompt": "Apakah Anda ingin memasang pembaruan sekarang?",
        "update_opt_install": "🚀 Pasang Pembaruan Sekarang (Auto-update in-app)",
        "update_opt_skip": "⏭️  Lewati (Skip untuk sekarang)",
        "update_downloading": "\n⬇️  Mengunduh pembaruan v{ver}...",
        "update_no_url": "[!] URL unduhan tidak tersedia.",
        "update_success": "✅ Berhasil memperbarui ke versi v{ver}!",
        "restarting_app": "🔄 Memulai ulang aplikasi...",
        "update_failed": "[x] Gagal memasang pembaruan: {err}",
        "update_skipped": "[*] Pembaruan dilewati.\n",
        "wait_internet": "Menunggu koneksi internet aktif",
        "internet_connected": "Koneksi internet: [Terhubung ✓] ({elapsed:.1f}s)",
        "internet_failed": "Gagal terhubung ke internet setelah {timeout} detik.",
        "cron_internet_failed": "Cron dibatalkan: Koneksi internet belum tersedia setelah 180 detik.",
        "cron_safe_hours": "Cron ditunda: {reason}. Pengiriman akan dilanjutkan pada jam aman.",
        "cron_already_sent": "Cron check: Streak hari ini ({date}) sudah terkirim sebelumnya. Selesai.",
        "cron_triggered": "Cron dipicu: Memulai proses otomatis...",
        "cron_attempt": "Menjalankan pengiriman streak (Percobaan {attempt}/{max_attempts})...",
        "cron_success": "Cron berhasil pada percobaan ke-{attempt}.",
        "cron_retry": "Percobaan ke-{attempt} belum berhasil ({msg}). Menunggu {delay} detik sebelum mencoba lagi...",
        "cron_exhausted": "Cron selesai: Seluruh percobaan telah habis.",
        "sched_macos_active": "macOS LaunchAgent (Aktif)",
        "sched_macos_loaded": "macOS LaunchAgent (Dimuat)",
        "sched_win_active": "Windows Task Scheduler (Aktif)",
        "sched_linux_active": "Linux Crontab (Aktif)",
        "sched_not_configured": "Belum Dikonfigurasi",
        "sched_unsupported": "Sistem Operasi Tidak Didukung",
        "sched_installed_mac": "[✓] Jadwal harian berhasil didaftarkan 1x sehari pukul {time} via macOS LaunchAgent!",
        "sched_installed_win": "[✓] Windows Task Scheduler berhasil didaftarkan pukul {time}.",
        "sched_installed_linux": "[✓] Linux Crontab berhasil didaftarkan pukul {time}.",
        "sched_removed_mac": "[✓] macOS LaunchAgent berhasil dihapus.",
        "sched_removed_win": "[✓] Windows Task Scheduler berhasil dihapus.",
        "sched_removed_linux": "[✓] Linux Crontab berhasil dihapus.",
        "dash_title": "⚡  TikTok Streak Auto-Saver & Helper Hub",
        "dash_account_status": "👤 Akun Sesi      : ",
        "dash_status_valid": "🟢 VALID (Aktif)",
        "dash_status_unauthed": "🔴 Belum Login",
        "dash_today_status": "📅 Status Hari Ini: ",
        "dash_today_sent": "✅ Streak Sudah Terkirim ({count} kontak)",
        "dash_today_pending": "⌛ Belum Terkirim Hari Ini",
        "dash_today_failed": "⚠️  Belum Terkirim ({summary})",
        "dash_today_failed_hint": "                   ℹ️  Gagal koneksi saat bangun tidur (Wi-Fi belum tersambung).",
        "dash_recipient_mode": "👥 Mode Penerima  : ",
        "dash_config": "💬 Konfigurasi    : ",
        "dash_sched": "⏰ Jadwal Auto    : ",
        "dash_logs": "📁 Log History    : Tersimpan {days} hari terakhir (Auto-prune)",
        "dash_warn_unauthed_title": "⚠️  STATUS AKUN: BELUM LOGIN / SESI TIKTOK KOSONG",
        "dash_warn_unauthed_desc1": "Bot tidak dapat mengirim streak sebelum Anda login!",
        "dash_warn_unauthed_desc2": "👉 Pilih opsi [1] di menu untuk login via browser.",
        "dash_mode_all": "🌟 Select All",
        "dash_mode_groups": "👥 Groups / Labeling",
        "dash_msg_mode_pool": "🎲 Pool Acak",
        "dash_msg_mode_fixed": "🔒 Fixed ('{msg}')",
        "menu_select": "Pilih Menu:",
        "menu_opt_login_req": "🔑 [WAJIB] LOGIN / HUBUNGKAN AKUN TIKTOK SEKARANG",
        "menu_opt_run_need_login": "🚀 Kirim Streak Sekarang (Run Check-in) [Butuh Login]",
        "menu_opt_run": "🚀 Kirim Streak Sekarang (Run Check-in)",
        "menu_opt_recipients": "👥 Kelola Penerima & Pesan (Kontak, Grup & Variasi Pesan)",
        "menu_opt_speed": "⚡ Pengaturan Kecepatan & Keamanan (Pace & Mode Browser)",
        "menu_opt_scheduler": "⏰ Jadwal Otomatis Harian (LaunchAgent @ {time} + Wake-up Catch-up)",
        "menu_opt_logs": "📜 Riwayat Aktivitas & Log (Tersimpan 3 Hari)",
        "menu_opt_account": "🔑 Akun & Pindai Kontak (Login & Scan DM TikTok)",
        "menu_opt_notifications": "🔔 Pengaturan Notifikasi (Telegram / Discord)",
        "menu_opt_check_update": "🔄 Cek Pembaruan Aplikasi (Check for Updates)",
        "menu_opt_lang": "🌐 Language / Bahasa (Saat ini: {current})",
        "menu_opt_exit": "🚪 Keluar",
        "goodbye": "\n👋 Sampai jumpa! Streak TikTok Anda aman.\n",
        "lang_menu_title": "🌐 Pilih Bahasa / Select Language:",
        "lang_opt_en": "🇬🇧 English (Default)",
        "lang_opt_id": "🇮🇩 Bahasa Indonesia",
        "lang_opt_back": "🔙 Kembali / Back",
        "lang_changed": "\n[✓] Bahasa berhasil diubah ke: {lang}\n",
        "current_lang_label": "Saat ini",
        "login_title": "🔑 Login Akun TikTok (Interactive Browser)",
        "login_step_1": "1. Jendela browser akan terbuka secara otomatis.",
        "login_step_2": "2. Silakan login (bisa scan QR via aplikasi TikTok di HP atau email/password).",
        "login_step_3": "3. Setelah berhasil masuk ke Beranda TikTok, kembali ke sini.",
        "login_press_enter": "\nTekan [ENTER] untuk membuka browser...",
        "login_wait_confirm": "\n👉 Jika Anda sudah BERHASIL LOGIN di browser, tekan [ENTER] di terminal ini...",
        "login_saved": "\n[✓] Sesi login berhasil disimpan di komputer!",
        "login_playwright_missing": "[!] Modul 'playwright' belum terpasang. Jalankan install.sh terlebih dahulu.",
        "scan_connecting": "\n[*] Menghubungkan ke TikTok untuk memindai daftar kontak DM...",
        "scan_expired": "[!] Sesi login kedaluwarsa. Silakan lakukan Login Akun terlebih dahulu.",
        "scan_found": "\n[✓] Berhasil menemukan {count} kontak di DM TikTok:",
        "scan_none": "[-] Tidak ada percakapan aktif yang terdeteksi.",
        "scan_failed": "[x] Gagal memindai kontak: {err}",
        "streak_starting": "Memulai proses pengiriman streak harian...",
        "streak_already_sent_log": "Streak untuk hari ini ({date}) sudah berhasil dikirim sebelumnya. Lewati.",
        "streak_internet_fail": "Koneksi internet tidak tersedia saat pengiriman streak.",
        "streak_verif_fail": "VERIFIKASI GAGAL: Chat aktif '{active}' != target '{target}'. Batal kirim demi keamanan.",
        "streak_select_all_checking": "[*] Mode SELECT ALL: Memeriksa {total} kontak chat DM...",
        "streak_skip_blacklist": "  [-] Melewati {name} (ada di daftar blacklist)",
        "streak_sending_to": "  [>] Mengirim streak ke {name} ('{msg}')...",
        "streak_sent_ok": "      [✓] Terkirim!",
        "streak_send_fail": "      [x] Gagal kirim pesan.",
        "streak_groups_processing": "[*] Mode GROUPS: Memproses {count} orang target...",
        "streak_groups_empty": "Mode Groups aktif, tetapi tidak ada anggota di dalam grup.",
        "streak_finding_contact": "  [>] Mencari kontak '{name}' (Pesan: '{msg}')...",
        "streak_contact_not_found": "      [x] Kontak '{name}' tidak ditemukan / gagal buka chat.",
        "streak_finished": "Selesai. {summary}",
        "streak_report_title": "📊 *Laporan Pengiriman Streak TikTok:*",
        "streak_report_success": "✅ *Berhasil ({count}):*",
        "streak_report_failed": "❌ *Gagal/Lewat ({count}):*",
        "recip_menu_title": "👥 Kelola Penerima & Pesan [Mode Aktif: {mode}]:",
        "recip_toggle_mode": "🔄 Ganti Mode Pengiriman (Saat ini: {mode})",
        "recip_checklist": "📋 Checklist Kontak & Tetapkan Grup (Interactive Multi-select)",
        "recip_groups": "🏷️  Kelola Label Grup",
        "recip_messages": "💬 Konfigurasi Pesan & Variasi (Default, Pool Acak & Khusus)",
        "recip_exclude": "🚫 Kelola Daftar Pengecualian (Blacklist / Exclude)",
        "recip_preview": "👁️  Pratinjau Pesan yang Akan Dikirim (Preview)",
        "recip_back": "🔙 Kembali ke Menu Utama",
        "recip_mode_changed": "\n[✓] Mode pengiriman diubah ke: {mode}\n",
        "sched_menu_title": "⏰ Pengatur Jadwal Harian [{os}] (Status: {icon} {desc}):",
        "sched_opt_install": "⏰ Pasang / Aktifkan Jadwal Harian (Jam {time} + Auto Catch-up)",
        "sched_opt_change_time": "🕒 Ubah Jam Eksekusi (Saat ini: Jam {time})",
        "sched_opt_remove": "🗑️  Matikan / Hapus Jadwal",
        "sched_prompt_new_time": "Masukkan jam baru (Format JJ:MM, contoh: 08:30):",
        "sched_time_changed": "\n[✓] Waktu jadwal diubah ke {time}.",
        "sched_time_invalid": "\n[!] Jam atau menit tidak valid.",
        "notif_menu_title": "🔔 Pengaturan Notifikasi ke HP:",
        "notif_telegram": "📱 Telegram Bot: {status}",
        "notif_discord": "💬 Discord Webhook: {status}",
        "notif_test_all": "🔔 Tes Semua Notifikasi Aktif",
        "notif_back": "🔙 Kembali ke Menu Utama",
        "notif_test_sending": "\n[*] Mengirim notifikasi tes ke semua channel aktif...",
        "notif_test_done": "[✓] Notifikasi tes selesai dikirim!\n",
        "status_active_upper": "🟢 AKTIF",
        "status_inactive_upper": "⚪ NONAKTIF",
        "account_menu_title": "🔑 Manajemen Akun & Kontak TikTok:",
        "account_opt_scan": "🔍 Pindai Kontak DM dari TikTok (Tersimpan: {count} kontak)",
        "account_opt_login": "🔑 Login / Hubungkan Akun TikTok (Buka Jendela Browser)",
        "account_opt_check": "ℹ️  Cek Ulang Status Sesi Login (Status: {status})",
        "account_opt_back": "🔙 Kembali ke Menu Utama",
        "logs_menu_title": "📜 Riwayat Aktivitas & Log (Retensi Otomatis 3 Hari):",
        "logs_opt_all": "📜 Lihat Semua Log (3 Hari Terakhir)",
        "logs_opt_job": "🚀 Filter Log Eksekusi Streak (JOB)",
        "logs_opt_config": "⚙️  Filter Perubahan Pengaturan (CONFIG)",
        "logs_opt_clean": "🧹 Bersihkan Log Manual Sekarang",
        "logs_opt_back": "🔙 Kembali ke Menu Utama",
        "logs_clean_confirm": "Hapus semua log aktivitas yang tersimpan sekarang?",
        "logs_cleaned": "\n[✓] Seluruh riwayat log berhasil dibersihkan!\n",
        "pool_menu_title": "📝 Daftar Variasi Pesan Acak (Pool):",
        "pool_empty": "  (Daftar pesan masih kosong)",
        "pool_opt_add": "➕ Tambah Variasi Pesan Baru",
        "pool_opt_preset": "📋 Tambah dari Template Preset Populer",
        "pool_opt_edit": "✏️  Edit Pesan yang Ada",
        "pool_opt_remove": "🗑️  Hapus Pesan dari Pool",
        "pool_opt_back": "🔙 Selesai / Kembali",
        "pool_add_hint": "\n💡 Variabel yang didukung:\n  {name}          = Nama lengkap kontak\n  {first_name}    = Nama depan kontak\n  {time_greeting} = Pagi / Siang / Sore / Malam\n  {day}           = Hari (Senin, Selasa, dll)\n  {date}          = Tanggal (contoh: 10 Nov)\n",
        "pool_prompt_new": "Tulis template pesan baru:",
        "pool_added": "[✓] Pesan berhasil ditambahkan ke pool!\n",
        "pool_preset_prompt": "Pilih template yang ingin dimasukkan ke pool:",
        "pool_updated": "[✓] Pool berhasil diperbarui ({count} variasi aktif).\n",
        "pool_edit_prompt": "Pilih pesan yang ingin diedit:",
        "pool_remove_prompt": "Pilih pesan yang ingin dihapus:",
        "overrides_title": "👤 Daftar Pesan Khusus per Kontak:",
        "overrides_empty": "  (Belum ada pesan khusus. Semua kontak memakai template default/pool)",
        "overrides_opt_add": "➕ Tetapkan Pesan Khusus untuk Kontak",
        "overrides_opt_remove": "🗑️  Hapus Pesan Khusus (Kembalikan ke Default)",
        "overrides_opt_back": "🔙 Selesai / Kembali",
        "preview_title": "👁️  PRATINJAU FORMAT PESAN STREAK (PREVIEW HASIL TEKS)",
        "preview_mode": " Mode Aktif : {mode}",
        "preview_to": "  Kepada: {name}{badge}",
        "preview_msg": "  Pesan : '{msg}'",
        "groups_title": "🏷️  DAFTAR GRUP & PESAN KHUSUS:",
        "groups_opt_add": "➕ Tambah Grup Baru",
        "groups_opt_edit": "✏️  Ubah Pesan Grup",
        "groups_opt_delete": "🗑️  Hapus Grup",
        "groups_opt_back": "🔙 Kembali",
        "exclude_title": "🚫 DAFTAR BLACKLIST / EXCLUDE (Dilewati di Mode All):",
        "exclude_opt_add": "➕ Tambah Akun ke Blacklist",
        "exclude_opt_remove": "🗑️  Hapus Akun dari Blacklist (Checklist)",
        "exclude_opt_back": "🔙 Kembali",
    }
}

def t(key: str, default: str = None, **kwargs) -> str:
    lang = CURRENT_LANG if CURRENT_LANG in TRANSLATIONS else DEFAULT_LANG
    s = TRANSLATIONS.get(lang, {}).get(key)
    if s is None:
        s = TRANSLATIONS.get(DEFAULT_LANG, {}).get(key, default if default is not None else key)
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s

def set_language(lang_code: str):
    global CURRENT_LANG
    if str(lang_code).lower() in ("id", "in", "indonesia", "indonesian"):
        CURRENT_LANG = "id"
    else:
        CURRENT_LANG = "en"

def handle_sigint(sig=None, frame=None):
    print(t("sigint_exit"))
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

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

    thread = threading.Thread(target=target, daemon=True)
    thread.start()

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
    """Checks latest update from server or GitHub."""
    import urllib.request

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

    update_data, _ = run_with_progress(t("checking_updates"), fetch_remote, timeout=3.5)

    if not update_data or "version" not in update_data:
        print(t("update_offline"))
        time.sleep(0.2)
        return

    latest_ver = update_data["version"]
    if parse_semver(latest_ver) <= parse_semver(APP_VERSION):
        print(t("update_latest", ver=APP_VERSION))
        time.sleep(0.3)
        if prompt_if_latest:
            print(t("update_already_latest", ver=APP_VERSION))
            import questionary
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        return

    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

    print("\n" + "=" * 62)
    print(t("update_available", current=APP_VERSION, latest=latest_ver))
    print(t("release_date", date=update_data.get('release_date', 'New')))
    print("=" * 62)
    print(t("changelog"))
    for change in update_data.get("changelog", []):
        print(f"  • {change}")
    print("=" * 62 + "\n")

    try:
        import questionary
        action = questionary.select(
            t("update_prompt"),
            choices=[
                t("update_opt_install"),
                t("update_opt_skip")
            ]
        ).ask()
    except Exception:
        action = input(f"{t('update_prompt')} [Y/n]: ").strip().lower()
        action = "yes" if action in ("", "y", "yes") else "no"

    if action and ("Install" in action or "Pasang" in action or action == "yes"):
        print(t("update_downloading", ver=latest_ver))
        download_url = update_data.get("download_url")
        if not download_url:
            print(t("update_no_url"))
            return

        try:
            req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0 (AutoUpdater)"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                new_code = resp.read().decode("utf-8")

            with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
                f.write(new_code)
            os.chmod(SCRIPT_PATH, 0o755)

            target_installed = INSTALL_DIR / "tiktok-streak.py"
            if target_installed.exists() and target_installed != SCRIPT_PATH:
                with open(target_installed, "w", encoding="utf-8") as f:
                    f.write(new_code)
                os.chmod(target_installed, 0o755)

            print(t("update_success", ver=latest_ver))
            print(t("restarting_app"))
            time.sleep(1)
            os.execv(sys.executable, [sys.executable, str(SCRIPT_PATH)] + sys.argv[1:])
        except Exception as e:
            print(t("update_failed", err=e))
            input(t("press_key_continue"))
    else:
        print(t("update_skipped"))

DEFAULT_CONFIG = {
    "language": "en",  # "en" (default) or "id"
    "mode": "all",  # "all" or "groups"
    "default_message": "🔥",
    "messages": {
        "mode": "pool",  # "pool" or "single"
        "pool": [
            "🔥",
            "Streak 🔥⚡",
            "Good {time_greeting} {first_name}! Streak 🔥",
            "Happy {day} {first_name}! 🔥",
            "Streak for today {first_name} 🔥✨"
        ],
        "append_random_emoji": False,
        "contact_overrides": {}
    },
    "safety": {
        "pace": "normal",
        "safe_hours": {
            "enabled": True,
            "start": 7,
            "end": 23
        }
    },
    "logging": {
        "retention_days": 3
    },
    "select_all": {
        "enabled": True,
        "message": "🔥",
        "exclude": ["TikTok", "TikTok Rewards", "TikTok Shop", "System Notification"]
    },
    "groups": {
        "Sahabat": {
            "enabled": True,
            "message": "🔥",
            "members": []
        },
        "Prioritas": {
            "enabled": True,
            "message": "🔥",
            "members": []
        },
        "Mutual": {
            "enabled": True,
            "message": "🔥",
            "members": []
        }
    },
    "current_account": "",
    "accounts": {},
    "streak_counts": {},
    "last_streak_dates": {},
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

def get_account_state(account: str = "") -> dict:
    state = load_state()
    if not account:
        try:
            cfg = load_config()
            account = cfg.get("current_account", "")
        except Exception:
            account = ""
    if account and "accounts" in state and account in state["accounts"]:
        return state["accounts"][account]
    return state

def save_state(success: bool, sent_count: int, failed_count: int, summary: str, session_expired: bool = None, sent_recipients: list = None, account: str = ""):
    state = load_state()
    today_str = str(date.today())
    if not account:
        try:
            cfg = load_config()
            account = cfg.get("current_account", "")
        except Exception:
            account = ""

    acc_state = {
        "last_attempt": datetime.now().isoformat(),
        "sent_count": sent_count,
        "failed_count": failed_count,
        "last_summary": summary,
        "session_expired": session_expired if session_expired is not None else False
    }
    if sent_recipients is not None:
        acc_state["sent_date"] = today_str
        acc_state["sent_recipients"] = list(sent_recipients)
    if success:
        acc_state["last_success_date"] = today_str
        acc_state["session_expired"] = False

    if account:
        state.setdefault("accounts", {})[account] = acc_state
        state["current_account"] = account

    state.update(acc_state)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# ==============================================================================
# Logging & 3-Day Retention Engine
# ==============================================================================

def clean_expired_logs(retention_days: int = 3):
    ensure_dirs()
    cutoff_date = date.today() - timedelta(days=retention_days)
    for log_path in LOGS_DIR.glob("activity_*.log"):
        try:
            date_part = log_path.stem.replace("activity_", "")
            file_date = datetime.strptime(date_part, "%Y-%m-%d").date()
            if file_date < cutoff_date:
                log_path.unlink()
        except Exception:
            pass

    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            valid_lines = []
            for line in lines:
                if line.startswith("["):
                    try:
                        line_date_str = line[1:11]
                        line_date = datetime.strptime(line_date_str, "%Y-%m-%d").date()
                        if line_date >= cutoff_date:
                            valid_lines.append(line)
                    except Exception:
                        valid_lines.append(line)
                else:
                    valid_lines.append(line)
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.writelines(valid_lines)
        except Exception:
            pass

def log_activity(category: str, message: str, print_to_console: bool = False):
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    formatted = f"[{timestamp}] [{category:<6}] {message}"

    if print_to_console:
        print(formatted)

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

    daily_file = LOGS_DIR / f"activity_{date_str}.log"
    try:
        with open(daily_file, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def log_message(msg: str):
    log_activity("JOB", msg, print_to_console=True)

# ==============================================================================
# Message Template Engine & Placeholders
# ==============================================================================

def format_message(template: str, contact_name: str) -> str:
    now = datetime.now()
    hour = now.hour

    if CURRENT_LANG == "id":
        if 5 <= hour < 11:
            time_greeting = "Pagi"
        elif 11 <= hour < 15:
            time_greeting = "Siang"
        elif 15 <= hour < 18:
            time_greeting = "Sore"
        else:
            time_greeting = "Malam"
        days_name = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        months_name = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    else:
        if 5 <= hour < 12:
            time_greeting = "Morning"
        elif 12 <= hour < 17:
            time_greeting = "Afternoon"
        elif 17 <= hour < 21:
            time_greeting = "Evening"
        else:
            time_greeting = "Night"
        days_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        months_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    day_name = days_name[now.weekday()]
    date_str = f"{now.day} {months_name[now.month - 1]}"
    first_name = contact_name.split()[0] if contact_name else ""

    text = template.replace("{name}", contact_name)
    text = text.replace("{first_name}", first_name)
    text = text.replace("{time_greeting}", time_greeting)
    text = text.replace("{day}", day_name)
    text = text.replace("{date}", date_str)
    return text

def resolve_message_for_contact(contact_name: str, group_msg: str = None) -> str:
    cfg = load_config()
    msg_cfg = cfg.get("messages", {})
    overrides = msg_cfg.get("contact_overrides", {})

    if contact_name in overrides and overrides[contact_name].strip():
        base_msg = overrides[contact_name].strip()
    elif group_msg and group_msg.strip() and group_msg != cfg.get("default_message", "🔥"):
        base_msg = group_msg.strip()
    elif msg_cfg.get("mode", "pool") == "pool" and msg_cfg.get("pool"):
        pool = [m for m in msg_cfg["pool"] if m.strip()]
        base_msg = random.choice(pool) if pool else cfg.get("default_message", "🔥")
    elif group_msg and group_msg.strip():
        base_msg = group_msg.strip()
    else:
        base_msg = cfg.get("default_message", "🔥")

    final_text = format_message(base_msg, contact_name)
    if msg_cfg.get("append_random_emoji", False):
        extra_emojis = ["🔥", "⚡", "✨", "💪", "🚀", "🌟"]
        final_text += " " + random.choice(extra_emojis)
    return final_text

# ==============================================================================
# Safety & Delay Helpers
# ==============================================================================

def get_message_delay() -> float:
    cfg = load_config()
    pace = cfg.get("safety", {}).get("pace", "normal")
    if pace == "fast":
        return random.uniform(1.2, 2.2)
    elif pace == "relaxed":
        return random.uniform(5.0, 8.0)
    else:  # normal
        return random.uniform(2.8, 4.5)

def get_click_delay() -> float:
    cfg = load_config()
    pace = cfg.get("safety", {}).get("pace", "normal")
    if pace == "fast":
        return random.uniform(0.8, 1.4)
    elif pace == "relaxed":
        return random.uniform(2.5, 4.0)
    else:  # normal
        return random.uniform(1.5, 2.5)

def is_within_safe_hours() -> tuple:
    cfg = load_config()
    safe_cfg = cfg.get("safety", {}).get("safe_hours", {})
    if not safe_cfg.get("enabled", True):
        return True, "Safe hours restriction disabled"

    now_hour = datetime.now().hour
    start = safe_cfg.get("start", 7)
    end = safe_cfg.get("end", 23)

    if start <= end:
        in_range = start <= now_hour < end
    else:
        in_range = now_hour >= start or now_hour < end

    if in_range:
        return True, "Within safe hours"
    else:
        reason = f"Outside safe dispatch hours ({start:02d}:00 - {end:02d}:00)" if CURRENT_LANG == "en" else f"Di luar jam aman pengiriman ({start:02d}:00 - {end:02d}:00)"
        return False, reason

def wait_for_internet(timeout: int = 180, check_interval: int = 3, verbose: bool = False) -> bool:
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
            sys.stdout.write(f"\r[*] {t('wait_internet')}... {spinner[step % len(spinner)]} [{bar}] {elapsed:.1f}s/{timeout}s")
            sys.stdout.flush()
            step += 1

        try:
            s = socket.create_connection(("1.1.1.1", 53), timeout=2)
            s.close()
            req = urllib.request.Request("https://www.google.com", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status in (200, 204, 301, 302):
                    if verbose:
                        sys.stdout.write(f"\r{' ' * 75}\r[✓] {t('internet_connected', elapsed=elapsed)}\n")
                        sys.stdout.flush()
                    return True
        except Exception:
            pass

        if elapsed >= 5 and (elapsed - last_logged >= 15):
            last_logged = elapsed

        time.sleep(check_interval)

    if verbose:
        sys.stdout.write(f"\r{' ' * 75}\r[!] {t('internet_failed', timeout=timeout)}\n")
        sys.stdout.flush()
    return False

# ==============================================================================
# Notifications (macOS Native, Telegram, Discord)
# ==============================================================================

def send_telegram_notification(bot_token: str, chat_id: str, title: str, text: str, success: bool) -> tuple:
    try:
        import requests
        import html
        icon = "✅" if success else "❌"
        safe_title = html.escape(title)
        safe_text = html.escape(text)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"{icon} <b>{safe_title}</b>\n\n{safe_text}\n\n<i>Time: {now_str}</i>"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}, timeout=10)
        data = resp.json()
        if data.get("ok"):
            return True, "Telegram notification sent successfully!"
        return False, f"Telegram API error: {data.get('description', 'Unknown')}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def send_discord_notification(webhook_url: str, title: str, text: str, success: bool) -> tuple:
    try:
        import requests
        color = 0x2ECC71 if success else 0xE74C3C
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "embeds": [{
                "title": f"{'✅' if success else '❌'} {title}",
                "description": text,
                "color": color,
                "footer": {"text": f"TikTok Streak Helper • {now_str}"}
            }]
        }
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code in (200, 204):
            return True, "Discord notification sent successfully!"
        return False, f"Discord Webhook error: HTTP {resp.status_code}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def send_notification(title: str, text: str, success: bool):
    cfg = load_config()
    notifs = cfg.get("notifications", {})

    if notifs.get("macos", {}).get("enabled", True) and OS_NAME == "Darwin":
        try:
            clean_text = text.replace(chr(34), chr(92) + chr(34)).replace(chr(10), " ")
            clean_title = title.replace('"', '\"')
            osa = f'display notification "{clean_text}" with title "{clean_title}"'
            subprocess.run(["osascript", "-e", osa], capture_output=True, timeout=5)
        except Exception:
            pass

    tg = notifs.get("telegram", {})
    if tg.get("enabled") and tg.get("bot_token") and tg.get("chat_id"):
        ok, msg = send_telegram_notification(tg["bot_token"], tg["chat_id"], title, text, success)
        log_activity("NOTIF", f"Telegram dispatch: {'Success' if ok else 'Failed'} ({msg})")

    dc = notifs.get("discord", {})
    if dc.get("enabled") and dc.get("webhook_url"):
        ok, msg = send_discord_notification(dc["webhook_url"], title, text, success)
        log_activity("NOTIF", f"Discord dispatch: {'Success' if ok else 'Failed'} ({msg})")

# ==============================================================================
# Auto-Scheduler (Windows Task Scheduler / macOS LaunchAgent / Linux Crontab)
# ==============================================================================

def get_scheduler_status() -> tuple:
    if OS_NAME == "Darwin":
        agents_dir = HOME_DIR / "Library/LaunchAgents"
        plist_path = agents_dir / "com.user.tiktok-streak.plist"
        old_plist = agents_dir / "com.user.tiktokstreak.plist"
        if plist_path.exists() or old_plist.exists():
            out = subprocess.run(["launchctl", "list"], capture_output=True, text=True).stdout
            if "tiktok" in out:
                return True, t("sched_macos_active")
            return True, t("sched_macos_loaded")
        return False, t("sched_not_configured")
    elif OS_NAME == "Windows":
        out = subprocess.run(["schtasks", "/query", "/tn", "TikTokStreakDaily"], capture_output=True, text=True).stdout
        if "TikTokStreakDaily" in out:
            return True, t("sched_win_active")
        return False, t("sched_not_configured")
    else:
        out = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        if "tiktok-streak" in out:
            return True, t("sched_linux_active")
        return False, t("sched_not_configured")

def install_scheduler():
    cfg = load_config()
    sched = cfg.get("schedule", {"hour": 9, "minute": 0})
    h = sched.get("hour", 9)
    m = sched.get("minute", 0)
    time_str = f"{h:02d}:{m:02d}"

    if OS_NAME == "Darwin":
        agents_dir = HOME_DIR / "Library/LaunchAgents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        plist_path = agents_dir / "com.user.tiktok-streak.plist"
        old_plist_path = agents_dir / "com.user.tiktokstreak.plist"

        # Clean up legacy plist if present
        if old_plist_path.exists():
            subprocess.run(["launchctl", "unload", str(old_plist_path)], capture_output=True)
            old_plist_path.unlink(missing_ok=True)

        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.tiktok-streak</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{SCRIPT_PATH}</string>
        <string>--cron</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{h}</integer>
        <key>Minute</key>
        <integer>{m}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{LOG_FILE}</string>
    <key>StandardErrorPath</key>
    <string>{LOG_FILE}</string>
</dict>
</plist>"""
        with open(plist_path, "w", encoding="utf-8") as f:
            f.write(content)

        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
        subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True)
        log_activity("CONFIG", f"macOS LaunchAgent registered at {time_str} (once per day)")
        print(t("sched_installed_mac", time=time_str))

    elif OS_NAME == "Windows":
        cmd = [
            "schtasks", "/create", "/tn", "TikTokStreakDaily",
            "/tr", f'"{sys.executable}" "{SCRIPT_PATH}" --cron',
            "/sc", "daily", "/st", time_str, "/f"
        ]
        subprocess.run(cmd, capture_output=True)
        log_activity("CONFIG", f"Windows Task Scheduler registered at {time_str}")
        print(t("sched_installed_win", time=time_str))

    else:
        curr = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        lines = [l for l in curr.splitlines() if "tiktok-streak" not in l]
        lines.append(f"{m} {h} * * * {sys.executable} {SCRIPT_PATH} --cron >> {LOG_FILE} 2>&1")
        new_cron = "\n".join(lines) + "\n"
        subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)
        log_activity("CONFIG", f"Linux Crontab registered at {time_str}")
        print(t("sched_installed_linux", time=time_str))

def remove_scheduler():
    if OS_NAME == "Darwin":
        agents_dir = HOME_DIR / "Library/LaunchAgents"
        for p in [agents_dir / "com.user.tiktok-streak.plist", agents_dir / "com.user.tiktokstreak.plist"]:
            if p.exists():
                subprocess.run(["launchctl", "unload", str(p)], capture_output=True)
                p.unlink(missing_ok=True)
        print(t("sched_removed_mac"))
    elif OS_NAME == "Windows":
        subprocess.run(["schtasks", "/delete", "/tn", "TikTokStreakDaily", "/f"], capture_output=True)
        print(t("sched_removed_win"))
    else:
        try:
            curr = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
            lines = [l for l in curr.splitlines() if "tiktok-streak" not in l]
            new_cron = "\n".join(lines) + "\n"
            subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)
            print(t("sched_removed_linux"))
        except Exception:
            pass

# ==============================================================================
# TikTok Browser Engine (Playwright)
# ==============================================================================

def check_login_status() -> bool:
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
        storage_state = list(PROFILE_DIR.glob("**/*Cookies*")) + list(PROFILE_DIR.glob("**/*storage*"))
        return len(storage_state) > 0

def get_logged_in_username(page) -> str:
    """Detects the currently logged in username from the TikTok web page DOM/Context."""
    try:
        uname = page.evaluate("""() => {
            const nav = document.querySelector('a[data-e2e="nav-profile"]');
            if (nav) {
                const href = nav.getAttribute("href") || "";
                const m = href.match(/\\/@([a-zA-Z0-9_.-]+)/);
                if (m) return m[1];
            }
            const profileLinks = document.querySelectorAll('header a[href*="/@"], div[class*="header"] a[href*="/@"]');
            for (let a of profileLinks) {
                const href = a.getAttribute("href") || "";
                const m = href.match(/\\/@([a-zA-Z0-9_.-]+)/);
                if (m) return m[1];
            }
            try {
                if (window.__UNIVERSAL_DATA_FOR_REHYDRATION__) {
                    const u = window.__UNIVERSAL_DATA_FOR_REHYDRATION__["__DEFAULT_SCOPE__"]["webapp.app-context"]?.user?.uniqueId;
                    if (u) return u;
                }
            } catch(e) {}
            return null;
        }""")
        return (uname or "").strip()
    except Exception:
        return ""

def sync_active_account(cfg: dict, detected_user: str) -> bool:
    """
    Syncs the active account configuration.
    If the detected account is different from cfg['current_account'],
    it archives the previous account state and switches to the detected account.
    Returns True if an account switch occurred.
    """
    if not detected_user:
        return False
    detected_user = detected_user.strip()
    accounts = cfg.setdefault("accounts", {})
    curr = cfg.get("current_account", "").strip()

    if curr == detected_user:
        accounts[detected_user] = {
            "contacts": list(cfg.get("contacts", [])),
            "recipients": list(cfg.get("recipients", [])),
            "usernames": dict(cfg.get("usernames", {})),
            "groups": dict(cfg.get("groups", {})),
            "streak_counts": dict(cfg.get("streak_counts", {})),
            "last_streak_dates": dict(cfg.get("last_streak_dates", {}))
        }
        save_config(cfg)
        return False

    if curr:
        accounts[curr] = {
            "contacts": list(cfg.get("contacts", [])),
            "recipients": list(cfg.get("recipients", [])),
            "usernames": dict(cfg.get("usernames", {})),
            "groups": dict(cfg.get("groups", {})),
            "streak_counts": dict(cfg.get("streak_counts", {})),
            "last_streak_dates": dict(cfg.get("last_streak_dates", {}))
        }
    elif not accounts and cfg.get("contacts"):
        accounts[detected_user] = {
            "contacts": list(cfg.get("contacts", [])),
            "recipients": list(cfg.get("recipients", [])),
            "usernames": dict(cfg.get("usernames", {})),
            "groups": dict(cfg.get("groups", {})),
            "streak_counts": dict(cfg.get("streak_counts", {})),
            "last_streak_dates": dict(cfg.get("last_streak_dates", {}))
        }
        cfg["current_account"] = detected_user
        save_config(cfg)
        return False

    cfg["current_account"] = detected_user
    if detected_user in accounts:
        acc_data = accounts[detected_user]
        cfg["contacts"] = list(acc_data.get("contacts", []))
        cfg["recipients"] = list(acc_data.get("recipients", []))
        cfg["usernames"] = dict(acc_data.get("usernames", {}))
        cfg["groups"] = dict(acc_data.get("groups", copy.deepcopy(DEFAULT_CONFIG["groups"])))
        cfg["streak_counts"] = dict(acc_data.get("streak_counts", {}))
        cfg["last_streak_dates"] = dict(acc_data.get("last_streak_dates", {}))
    else:
        cfg["contacts"] = []
        cfg["recipients"] = []
        cfg["usernames"] = {}
        cfg["groups"] = copy.deepcopy(DEFAULT_CONFIG["groups"])
        cfg["streak_counts"] = {}
        cfg["last_streak_dates"] = {}
        accounts[detected_user] = {
            "contacts": [],
            "recipients": [],
            "usernames": {},
            "groups": copy.deepcopy(DEFAULT_CONFIG["groups"]),
            "streak_counts": {},
            "last_streak_dates": {}
        }
    save_config(cfg)
    return True

def logout_session() -> bool:
    """Clears browser cookies and session to allow logging in with another TikTok account."""
    import shutil
    try:
        if PROFILE_DIR.exists():
            shutil.rmtree(PROFILE_DIR, ignore_errors=True)
            PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        st = load_state()
        st["session_expired"] = True
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[!] Error clearing session: {e}")
        return False

def launch_browser_context(p, headless: bool = True):
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    opts = {
        "user_data_dir": str(PROFILE_DIR),
        "headless": headless,
        "viewport": {"width": 1280, "height": 800},
        "args": ["--disable-blink-features=AutomationControlled"]
    }

    try:
        return p.chromium.launch_persistent_context(**opts)
    except Exception:
        pass

    try:
        opts_chrome = dict(opts)
        opts_chrome["channel"] = "chrome"
        return p.chromium.launch_persistent_context(**opts_chrome)
    except Exception:
        pass

    try:
        opts_edge = dict(opts)
        opts_edge["channel"] = "msedge"
        return p.chromium.launch_persistent_context(**opts_edge)
    except Exception:
        pass

    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=180,
        check=False
    )
    return p.chromium.launch_persistent_context(**opts)

def interactive_login():
    print("\n" + "=" * 58)
    print(t("login_title"))
    print("=" * 58)
    print(t("login_step_1"))
    print(t("login_step_2"))
    print(t("login_step_3"))
    print("=" * 58)
    input(t("login_press_enter"))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(t("login_playwright_missing"))
        return

    detected_user = ""
    with sync_playwright() as p:
        context = launch_browser_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.tiktok.com/login", wait_until="networkidle")

        input(t("login_wait_confirm"))
        try:
            page.goto("https://www.tiktok.com/messages", wait_until="networkidle", timeout=20000)
            time.sleep(2)
            detected_user = get_logged_in_username(page)
        except Exception:
            pass
        context.close()

    st = load_state()
    st["session_expired"] = False
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2, ensure_ascii=False)

    print(t("login_saved"))
    if detected_user:
        cfg = load_config()
        switched = sync_active_account(cfg, detected_user)
        print(f"👤 Logged in as: @{detected_user}" if CURRENT_LANG == "en" else f"👤 Login sebagai: @{detected_user}")
        if switched:
            print(f"🔄 Switched account profile to: @{detected_user}" if CURRENT_LANG == "en" else f"🔄 Profil akun beralih ke: @{detected_user}")
        if not cfg.get("contacts"):
            do_scan = questionary.confirm(
                "No contacts saved for this account. Scan DM contacts now?" if CURRENT_LANG == "en" else "Belum ada kontak tersimpan untuk akun ini. Pindai kontak DM sekarang?",
                default=True
            ).ask()
            if do_scan:
                scan_dm_contacts(verbose=True)

def scan_dm_contacts(verbose: bool = True) -> list:
    if verbose:
        print(t("scan_connecting"))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(t("login_playwright_missing"))
        return []

    cfg = load_config()
    detected_contacts = []
    usernames = cfg.setdefault("usernames", {})
    streak_counts = cfg.setdefault("streak_counts", {})
    detected_user = ""

    with sync_playwright() as p:
        try:
            context = launch_browser_context(p, headless=True)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://www.tiktok.com/messages", wait_until="networkidle", timeout=60000)
            time.sleep(4)

            if "login" in page.url:
                if verbose:
                    print(t("scan_expired"))
                context.close()
                return []

            detected_user = get_logged_in_username(page)
            if detected_user:
                switched = sync_active_account(cfg, detected_user)
                if switched and verbose:
                    print(f"[*] Account detected: @{detected_user}")
                usernames = cfg.setdefault("usernames", {})
                streak_counts = cfg.setdefault("streak_counts", {})

            # Harvest any profile links already rendered on the page
            try:
                page_map = page.evaluate("""() => {
                    const map = {};
                    const anchors = document.querySelectorAll('a[href*="/@"]');
                    for (let a of anchors) {
                        let href = a.getAttribute("href") || "";
                        let m = href.match(/\\/@([a-zA-Z0-9_.-]+)/);
                        if (m) {
                            let u = m[1];
                            let text = a.innerText.trim();
                            if (text && text.length > 0 && text.length < 35 && !text.includes("\\n")) {
                                map[text] = u;
                            }
                        }
                    }
                    return map;
                }""")
                if page_map and isinstance(page_map, dict):
                    usernames.update(page_map)
            except Exception:
                pass

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
                        if name not in usernames:
                            try:
                                it.click()
                                header_nick = page.locator('[data-e2e="dm-new-chat-nickname"]')
                                matched_header = False
                                for _ in range(6):
                                    time.sleep(0.4)
                                    if header_nick.count() > 0 and match_target_names(header_nick.first.inner_text().strip(), name):
                                        matched_header = True
                                        break
                                if matched_header:
                                    uname = page.evaluate("""() => {
                                        const u = document.querySelector('[data-e2e="chat-uniqueid"]');
                                        if (u && u.innerText) return u.innerText.replace(/^@/, "").trim();
                                        const a = document.querySelector('a[href*="/@"][data-discover]');
                                        if (a) {
                                            const m = a.getAttribute("href").match(/\\/@([a-zA-Z0-9_.-]+)/);
                                            if (m) return m[1];
                                        }
                                        return null;
                                    }""")
                                    if uname:
                                        usernames[name] = uname
                            except Exception:
                                pass

                page.mouse.wheel(0, 450)
                time.sleep(0.3)

            context.close()
        except Exception as e:
            if verbose:
                print(t("scan_failed", err=e))

    if detected_contacts:
        cfg["contacts"] = detected_contacts
        cfg["usernames"] = usernames
        for c in detected_contacts:
            if c not in streak_counts:
                streak_counts[c] = 1
        cfg["streak_counts"] = streak_counts
        if not cfg.get("recipients"):
            cfg["recipients"] = list(detected_contacts)
        if detected_user:
            sync_active_account(cfg, detected_user)
        else:
            save_config(cfg)

        if verbose:
            print(t("scan_found", count=len(detected_contacts)))
            print("-" * 55)
            for idx, name in enumerate(detected_contacts, 1):
                u = usernames.get(name)
                strk = streak_counts.get(name, 1)
                label = f"{name} (@{u})" if u and u.lower() != name.lower() else (f"@{u}" if u else name)
                print(f" {idx:2d}. {label:<38} [🔥 {strk}]")
            print("-" * 55)
    else:
        if verbose:
            print(t("scan_none"))

    return detected_contacts

def normalize_target_name(name: str) -> str:
    """Normalize names for comparison: lowercase, whitespace collapsed, and emoji stripped."""
    if not name:
        return ""
    cleaned = re.sub(r'[^\w\s]', '', name)
    return " ".join(cleaned.lower().split())

def match_target_names(name1: str, name2: str) -> bool:
    """Check if two names match either exactly or after emoji/whitespace normalization."""
    if not name1 or not name2:
        return False
    n1_raw = name1.strip().lower()
    n2_raw = name2.strip().lower()
    if n1_raw == n2_raw:
        return True
    n1_clean = normalize_target_name(name1)
    n2_clean = normalize_target_name(name2)
    if n1_clean and n2_clean and n1_clean == n2_clean:
        return True
    return False

def send_message_in_chat(page, message: str, expected_target: str = None) -> bool:
    try:
        if expected_target:
            cfg = load_config()
            expected_uname = cfg.get("usernames", {}).get(expected_target, "").lower().lstrip("@")
            header_nick = page.locator('[data-e2e="dm-new-chat-nickname"]')
            header_uniqueid = page.locator('[data-e2e="chat-uniqueid"]')
            matched = False
            active_name = ""
            active_uid = ""
            # Wait up to 5 seconds (10 x 0.5s) for the chat pane to switch to expected_target
            for _ in range(10):
                uid = ""
                if header_uniqueid.count() > 0:
                    uid = header_uniqueid.first.inner_text().strip().lower().lstrip("@")
                    active_uid = uid

                name = ""
                if header_nick.count() > 0:
                    name = header_nick.first.inner_text().strip()
                    active_name = name

                if expected_uname:
                    if uid:
                        if uid == expected_uname:
                            matched = True
                            break
                        else:
                            # Active chat uniqueId is different from expected_uname!
                            time.sleep(0.5)
                            continue
                    elif name and match_target_names(name, expected_target):
                        matched = True
                        break
                else:
                    if name and match_target_names(name, expected_target):
                        matched = True
                        if uid:
                            cfg.setdefault("usernames", {})[expected_target] = uid
                            save_config(cfg)
                        break

                time.sleep(0.5)

            if not matched:
                display_active = f"@{active_uid}" if active_uid else (active_name or "unknown")
                display_target = f"@{expected_uname}" if expected_uname else expected_target
                log_message(t("streak_verif_fail", active=display_active.lower(), target=display_target.lower()))
                return False

        chatbox = page.locator('[data-e2e="dm-new-chatbox"]')
        if chatbox.count() > 0:
            box = chatbox.locator('div[contenteditable="true"]').first
        else:
            box = page.locator('div[contenteditable="true"]').first

        box.wait_for(state="visible", timeout=8000)
        box.click()
        time.sleep(0.5)
        page.keyboard.insert_text(message)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(2)
        return True
    except Exception as e:
        log_message(f"Error sending message in chat: {e}")
        return False

def reset_conversation_list_scroll(page):
    try:
        first_item = page.locator('[data-e2e="dm-new-conversation-item"]').first
        if first_item.count() > 0:
            parent = first_item.locator('xpath=../..')
            parent.evaluate('e => { e.scrollTop = 0; }')
            time.sleep(0.4)
    except Exception:
        pass

def select_and_open_chat(page, target_name: str, max_scroll_attempts: int = 15) -> bool:
    cfg = load_config()
    expected_uname = cfg.get("usernames", {}).get(target_name, "").lower().lstrip("@")
    known_contacts = cfg.get("contacts", [])

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
                matches = match_target_names(current_nick, target_name)
                # Only fallback to username match if current_nick is NOT another known contact in the list
                if not matches and expected_uname:
                    if current_nick not in known_contacts:
                        if current_nick.lower().lstrip("@") == expected_uname:
                            matches = True
                        elif cfg.get("usernames", {}).get(current_nick, "").lower().lstrip("@") == expected_uname:
                            matches = True

                if matches:
                    nick_el.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    nick_el.click()

                    # Wait up to 3.5 seconds for chat header to match target
                    chat_header_nick = page.locator('[data-e2e="dm-new-chat-nickname"]')
                    chat_uniqueid = page.locator('[data-e2e="chat-uniqueid"]')
                    for _ in range(7):
                        time.sleep(0.5)
                        uid = ""
                        if chat_uniqueid.count() > 0:
                            uid = chat_uniqueid.first.inner_text().strip().lower().lstrip("@")
                        header_text = ""
                        if chat_header_nick.count() > 0:
                            header_text = chat_header_nick.first.inner_text().strip()

                        if expected_uname:
                            if uid:
                                if uid == expected_uname:
                                    return True
                            elif header_text and match_target_names(header_text, target_name):
                                return True
                        else:
                            if header_text and match_target_names(header_text, target_name):
                                if uid:
                                    cfg.setdefault("usernames", {})[target_name] = uid
                                    save_config(cfg)
                                return True

                    # Fallback click on parent item
                    item.click()
                    for _ in range(5):
                        time.sleep(0.4)
                        uid = ""
                        if chat_uniqueid.count() > 0:
                            uid = chat_uniqueid.first.inner_text().strip().lower().lstrip("@")
                        header_text = ""
                        if chat_header_nick.count() > 0:
                            header_text = chat_header_nick.first.inner_text().strip()

                        if expected_uname:
                            if uid:
                                if uid == expected_uname:
                                    return True
                            elif header_text and match_target_names(header_text, target_name):
                                return True
                        else:
                            if header_text and match_target_names(header_text, target_name):
                                if uid:
                                    cfg.setdefault("usernames", {})[target_name] = uid
                                    save_config(cfg)
                                return True

            # Scroll conversation list container
            try:
                first_item = page.locator('[data-e2e="dm-new-conversation-item"]').first
                if first_item.count() > 0:
                    first_item.hover()
                    parent = first_item.locator('xpath=../..')
                    parent.evaluate('e => { e.scrollTop += 400; }')
            except Exception:
                pass
            page.mouse.wheel(0, 400)
            time.sleep(0.4)

        if phase == 0:
            reset_conversation_list_scroll(page)
            time.sleep(0.5)

    return False

def get_active_recipients(cfg) -> list:
    contacts = cfg.get("contacts", [])
    if "recipients" in cfg:
        return [c for c in contacts if c in cfg["recipients"]]
    if cfg.get("mode") == "groups":
        group_members = set()
        for g in cfg.get("groups", {}).values():
            group_members.update(g.get("members", []))
        return [c for c in contacts if c in group_members]
    excludes = [x.lower() for x in cfg.get("select_all", {}).get("exclude", [])]
    return [c for c in contacts if c.lower() not in excludes]

def run_send_streak(force: bool = False, verbose: bool = True) -> dict:
    cfg = load_config()
    current_acc = cfg.get("current_account", "")
    acc_state = get_account_state(current_acc)
    today_str = str(date.today())

    if not force and acc_state.get("last_success_date") == today_str:
        msg = t("streak_already_sent_log", date=today_str)
        if verbose:
            print(f"[*] {msg}")
        return {"success": True, "message": msg, "sent": acc_state.get("sent_count", 0)}

    sent_today = set()
    if not force and acc_state.get("sent_date") == today_str:
        sent_today = set(acc_state.get("sent_recipients", []))

    default_msg = cfg.get("default_message", "🔥")

    log_message(t("streak_starting"))

    if not wait_for_internet(timeout=60, check_interval=3, verbose=verbose):
        err = t("streak_internet_fail")
        log_message(err)
        return {"success": False, "message": err, "sent": 0, "failed": 1}

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        err = t("login_playwright_missing")
        log_message(err)
        return {"success": False, "message": err}

    success_list = []
    fail_list = []
    is_auth_error = False

    with sync_playwright() as p:
        try:
            context = launch_browser_context(p, headless=cfg.get("headless", True))
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://www.tiktok.com/messages", wait_until="networkidle", timeout=60000)
            time.sleep(5)

            if "login" in page.url:
                is_auth_error = True
                raise Exception("Session expired. Please log in again via Account menu.")

            detected_user = get_logged_in_username(page)
            if detected_user:
                switched = sync_active_account(cfg, detected_user)
                if switched or detected_user != current_acc:
                    current_acc = detected_user
                    acc_state = get_account_state(current_acc)
                    if not force and acc_state.get("last_success_date") == today_str:
                        msg = t("streak_already_sent_log", date=today_str)
                        if verbose:
                            print(f"[*] {msg}")
                        context.close()
                        return {"success": True, "message": msg, "sent": acc_state.get("sent_count", 0)}
                    sent_today = set(acc_state.get("sent_recipients", [])) if (not force and acc_state.get("sent_date") == today_str) else set()
                if verbose:
                    print(f"[*] Active account: @{current_acc}")

            target_recipients = get_active_recipients(cfg)
            if not target_recipients:
                err = "No recipients selected. Please configure recipients in Manage Recipients menu." if CURRENT_LANG == "en" else "Tidak ada penerima yang dipilih. Silakan atur di menu Kelola Penerima."
                raise Exception(err)

            pending_recipients = [r for r in target_recipients if force or r not in sent_today]
            if not pending_recipients and not force:
                msg = t("streak_already_sent_log", date=today_str)
                if verbose:
                    print(f"[*] {msg}")
                save_state(True, len(target_recipients), 0, f"Sent: {len(target_recipients)}, Failed: 0", sent_recipients=list(sent_today), account=current_acc)
                context.close()
                return {"success": True, "message": msg, "sent": len(target_recipients)}

            if verbose:
                if sent_today:
                    print(f"[*] Dispatching streaks to {len(pending_recipients)} remaining recipients ({len(sent_today)} already sent today)...")
                else:
                    print(f"[*] Dispatching streaks to {len(target_recipients)} active recipients...")

            for target_name in target_recipients:
                if not force and target_name in sent_today:
                    if verbose:
                        print(f"  [-] Skipping {target_name} (Streak already sent today)")
                    continue

                final_msg = resolve_message_for_contact(target_name, group_msg=default_msg)
                if verbose:
                    print(t("streak_finding_contact", name=target_name, msg=final_msg))

                found = select_and_open_chat(page, target_name)
                if found:
                    time.sleep(get_click_delay())
                    if send_message_in_chat(page, final_msg, expected_target=target_name):
                        streak_counts = cfg.setdefault("streak_counts", {})
                        last_streak_dates = cfg.setdefault("last_streak_dates", {})
                        if target_name not in streak_counts:
                            current_n = 0
                            new_n = 1
                            streak_counts[target_name] = 1
                            last_streak_dates[target_name] = today_str
                        else:
                            current_n = int(streak_counts[target_name])
                            last_d = last_streak_dates.get(target_name)
                            if last_d != today_str:
                                new_n = current_n + 1
                                streak_counts[target_name] = new_n
                                last_streak_dates[target_name] = today_str
                            else:
                                new_n = current_n

                        save_config(cfg)
                        sent_today.add(target_name)
                        success_list.append(f"{target_name} ('{final_msg}') [🔥 {new_n}]")
                        log_activity("JOB", f"Streak sent to '{target_name}' -> '{final_msg}' [Streak 🔥 {current_n} ➔ {new_n}]")
                        if verbose:
                            print(f"      [✓] Sent ({final_msg})! [Streak 🔥 {current_n} ➔ {new_n}]")
                    else:
                        fail_list.append(target_name)
                        log_activity("ERROR", f"Failed to verify/send to '{target_name}'")
                        if verbose:
                            print(f"      [x] Failed to send message.")
                else:
                    fail_list.append(f"{target_name} (Not found)")
                    log_activity("ERROR", f"Contact '{target_name}' not found in DM")
                    if verbose:
                        print(t("streak_contact_not_found", name=target_name))
                time.sleep(get_message_delay())

            context.close()
        except Exception as e:
            err_text = str(e)
            if "Session expired" in err_text:
                is_auth_error = True
            fail_list.append(f"System Error: {err_text}")
            log_message(f"Error during streak run: {e}")

    all_targets_sent = all(t in sent_today for t in target_recipients)
    overall_success = all_targets_sent and len(fail_list) == 0
    total_sent = len(sent_today)
    summary = f"Sent: {total_sent}, Failed: {len(fail_list)}"
    save_state(overall_success, total_sent, len(fail_list), summary, session_expired=True if is_auth_error else None, sent_recipients=list(sent_today), account=current_acc)

    report = f"{t('streak_report_title')}\n"
    if current_acc:
        report += f"Account: @{current_acc}\n"
    if success_list:
        report += f"\n{t('streak_report_success', count=len(success_list))}\n- " + "\n- ".join(success_list)
    if fail_list:
        report += f"\n\n{t('streak_report_failed', count=len(fail_list))}\n- " + "\n- ".join(fail_list)

    if success_list or fail_list:
        send_notification(
            title=f"TikTok Streak Saver (@{current_acc})" if current_acc else "TikTok Streak Saver",
            text=report,
            success=overall_success
        )

    log_message(t("streak_finished", summary=summary))
    return {
        "success": overall_success,
        "message": summary,
        "sent": total_sent,
        "failed": len(fail_list),
        "is_auth_error": is_auth_error
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
        print(f"│  {t('dash_warn_unauthed_title'):<52} │")
        print(f"│  {t('dash_warn_unauthed_desc1'):<52} │")
        print(f"│  {t('dash_warn_unauthed_desc2'):<52} │")
        print("╰" + "─" * 56 + "╯\n")

    contacts = cfg.get("contacts", [])
    active_recips = get_active_recipients(cfg)
    msg_cfg = cfg.get("messages", {})
    msg_mode = t("dash_msg_mode_pool") if msg_cfg.get("mode", "pool") == "pool" else t("dash_msg_mode_fixed", msg=cfg.get('default_message', '🔥'))
    pace_name = cfg.get("safety", {}).get("pace", "normal").capitalize()
    retention = cfg.get("logging", {}).get("retention_days", 3)

    print("\n" + "=" * 58)
    print(t("dash_title"))
    print("=" * 58)
    curr_user = cfg.get("current_account", "")
    user_suffix = f" (@{curr_user})" if curr_user else ""
    print(f"{t('dash_account_status')}{t('dash_status_valid') if is_logged_in else t('dash_status_unauthed')}{user_suffix}")
    if has_run_today:
        print(f"{t('dash_today_status')}{t('dash_today_sent', count=state.get('sent_count', 0))}")
    else:
        last_attempt = state.get("last_attempt", "")
        if last_attempt.startswith(today_str) and state.get("failed_count", 0) > 0:
            print(f"{t('dash_today_status')}{t('dash_today_failed', summary=state.get('last_summary', ''))}")
            print(t("dash_today_failed_hint"))
        else:
            print(f"{t('dash_today_status')}{t('dash_today_pending')}")
    print(f"{t('dash_recipient_mode')}{len(active_recips)} active / {len(contacts)} total (Checklist)")
    print(f"{t('dash_config')}{msg_mode} | ⚡ Pace: {pace_name}")
    print(f"{t('dash_sched')}{'🟢' if is_sched_active else '⚪'} {sched_desc}")
    print(t("dash_logs", days=retention))
    print("=" * 58 + "\n")

def menu_manage_recipients():
    while True:
        cfg = load_config()
        contacts = cfg.get("contacts", [])
        active_recipients = get_active_recipients(cfg)
        usernames = cfg.get("usernames", {})
        streak_counts = cfg.setdefault("streak_counts", {})
        last_streak_dates = cfg.setdefault("last_streak_dates", {})
        today_str = str(date.today())

        def format_recipient_label(name):
            u = usernames.get(name)
            strk = streak_counts.get(name, 1)
            streak_badge = f"🔥 {strk}"
            if u and u.lower() != name.lower():
                return f"{name} (@{u}) [{streak_badge}]"
            elif u:
                return f"@{u} [{streak_badge}]"
            return f"{name} [{streak_badge}]"

        choices = [
            Choice(
                f"☑️  Select Recipients ({len(active_recipients)} of {len(contacts)} active)" if CURRENT_LANG == "en" else f"☑️  Pilih Penerima ({len(active_recipients)} dari {len(contacts)} aktif)",
                value="checklist"
            ),
            Choice("⚡ Set Dispatch Speed (Pace)" if CURRENT_LANG == "en" else "⚡ Atur Kecepatan Pengiriman Pesan", value="speed"),
            Choice("✏️  Edit / Set Contact Username" if CURRENT_LANG == "en" else "✏️  Atur / Ubah Username Kontak", value="edit_username"),
            Choice("💬 Edit Default Streak Message" if CURRENT_LANG == "en" else "💬 Ubah Pesan Default Streak", value="message"),
            Choice("👁️  Preview Recipient List & Streaks (🔥)" if CURRENT_LANG == "en" else "👁️  Lihat Daftar Penerima & Jumlah Api (🔥)", value="preview"),
            Choice("🔥 Manage / Calibrate Streak Counts (Api)" if CURRENT_LANG == "en" else "🔥 Atur / Kalibrasi Jumlah Api (Streak 🔥)", value="manage_streaks"),
            Separator(),
            Choice(t("recip_back"), value="back")
        ]

        action = questionary.select(
            "Manage Streak Recipients:" if CURRENT_LANG == "en" else "Kelola Penerima Streak:",
            choices=choices
        ).ask()

        if action in ("back", None):
            break
        elif action == "speed":
            menu_safety_settings()
        elif action == "manage_streaks":
            menu_manage_streak_counts()
        elif action == "checklist":
            if not contacts:
                print("\n[!] No contacts saved. Please scan contacts in Account menu first.\n" if CURRENT_LANG == "en" else "\n[!] Belum ada kontak yang tersimpan. Silakan pilih 'Pindai Kontak' di Menu Akun terlebih dahulu.\n")
                questionary.press_any_key_to_continue(t("press_key_return")).ask()
                continue

            choices_c = [
                Choice(title=format_recipient_label(c), value=c, checked=(c in active_recipients))
                for c in contacts
            ]

            print("\n💡 Controls: [Space] Toggle, [a] Select All / Invert, [Enter] Save\n" if CURRENT_LANG == "en" else "\n💡 Navigasi: [Spasi] Pilih, [a] Pilih Semua, [Enter] Simpan\n")

            selected = questionary.checkbox(
                "Select contacts who will receive streaks:" if CURRENT_LANG == "en" else "Pilih kontak yang akan menerima streak:",
                choices=choices_c,
                instruction="(Space: toggle, a: all, Enter: save)" if CURRENT_LANG == "en" else "(Spasi: pilih, a: semua, Enter: simpan)"
            ).ask()

            if selected is not None:
                cfg["recipients"] = list(selected)
                curr_acc = cfg.get("current_account", "")
                if curr_acc:
                    sync_active_account(cfg, curr_acc)
                else:
                    save_config(cfg)
                print(f"\n[✓] Saved! {len(selected)} of {len(contacts)} contacts selected to receive streaks.\n" if CURRENT_LANG == "en" else f"\n[✓] Tersimpan! {len(selected)} dari {len(contacts)} kontak dipilih menerima streak.\n")
                questionary.press_any_key_to_continue(t("press_key_return")).ask()

        elif action == "edit_username":
            if not contacts:
                print("\n[!] No contacts saved.\n" if CURRENT_LANG == "en" else "\n[!] Belum ada kontak tersimpan.\n")
                questionary.press_any_key_to_continue(t("press_key_return")).ask()
                continue
            contact_choices = [
                Choice(title=format_recipient_label(c), value=c)
                for c in contacts
            ] + [Separator(), Choice(t("recip_back"), value="back")]
            chosen = questionary.select(
                "Select contact to set/edit username:" if CURRENT_LANG == "en" else "Pilih kontak untuk atur/ubah username:",
                choices=contact_choices
            ).ask()
            if chosen and chosen != "back":
                current_u = usernames.get(chosen, "")
                new_u = questionary.text(
                    f"Username for '{chosen}':" if CURRENT_LANG == "en" else f"Username untuk '{chosen}':",
                    default=current_u
                ).ask()
                if new_u is not None:
                    new_u = new_u.strip().lstrip("@")
                    if new_u:
                        cfg.setdefault("usernames", {})[chosen] = new_u
                    elif chosen in cfg.get("usernames", {}):
                        del cfg["usernames"][chosen]
                    curr_acc = cfg.get("current_account", "")
                    if curr_acc:
                        sync_active_account(cfg, curr_acc)
                    else:
                        save_config(cfg)
                    print("\n[✓] Username updated!\n" if CURRENT_LANG == "en" else "\n[✓] Username berhasil diperbarui!\n")
                    questionary.press_any_key_to_continue(t("press_key_return")).ask()

        elif action == "message":
            curr_def = cfg.get("default_message", "🔥")
            new_def = questionary.text("Default Streak Message:" if CURRENT_LANG == "en" else "Pesan Default Streak:", default=curr_def).ask()
            if new_def:
                cfg["default_message"] = new_def
                save_config(cfg)
                print("\n[✓] Saved!\n")

        elif action == "preview":
            print("\n" + "=" * 76)
            print("📋 ACTIVE RECIPIENTS & STREAK COUNT (🔥):" if CURRENT_LANG == "en" else "📋 DAFTAR PENERIMA & JUMLAH API (STREAK 🔥):")
            print("=" * 76)
            print(f" {'No':<3} {'Nama Kontak':<26} {'Username':<18} {'Api/Streak':<12} {'Status':<15}")
            print("-" * 76)
            for idx, c in enumerate(contacts, 1):
                status = "✅ YES" if c in active_recipients else "❌ SKIP"
                u = usernames.get(c, "-")
                u_str = f"@{u}" if u != "-" else "-"
                strk = streak_counts.get(c, 1)
                last_d = last_streak_dates.get(c, "-")
                d_info = f"({last_d})" if last_d != "-" else "(Belum pernah)"
                print(f" {idx:2d}. {c:<26} {u_str:<18} 🔥 {strk:<9} {status:<8} {d_info}")
            print("=" * 76 + "\n")
            questionary.press_any_key_to_continue(t("press_key_return")).ask()

def menu_manage_streak_counts():
    while True:
        cfg = load_config()
        contacts = cfg.get("contacts", [])
        usernames = cfg.get("usernames", {})
        streak_counts = cfg.setdefault("streak_counts", {})
        last_streak_dates = cfg.setdefault("last_streak_dates", {})
        today_str = str(date.today())

        if not contacts:
            print("\n[!] No contacts saved. Please scan contacts first.\n" if CURRENT_LANG == "en" else "\n[!] Belum ada kontak tersimpan. Silakan pindai kontak terlebih dahulu.\n")
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
            break

        choices = [
            Choice("📋 View Streak Counts Table" if CURRENT_LANG == "en" else "📋 Lihat Tabel Jumlah Api / Streak", value="table"),
            Choice("✏️  Calibrate Contact Streak Count" if CURRENT_LANG == "en" else "✏️  Kalibrasi / Ubah Jumlah Api Kontak", value="edit_one"),
            Choice("🔢 Set Default Streak Count for All Contacts" if CURRENT_LANG == "en" else "🔢 Setel Angka Api untuk Semua Kontak Sekaligus", value="set_all"),
            Choice("🔄 Reset Streak Count for Contact" if CURRENT_LANG == "en" else "🔄 Reset / Nolkan Streak Kontak", value="reset_one"),
            Separator(),
            Choice(t("recip_back"), value="back")
        ]

        action = questionary.select(
            "Manage / Calibrate Streak Counts (🔥):" if CURRENT_LANG == "en" else "Kelola / Kalibrasi Jumlah Api (Streak 🔥):",
            choices=choices
        ).ask()

        if action in ("back", None):
            break

        elif action == "table":
            print("\n" + "=" * 76)
            print("🔥 PREVIEW JUMLAH API / STREAK KONTAK" if CURRENT_LANG != "en" else "🔥 CONTACT STREAK COUNTS PREVIEW")
            print("=" * 76)
            print(f" {'No':<3} {'Nama Kontak':<26} {'Username':<18} {'Api/Streak':<12} {'Status Hari Ini':<15}")
            print("-" * 76)
            for idx, c in enumerate(contacts, 1):
                u = usernames.get(c, "-")
                u_str = f"@{u}" if u != "-" else "-"
                strk = streak_counts.get(c, 1)
                last_d = last_streak_dates.get(c, "-")
                status = "✅ Terkirim" if last_d == today_str else "⌛ Belum"
                print(f" {idx:2d}. {c:<26} {u_str:<18} 🔥 {strk:<9} {status} ({last_d})")
            print("=" * 76 + "\n")
            questionary.press_any_key_to_continue(t("press_key_return")).ask()

        elif action == "edit_one":
            contact_choices = [
                Choice(
                    title=f"{c} (@{usernames.get(c, '-')}) [🔥 {streak_counts.get(c, 1)}]",
                    value=c
                )
                for c in contacts
            ] + [Separator(), Choice(t("recip_back"), value="back")]

            chosen = questionary.select(
                "Select contact to calibrate streak count:" if CURRENT_LANG == "en" else "Pilih kontak yang ingin dikalibrasi jumlah apinya:",
                choices=contact_choices
            ).ask()

            if chosen and chosen != "back":
                current_val = streak_counts.get(chosen, 1)
                new_val_str = questionary.text(
                    f"New streak count for '{chosen}' (e.g. from your TikTok app):" if CURRENT_LANG == "en" else f"Jumlah api baru untuk '{chosen}' (sesuai app TikTok):",
                    default=str(current_val)
                ).ask()
                if new_val_str and new_val_str.isdigit():
                    new_val = int(new_val_str)
                    streak_counts[chosen] = new_val
                    cfg["streak_counts"] = streak_counts
                    curr_acc = cfg.get("current_account", "")
                    if curr_acc:
                        sync_active_account(cfg, curr_acc)
                    else:
                        save_config(cfg)
                    print(f"\n[✓] Streak for '{chosen}' calibrated to: 🔥 {new_val}\n" if CURRENT_LANG == "en" else f"\n[✓] Jumlah api untuk '{chosen}' berhasil diubah ke: 🔥 {new_val}\n")
                    questionary.press_any_key_to_continue(t("press_key_return")).ask()

        elif action == "set_all":
            val_str = questionary.text(
                "Set streak count for ALL contacts (e.g. 1):" if CURRENT_LANG == "en" else "Masukkan angka streak untuk SEMUA kontak sekaligus (misal: 1):",
                default="1"
            ).ask()
            if val_str and val_str.isdigit():
                val = int(val_str)
                for c in contacts:
                    streak_counts[c] = val
                cfg["streak_counts"] = streak_counts
                curr_acc = cfg.get("current_account", "")
                if curr_acc:
                    sync_active_account(cfg, curr_acc)
                else:
                    save_config(cfg)
                print(f"\n[✓] All {len(contacts)} contacts set to: 🔥 {val}\n" if CURRENT_LANG == "en" else f"\n[✓] Seluruh {len(contacts)} kontak berhasil diatur ke: 🔥 {val}\n")
                questionary.press_any_key_to_continue(t("press_key_return")).ask()

        elif action == "reset_one":
            contact_choices = [
                Choice(
                    title=f"{c} (@{usernames.get(c, '-')}) [🔥 {streak_counts.get(c, 1)}]",
                    value=c
                )
                for c in contacts
            ] + [Separator(), Choice(t("recip_back"), value="back")]

            chosen = questionary.select(
                "Select contact to reset streak count:" if CURRENT_LANG == "en" else "Pilih kontak untuk di-reset:",
                choices=contact_choices
            ).ask()

            if chosen and chosen != "back":
                streak_counts[chosen] = 0
                if chosen in last_streak_dates:
                    del last_streak_dates[chosen]
                cfg["streak_counts"] = streak_counts
                cfg["last_streak_dates"] = last_streak_dates
                curr_acc = cfg.get("current_account", "")
                if curr_acc:
                    sync_active_account(cfg, curr_acc)
                else:
                    save_config(cfg)
                print(f"\n[✓] Streak for '{chosen}' reset to: 0\n" if CURRENT_LANG == "en" else f"\n[✓] Streak untuk '{chosen}' di-reset ke: 0\n")
                questionary.press_any_key_to_continue(t("press_key_return")).ask()

def menu_safety_settings():
    while True:
        cfg = load_config()
        safety = cfg.setdefault("safety", {})
        pace = safety.get("pace", "normal")
        safe_hours = safety.get("safe_hours", {"enabled": True, "start": 7, "end": 23})
        headless = cfg.get("headless", True)

        pace_label = {
            "fast": "🚀 Fast (1.2 - 2.2s)" if CURRENT_LANG == "en" else "🚀 Cepat (1.2 - 2.2 detik)",
            "normal": "⚡ Normal / Natural (2.8 - 4.5s)" if CURRENT_LANG == "en" else "⚡ Normal / Natural (2.8 - 4.5 detik)",
            "relaxed": "🛡️ Relaxed / Anti-Limit (5.0 - 8.0s)" if CURRENT_LANG == "en" else "🛡️ Santai / Anti-Limit (5.0 - 8.0 detik)"
        }.get(pace, "⚡ Normal (2.8 - 4.5s)")

        sh_status = (f"🟢 Active ({safe_hours.get('start', 7):02d}:00 - {safe_hours.get('end', 23):02d}:00)" if CURRENT_LANG == "en" else f"🟢 Aktif ({safe_hours.get('start', 7):02d}:00 - {safe_hours.get('end', 23):02d}:00)") if safe_hours.get("enabled", True) else ("⚪ Disabled" if CURRENT_LANG == "en" else "⚪ Nonaktif")
        hl_status = ("🟢 Background (Headless)" if CURRENT_LANG == "en" else "🟢 Latar Belakang (Headless)") if headless else ("🖥️ Visible Window" if CURRENT_LANG == "en" else "🖥️ Jendela Terlihat")

        choices = [
            Choice(f"⚡ {'Dispatch Speed / Pace:' if CURRENT_LANG == 'en' else 'Kecepatan Pengiriman:'} {pace_label}", value="change_pace"),
            Choice(f"🌙 {'Safe Dispatch Hours:' if CURRENT_LANG == 'en' else 'Batas Jam Aman:'} {sh_status}", value="toggle_safe_hours"),
            Choice(f"🖥️  {'Browser Window Mode:' if CURRENT_LANG == 'en' else 'Mode Jendela Browser:'} {hl_status}", value="toggle_headless"),
            Separator(),
            Choice(t("recip_back"), value="back")
        ]

        action = questionary.select(
            "⚙️  Dispatch Speed & Safety Settings:" if CURRENT_LANG == "en" else "⚙️  Pengaturan Kecepatan & Keamanan Pengiriman:",
            choices=choices
        ).ask()

        if action in ("back", None):
            break

        if action == "change_pace":
            new_pace = questionary.select(
                "Select message dispatch speed / delay between contacts:" if CURRENT_LANG == "en" else "Pilih kecepatan jeda pengiriman pesan antar kontak:",
                choices=[
                    Choice("⚡ Normal / Natural (2.8 - 4.5s) [Recommended]" if CURRENT_LANG == "en" else "⚡ Normal / Natural (Jeda 2.8 - 4.5 detik) [Direkomendasikan]", value="normal"),
                    Choice("🚀 Fast (1.2 - 2.2s) [Faster dispatch]" if CURRENT_LANG == "en" else "🚀 Cepat (Jeda 1.2 - 2.2 detik) [Pengiriman lebih cepat]", value="fast"),
                    Choice("🛡️ Relaxed (5.0 - 8.0s) [Maximum safety / anti-limit]" if CURRENT_LANG == "en" else "🛡️ Santai (Jeda 5.0 - 8.0 detik) [Aman maksimal anti-limit]", value="relaxed")
                ]
            ).ask()
            if new_pace:
                cfg.setdefault("safety", {})["pace"] = new_pace
                save_config(cfg)
                log_activity("CONFIG", f"Dispatch speed updated to: {new_pace.upper()}")
                print(f"\n[✓] {'Dispatch speed updated to:' if CURRENT_LANG == 'en' else 'Kecepatan pengiriman diubah ke:'} {new_pace.upper()}\n")
                questionary.press_any_key_to_continue(t("press_key_return")).ask()

        elif action == "toggle_safe_hours":
            is_enabled = safe_hours.get("enabled", True)
            toggle_choice = questionary.select(
                "Safe Hours Settings:" if CURRENT_LANG == "en" else "Pengaturan Batas Jam Aman:",
                choices=[
                    Choice(f"{'⚪ Disable' if is_enabled else '🟢 Enable'} Safe Hours" if CURRENT_LANG == "en" else f"{'⚪ Matikan' if is_enabled else '🟢 Aktifkan'} Batas Jam Aman", value="toggle"),
                    Choice("🕒 Change Safe Hours Range" if CURRENT_LANG == "en" else "🕒 Ubah Rentang Jam Aman", value="edit_hours"),
                    Choice("🔙 Cancel" if CURRENT_LANG == "en" else "🔙 Batal", value="back")
                ]
            ).ask()
            if toggle_choice == "toggle":
                safe_hours["enabled"] = not is_enabled
                cfg.setdefault("safety", {})["safe_hours"] = safe_hours
                save_config(cfg)
                status = "ENABLED" if safe_hours["enabled"] else "DISABLED"
                log_activity("CONFIG", f"Safe hours changed to: {status}")
                print(f"\n[✓] Safe hours: {status}\n")
                questionary.press_any_key_to_continue(t("press_key_return")).ask()
            elif toggle_choice == "edit_hours":
                s_str = questionary.text("Start hour (0-23):" if CURRENT_LANG == "en" else "Mulai jam berapa (0-23):", default=str(safe_hours.get("start", 7))).ask()
                e_str = questionary.text("End hour (0-23):" if CURRENT_LANG == "en" else "Sampai jam berapa (0-23):", default=str(safe_hours.get("end", 23))).ask()
                try:
                    s_int = int(s_str)
                    e_int = int(e_str)
                    if 0 <= s_int <= 23 and 0 <= e_int <= 23:
                        safe_hours["start"] = s_int
                        safe_hours["end"] = e_int
                        cfg.setdefault("safety", {})["safe_hours"] = safe_hours
                        save_config(cfg)
                        print(f"\n[✓] Safe hours range updated: {s_int:02d}:00 - {e_int:02d}:00\n")
                        questionary.press_any_key_to_continue(t("press_key_return")).ask()
                except ValueError:
                    print("\n[!] Invalid hour format.\n")

        elif action == "toggle_headless":
            cfg["headless"] = not headless
            save_config(cfg)
            status = "HEADLESS (Background)" if cfg["headless"] else "VISIBLE WINDOW"
            log_activity("CONFIG", f"Browser mode changed to: {status}")
            print(f"\n[✓] Browser display mode: {status}\n")
            questionary.press_any_key_to_continue(t("press_key_return")).ask()

def menu_manage_scheduler():
    while True:
        is_active, desc = get_scheduler_status()
        cfg = load_config()
        sched = cfg.get("schedule", {"hour": 9, "minute": 0})
        time_str = f"{sched['hour']:02d}:{sched['minute']:02d}"

        choices = [
            Choice(t("sched_opt_install", time=time_str), value="install"),
            Choice(t("sched_opt_change_time", time=time_str), value="change_time"),
            Choice(t("sched_opt_remove"), value="remove"),
            Separator(),
            Choice("🔙 Back to Main Menu" if CURRENT_LANG == "en" else "🔙 Kembali ke Menu Utama", value="back")
        ]

        action = questionary.select(
            t("sched_menu_title", os=OS_NAME, icon='🟢' if is_active else '⚪', desc=desc),
            choices=choices
        ).ask()

        if action in ("back", None):
            break
        elif action == "install":
            install_scheduler()
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        elif action == "change_time":
            new_time = questionary.text(
                t("sched_prompt_new_time"),
                default=time_str
            ).ask()
            if new_time and ":" in new_time:
                try:
                    h, m = map(int, new_time.split(":", 1))
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        cfg["schedule"] = {"hour": h, "minute": m}
                        save_config(cfg)
                        print(t("sched_time_changed", time=f"{h:02d}:{m:02d}"))
                        if is_active:
                            install_scheduler()
                    else:
                        print(t("sched_time_invalid"))
                except ValueError:
                    print(t("sched_time_invalid"))
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        elif action == "remove":
            remove_scheduler()
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def show_telegram_guide():
    print("\n" + "=" * 62)
    if CURRENT_LANG == "en":
        print("📖 Telegram Bot Quick Integration Guide (1 Minute):")
        print("=" * 62)
        print("1. Open Telegram on your Phone or Laptop.")
        print("2. Search for @BotFather (verified official bot).")
        print("3. Send /newbot command and follow instructions:")
        print("   -> Set bot display name (e.g., 'Streak Helper')")
        print("   -> Set bot username ending in 'bot' (e.g., 'sam_streak_bot')")
        print("   -> BotFather will provide your HTTP API Token.")
        print("4. Get your personal Chat ID:")
        print("   -> Search @userinfobot on Telegram, click Start.")
        print("   -> It immediately replies with your 'Id: 123456789' (Chat ID).")
        print("5. CRITICAL: Open your created bot (step 3) and click START!")
    else:
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
    print("=" * 62 + "\n")
    questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def menu_telegram_settings():
    while True:
        cfg = load_config()
        tg = cfg.setdefault("notifications", {}).setdefault("telegram", {})
        enabled = tg.get("enabled", False)
        token = tg.get("bot_token", "")
        chat_id = tg.get("chat_id", "")
        masked_token = (token[:6] + "..." + token[-4:]) if len(token) > 10 else (token or "(Not set)" if CURRENT_LANG == "en" else "(Belum diisi)")

        print("\n" + "=" * 58)
        print("📱 Telegram Bot Settings:" if CURRENT_LANG == "en" else "📱 Pengaturan Telegram Bot:")
        print(f"   Status      : {t('status_active_upper') if enabled else t('status_inactive_upper')}")
        print(f"   Bot Token   : {masked_token}")
        print(f"   Chat ID     : {chat_id or ('(Not set)' if CURRENT_LANG == "en" else '(Belum diisi)')}")
        print("=" * 58 + "\n")

        choices = [
            Choice(f"🔄 {'Disable' if enabled else 'Enable'} Telegram Notifications" if CURRENT_LANG == "en" else f"🔄 {'Nonaktifkan' if enabled else 'Aktifkan'} Notifikasi Telegram", value="toggle"),
            Choice("✏️  Configure Bot Token & Chat ID" if CURRENT_LANG == "en" else "✏️  Atur / Ubah Bot Token & Chat ID", value="edit"),
            Choice("🔔 Test Send Notification Now" if CURRENT_LANG == "en" else "🔔 Tes Kirim Notifikasi ke Telegram Sekarang", value="test"),
            Choice("📖 Integration Guide" if CURRENT_LANG == "en" else "📖 Panduan Cara Buat Bot & Dapatkan Chat ID", value="guide"),
            Separator(),
            Choice("🔙 Back" if CURRENT_LANG == "en" else "🔙 Kembali", value="back")
        ]

        action = questionary.select("Select Action:" if CURRENT_LANG == "en" else "Pilih Aksi Telegram:", choices=choices).ask()
        if action in ("back", None):
            break
        elif action == "toggle":
            tg["enabled"] = not enabled
            if tg["enabled"] and (not token or not chat_id):
                new_token = questionary.text("Enter Telegram Bot Token:" if CURRENT_LANG == "en" else "Masukkan Telegram Bot Token:", default=token).ask()
                new_id = questionary.text("Enter Telegram Chat ID:" if CURRENT_LANG == "en" else "Masukkan Telegram Chat ID:", default=chat_id).ask()
                if new_token:
                    tg["bot_token"] = new_token.strip()
                if new_id:
                    tg["chat_id"] = new_id.strip()
            save_config(cfg)
            log_activity("CONFIG", f"Telegram Bot status changed to: {'ACTIVE' if tg['enabled'] else 'INACTIVE'}")
            print(f"\n[✓] Telegram: {t('status_active_upper') if tg['enabled'] else t('status_inactive_upper')}\n")
        elif action == "edit":
            new_token = questionary.text("Enter Telegram Bot Token:" if CURRENT_LANG == "en" else "Masukkan Telegram Bot Token:", default=token).ask()
            new_id = questionary.text("Enter Telegram Chat ID:" if CURRENT_LANG == "en" else "Masukkan Telegram Chat ID:", default=chat_id).ask()
            if new_token is not None:
                tg["bot_token"] = new_token.strip()
            if new_id is not None:
                tg["chat_id"] = new_id.strip()
            if tg.get("bot_token") and tg.get("chat_id"):
                tg["enabled"] = True
            save_config(cfg)
            print("\n[✓] Saved!\n")
        elif action == "test":
            if not tg.get("bot_token") or not tg.get("chat_id"):
                print("\n[!] Please configure Bot Token and Chat ID first.\n" if CURRENT_LANG == "en" else "\n[!] Lengkapi Bot Token dan Chat ID terlebih dahulu di opsi [Edit].\n")
            else:
                ok, msg = send_telegram_notification(
                    tg["bot_token"], tg["chat_id"],
                    "TikTok Streak Notification Test",
                    "Hello! Your TikTok Streak helper is successfully connected to Telegram 🎉",
                    success=True
                )
                print(f"[{'✓' if ok else '!'}] {msg}\n")
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        elif action == "guide":
            show_telegram_guide()

def menu_discord_settings():
    while True:
        cfg = load_config()
        dc = cfg.setdefault("notifications", {}).setdefault("discord", {})
        enabled = dc.get("enabled", False)
        webhook = dc.get("webhook_url", "")
        masked_url = (webhook[:30] + "..." + webhook[-6:]) if len(webhook) > 40 else (webhook or "(Not set)" if CURRENT_LANG == "en" else "(Belum diisi)")

        print("\n" + "=" * 58)
        print("💬 Discord Webhook Settings:" if CURRENT_LANG == "en" else "💬 Pengaturan Discord Webhook:")
        print(f"   Status      : {t('status_active_upper') if enabled else t('status_inactive_upper')}")
        print(f"   Webhook URL : {masked_url}")
        print("=" * 58 + "\n")

        choices = [
            Choice(f"🔄 {'Disable' if enabled else 'Enable'} Discord Webhook" if CURRENT_LANG == "en" else f"🔄 {'Nonaktifkan' if enabled else 'Aktifkan'} Discord Webhook", value="toggle"),
            Choice("✏️  Set Discord Webhook URL" if CURRENT_LANG == "en" else "✏️  Atur / Ubah Discord Webhook URL", value="edit"),
            Choice("🔔 Test Send Notification Now" if CURRENT_LANG == "en" else "🔔 Tes Kirim Notifikasi ke Discord Sekarang", value="test"),
            Separator(),
            Choice("🔙 Back" if CURRENT_LANG == "en" else "🔙 Kembali", value="back")
        ]

        action = questionary.select("Select Action:" if CURRENT_LANG == "en" else "Pilih Aksi Discord:", choices=choices).ask()
        if action in ("back", None):
            break
        elif action == "toggle":
            dc["enabled"] = not enabled
            if dc["enabled"] and not webhook:
                new_url = questionary.text("Enter Discord Webhook URL:" if CURRENT_LANG == "en" else "Masukkan Discord Webhook URL:").ask()
                if new_url:
                    dc["webhook_url"] = new_url.strip()
            save_config(cfg)
            print(f"\n[✓] Discord Webhook: {t('status_active_upper') if dc['enabled'] else t('status_inactive_upper')}\n")
        elif action == "edit":
            new_url = questionary.text("Enter Discord Webhook URL:" if CURRENT_LANG == "en" else "Masukkan Discord Webhook URL:", default=webhook).ask()
            if new_url is not None:
                dc["webhook_url"] = new_url.strip()
            if dc.get("webhook_url"):
                dc["enabled"] = True
            save_config(cfg)
            print("\n[✓] Saved!\n")
        elif action == "test":
            if not dc.get("webhook_url"):
                print("\n[!] Please set Webhook URL first.\n")
            else:
                ok, msg = send_discord_notification(
                    dc["webhook_url"],
                    "TikTok Streak Notification Test",
                    "Hello! Your Discord webhook is connected successfully 🎉",
                    success=True
                )
                print(f"[{'✓' if ok else '!'}] {msg}\n")
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def menu_notifications():
    while True:
        cfg = load_config()
        notifs = cfg.get("notifications", {})
        tg = notifs.get("telegram", {})
        dc = notifs.get("discord", {})

        choices = [
            Choice(t("notif_telegram", status=t('status_active_upper') if tg.get('enabled') else t('status_inactive_upper')), value="telegram"),
            Choice(t("notif_discord", status=t('status_active_upper') if dc.get('enabled') else t('status_inactive_upper')), value="discord"),
            Choice(t("notif_test_all"), value="test_all"),
            Separator(),
            Choice(t("notif_back"), value="back")
        ]

        action = questionary.select(t("notif_menu_title"), choices=choices).ask()
        if action in ("back", None):
            break
        elif action == "telegram":
            menu_telegram_settings()
        elif action == "discord":
            menu_discord_settings()
        elif action == "test_all":
            print(t("notif_test_sending"))
            send_notification("TikTok Streak Notification Test", "Test alert! Streak notification successfully delivered.", success=True)
            print(t("notif_test_done"))
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def menu_pool_editor():
    PRESET_TEMPLATES = [
        "🔥",
        "Streak 🔥⚡",
        "Good {time_greeting} {first_name}! Streak 🔥",
        "Happy {day} {first_name}! 🔥",
        "Streak for today {first_name} 🔥✨",
        "Good morning {first_name}! Don't forget our streak 🔥",
        "Streak {date} 🔥💪"
    ]

    while True:
        cfg = load_config()
        pool = cfg.get("messages", {}).get("pool", [])

        print("\n" + "=" * 58)
        print(t("pool_menu_title"))
        print("=" * 58)
        if not pool:
            print(t("pool_empty"))
        else:
            for idx, p in enumerate(pool, 1):
                print(f" {idx:2d}. {p}")
        print("=" * 58 + "\n")

        choices = [
            Choice(t("pool_opt_add"), value="add"),
            Choice(t("pool_opt_preset"), value="preset"),
            Choice(t("pool_opt_edit"), value="edit"),
            Choice(t("pool_opt_remove"), value="remove"),
            Separator(),
            Choice(t("pool_opt_back"), value="back")
        ]

        act = questionary.select("Manage Message Pool:" if CURRENT_LANG == "en" else "Kelola Pool Pesan:", choices=choices).ask()
        if act in ("back", None):
            break
        elif act == "add":
            print(t("pool_add_hint"))
            new_text = questionary.text(t("pool_prompt_new")).ask()
            if new_text and new_text.strip():
                pool.append(new_text.strip())
                cfg["messages"]["pool"] = pool
                save_config(cfg)
                print(t("pool_added"))
        elif act == "preset":
            selected = questionary.checkbox(
                t("pool_preset_prompt"),
                choices=[Choice(title=p, value=p, checked=(p in pool)) for p in PRESET_TEMPLATES]
            ).ask()
            if selected is not None:
                for sp in selected:
                    if sp not in pool:
                        pool.append(sp)
                cfg["messages"]["pool"] = pool
                save_config(cfg)
                print(t("pool_updated", count=len(pool)))
        elif act == "edit":
            if not pool:
                continue
            item_choices = [Choice(f"{i}. {p}", value=i-1) for i, p in enumerate(pool, 1)] + [Separator(), Choice("🔙 Cancel", value="cancel")]
            chosen = questionary.select(t("pool_edit_prompt"), choices=item_choices).ask()
            if chosen not in ("cancel", None):
                old_val = pool[chosen]
                new_val = questionary.text("Edit template:", default=old_val).ask()
                if new_val and new_val.strip():
                    pool[chosen] = new_val.strip()
                    cfg["messages"]["pool"] = pool
                    save_config(cfg)
                    print("\n[✓] Updated!\n")
        elif act == "remove":
            if not pool:
                continue
            item_choices = [Choice(f"{i}. {p}", value=p) for i, p in enumerate(pool, 1)]
            to_remove = questionary.checkbox(t("pool_remove_prompt"), choices=item_choices).ask()
            if to_remove:
                pool = [p for p in pool if p not in to_remove]
                cfg["messages"]["pool"] = pool
                save_config(cfg)
                print("\n[✓] Removed!\n")

def menu_contact_overrides():
    while True:
        cfg = load_config()
        contacts = cfg.get("contacts", [])
        overrides = cfg.get("messages", {}).get("contact_overrides", {})

        print("\n" + "=" * 58)
        print(t("overrides_title"))
        print("=" * 58)
        if not overrides:
            print(t("overrides_empty"))
        else:
            for c_name, custom_msg in overrides.items():
                print(f"  • {c_name:<20} -> '{custom_msg}'")
        print("=" * 58 + "\n")

        choices = [
            Choice(t("overrides_opt_add"), value="add"),
            Choice(t("overrides_opt_remove"), value="remove"),
            Separator(),
            Choice(t("overrides_opt_back"), value="back")
        ]

        act = questionary.select("Manage Contact Overrides:" if CURRENT_LANG == "en" else "Kelola Pesan Khusus Kontak:", choices=choices).ask()
        if act in ("back", None):
            break
        elif act == "add":
            if not contacts:
                continue
            contact_choices = [Choice(c, value=c) for c in contacts] + [Separator(), Choice("🔙 Cancel", value="cancel")]
            chosen = questionary.select("Select contact:" if CURRENT_LANG == "en" else "Pilih kontak:", choices=contact_choices).ask()
            if chosen and chosen != "cancel":
                cur_override = overrides.get(chosen, "")
                msg_input = questionary.text(
                    f"Custom message for '{chosen}':",
                    default=cur_override or ("Good {time_greeting} {first_name}! Streak 🔥" if CURRENT_LANG == "en" else "Semangat hari ini {first_name}! Streak 🔥")
                ).ask()
                if msg_input and msg_input.strip():
                    overrides[chosen] = msg_input.strip()
                    cfg["messages"]["contact_overrides"] = overrides
                    save_config(cfg)
                    print("\n[✓] Saved!\n")
        elif act == "remove":
            if not overrides:
                continue
            remove_choices = [Choice(f"{c}: '{m}'", value=c) for c, m in overrides.items()]
            chosen_to_del = questionary.checkbox("Select contacts to reset:" if CURRENT_LANG == "en" else "Pilih kontak untuk menghapus pesan khususnya:", choices=remove_choices).ask()
            if chosen_to_del:
                for c in chosen_to_del:
                    if c in overrides:
                        del overrides[c]
                cfg["messages"]["contact_overrides"] = overrides
                save_config(cfg)
                print("\n[✓] Reset!\n")

def show_message_preview():
    cfg = load_config()
    contacts = cfg.get("contacts", [])
    if not contacts:
        contacts = ["Alice Smith", "Bob Johnson", "Charlie Brown"] if CURRENT_LANG == "en" else ["Budi Santoso", "Siti Aminah", "David Wijaya"]

    print("\n" + "=" * 65)
    print(t("preview_title"))
    print("=" * 65)
    recip_mode = cfg.get("mode", "all")
    msg_mode = cfg.get("messages", {}).get("mode", "single")
    mode_text = t("dash_msg_mode_pool") if msg_mode == "pool" else t("dash_msg_mode_fixed", msg=cfg.get('default_message', '🔥'))
    print(t("preview_mode", mode=mode_text))
    recip_label = ("Select All (All Contacts)" if recip_mode == "all" else "Groups / Labeling") if CURRENT_LANG == "en" else ("Select All (Semua Kontak)" if recip_mode == "all" else "Groups / Labeling")
    print(f"Recipient Mode: {recip_label}" if CURRENT_LANG == "en" else f"Mode Penerima : {recip_label}")
    print("-" * 65)

    sample = contacts[:6]
    for c in sample:
        group_msg = None
        group_name = None
        if recip_mode == "groups":
            for g_name, g_info in cfg.get("groups", {}).items():
                if g_info.get("enabled", True) and c in g_info.get("members", []):
                    group_msg = g_info.get("message")
                    group_name = g_name
                    break
        resolved = resolve_message_for_contact(c, group_msg=group_msg)
        is_override = c in cfg.get("messages", {}).get("contact_overrides", {})
        badge = " [Custom Contact]" if is_override else (f" [Group: {group_name}]" if group_name else "")
        print(t("preview_to", name=f"{c:<18}", badge=badge))
        print(t("preview_msg", msg=resolved))
        print()
    print("=" * 65 + "\n")
    questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def menu_manage_messages():
    while True:
        cfg = load_config()
        msg_cfg = cfg.get("messages", {})
        mode = msg_cfg.get("mode", "single")
        mode_label = t("dash_msg_mode_pool") if mode == "pool" else t("dash_msg_mode_fixed", msg=cfg.get('default_message', '🔥'))
        default_msg = cfg.get("default_message", "🔥")
        pool = msg_cfg.get("pool", [])
        overrides = msg_cfg.get("contact_overrides", {})

        choices = [
            Choice(f"🔄 Switch Mode (Current: {mode_label})" if CURRENT_LANG == "en" else f"🔄 Ganti Mode Pesan (Saat ini: {mode_label})", value="toggle_mode"),
            Choice(f"💬 Change Default Message (Current: '{default_msg}')" if CURRENT_LANG == "en" else f"💬 Ubah Pesan Default (Saat ini: '{default_msg}')", value="default_msg"),
            Choice(f"🎲 Manage Message Pool ({len(pool)} variations)" if CURRENT_LANG == "en" else f"🎲 Kelola Pool Variasi Acak ({len(pool)} variasi tersimpan)", value="pool"),
            Choice(f"👤 Custom Contact Messages ({len(overrides)} custom)" if CURRENT_LANG == "en" else f"👤 Pesan Khusus per Kontak ({len(overrides)} kontak khusus)", value="overrides"),
            Choice("👁️  Preview Output Messages" if CURRENT_LANG == "en" else "👁️  Pratinjau Hasil Pesan (Preview)", value="preview"),
            Separator(),
            Choice("🔙 Return" if CURRENT_LANG == "en" else "🔙 Selesai / Kembali", value="back")
        ]

        act = questionary.select("Configure Streak Messages:" if CURRENT_LANG == "en" else "💬 Konfigurasi Format Pesan Streak:", choices=choices).ask()
        if act in ("back", None):
            break
        elif act == "toggle_mode":
            new_mode = "pool" if mode == "single" else "single"
            msg_cfg["mode"] = new_mode
            cfg["messages"] = msg_cfg
            save_config(cfg)
            print("\n[✓] Mode updated!\n")
        elif act == "default_msg":
            new_def = questionary.text("Enter new default message:" if CURRENT_LANG == "en" else "Masukkan pesan default baru:", default=default_msg).ask()
            if new_def:
                cfg["default_message"] = new_def
                if cfg.get("groups"):
                    sync_groups = questionary.confirm(
                        "Also apply new message to all existing groups?" if CURRENT_LANG == "en" else "Terapkan juga pesan baru ini ke semua grup yang ada?",
                        default=True
                    ).ask()
                    if sync_groups:
                        for g in cfg.get("groups", {}).values():
                            g["message"] = new_def
                save_config(cfg)
                print("\n[✓] Default message updated!\n")
        elif act == "pool":
            menu_pool_editor()
        elif act == "overrides":
            menu_contact_overrides()
        elif act == "preview":
            show_message_preview()

def menu_account():
    while True:
        cfg = load_config()
        curr_acc = cfg.get("current_account", "")
        contacts = cfg.get("contacts", [])
        is_logged_in = check_login_status()
        status_label = t("dash_status_valid") if is_logged_in else t("dash_status_unauthed")
        acc_label = f"@{curr_acc}" if curr_acc else ("Not detected" if CURRENT_LANG == "en" else "Belum terdeteksi")

        choices = [
            Choice(f"👤 {'Active Account:' if CURRENT_LANG == 'en' else 'Akun Aktif:'} {acc_label}", value="info"),
            Choice(t("account_opt_scan", count=len(contacts)), value="scan"),
            Choice(t("account_opt_login"), value="login"),
            Choice("🔄 Detect / Switch Active Account" if CURRENT_LANG == "en" else "🔄 Deteksi / Ganti Akun Aktif", value="detect_account"),
            Choice(t("account_opt_check", status=status_label), value="check"),
            Choice("🚪 Logout & Clear Browser Session" if CURRENT_LANG == "en" else "🚪 Logout & Bersihkan Sesi Browser", value="logout"),
            Separator(),
            Choice(t("account_opt_back"), value="back")
        ]

        action = questionary.select(t("account_menu_title"), choices=choices).ask()
        if action in ("back", None):
            break
        elif action == "info":
            accounts = cfg.get("accounts", {})
            print("\n" + "=" * 55)
            print(f"👤 {'ACTIVE ACCOUNT INFORMATION' if CURRENT_LANG == 'en' else 'INFORMASI AKUN AKTIF'}")
            print("=" * 55)
            print(f" • Username   : @{curr_acc if curr_acc else 'None'}")
            print(f" • Contacts   : {len(contacts)} contacts")
            print(f" • Recipients : {len(get_active_recipients(cfg))} active")
            print(f" • Session    : {status_label}")
            if accounts:
                print(f"\n📂 Saved Account Profiles ({len(accounts)}):")
                for acc, data in accounts.items():
                    mark = " (Active)" if acc == curr_acc else ""
                    print(f"   - @{acc}: {len(data.get('contacts', []))} contacts{mark}")
            print("=" * 55 + "\n")
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "scan":
            scan_dm_contacts(verbose=True)
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "login":
            interactive_login()
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "detect_account":
            print("\n[*] Detecting active TikTok account from browser profile...")
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    ctx = launch_browser_context(p, headless=True)
                    page = ctx.pages[0] if ctx.pages else ctx.new_page()
                    page.goto("https://www.tiktok.com/messages", wait_until="networkidle", timeout=30000)
                    time.sleep(2)
                    detected = get_logged_in_username(page)
                    ctx.close()
                if detected:
                    switched = sync_active_account(cfg, detected)
                    print(f"\n[✓] Detected active account: @{detected}")
                    if switched:
                        print(f"[✓] Switched active configuration to @{detected}!")
                    else:
                        print("[*] Already using active account profile.")
                else:
                    print("\n[!] Could not detect active account. Session might be expired.\n")
            except Exception as e:
                print(f"\n[x] Detection failed: {e}\n")
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "check":
            ok, _ = run_with_progress(t("checking_updates"), check_login_status, timeout=2.0)
            print(f"[{'✓' if ok else '!'}] Status: {t('dash_status_valid') if ok else t('dash_status_unauthed')}\n")
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "logout":
            confirm = questionary.confirm(
                "Are you sure you want to log out and clear browser cookies?" if CURRENT_LANG == "en" else "Apakah Anda yakin ingin logout dan membersihkan sesi browser?",
                default=False
            ).ask()
            if confirm:
                if logout_session():
                    print("\n[✓] Browser session cleared. You can now log into a different account via 'Login TikTok'.\n" if CURRENT_LANG == "en" else "\n[✓] Sesi browser berhasil dibersihkan. Anda dapat login dengan akun lain melalui menu 'Login Akun TikTok'.\n")
                else:
                    print("\n[x] Failed to clear session.\n")
                questionary.press_any_key_to_continue(t("press_key_return")).ask()

def display_logs(date_filter: str = None, category_filter: str = None, max_lines: int = 40):
    clean_expired_logs(retention_days=3)
    if not os.path.exists(LOG_DIR):
        print("\n[!] No logs found.\n")
        return

    files = sorted([f for f in os.listdir(LOG_DIR) if f.startswith("activity_") and f.endswith(".log")])
    if not files:
        print("\n[!] No logs recorded.\n")
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
    print("📜 ACTIVITY HISTORY & LOGS:" if CURRENT_LANG == "en" else "📜 RIWAYAT AKTIVITAS & LOG:")
    print("=" * 70)
    if not all_entries:
        print("  (No logs matching filter)")
    else:
        for entry in all_entries[-max_lines:]:
            print(f"  {entry}")
    print("=" * 70 + "\n")

def menu_view_logs():
    while True:
        choices = [
            Choice(t("logs_opt_all"), value="all"),
            Choice(t("logs_opt_job"), value="job"),
            Choice(t("logs_opt_config"), value="config"),
            Choice(t("logs_opt_clean"), value="clean"),
            Separator(),
            Choice(t("logs_opt_back"), value="back")
        ]

        act = questionary.select(t("logs_menu_title"), choices=choices).ask()
        if act in ("back", None):
            break
        elif act == "all":
            display_logs()
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        elif act == "job":
            display_logs(category_filter="JOB")
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        elif act == "config":
            display_logs(category_filter="CONFIG")
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()
        elif act == "clean":
            confirm = questionary.confirm(t("logs_clean_confirm")).ask()
            if confirm:
                if os.path.exists(LOG_DIR):
                    for f in os.listdir(LOG_DIR):
                        if f.startswith("activity_") and f.endswith(".log"):
                            try:
                                os.remove(os.path.join(LOG_DIR, f))
                            except Exception:
                                pass
                log_activity("SYSTEM", "Logs cleared manually by user.")
                print(t("logs_cleaned"))
            questionary.press_any_key_to_continue(t("press_key_continue")).ask()

def menu_language():
    cfg = load_config()
    choices = [
        Choice(t("lang_opt_en"), value="en"),
        Choice(t("lang_opt_id"), value="id"),
        Separator(),
        Choice(t("lang_opt_back"), value="back")
    ]
    chosen = questionary.select(t("lang_menu_title"), choices=choices).ask()
    if chosen and chosen != "back":
        cfg["language"] = chosen
        save_config(cfg)
        set_language(chosen)
        lang_name = "English" if chosen == "en" else "Bahasa Indonesia"
        print(t("lang_changed", lang=lang_name))

def interactive_hub():
    while True:
        cfg = load_config()
        set_language(cfg.get("language", "en"))
        print_dashboard()
        is_logged_in = check_login_status()

        sched = cfg.get("schedule", {"hour": 9, "minute": 0})
        time_str = f"{sched.get('hour', 9):02d}:{sched.get('minute', 0):02d}"
        lang_name = "English" if CURRENT_LANG == "en" else "Bahasa Indonesia"

        choices = []
        if not is_logged_in:
            choices.append(Choice(t("menu_opt_login_req"), value="account"))
            choices.append(Choice(t("menu_opt_run_need_login"), value="run"))
        else:
            choices.append(Choice(t("menu_opt_run"), value="run"))

        choices.extend([
            Choice(t("menu_opt_recipients"), value="recipients"),
            Choice(t("menu_opt_speed"), value="safety"),
            Choice(t("menu_opt_scheduler", time=time_str), value="scheduler"),
            Choice(t("menu_opt_logs"), value="logs"),
        ])

        if is_logged_in:
            choices.append(Choice(t("menu_opt_account"), value="account"))

        choices.extend([
            Choice(t("menu_opt_notifications"), value="notifications"),
            Choice(t("menu_opt_check_update"), value="check_update"),
            Choice(t("menu_opt_lang", current=lang_name), value="language"),
            Separator(),
            Choice(t("menu_opt_exit"), value="exit")
        ])

        action = questionary.select(
            t("menu_select"),
            choices=choices,
            use_indicator=True
        ).ask()

        if action in ("exit", None):
            print(t("goodbye"))
            break
        elif action == "run":
            run_send_streak(force=True, verbose=True)
            questionary.press_any_key_to_continue(t("press_key_return")).ask()
        elif action == "recipients":
            menu_manage_recipients()
        elif action == "safety":
            menu_safety_settings()
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
        elif action == "language":
            menu_language()

def print_streak_table(cfg: dict = None):
    if cfg is None:
        cfg = load_config()
    contacts = cfg.get("contacts", [])
    usernames = cfg.get("usernames", {})
    streak_counts = cfg.get("streak_counts", {})
    last_streak_dates = cfg.get("last_streak_dates", {})
    today_str = str(date.today())
    curr_acc = cfg.get("current_account", "")

    print("\n" + "=" * 76)
    title = f"🔥 TIKTOK STREAK COUNTER - @{curr_acc}" if curr_acc else "🔥 TIKTOK STREAK COUNTER"
    print(title)
    print("=" * 76)
    print(f" {'No':<3} {'Nama Kontak':<26} {'Username':<18} {'Api/Streak':<12} {'Status Hari Ini':<15}")
    print("-" * 76)
    for idx, c in enumerate(contacts, 1):
        u = usernames.get(c, "-")
        u_str = f"@{u}" if u != "-" else "-"
        strk = streak_counts.get(c, 1)
        last_d = last_streak_dates.get(c, "-")
        status = "✅ Terkirim" if last_d == today_str else "⌛ Belum"
        print(f" {idx:2d}. {c:<26} {u_str:<18} 🔥 {strk:<9} {status} ({last_d})")
    print("=" * 76 + "\n")

def run_cron_job(max_retries: int = 1, retry_delay: int = 40):
    cfg = load_config()
    current_acc = cfg.get("current_account", "")
    state = get_account_state(current_acc)
    today_str = str(date.today())
    if state.get("last_success_date") == today_str:
        log_activity("SYSTEM", t("cron_already_sent", date=today_str))
        return

    # Schedulers run once per day. If already attempted today, leave any remaining/failed for manual run.
    last_attempt = state.get("last_attempt", "")
    if state.get("sent_date") == today_str or (last_attempt and last_attempt.startswith(today_str)):
        log_activity("SYSTEM", f"Cron check: Streak already attempted today ({today_str}). Remaining/failed contacts left for manual run.")
        return

    if state.get("session_expired"):
        log_activity("SYSTEM", "Cron skipped: TikTok login session expired. Please log in via Account menu.")
        return

    is_safe, reason = is_within_safe_hours()
    if not is_safe:
        log_activity("SYSTEM", t("cron_safe_hours", reason=reason))
        return

    log_activity("SYSTEM", t("cron_triggered"))

    if not wait_for_internet(timeout=180, check_interval=3, verbose=False):
        log_activity("ERROR", t("cron_internet_failed"))
        return

    for attempt in range(1, max_retries + 1):
        log_activity("JOB", t("cron_attempt", attempt=attempt, max_attempts=max_retries))
        res = run_send_streak(force=False, verbose=False)
        if res.get("success"):
            log_activity("SYSTEM", t("cron_success", attempt=attempt))
            return

        if res.get("is_auth_error") or "session expired" in str(res.get("message", "")).lower():
            log_activity("SYSTEM", "Cron aborted: Login required. Will not retry until logged in.")
            return

        if attempt < max_retries:
            log_activity("SYSTEM", t("cron_retry", attempt=attempt, msg=res.get('message'), delay=retry_delay))
            time.sleep(retry_delay)
            wait_for_internet(timeout=60, check_interval=3, verbose=False)
        else:
            log_activity("ERROR", t("cron_exhausted"))

def main():
    parser = argparse.ArgumentParser(description="⚡ TikTok Streak Auto-Saver & Helper Hub")
    parser.add_argument("--cron", action="store_true", help="Run unattended in background via scheduler")
    parser.add_argument("--force", action="store_true", help="Force send streak even if already sent today")
    parser.add_argument("--streaks", action="store_true", help="Display contacts and streak counts table")
    parser.add_argument("--login", action="store_true", help="Open visual browser for login")
    parser.add_argument("--scan", action="store_true", help="Scan DM contacts from TikTok")
    parser.add_argument("--lang", "--language", choices=["en", "id"], help="Set UI language (en/id)")

    args = parser.parse_args()

    cfg = load_config()
    if args.lang:
        set_language(args.lang)
    else:
        set_language(cfg.get("language", "en"))

    if args.cron:
        run_cron_job()
    elif args.force:
        wait_for_internet(timeout=15, verbose=True)
        run_send_streak(force=True, verbose=True)
    elif args.streaks:
        print_streak_table(cfg)
    elif args.login:
        interactive_login()
    elif args.scan:
        wait_for_internet(timeout=15, verbose=True)
        scan_dm_contacts(verbose=True)
    else:
        check_for_updates(prompt_if_latest=False)
        interactive_hub()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        handle_sigint()
