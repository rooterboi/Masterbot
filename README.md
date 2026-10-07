# 🎬 Kino va Serial Bot (aiogram 3 + SQLite)

Premium/oddiy foydalanuvchilar, referal balans, promokodlar, majburiy obuna, avto-post, broadcast
va **adminlarni qo'shish/olib tashlash** bor admin panel.

## 1. GitHub'ga yuklash
```bash
git init && git add . && git commit -m "kino bot"
git branch -M main
git remote add origin https://github.com/<login>/<repo>.git
git push -u origin main
```

## 2. Render (bepul tarif)
1. render.com → **New → Web Service** → GitHub repo'ni tanlang.
2. Runtime: **Python 3**, Build: `pip install -r requirements.txt`, Start: `python main.py`, Plan: **Free**.
   (Yoki **New → Blueprint** — `render.yaml` avtomatik o'qiladi.)
3. **Environment** bo'limiga qo'shing:
   - `BOT_TOKEN` — @BotFather'dan token
   - `OWNER_ID` — sizning Telegram ID (@userinfobot orqali bilib oling)
   - `PYTHON_VERSION` = `3.11.9`
4. Deploy tugagach botga `/admin` yozing.

Bot webhook rejimida ishlaydi (`RENDER_EXTERNAL_URL` avtomatik olinadi), shuning uchun
Render uxlab qolsa ham Telegram xabar yuborganda uyg'onadi (birinchi javob ~30–60 soniya kechikishi mumkin).
Uyg'oq tutish uchun UptimeRobot'da `https://<sizning-servis>.onrender.com/health` ni 5 daqiqada bir ping qiling.

## ⚠️ Muhim: bepul tarifda SQLite
Render bepul tarifida disk **vaqtinchalik** — qayta deploy/restart bo'lganda baza o'chadi.
Himoya: bot har `BACKUP_HOURS` (standart 6) soatda bazani **egasiga (OWNER_ID) Telegram orqali yuboradi**.
Yangi deploydan so'ng: `/admin → 💾 Baza → ♻️ Zaxiradan tiklash` va oxirgi `.db` faylni yuboring.
Doimiy saqlash uchun pullik Render Disk yoki tashqi baza (Turso/Postgres) kerak bo'ladi.

## Adminlar
`/admin → 👮 Adminlarni boshqarish` (faqat Bosh Admin):
- ➕ Yangi Admin Qo'shish — ID kiritiladi
- ❌ ro'yxatdagi tugma yoki 🆔 ID orqali olib tashlash

## Lokal ishga tushirish
```bash
pip install -r requirements.txt
cp .env.example .env   # BOT_TOKEN va OWNER_ID ni to'ldiring
python main.py
```

## Tuzilma
`main.py` · `app/db.py` (7 jadval + channels) · `app/handlers/user.py` · `app/handlers/admin.py`
