# 🤖 PostBuilder Pro Bot

Peşəkar Telegram Post və Button Builder Botu — **v2.0.0**

## 🚀 Xüsusiyyətlər

- ✅ Vizual post qurucusu (mətn, media, düymələr)
- ✅ 10+ düymə növü (URL, Callback, Web App, Share, Switch Inline, Copy, Login, Game, Pay...)
- ✅ Şəkil, Video, Audio, Səs, GIF, Sənəd, Albom dəstəyi
- ✅ 12 hazır şablon (Kanal, Xəbər, Elan, Giveaway, FAQ, Dəstək...)
- ✅ JSON import/export
- ✅ Qaralamalar və şablonlar (istifadəçi başına 50 qaralama)
- ✅ Planlaşdırılmış göndəriş
- ✅ Çox hədəfə göndəriş (eyni anda 10 hədəfə)
- ✅ Premium alətlər: Deep Link, UTM Generator, QR Kod, MD↔HTML çevirmə
- ✅ Admin panel: Statistika, Broadcast, Blok, Texniki xidmət rejimi
- ✅ Azərbaycan, Rus, İngilis dil dəstəyi
- ✅ Throttling middleware (spam qoruması)
- ✅ Asinxron SQLite/PostgreSQL verilənlər bazası

---

## ⚡ Quraşdırma

### 1. Kodu yükləyin

```bash
git clone <repo>
cd postbuilder_bot
```

### 2. Virtual mühit yaradın

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Asılılıqları quraşdırın

```bash
pip install -r requirements.txt
```

### 4. `.env` faylını yaradın

```bash
cp .env.example .env
nano .env
```

`.env` faylında token və admin ID-lərini yazın:

```
BOT_TOKEN=1234567890:ABCdef...
ADMIN_IDS=123456789
```

### 5. Botu işə salın

```bash
python main.py
```

---

## 📁 Layihə Strukturu

```
postbuilder_bot/
├── main.py              # Ana başlanğıc nöqtəsi
├── config.py            # Konfiqurasiya
├── states.py            # FSM State-lər
├── requirements.txt
├── .env.example
├── database/
│   ├── __init__.py
│   └── db.py            # SQLAlchemy modellər + repository
├── handlers/
│   ├── start.py         # /start, ana menyu
│   ├── post_builder.py  # Post qurucusu
│   ├── button_builder.py# Düymə qurucusu
│   ├── media_handler.py # Media emalı
│   ├── templates_handler.py # Şablonlar
│   ├── send_handler.py  # Göndərmə
│   ├── drafts_handler.py# Qaralamalar
│   ├── json_handler.py  # JSON rejimi
│   ├── premium_handler.py # Premium alətlər
│   └── admin_handler.py # Admin panel
├── keyboards/
│   └── keyboards.py     # Bütün klaviaturalar
├── locales/
│   └── strings.py       # AZ/RU/EN lokalizasiya
├── middlewares/
│   ├── logging_middleware.py
│   ├── throttling.py
│   └── maintenance.py
└── utils/
    ├── post_data.py     # Post məlumat modeli
    └── helpers.py       # Köməkçi funksiyalar
```

---

## 🔑 Bot Komandaları

| Komanda | Təsvir |
|---------|--------|
| `/start` | Botu başlat |
| `/menu` | Ana menyuya qayıt |
| `/admin` | Admin paneli (yalnız adminlər) |
| `/help` | Kömək menyusu |

---

## 🔧 Konfiqurasiya

`config.py` faylında aşağıdakıları dəyişə bilərsiniz:

```python
MAX_BUTTONS_PER_ROW = 8    # Bir sətirdə max düymə
MAX_BUTTON_ROWS = 100      # Max sətir sayı
MAX_DRAFTS_PER_USER = 50   # İstifadəçi başına max qaralama
MAX_TARGETS_AT_ONCE = 10   # Eyni anda max hədəf
```

---

## 🛡 Təhlükəsizlik

- Throttling middleware (0.5s aralıq)
- Texniki xidmət rejimi
- İstifadəçi bloklama sistemi
- Admin əməliyyatları yalnız təsdiqlənmiş admin ID-ləri üçün

---

## 📦 Asılılıqlar

- **aiogram 3.13** — asinxron Telegram Bot framework
- **SQLAlchemy 2.0** — asinxron ORM
- **aiosqlite** — asinxron SQLite driveri
- **cachetools** — throttling üçün TTL cache
- **qrcode + Pillow** — QR kod yaratma

---

## 📝 Lisenziya

MIT License
