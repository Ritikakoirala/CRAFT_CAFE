# ☕ Craft Cafe v2 — Premium Full-Stack Django Website

A Michelin-level cafe ordering system with real-time emails, luxury UI, and the Craft Cafe logo.

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

--
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

