/* ================================================================
   CRAFT CAFE — Luxury JS
   Features: theme, scroll reveal, AJAX cart, mobile nav
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Theme ──────────────────────────────────────────────── */
  const root = document.documentElement;
  const saved = localStorage.getItem('cc-theme') || 'dark';
  root.setAttribute('data-theme', saved);
  syncThemeIcon(saved);

  document.getElementById('themeToggle')?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('cc-theme', next);
    syncThemeIcon(next);
  });

  function syncThemeIcon(t) {
    const i = document.getElementById('themeIcon');
    if (!i) return;
    i.className = t === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars';
  }

  /* ── Mobile nav ─────────────────────────────────────────── */
  const burger = document.getElementById('navBurger');
  const navLinks = document.getElementById('navLinks');
  burger?.addEventListener('click', () => {
    navLinks?.classList.toggle('is-open');
    const open = navLinks?.classList.contains('is-open');
    burger.setAttribute('aria-expanded', open);
    // Animate burger
    const spans = burger.querySelectorAll('span');
    if (open) {
      spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
    } else {
      spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
    }
  });

  /* ── Sticky nav shadow ──────────────────────────────────── */
  const nav = document.getElementById('mainNav');
  const onScroll = () => {
    if (!nav) return;
    nav.style.boxShadow = window.scrollY > 20 ? '0 4px 24px rgba(0,0,0,.12)' : '';
  };
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ── Scroll reveal ──────────────────────────────────────── */
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('is-visible');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('is-visible'));
  }

  /* ── AJAX add-to-cart ───────────────────────────────────── */
  document.querySelectorAll('.add-cart-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button');
      const orig = btn.innerHTML;
      btn.innerHTML = '<i class="bi bi-check-lg"></i>';
      btn.style.background = '#22c55e';
      btn.disabled = true;

      try {
        const res = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        if (data.success) {
          updateCartDot(data.cart_count);
          showToast('Added to cart! 🛒');
        }
      } catch {
        form.submit();
      } finally {
        setTimeout(() => {
          btn.innerHTML = orig;
          btn.style.background = '';
          btn.disabled = false;
        }, 900);
      }
    });
  });

  function updateCartDot(count) {
    let dot = document.querySelector('.cart-dot');
    const wrap = document.querySelector('.cart-icon-wrap');
    if (!wrap) return;
    if (count > 0) {
      if (!dot) {
        dot = document.createElement('span');
        dot.className = 'cart-dot';
        wrap.appendChild(dot);
      }
      dot.textContent = count;
    } else if (dot) {
      dot.remove();
    }
  }

  /* ── Toast ──────────────────────────────────────────────── */
  function showToast(msg, type = 'success') {
    let wrap = document.querySelector('.flash-wrap');
    if (!wrap) {
      wrap = document.createElement('div');
      wrap.className = 'flash-wrap';
      document.body.appendChild(wrap);
    }
    const el = document.createElement('div');
    el.className = `flash flash--${type}`;
    el.innerHTML = `<span>${msg}</span><button onclick="this.parentElement.remove()">×</button>`;
    wrap.appendChild(el);
    setTimeout(() => el.remove(), 3000);
  }

  /* ── Auto-dismiss flash messages ───────────────────────── */
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => el?.remove(), 4000);
  });

  /* ── Hero card stack hover depth ───────────────────────── */
  const stack = document.querySelector('.hero-card-stack');
  if (stack) {
    stack.addEventListener('mouseleave', () => {
      stack.querySelectorAll('.hc').forEach(c => c.style.transform = '');
    });
  }

});
