# ☕ Craft Cafe v2 — Premium Full-Stack Django Website

A Michelin-level cafe ordering system with real-time emails, luxury UI, and the Craft Cafe logo.

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Extract project & enter directory
cd craft_cafe_v2

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Copy env template and configure
cp .env.example .env
# Edit .env with your email credentials (see Email Setup below)

# 5. Run database migrations
python manage.py makemigrations
python manage.py migrate

# 6. Seed the full menu (23 items across 3 categories)
python manage.py seed_data

# 7. Create admin/owner account
python manage.py createsuperuser

# 8. Launch!
python manage.py runserver
```

Open: **http://127.0.0.1:8000**

---

## 📧 Email Setup (2 methods)

### Method 1: Gmail SMTP (Quickest — 5 min setup)

1. Enable **2-Factor Authentication** on your Google account
2. Go to **Google Account → Security → App Passwords**
3. Generate an App Password for "Mail"
4. Edit your `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx   ← 16-char App Password (NOT your Gmail password)
DEFAULT_FROM_EMAIL=Craft Cafe <your-gmail@gmail.com>
ADMIN_EMAIL=rai.rohan1800@gmail.com
```

### Method 2: Development (No email account needed)

Emails print to your terminal console — great for testing:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### When Emails Are Sent

| Trigger | Recipient | Template |
|---------|-----------|----------|
| Customer places order | Customer | Order confirmation + items |
| Customer places order | Cafe owner | New order alert + details |
| Admin updates status | Customer | Status update (Preparing/On the Way/Delivered) |
| Contact form submitted | Cafe owner | Contact message |
| Contact form submitted | Visitor | Auto-reply |
| Feedback submitted | Customer (if email given) | Thank-you email |

---

## 🌐 Key URLs

| URL | Description |
|-----|-------------|
| `/` | Home — hero, featured, reviews |
| `/menu/` | Full menu with category filter |
| `/cart/` | Shopping cart |
| `/checkout/` | Place order + payment |
| `/feedback/` | Leave star rating + review |
| `/contact/` | Contact form (sends email) |
| `/login/` `/register/` | Auth pages |
| `/dashboard/` | Admin dashboard (staff only) |
| `/admin/` | Django admin panel |

---

## 🎨 Design System

**Fonts:** Cormorant Garamond (display) + Jost (body)

**Palette:**
- `#C8793A` — Burnt amber (primary accent)
- `#0E0907` — Deep espresso (dark bg)
- `#F8F2E8` — Warm cream (light bg)
- `#8A7A68` — Mist (secondary text)

**Features:**
- ✅ Dark / Light theme toggle (persisted in localStorage)
- ✅ CSS grain texture overlay for premium feel
- ✅ Scroll-triggered reveal animations
- ✅ Floating hero card stack
- ✅ Animated marquee ticker
- ✅ Glassmorphism-inspired nav
- ✅ Mobile-first responsive grid
- ✅ AJAX cart with live badge

---

## 🚢 Deploy to Render (Free)

1. Push to GitHub
2. [render.com](https://render.com) → New Web Service → connect repo
3. **Build command:** `./build.sh`
4. **Start command:** `gunicorn craft_cafe.wsgi`
5. **Environment Variables:**
   ```
   SECRET_KEY=your-long-random-secret-key
   DEBUG=False
   ALLOWED_HOSTS=yourapp.onrender.com
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST_USER=your-gmail@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=Craft Cafe <your-gmail@gmail.com>
   ADMIN_EMAIL=rai.rohan1800@gmail.com
   ```

---

## 🚢 Deploy to PythonAnywhere (Free)

1. Sign up at [pythonanywhere.com](https://pythonanywhere.com)
2. Bash console:
   ```bash
   git clone <your-repo>
   cd craft_cafe_v2
   pip3 install --user -r requirements.txt
   python manage.py migrate
   python manage.py seed_data
   python manage.py collectstatic --no-input
   ```
3. Web tab → Add app → Manual config → Python 3.11
4. WSGI file → point to `craft_cafe.wsgi`
5. Set environment variables in the Web tab

---

## 📁 New Files in v2

```
cafe/
├── email_service.py              ← All email functions

templates/
├── emails/
│   ├── base_email.html           ← Shared email layout
│   ├── order_confirmation.html   ← Customer order confirm
│   ├── order_status.html         ← Status update emails
│   ├── admin_new_order.html      ← Owner alert email
│   ├── contact_message.html      ← Contact form → owner
│   ├── contact_autoreply.html    ← Auto-reply to visitor
│   └── feedback_thanks.html      ← Thank-you after review

static/
├── css/luxury.css                ← Full premium UI system
├── js/luxury.js                  ← Theme, animations, AJAX
└── images/logo.png               ← Your Craft Cafe logo

.env.example                      ← Environment variable template
```

---

Made with ☕ by **Røhån** · Craft Cafe, Kathmandu
