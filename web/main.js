/* ── WAVE & PARTICLE BACKGROUND ── */
const canvas = document.getElementById('waveCanvas');
const ctx = canvas.getContext('2d');

function resize() {
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

const waves = Array.from({ length: 4 }, (_, i) => ({
  amp:    40  + i * 20,
  freq:   0.003 + i * 0.0001,
  speed:  0.0000008 + i * 0.000000001,
  offset: i * Math.PI / 2,
  y:      0.55 + i * 0.12,
  alpha:  0.06 - i * 0.01,
}));

const particles = Array.from({ length: 60 }, () => ({
  x:     Math.random() * window.innerWidth,
  y:     Math.random() * window.innerHeight,
  r:     Math.random() * 1.5 + 0.5,
  vx:    (Math.random() - 0.5) * 0.3,
  vy:    (Math.random() - 0.5) * 0.15,
  alpha: Math.random() * 0.5 + 0.1,
}));

let t = 0;

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Waves
  waves.forEach(w => {
    ctx.beginPath();
    ctx.moveTo(0, canvas.height);
    for (let x = 0; x <= canvas.width; x += 4) {
      const y = canvas.height * w.y
        + Math.sin(x * w.freq + t * w.speed * 1000 + w.offset) * w.amp;
      ctx.lineTo(x, y);
    }
    ctx.lineTo(canvas.width, canvas.height);
    ctx.closePath();
    ctx.fillStyle = `rgba(0, 200, 255, ${w.alpha})`;
    ctx.fill();
  });

  // Particles
  particles.forEach(p => {
    p.x += p.vx;
    p.y += p.vy;
    if (p.x < 0) p.x = canvas.width;
    if (p.x > canvas.width)  p.x = 0;
    if (p.y < 0) p.y = canvas.height;
    if (p.y > canvas.height) p.y = 0;

    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0, 200, 255, ${p.alpha})`;
    ctx.fill();
  });

  t = Date.now();
  requestAnimationFrame(draw);
}
draw();


/* ── SPORTS CARDS ── */
const sports = [
  { icon: '🏄', name: 'Surf',      status: 'good', text: 'Óptimo' },
  { icon: '🪁', name: 'Kitesurf',  status: 'warn', text: 'Viento fuerte' },
  { icon: '🚴', name: 'Ciclismo',  status: 'good', text: 'Ideal' },
  { icon: '🏃', name: 'Trail',     status: 'good', text: 'Perfecto' },
  { icon: '⛵', name: 'Vela',      status: 'warn', text: 'Precaución' },
  { icon: '🧗', name: 'Escalada',  status: 'bad',  text: 'Lluvia' },
  { icon: '🏊', name: 'Natación',  status: 'good', text: 'Ideal' },
  { icon: '🛶', name: 'Kayak',     status: 'warn', text: 'Corriente' },
];

const grid = document.getElementById('sportsGrid');
sports.forEach(s => {
  grid.innerHTML += `
    <div class="sport-card">
      <span class="sport-icon">${s.icon}</span>
      <div class="sport-name">${s.name}</div>
      <div class="sport-status status-${s.status}">${s.text}</div>
    </div>`;
});


/* ── ANIMATED COUNTERS ── */
function animCounter(el, target) {
  let n = 0;
  const step = Math.ceil(target / 60);
  const iv = setInterval(() => {
    n = Math.min(n + step, target);
    el.textContent = n.toLocaleString();
    if (n >= target) clearInterval(iv);
  }, 25);
}

const statsObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      animCounter(document.getElementById('counter1'), 47);
      animCounter(document.getElementById('counter2'), 128);
      animCounter(document.getElementById('counter3'), 312);
      animCounter(document.getElementById('counter4'), 1840);
      statsObserver.disconnect();
    }
  });
}, { threshold: 0.3 });

statsObserver.observe(document.querySelector('.stats-row'));


/* ── GRAFANA DASHBOARD TABS ── */

/*
  CONFIGURACIÓN: añade aquí las URLs de tus dashboards de Grafana.
  Formato: http://TU_SERVIDOR:3000/d/DASHBOARD_ID/nombre?orgId=1&theme=dark&kiosk

  Para habilitar el embed en grafana.ini:
    allow_embedding = true
  Y si usas acceso anónimo:
    [auth.anonymous]
    enabled  = true
    org_role = Viewer
*/
const dashboardConfig = {
  surf:    { name: 'Surf & Kite',   url: 'http://localhost:3000/goto/ffemt6go9mc5cb?orgId=1&kiosk=1' },
  ciclo:   { name: 'Ciclismo',      url: 'http://localhost:3000/goto/ffemt6go9mc5cb?orgId=1&kiosk=1' },
  trail:   { name: 'Trail Running', url: 'http://localhost:3000/goto/ffemt6go9mc5cb?orgId=1&kiosk=1' },
  vela:    { name: 'Vela',          url: 'http://localhost:3000/goto/ffemt6go9mc5cb?orgId=1&kiosk=1' },
  general: { name: 'General',       url: 'http://localhost:3000/goto/ffemt6go9mc5cb?orgId=1&kiosk=1' },
};

function switchTab(btn, key) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');

  const cfg = dashboardConfig[key];
  const ph  = document.getElementById('grafanaPlaceholder');

  if (cfg.url) {
    ph.innerHTML = `<iframe class="grafana-frame" src="${cfg.url}" allowfullscreen></iframe>`;
  } else {
    ph.innerHTML = `
      <div class="big-icon">📊</div>
      <strong style="color:var(--text)">Dashboard: ${cfg.name}</strong>
      <p>Configura la URL de tu dashboard de Grafana para visualizarlo aquí.</p>
      <span class="config-badge">⚙ Pendiente de configuración</span>
      <small style="margin-top:.5rem; opacity:.6">Ver comentarios en main.js</small>`;
  }
}
