# ⚡ tiktok-streak — TikTok Streak Auto-Saver & Helper Hub

A zero-hassle, cross-platform interactive CLI hub and daily streak assistant for **TikTok**.

Modeled around the same simple philosophy as **genshin-checkin**: **"Run and pick options easily."** No manual python execution commands, no JSON hacking, and automatic background streak sending with wake-up catch-up whenever you want it.

---

## 🌟 Fitur Utama

- **Interactive Terminal Hub**: Tampilan dashboard visual di terminal. Cukup ketik `tiktok-streak` dan pilih opsi menggunakan angka `[1-6]`.
- **Mode "Select All"**: Kirim streak ke semua kontak DM aktif secara otomatis.
- **Daftar Pengecualian (Blacklist / Exclude)**: Lewati akun resmi TikTok, akun olshop, atau orang tertentu secara otomatis di mode *Select All*.
- **Grouping & Labeling**: Kelompokkan kontak ke label (*Sahabat*, *Prioritas*, *Mutual*, dll.) dengan pesan kustom untuk masing-masing grup.
- **Auto-Scan DM Contacts**: Deteksi otomatis nama-nama kontak di DM TikTok Anda langsung dari menu terminal.
- **Cross-Platform Daily Automation**:
  - **macOS**: Otomatis mendaftarkan **LaunchAgent** (`launchd`) jam 09:00 pagi. Jika laptop mati atau *sleep*, script otomatis langsung mengejar pengiriman saat laptop dibuka/dinyalakan.
  - **Windows**: Terintegrasi dengan **Windows Task Scheduler** (`schtasks`).
  - **Linux**: Terintegrasi dengan **Crontab**.
- **Notifikasi ke HP**: Kirim rekap hasil pengiriman streak ke **Telegram Bot** atau **Discord Webhook**, serta banner notifikasi native macOS.

---

## 🖥️ Terminal Dashboard

```text
==========================================================
⚡  TikTok Streak Auto-Saver & Helper Hub
==========================================================
👤 Akun Sesi:      🟢 VALID (Aktif)
📅 Status Hari Ini: ✅ Streak Sudah Terkirim
👥 Mode Penerima:   🌟 Select All (Exclude: 3)
⏰ Jadwal Auto:     🟢 Active (macOS LaunchAgent / 09:00 AM)
==========================================================
 [1] 🚀 Kirim Streak Sekarang (Run Check-in)
 [2] 👥 Kelola Penerima & Grup (Select All / Checklist)
 [3] 🔍 Pindai Kontak DM dari TikTok (Auto-detect)
 [4] ⏰ Pasang / Atur Jadwal Harian (Catch-up saat laptop nyala)
 [5] 🔑 Login / Hubungkan Akun TikTok (Browser Window)
 [6] 🔔 Pengaturan Notifikasi (Telegram / Discord)
 [0] 🚪 Keluar
==========================================================
Pilih opsi [0-6]: 
```

---

## ⚡ Quick Start

### 🍎 macOS & 🐧 Linux

1. Masuk ke folder repository dan jalankan installer:
   ```bash
   chmod +x install.sh && ./install.sh
   ```
2. Setelah itu, buka terminal mana saja dan cukup ketik:
   ```bash
   tiktok-streak
   ```

### 🪟 Windows

1. Double-click file **`tiktok-streak.bat`** (atau ketik `tiktok-streak.bat` di PowerShell / CMD).

---

## 🔑 Alur Pemakaian Pertama Kali

1. **Jalankan:** Ketik `tiktok-streak` di terminal.
2. **Login Akun:** Pilih menu `[5] 🔑 Login / Hubungkan Akun TikTok`. Jendela browser akan terbuka. Login ke akun TikTok Anda (bisa scan QR dari aplikasi TikTok di HP). Tekan ENTER di terminal jika sudah login.
3. **Pindai Kontak:** Pilih menu `[3] 🔍 Pindai Kontak DM dari TikTok` untuk mendeteksi daftar nama teman Anda.
4. **Atur Penerima:** Pilih menu `[2] 👥 Kelola Penerima & Grup` untuk menentukan apakah ingin pakai mode *Select All* atau *Grouping*.
5. **Aktifkan Jadwal:** Pilih menu `[4] ⏰ Pasang / Atur Jadwal Harian` agar berjalan otomatis setiap hari di latar belakang.
