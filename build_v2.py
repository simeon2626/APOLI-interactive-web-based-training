"""Generate modern single-file HTML presentation from extracted content."""
import json, base64, os
from pathlib import Path

BASE = Path(r"d:\presentation\extracted")
IMAGES = BASE / "images"
OUT = Path(r"d:\presentation\Тема-1") / "presentation.html"

def img_b64(name):
    path = IMAGES / name
    if not path.exists():
        return ""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = path.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif"}.get(ext, "image/png")
    return f"data:{mime};base64,{data}"

def img_tag(src, alt="", cls="full-img", style=""):
    if not src:
        return '<div style="height:280px;display:flex;align-items:center;justify-content:center;background:var(--surface);border-radius:var(--radius);font-size:48px;color:var(--text-muted)">x</div>'
    return '<img src="' + src + '" alt="' + alt + '" class="' + cls + '" style="' + style + '">'

# Preload images
browser_logos = [img_b64("main_slide4_img" + str(i) + ".png") for i in range(5)]
hyperlink_img = img_b64("main_slide8_img5.png")
safety_img    = img_b64("main_slide18_img7.jpg")
google_demo   = img_b64("demo_slide2_img0.png")
lec = [img_b64("lecture_doc_img" + str(i) + ".png") for i in range(14)]
# Verified image mapping:
# lec[1]  = Firefox with Bulgarian Wikipedia (Figure 3)
# lec[2]  = Google search results "обяви за работа" (Figure 5)
# lec[3]  = Chrome+Firefox+Edge comparison (Figure 2)
# lec[5]  = Firefox showing Bing (Figure 4 - Bing)
# lec[8]  = Firefox showing Google (Figure 4 - Google)

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #0f172a; --surface: #1e293b; --surface2: #263147;
  --accent: #6366f1; --accent2: #818cf8; --accent3: #38bdf8;
  --green: #22c55e; --red: #ef4444; --yellow: #f59e0b;
  --text: #f1f5f9; --text-muted: #94a3b8; --border: #334155;
  --radius: 16px; --radius-sm: 8px;
  --shadow: 0 25px 50px rgba(0,0,0,0.5);
}
html, body { height: 100%; overflow: hidden; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); }
#progress-bar { position: fixed; top: 0; left: 0; height: 3px; background: linear-gradient(90deg, var(--accent), var(--accent3)); transition: width 0.5s ease; z-index: 1000; box-shadow: 0 0 10px var(--accent); }
.nav-btn { position: fixed; top: 50%; transform: translateY(-50%); width: 48px; height: 48px; border-radius: 50%; border: 1px solid var(--border); background: rgba(30,41,59,0.8); backdrop-filter: blur(8px); cursor: pointer; color: var(--text); font-size: 20px; display: flex; align-items: center; justify-content: center; transition: all 0.3s; z-index: 100; }
.nav-btn:hover { background: var(--accent); border-color: var(--accent); box-shadow: 0 0 20px rgba(99,102,241,0.4); }
.nav-btn:disabled { opacity: 0.2; cursor: not-allowed; }
#btn-prev { left: 16px; } #btn-next { right: 16px; }
#nav { position: fixed; top: 16px; left: 16px; display: flex; flex-direction: row; flex-wrap: nowrap; align-items: center; gap: 4px; z-index: 200; background: rgba(15,23,42,0.75); backdrop-filter: blur(10px); padding: 7px 14px; border-radius: 50px; border: 1px solid var(--border); overflow: hidden; }
#nav-dots { display: flex; flex-direction: row; flex-wrap: nowrap; align-items: center; gap: 4px; }
.nav-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--border); cursor: pointer; transition: all 0.3s ease; flex-shrink: 0; }
.nav-dot.active { background: var(--accent); transform: scale(1.6); box-shadow: 0 0 5px var(--accent); }
.nav-dot:hover:not(.active) { background: var(--accent2); }
#slide-counter { font-size: 11px; color: var(--text-muted); margin-left: 8px; white-space: nowrap; flex-shrink: 0; }
#section-menu { position: fixed; top: 16px; right: 16px; z-index: 200; display: flex; gap: 8px; align-items: center; }
.section-pill { padding: 5px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid var(--border); background: rgba(30,41,59,0.8); backdrop-filter: blur(8px); cursor: pointer; transition: all 0.3s; color: var(--text-muted); }
.section-pill:hover, .section-pill.active { background: var(--accent); border-color: var(--accent); color: #fff; box-shadow: 0 0 16px rgba(99,102,241,0.4); }
#slides-wrapper { width: 100%; height: 100%; position: relative; overflow: hidden; }
.slide { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 80px 40px; opacity: 0; pointer-events: none; transform: translateX(60px); transition: opacity 0.5s ease, transform 0.5s ease; }
.slide.active { opacity: 1; pointer-events: all; transform: translateX(0); }
.slide.prev { opacity: 0; transform: translateX(-60px); }
.slide-title { background: radial-gradient(ellipse at 60% 40%, #312e81 0%, var(--bg) 70%); }
.slide-title .kicker { font-size: 13px; font-weight: 600; letter-spacing: 3px; text-transform: uppercase; color: var(--accent2); margin-bottom: 20px; }
.slide-title h1 { font-size: clamp(24px, 3.5vw, 42px); font-weight: 800; text-align: center; line-height: 1.25; max-width: 800px; background: linear-gradient(135deg, #fff 30%, var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.slide-title .subtitle { margin-top: 24px; color: var(--text-muted); font-size: 15px; }
.digcomp-badge { margin-top: 40px; padding: 10px 24px; border-radius: 50px; border: 1px solid rgba(99,102,241,0.4); background: rgba(99,102,241,0.1); font-size: 12px; color: var(--accent2); text-align: center; }
.slide-section { background: radial-gradient(ellipse at 50% 50%, #1e1b4b 0%, var(--bg) 65%); }
.section-number { font-size: 72px; font-weight: 900; line-height: 1; background: linear-gradient(135deg, var(--accent), var(--accent3)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; opacity: 0.5; position: relative; margin-bottom: 8px; }
.slide-section h2 { font-size: clamp(28px, 4vw, 52px); font-weight: 800; text-align: center; background: linear-gradient(135deg, #fff, var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.slide-section .section-desc { color: var(--text-muted); font-size: 16px; text-align: center; margin-top: 12px; max-width: 500px; }
.slide-content { align-items: flex-start; justify-content: flex-start; padding-top: 80px; }
.slide-content h2 { font-size: clamp(20px, 2.5vw, 32px); font-weight: 800; background: linear-gradient(135deg, #fff 60%, var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding-bottom: 12px; border-bottom: 2px solid; border-image: linear-gradient(90deg, var(--accent), transparent) 1; margin-bottom: 28px; width: 100%; }
.slide-body { width: 100%; flex: 1; display: flex; gap: 32px; min-height: 0; }
.slide-text { flex: 1; min-width: 0; }
.slide-img { flex: 0 0 auto; display: flex; align-items: flex-start; justify-content: center; }
.slide-img img { max-width: 360px; max-height: 320px; border-radius: var(--radius); box-shadow: var(--shadow); object-fit: contain; }
ul.bullets { list-style: none; display: flex; flex-direction: column; gap: 12px; }
ul.bullets li { display: flex; align-items: flex-start; gap: 12px; font-size: clamp(14px, 1.4vw, 17px); line-height: 1.6; color: var(--text); }
ul.bullets li::before { content: ''; flex-shrink: 0; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); margin-top: 8px; box-shadow: 0 0 8px var(--accent); }
ul.bullets li.sub { padding-left: 20px; }
ul.bullets li.sub::before { background: var(--accent3); width: 6px; height: 6px; }
.hl { color: var(--accent2); font-weight: 600; }
.cards { display: grid; gap: 16px; width: 100%; }
.cards.c2 { grid-template-columns: repeat(2, 1fr); }
.cards.c3 { grid-template-columns: repeat(3, 1fr); }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; transition: all 0.3s; }
.card:hover { border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(99,102,241,0.2); }
.card .ci { font-size: 32px; margin-bottom: 10px; }
.card h3 { font-size: 16px; font-weight: 700; margin-bottom: 8px; color: var(--accent2); }
.card p { font-size: 14px; color: var(--text-muted); line-height: 1.6; }
.browser-grid { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }
.browser-card { display: flex; flex-direction: column; align-items: center; gap: 8px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 28px; transition: all 0.3s; }
.browser-card:hover { border-color: var(--accent); transform: translateY(-4px); box-shadow: 0 12px 30px rgba(99,102,241,0.2); }
.browser-card span { font-size: 13px; color: var(--text-muted); font-weight: 600; }
.tip-box { background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(56,189,248,0.1)); border: 1px solid rgba(99,102,241,0.4); border-radius: var(--radius); padding: 16px 20px; margin-top: 16px; font-size: 14px; color: var(--text-muted); line-height: 1.6; }
.tip-box strong { color: var(--accent2); }
.warn-box { background: linear-gradient(135deg, rgba(245,158,11,0.12), rgba(239,68,68,0.08)); border: 1px solid rgba(245,158,11,0.4); border-radius: var(--radius); padding: 16px 20px; margin-top: 16px; font-size: 14px; color: var(--text-muted); line-height: 1.6; }
.warn-box strong { color: var(--yellow); }
.img-caption { margin-top: 12px; font-size: 13px; color: var(--text-muted); text-align: center; font-style: italic; }
.full-img { max-width: 100%; max-height: 55vh; border-radius: var(--radius); box-shadow: var(--shadow); object-fit: contain; }
.result-item { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px 16px; margin-bottom: 10px; transition: border-color 0.2s; }
.result-item:hover { border-color: var(--accent); }
.r-url { font-size: 12px; color: var(--green); margin-bottom: 4px; }
.r-title { font-size: 15px; font-weight: 600; color: var(--accent2); margin-bottom: 4px; }
.r-desc { font-size: 13px; color: var(--text-muted); line-height: 1.5; }
.result-item.ad { border-color: rgba(245,158,11,0.4); }
.result-item.ad .r-url::before { content: 'Реклама · '; color: var(--yellow); font-weight: 600; }
.safety-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; width: 100%; }
.safety-item { display: flex; gap: 12px; align-items: flex-start; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px; }
.safety-icon { font-size: 24px; flex-shrink: 0; margin-top: 2px; }
.safety-text { font-size: 13px; color: var(--text-muted); line-height: 1.5; }
.safety-text strong { color: var(--text); display: block; margin-bottom: 2px; font-size: 14px; }
.slide-quiz { background: radial-gradient(ellipse at 30% 70%, #1e1b4b 0%, var(--bg) 60%); }
.quiz-container { width: 100%; max-width: 780px; }
.quiz-progress { display: flex; gap: 6px; margin-bottom: 32px; }
.quiz-step { height: 4px; flex: 1; border-radius: 2px; background: var(--border); transition: background 0.4s; }
.quiz-step.done { background: var(--green); }
.quiz-step.current { background: var(--accent); }
.question-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px 32px; margin-bottom: 20px; }
.q-number { font-size: 12px; font-weight: 700; color: var(--accent2); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
.q-text { font-size: clamp(16px, 2vw, 20px); font-weight: 600; line-height: 1.5; margin-bottom: 24px; }
.q-multi-label { font-size: 12px; color: var(--text-muted); margin-bottom: 14px; font-style: italic; }
.options { display: flex; flex-direction: column; gap: 10px; }
.option { display: flex; align-items: center; gap: 14px; background: var(--surface2); border: 2px solid var(--border); border-radius: var(--radius-sm); padding: 14px 18px; cursor: pointer; transition: all 0.25s; font-size: 15px; }
.option:hover:not(.disabled) { border-color: var(--accent); background: rgba(99,102,241,0.1); }
.option.selected { border-color: var(--accent); background: rgba(99,102,241,0.15); }
.option.correct { border-color: var(--green) !important; background: rgba(34,197,94,0.15) !important; color: var(--green); }
.option.wrong { border-color: var(--red) !important; background: rgba(239,68,68,0.1) !important; color: rgba(239,68,68,0.8); }
.option.disabled { cursor: not-allowed; }
.option-letter { width: 28px; height: 28px; border-radius: 6px; flex-shrink: 0; background: var(--border); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; transition: all 0.25s; }
.option.selected .option-letter { background: var(--accent); color: #fff; }
.option.correct .option-letter { background: var(--green); color: #fff; }
.option.wrong .option-letter { background: var(--red); color: #fff; }
.q-feedback { margin-top: 16px; padding: 14px 18px; border-radius: var(--radius-sm); font-size: 14px; line-height: 1.6; display: none; }
.q-feedback.show { display: block; }
.q-feedback.correct { background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.4); color: var(--green); }
.q-feedback.wrong { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); color: #fca5a5; }
.quiz-btn { padding: 12px 32px; border-radius: 50px; border: none; cursor: pointer; font-size: 15px; font-weight: 700; transition: all 0.3s; margin-top: 8px; }
.quiz-btn.primary { background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #fff; box-shadow: 0 4px 20px rgba(99,102,241,0.4); }
.quiz-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(99,102,241,0.6); }
.quiz-btn.primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
.quiz-btn.secondary { background: var(--surface2); color: var(--text); border: 1px solid var(--border); }
.quiz-btn.secondary:hover { border-color: var(--accent); color: var(--accent2); }
.score-screen { text-align: center; display: none; flex-direction: column; align-items: center; gap: 20px; }
.score-screen.show { display: flex; }
.score-circle { width: 120px; height: 120px; border-radius: 50%; border: 4px solid var(--accent); display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(rgba(99,102,241,0.2), transparent); box-shadow: 0 0 40px rgba(99,102,241,0.3); }
.score-num { font-size: 42px; font-weight: 900; color: var(--accent2); }
.score-total { font-size: 14px; color: var(--text-muted); }
.score-msg { font-size: 20px; font-weight: 700; }
.score-detail { font-size: 14px; color: var(--text-muted); max-width: 460px; text-align: center; line-height: 1.7; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-children > * { opacity: 0; animation: fadeUp 0.5s ease forwards; }
.animate-children > *:nth-child(1) { animation-delay: 0.08s; }
.animate-children > *:nth-child(2) { animation-delay: 0.16s; }
.animate-children > *:nth-child(3) { animation-delay: 0.24s; }
.animate-children > *:nth-child(4) { animation-delay: 0.32s; }
.animate-children > *:nth-child(5) { animation-delay: 0.40s; }
.animate-children > *:nth-child(6) { animation-delay: 0.48s; }
.animate-children > *:nth-child(7) { animation-delay: 0.56s; }
.animate-children > *:nth-child(8) { animation-delay: 0.64s; }
.scrollable { overflow-y: auto; max-height: calc(100vh - 200px); scrollbar-width: thin; scrollbar-color: var(--border) transparent; }
.scrollable::-webkit-scrollbar { width: 4px; }
.scrollable::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
kbd { padding: 2px 5px; border: 1px solid var(--border); border-radius: 4px; background: var(--surface); font-size: 11px; }
@media (max-width: 768px) {
  .slide { padding: 50px 24px 40px; }
  .slide-body { flex-direction: column; }
  .cards.c2, .cards.c3, .safety-grid { grid-template-columns: 1fr; }
  #section-menu { display: none; }
  .nav-btn { width: 38px; height: 38px; font-size: 16px; }
  #nav { max-width: calc(100vw - 90px); }
}
.ctrl-sep { width: 1px; height: 18px; background: var(--border); margin: 0 2px; flex-shrink: 0; }
.ui-btn { width: 30px; height: 30px; border-radius: 50%; border: 1px solid var(--border); background: transparent; cursor: pointer; color: var(--text-muted); font-size: 14px; display: flex; align-items: center; justify-content: center; transition: all 0.3s; padding: 0; flex-shrink: 0; }
.ui-btn:hover { background: var(--accent); border-color: var(--accent); color: #fff; }
body.light {
  --bg: #f0f4f8; --surface: #ffffff; --surface2: #e8eef6;
  --text: #1e293b; --text-muted: #475569; --border: #c8d3df;
  --shadow: 0 25px 50px rgba(0,0,0,0.12);
}
body.light #nav { background: rgba(240,244,248,0.92); }
body.light #section-menu { background: rgba(240,244,248,0.92); backdrop-filter: blur(10px); border-radius: 50px; border: 1px solid var(--border); padding: 5px 12px; }
body.light .section-pill { background: rgba(255,255,255,0.8); color: var(--text-muted); }
body.light .nav-btn { background: rgba(255,255,255,0.9); color: var(--text); }
body.light .slide-title { background: radial-gradient(ellipse at 60% 40%, #c7d2fe 0%, var(--bg) 70%); }
body.light .slide-section { background: radial-gradient(ellipse at 50% 50%, #ddd6fe 0%, var(--bg) 65%); }
body.light .slide-quiz { background: radial-gradient(ellipse at 30% 70%, #c7d2fe 0%, var(--bg) 60%); }
body.light .slide-title h1 { background: linear-gradient(135deg, #1e1b4b 30%, var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
body.light .slide-section h2 { background: linear-gradient(135deg, #1e1b4b, var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
body.light .slide-content h2 { background: linear-gradient(135deg, #1e293b 60%, var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
body.light .section-number { background: linear-gradient(135deg, var(--accent), var(--accent3)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
"""

JS = """
const slides = Array.from(document.querySelectorAll('.slide'));
const TOTAL = slides.length;
let current = 0;

function goToSlide(n) {
  if (n < 0 || n >= TOTAL) return;
  const prev = slides[current];
  const next = slides[n];
  if (prev === next) return;
  prev.classList.remove('active');
  prev.classList.add('prev');
  setTimeout(function() { prev.classList.remove('prev'); }, 600);
  next.querySelectorAll('.animate-children').forEach(function(el) {
    el.querySelectorAll(':scope > *').forEach(function(c) {
      c.style.animation = 'none'; c.offsetHeight; c.style.animation = '';
    });
  });
  next.classList.add('active');
  current = n;
  updateNav();
}
function changeSlide(dir) { goToSlide(current + dir); }

function updateNav() {
  var pct = TOTAL <= 1 ? 100 : (current / (TOTAL - 1)) * 100;
  document.getElementById('progress-bar').style.width = pct + '%';
  document.getElementById('slide-counter').textContent = (current + 1) + ' / ' + TOTAL;
  document.querySelectorAll('.nav-dot').forEach(function(d, i) { d.classList.toggle('active', i === current); });
  document.getElementById('btn-prev').disabled = current === 0;
  document.getElementById('btn-next').disabled = current === TOTAL - 1;
  var anchors = [0, 1, 4, 13, 21, 25];
  var pills = document.querySelectorAll('.section-pill');
  var activeSec = 0;
  anchors.forEach(function(s, i) { if (current >= s) activeSec = i; });
  pills.forEach(function(p, i) { p.classList.toggle('active', i === activeSec); });
}

(function buildDots() {
  var c = document.getElementById('nav-dots');
  for (var i = 0; i < TOTAL; i++) {
    var d = document.createElement('div');
    d.className = 'nav-dot' + (i === 0 ? ' active' : '');
    d.onclick = (function(idx) { return function() { goToSlide(idx); }; })(i);
    d.title = 'Slide ' + (i + 1);
    c.appendChild(d);
  }
})();
updateNav();

document.addEventListener('keydown', function(e) {
  if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); changeSlide(1); }
  if (e.key === 'ArrowLeft') { e.preventDefault(); changeSlide(-1); }
  if (e.key === 'Home') goToSlide(0);
  if (e.key === 'End') goToSlide(TOTAL - 1);
});
var touchStartX = 0;
document.addEventListener('touchstart', function(e) { touchStartX = e.touches[0].clientX; }, {passive:true});
document.addEventListener('touchend', function(e) {
  var dx = e.changedTouches[0].clientX - touchStartX;
  if (Math.abs(dx) > 50) changeSlide(dx < 0 ? 1 : -1);
}, {passive:true});

function toggleTheme() {
  var isLight = document.body.classList.toggle('light');
  document.getElementById('btn-theme').innerHTML = isLight ? '&#9728;&#65039;' : '&#127769;';
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else if (document.exitFullscreen) {
    document.exitFullscreen();
  }
}

// ===== QUIZ =====
var quizAnswers = [null, [], null];
var quizChecked = [false, false, false];
var quizCorrect = [false, false, false];
var currentQ = 0;

function selectOption(qIdx, optIdx) {
  if (quizChecked[qIdx]) return;
  quizAnswers[qIdx] = optIdx;
  document.querySelectorAll('#opts-' + qIdx + ' .option').forEach(function(o, i) {
    o.classList.toggle('selected', i === optIdx);
  });
  document.getElementById('qbtn-check-' + qIdx).disabled = false;
}

function toggleMultiOption(qIdx, optIdx) {
  if (quizChecked[qIdx]) return;
  var idx = quizAnswers[qIdx].indexOf(optIdx);
  if (idx === -1) quizAnswers[qIdx].push(optIdx);
  else quizAnswers[qIdx].splice(idx, 1);
  document.querySelectorAll('#opts-' + qIdx + ' .option').forEach(function(o, i) {
    o.classList.toggle('selected', quizAnswers[qIdx].indexOf(i) !== -1);
  });
  document.getElementById('qbtn-check-' + qIdx).disabled = quizAnswers[qIdx].length === 0;
}

function checkAnswer(qIdx, correctIdx, isLast) {
  if (quizAnswers[qIdx] === null) return;
  quizChecked[qIdx] = true;
  document.getElementById('qbtn-check-' + qIdx).disabled = true;
  var opts = document.querySelectorAll('#opts-' + qIdx + ' .option');
  opts.forEach(function(o) { o.classList.add('disabled'); });
  var chosen = quizAnswers[qIdx];
  var isRight = chosen === correctIdx;
  quizCorrect[qIdx] = isRight;
  opts[correctIdx].classList.add('correct');
  if (!isRight) opts[chosen].classList.add('wrong');
  var fb = document.getElementById('qfb-' + qIdx);
  var feedbacks = {
    0: {
      ok: '\u2705 <strong>\u041f\u0440\u0430\u0432\u0438\u043b\u043d\u043e!</strong> \u0418\u043d\u0442\u0435\u0440\u043d\u0435\u0442 \u0435 \u0433\u043b\u043e\u0431\u0430\u043b\u043d\u0430 \u043c\u0440\u0435\u0436\u0430 \u043e\u0442 \u043c\u0440\u0435\u0436\u0438, \u043a\u043e\u044f\u0442\u043e \u0441\u0432\u044a\u0440\u0437\u0432\u0430 \u043c\u0438\u043b\u0438\u0430\u0440\u0434\u0438 \u043f\u043e\u0442\u0440\u0435\u0431\u0438\u0442\u0435\u043b\u0438 \u043f\u043e \u0446\u0435\u043b\u0438\u044f \u0441\u0432\u044f\u0442.',
      err: '\u274c <strong>\u041d\u0435\u043f\u0440\u0430\u0432\u0438\u043b\u043d\u043e.</strong> \u041f\u0440\u0430\u0432\u0438\u043b\u043d\u0438\u044f\u0442 \u043e\u0442\u0433\u043e\u0432\u043e\u0440 \u0435 <strong>\u0412)</strong>. \u0418\u043d\u0442\u0435\u0440\u043d\u0435\u0442 \u0435 <em>\u0433\u043b\u043e\u0431\u0430\u043b\u043d\u0430</em> \u043c\u0440\u0435\u0436\u0430 \u2014 \u043d\u0435 \u0435 \u043b\u043e\u043a\u0430\u043b\u043d\u0430 \u0438 \u043d\u0435 \u0435 \u0441\u0430\u043c\u043e \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u0430.'
    },
    2: {
      ok: '\u2705 <strong>\u041f\u0440\u0430\u0432\u0438\u043b\u043d\u043e!</strong> \u0422\u0432\u044a\u0440\u0434\u0435\u043d\u0438\u0435\u0442\u043e \u201e\u043c\u043e\u0436\u0435\u043c \u0434\u0430 \u0442\u044a\u0440\u0441\u0438\u043c \u0441\u0430\u043c\u043e \u043d\u0430 \u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u0438\u201c \u0435 <em>\u043d\u0435\u0432\u044f\u0440\u043d\u043e</em> \u2014 \u0442\u044a\u0440\u0441\u0430\u0447\u043a\u0438\u0442\u0435 \u043f\u043e\u0434\u0434\u044a\u0440\u0436\u0430\u0442 \u0432\u0441\u0438\u0447\u043a\u0438 \u0435\u0437\u0438\u0446\u0438, \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u0435\u043b\u043d\u043e \u0431\u044a\u043b\u0433\u0430\u0440\u0441\u043a\u0438.',
      err: '\u274c <strong>\u041d\u0435\u043f\u0440\u0430\u0432\u0438\u043b\u043d\u043e.</strong> \u041e\u0442\u0433\u043e\u0432\u043e\u0440 <strong>\u0411)</strong> \u0435 \u043d\u0435\u0432\u044f\u0440\u043d\u043e\u0442\u043e \u0442\u0432\u044a\u0440\u0434\u0435\u043d\u0438\u0435 \u2014 \u0432 \u0418\u043d\u0442\u0435\u0440\u043d\u0435\u0442 \u043c\u043e\u0436\u0435\u043c \u0434\u0430 \u0442\u044a\u0440\u0441\u0438\u043c \u043d\u0430 \u0432\u0441\u044f\u043a\u0430\u043a\u044a\u0432 \u0435\u0437\u0438\u043a.'
    }
  };
  fb.className = 'q-feedback show ' + (isRight ? 'correct' : 'wrong');
  fb.innerHTML = isRight ? feedbacks[qIdx].ok : feedbacks[qIdx].err;
  setTimeout(function() {
    if (!isLast) {
      currentQ = qIdx + 1;
      document.getElementById('qblock-' + qIdx).style.display = 'none';
      document.getElementById('qblock-' + currentQ).style.display = 'block';
      document.getElementById('qstep-' + qIdx).className = 'quiz-step done';
      if (currentQ < 3) document.getElementById('qstep-' + currentQ).className = 'quiz-step current';
    } else { showScore(); }
  }, 2200);
}

function checkMultiAnswer(qIdx, correctSet) {
  if (quizAnswers[qIdx].length === 0) return;
  quizChecked[qIdx] = true;
  document.getElementById('qbtn-check-' + qIdx).disabled = true;
  var opts = document.querySelectorAll('#opts-' + qIdx + ' .option');
  opts.forEach(function(o) { o.classList.add('disabled'); });
  var chosen = quizAnswers[qIdx];
  var choseWrong = chosen.indexOf(2) !== -1;
  var missedCorrect = correctSet.some(function(i) { return chosen.indexOf(i) === -1; });
  var isRight = !choseWrong && !missedCorrect;
  quizCorrect[qIdx] = isRight;
  opts.forEach(function(o, i) {
    if (correctSet.indexOf(i) !== -1) o.classList.add('correct');
    else if (chosen.indexOf(i) !== -1) o.classList.add('wrong');
  });
  var fb = document.getElementById('qfb-' + qIdx);
  fb.className = 'q-feedback show ' + (isRight ? 'correct' : 'wrong');
  fb.innerHTML = isRight
    ? '\u2705 <strong>\u041f\u0440\u0430\u0432\u0438\u043b\u043d\u043e!</strong> Google \u0438 Bing \u0441\u0430 \u0442\u044a\u0440\u0441\u0435\u0449\u0438 \u043c\u0430\u0448\u0438\u043d\u0438; Firefox \u0438 Chrome \u0441\u0430 \u0431\u0440\u0430\u0443\u0437\u044a\u0440\u0438.'
    : '\u274c <strong>\u0412\u043d\u0438\u043c\u0430\u043d\u0438\u0435:</strong> <strong>Chrome \u0435 \u0431\u0440\u0430\u0443\u0437\u044a\u0440</strong>, \u0430 \u043d\u0435 \u0442\u044a\u0440\u0441\u0435\u0449\u0430 \u043c\u0430\u0448\u0438\u043d\u0430! Google \u0438 Bing \u0441\u0430 \u0442\u044a\u0440\u0441\u0430\u0447\u043a\u0438; Firefox \u0438 Chrome \u2014 \u0431\u0440\u0430\u0443\u0437\u044a\u0440\u0438.';
  setTimeout(function() {
    currentQ = qIdx + 1;
    document.getElementById('qblock-' + qIdx).style.display = 'none';
    document.getElementById('qblock-' + currentQ).style.display = 'block';
    document.getElementById('qstep-' + qIdx).className = 'quiz-step done';
    document.getElementById('qstep-' + currentQ).className = 'quiz-step current';
  }, 2200);
}

function showScore() {
  document.querySelectorAll('[id^=qblock-]').forEach(function(b) { b.style.display = 'none'; });
  document.getElementById('score-screen').classList.add('show');
  document.querySelectorAll('.quiz-step').forEach(function(s) { s.className = 'quiz-step done'; });
  var score = quizCorrect.filter(Boolean).length;
  document.getElementById('score-num').textContent = score;
  var msgs = ['\u041e\u043f\u0438\u0442\u0430\u0439\u0442\u0435 \u043e\u0442\u043d\u043e\u0432\u043e! \U0001F4AA', '\u0414\u043e\u0431\u044a\u0440 \u0441\u0442\u0430\u0440\u0442! \U0001F4DA', '\u041c\u043d\u043e\u0433\u043e \u0434\u043e\u0431\u0440\u0435! \U0001F44D', '\u041e\u0442\u043b\u0438\u0447\u0435\u043d \u0440\u0435\u0437\u0443\u043b\u0442\u0430\u0442! \U0001F3C6'];
  var details = [
    '\u041f\u0440\u0435\u0433\u043b\u0435\u0434\u0430\u0439\u0442\u0435 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430 \u0438 \u043e\u043f\u0438\u0442\u0430\u0439\u0442\u0435 \u043e\u0442\u043d\u043e\u0432\u043e \u2014 \u0449\u0435 \u0441\u0435 \u0441\u043f\u0440\u0430\u0432\u0438\u0442\u0435!',
    '\u041f\u0440\u043e\u0447\u0435\u0442\u0435\u0442\u0435 \u043f\u043e\u0432\u0442\u043e\u0440\u043d\u043e \u0440\u0430\u0437\u0434\u0435\u043b\u0438\u0442\u0435, \u043f\u0440\u0438 \u043a\u043e\u0438\u0442\u043e \u0438\u043c\u0430\u0442\u0435 \u0433\u0440\u0435\u0448\u043a\u0438.',
    '\u041f\u043e\u0447\u0442\u0438 \u043f\u0435\u0440\u0444\u0435\u043a\u0442\u043d\u043e! \u041f\u0440\u0435\u0433\u043b\u0435\u0434\u0430\u0439\u0442\u0435 \u0432\u044a\u043f\u0440\u043e\u0441\u0438\u0442\u0435 \u0441 \u0433\u0440\u0435\u0448\u043a\u0438 \u0437\u0430 \u043f\u044a\u043b\u043d\u043e \u0440\u0430\u0437\u0431\u0438\u0440\u0430\u043d\u0435.',
    '\u0423\u0441\u0432\u043e\u0438\u043b\u0438 \u0441\u0442\u0435 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430 \u043e\u0442\u043b\u0438\u0447\u043d\u043e! \u0413\u043e\u0442\u043e\u0432\u0438 \u0441\u0442\u0435 \u0437\u0430 \u0441\u043b\u0435\u0434\u0432\u0430\u0449\u0430\u0442\u0430 \u0442\u0435\u043c\u0430.'
  ];
  document.getElementById('score-msg').textContent = msgs[score];
  document.getElementById('score-detail').textContent = details[score];
}

function resetQuiz() {
  quizAnswers = [null, [], null];
  quizChecked = [false, false, false];
  quizCorrect = [false, false, false];
  currentQ = 0;
  for (var i = 0; i < 3; i++) {
    document.getElementById('qblock-' + i).style.display = i === 0 ? 'block' : 'none';
    document.querySelectorAll('#opts-' + i + ' .option').forEach(function(o) { o.className = 'option'; });
    document.getElementById('qfb-' + i).className = 'q-feedback';
    document.getElementById('qbtn-check-' + i).disabled = true;
    document.getElementById('qstep-' + i).className = 'quiz-step' + (i === 0 ? ' current' : '');
  }
  document.getElementById('score-screen').classList.remove('show');
}
"""

def build_browser_cards():
    names = ["Google Chrome", "Mozilla Firefox", "Opera", "Microsoft Edge", "Safari"]
    bgs   = ["Хром", "Файърфокс", "Опера", "Едж", "Сафари"]
    result = ""
    for i, (name, bg) in enumerate(zip(names, bgs)):
        logo = browser_logos[i] if i < len(browser_logos) else ""
        img_h = '<img src="' + logo + '" alt="' + name + '" style="width:52px;height:52px;object-fit:contain">' if logo else '<div style="font-size:48px">&#127760;</div>'
        result += '<div class="browser-card">' + img_h + '<span>' + name + '</span><span style="font-size:11px;color:var(--accent2)">' + bg + '</span></div>\n'
    return result

# Build HTML
parts = []

parts.append("""<!DOCTYPE html>
<html lang="bg">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Тема 1.1 — Сърфиране, търсене и филтриране на данни</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap" rel="stylesheet">
<style>
""" + CSS + """
</style>
</head>
<body>
<div id="progress-bar" style="width:0%"></div>
<button class="nav-btn" id="btn-prev" onclick="changeSlide(-1)">&#8592;</button>
<button class="nav-btn" id="btn-next" onclick="changeSlide(1)">&#8594;</button>
<div id="section-menu">
  <div class="section-pill" onclick="goToSlide(0)">Начало</div>
  <div class="section-pill" onclick="goToSlide(1)">Интернет</div>
  <div class="section-pill" onclick="goToSlide(4)">Браузър</div>
  <div class="section-pill" onclick="goToSlide(13)">Търсене</div>
  <div class="section-pill" onclick="goToSlide(21)">Безопасност</div>
  <div class="section-pill" onclick="goToSlide(25)">Тест</div>
  <div class="ctrl-sep"></div>
  <button class="ui-btn" id="btn-theme" onclick="toggleTheme()" title="\u0422\u044a\u043c\u0435\u043d/\u0441\u0432\u0435\u0442\u044a\u043b \u0440\u0435\u0436\u0438\u043c">&#127769;</button>
  <button class="ui-btn" id="btn-fs" onclick="toggleFullscreen()" title="\u0426\u044f\u043b \u0435\u043a\u0440\u0430\u043d">&#x26F6;</button>
</div>

<div id="slides-wrapper">
""")

# SLIDE 0: TITLE
parts.append("""<div class="slide slide-title active">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center">
    <div class="kicker">Тема 1.1</div>
    <h1>Сърфиране, търсене и филтриране на данни,<br>информация и дигитално съдържание</h1>
    <p class="subtitle">Мултимедийна презентация-урок</p>
    <div class="digcomp-badge">&#128203; Европейска Рамка на дигиталните компетентности (DigComp 2.1) &middot; Нива 1&ndash;2</div>
    <div style="margin-top:50px;display:flex;gap:16px;flex-wrap:wrap;justify-content:center">
      <div class="card" style="width:auto;padding:14px 22px;display:flex;gap:10px;align-items:center">
        <span style="font-size:22px">&#127760;</span>
        <div><div style="font-size:13px;font-weight:700;color:var(--accent2)">4 раздела</div><div style="font-size:12px;color:var(--text-muted)">теоретичен материал</div></div>
      </div>
      <div class="card" style="width:auto;padding:14px 22px;display:flex;gap:10px;align-items:center">
        <span style="font-size:22px">&#128269;</span>
        <div><div style="font-size:13px;font-weight:700;color:var(--accent2)">4 практически задачи</div><div style="font-size:12px;color:var(--text-muted)">интерактивни примери</div></div>
      </div>
      <div class="card" style="width:auto;padding:14px 22px;display:flex;gap:10px;align-items:center">
        <span style="font-size:22px">&#9989;</span>
        <div><div style="font-size:13px;font-weight:700;color:var(--accent2)">Тест за самооценка</div><div style="font-size:12px;color:var(--text-muted)">3 въпроса с обратна връзка</div></div>
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 1: SECTION INTERNET
parts.append("""<div class="slide slide-section">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:12px;position:relative">
    <div class="section-number">01</div>
    <h2>Интернет</h2>
    <p class="section-desc">Какво представлява глобалната мрежа и какво можем да правим с нея</p>
  </div>
</div>
""")

# SLIDE 2: КАКВО Е ИНТЕРНЕТ
parts.append("""<div class="slide slide-content">
  <h2>Какво е Интернет?</h2>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets" style="gap:20px">
        <li>Интернет е най-голямата <span class="hl">компютърна мрежа</span> в световен мащаб</li>
        <li>Представлява <span class="hl">&bdquo;мрежа от мрежи&ldquo;</span> &mdash; свързва милиони частни, обществени, университетски, фирмени и държавни мрежи</li>
        <li>Осигурява <span class="hl">отдалечен достъп</span> до голямо разнообразие от информационни ресурси и услуги</li>
      </ul>
      <div class="tip-box" style="margin-top:28px;margin-bottom:28px">
        <strong>&#128161; Знаете ли?</strong><br>
        Думата &bdquo;Интернет&ldquo; идва от <em>inter</em> (между) + <em>network</em> (мрежа). Накратко се казва и <strong>&bdquo;нет&ldquo;</strong>.
      </div>
      <ul class="bullets" style="gap:20px">
        <li><strong>&#128073;</strong> Интернет е като огромна мрежа, която свързва компютри по целия свят. Благодарение на него можем за секунди да намерим информация, да гледаме видеа или да общуваме с хора, които са далеч от нас.</li>
        <li><strong>&#128073;</strong> Най-просто казано: Интернет е мястото, където търсим, учим и общуваме онлайн. &#127757;</li>
      </ul>
    </div>
    <div class="slide-img">
      <div style="width:230px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:24px;text-align:center">
        <div style="font-size:60px;margin-bottom:12px">&#127760;</div>
        <div style="font-size:13px;color:var(--text-muted);line-height:1.8">Свързва<br><strong style="color:var(--accent2)">милиарди</strong><br>потребители<br>по целия свят</div>
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 3: В ИНТЕРНЕТ МОЖЕМ
parts.append("""<div class="slide slide-content">
  <h2>В Интернет можем...</h2>
  <div class="slide-body">
    <div class="animate-children" style="width:100%">
      <div class="cards c3" style="margin-bottom:20px">
        <div class="card"><div class="ci">&#127780;&#65039;</div><h3>Прогноза за времето</h3><p>Проверяваме актуалните метеорологични условия и прогноза</p></div>
        <div class="card"><div class="ci">&#128240;</div><h3>Новини</h3><p>Следим актуалните новини и събития от цял свят</p></div>
        <div class="card"><div class="ci">&#9992;&#65039;</div><h3>Ваканция</h3><p>Избираме места, резервираме билети и хотели онлайн</p></div>
        <div class="card"><div class="ci">&#128188;</div><h3>Обяви за работа</h3><p>Търсим нови кариерни възможности и оферти</p></div>
        <div class="card"><div class="ci">&#128179;</div><h3>Онлайн плащания</h3><p>Плащаме сметки за ток, вода, телефон и интернет</p></div>
        <div class="card"><div class="ci">&#128172;</div><h3>Комуникация</h3><p>Общуваме чрез текст, аудио и видеовръзка</p></div>
      </div>
      <div class="tip-box">
        <strong>И много, много повече!</strong> Интернет е неразделна и незаменима част от съвременния свят.
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 4: SECTION БРАУЗЪР
parts.append("""<div class="slide slide-section">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:12px;position:relative">
    <div class="section-number">02</div>
    <h2>Интернет браузър</h2>
    <p class="section-desc">Програмата, чрез която влизаме и сърфираме в Интернет</p>
  </div>
</div>
""")

# SLIDE 5: КАКВО Е БРАУЗЪР
parts.append("""<div class="slide slide-content">
  <h2>Интернет браузър</h2>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Специална програма за <span class="hl">влизане и сърфиране</span> в Интернет</li>
        <li>Служи за <span class="hl">отваряне и разглеждане</span> на уеб страници</li>
        <li>Осигурява <span class="hl">връзката</span> между потребителя и информацията в глобалната мрежа</li>
        <li>За да влезем в Интернет, браузърът трябва да е <span class="hl">инсталиран</span> на компютъра</li>
        <li><span class="hl">Браузърът</span> и <span class="hl">търсачката</span> са <em>различни</em> неща! (Chrome е браузър, Google е търсачка)</li>
      </ul>
      <div class="tip-box">
        <strong>&#128204; Аналогия:</strong> Браузърът е като автомобил &mdash; превозва ви до дестинацията. Търсачката е като GPS &mdash; помага ви да намерите пътя.
      </div>
    </div>
    <div class="slide-img">
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;width:200px;text-align:center">
        <div style="font-size:48px;margin-bottom:8px">&#127760;</div>
        <div style="font-size:12px;color:var(--text-muted);line-height:1.7">Браузърът е прозорецът<br>към Интернет</div>
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 6: ПОПУЛЯРНИ БРАУЗЪРИ
parts.append('<div class="slide slide-content">\n  <h2>Популярни интернет браузъри</h2>\n  <div class="slide-body" style="flex-direction:column">\n    <div style="width:100%" class="animate-children">\n      <div class="browser-grid">\n' + build_browser_cards() + '      </div>\n      <div class="tip-box" style="margin-top:20px">\n        <strong>&#128161; Важно:</strong> Браузърът <strong>НЕ е</strong> същото като търсещата машина! Браузърът е програма, търсачката е уеб страница отворена в браузъра.\n      </div>\n    </div>\n  </div>\n</div>\n')

# SLIDE 7: СТРУКТУРА НА БРАУЗЪР
parts.append("""<div class="slide slide-content">
  <h2>Структура на браузъра</h2>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li><span class="hl">Прозорец</span> &mdash; браузърът се отваря в отделен прозорец, като всяка друга програма</li>
        <li><span class="hl">Раздел (таб)</span> &mdash; всяка отделна уеб страница; може да отвряте много раздели едновременно</li>
        <li><span class="hl">Начална страница</span> &mdash; разделът, зареждащ се автоматично при стартиране</li>
        <li><span class="hl">Адресно поле</span> &mdash; изписва се адресът (URL) на уеб страницата; играе и роля на търсачка</li>
        <li><span class="hl">Бутони за навигация</span> &mdash; &#8592; назад, &#8594; напред, &#8635; презареждане</li>
      </ul>
    </div>
    <div class="slide-img">
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;width:270px">
        <div style="background:var(--surface2);border-radius:6px;padding:8px 12px;margin-bottom:8px;display:flex;gap:6px;align-items:center">
          <div style="width:10px;height:10px;border-radius:50%;background:#ef4444"></div>
          <div style="width:10px;height:10px;border-radius:50%;background:#f59e0b"></div>
          <div style="width:10px;height:10px;border-radius:50%;background:#22c55e"></div>
          <div style="margin-left:8px;font-size:10px;color:var(--text-muted)">Прозорец</div>
        </div>
        <div style="background:var(--bg);border-radius:4px 4px 0 0;padding:5px 8px;font-size:10px;color:var(--text-muted);border-bottom:1px solid var(--border);display:flex;gap:4px">
          <span style="background:var(--accent)20;padding:2px 8px;border-radius:4px 4px 0 0;color:var(--accent2)">Раздел 1</span>
          <span style="padding:2px 8px">Раздел 2</span>
          <span style="margin-left:4px">+</span>
        </div>
        <div style="background:var(--bg);padding:6px 8px;margin:6px 0;font-size:10px;color:var(--text-muted);display:flex;gap:6px;align-items:center">
          <span>&#8592; &#8594;</span>
          <div style="flex:1;background:var(--surface);border-radius:3px;padding:3px 8px">https://bg.wikipedia.org</div>
        </div>
        <div style="background:var(--surface2);border-radius:4px;padding:14px;font-size:11px;color:var(--text-muted);text-align:center;min-height:70px;display:flex;align-items:center;justify-content:center">
          &#127760; Съдържание на уеб страницата
        </div>
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 8: ИНТЕРНЕТ СТРАНИЦА
parts.append("""<div class="slide slide-content">
  <h2>Интернет страница (Уеб страница)</h2>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Специален файл, съдържащ информация под формата на <span class="hl">текст, изображения, видео и аудио</span></li>
        <li>Има <span class="hl">уникален адрес (URL)</span> &mdash; указва точното място в Интернет</li>
        <li>Адресът се изписва в <span class="hl">адресното поле</span> на браузъра</li>
        <li>Свързаните уеб страници, собственост на един автор, образуват <span class="hl">уеб сайт</span></li>
        <li>При последователно отваряне потребителят може да се <span class="hl">придвижва назад и напред</span></li>
      </ul>
      <div class="tip-box">
        <strong>&#128204; ЗАДАЧА 1:</strong> Потърсете кои браузъри са инсталирани на вашия компютър. Отворете един от тях и разгледайте началната страница.
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 9: БРАУЗЪРИ — СРАВНЕНИЕ
parts.append('<div class="slide slide-content">\n  <h2>Chrome, Firefox и Edge &mdash; сравнение</h2>\n  <div class="slide-body" style="flex-direction:column;align-items:center">\n    <div style="width:100%;text-align:center" class="animate-children">\n      ' + img_tag(lec[3], 'Сравнение браузъри') + '\n      <p class="img-caption">Фигура 2: Chrome, Firefox и Edge &mdash; всички отварят едни и същи два раздела (Уикипедия и нов раздел)</p>\n    </div>\n    <div class="tip-box" style="margin-top:16px">\n      <strong>&#128161; Забележете:</strong> Въпреки визуалните разлики в интерфейса, всички браузъри изпълняват едни и същи основни функции.\n    </div>\n  </div>\n</div>\n')

# SLIDE 10: ХИПЕРВРЪЗКИ
hl_img = '<img src="' + hyperlink_img + '" alt="hlink" style="max-width:180px;max-height:120px;border-radius:var(--radius);box-shadow:var(--shadow);object-fit:contain;background:white;padding:8px">' if hyperlink_img else '<div style="font-size:48px;text-align:center">&#128279;</div>'
parts.append('<div class="slide slide-content">\n  <h2>Хипервръзки (Линкове)</h2>\n  <div class="slide-body">\n    <div class="slide-text scrollable animate-children">\n      <ul class="bullets">\n        <li>Интерактивен обект, водещ до <span class="hl">друга уеб страница или раздел</span></li>\n        <li>Може да бъде <span class="hl">текст</span> (обикновено подчертан и оцветен) или <span class="hl">изображение</span></li>\n        <li>При посочване с мишка курсорът се променя на <span class="hl" style="font-size:18px">&#9757;&#65039;</span></li>\n        <li>Чрез тях се осъществява <span class="hl">навигацията</span> (придвижването) между уеб страниците</li>\n        <li>Разговорно &mdash; <span class="hl">&bdquo;линк&ldquo;</span> (от англ. <em>hyperlink</em>)</li>\n      </ul>\n      <div class="tip-box">\n        <strong>&#128204; ЗАДАЧА 2:</strong> Отворете <strong>wikipedia.org</strong> и намерете хипервръзката за български език. Последвайте я, след което се върнете назад с бутона &#8592;\n      </div>\n    </div>\n    <div class="slide-img" style="flex:0 0 200px;flex-direction:column;gap:12px">\n      ' + hl_img + '\n      <div style="font-size:11px;color:var(--text-muted);text-align:center">Курсорите при хипервръзка</div>\n    </div>\n  </div>\n</div>\n')

# SLIDE 11: WIKIPEDIA DEMO
parts.append('<div class="slide slide-content">\n  <h2>Пример: Началната страница на Уикипедия</h2>\n  <div class="slide-body" style="flex-direction:column;align-items:flex-start">\n    <div style="width:100%;text-align:center" class="animate-children">\n      <p style="color:var(--text-muted);margin-bottom:14px;font-size:14px">Интерфейс на браузъра Firefox с отворената началната страница на bg.wikipedia.org</p>\n      ' + img_tag(lec[1], 'Wikipedia Firefox') + '\n      <p class="img-caption">Фигура 3: Адресното поле, разделите, бутоните за навигация, хипервръзките</p>\n    </div>\n  </div>\n</div>\n')

# SLIDE 12: ЗАДАЧА WIKIPEDIA
parts.append("""<div class="slide slide-content">
  <h2>Задача 2 &mdash; Разгледайте Уикипедия</h2>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Копирайте в адресното поле: <span class="hl">https://www.wikipedia.org</span></li>
        <li>Намерете и последвайте хипервръзката за <span class="hl">български език</span> &mdash; ще се отвори bg.wikipedia.org</li>
        <li>Използвайте бутона <span class="hl">&#8592; (назад)</span> и се върнете в предишната страница</li>
        <li>Последвайте връзката <span class="hl">&bdquo;Картинка на деня&ldquo;</span></li>
        <li>Намерете и натиснете върху различни хипервръзки и проследете движението между страниците</li>
      </ul>
      <div class="warn-box">
        <strong>&#9888;&#65039; Забележете:</strong> Използвайте бутоните &#8592; и &#8594; на браузъра &mdash; те са различни от връзките в страницата!
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 13: SECTION ТЪРСЕНЕ
parts.append("""<div class="slide slide-section">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:12px;position:relative">
    <div class="section-number">03</div>
    <h2>Търсене в Интернет</h2>
    <p class="section-desc">Търсачки, техники за ефективно търсене и критична оценка</p>
  </div>
</div>
""")

# SLIDE 14: ТЪРСЕЩА МАШИНА
parts.append("""<div class="slide slide-content">
  <h2>Търсеща машина (търсачка)</h2>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Специализиран <span class="hl">софтуер за търсене</span> на информация в Интернет</li>
        <li>Отваря се в браузъра като уеб страница и има собствен <span class="hl">URL адрес</span></li>
        <li>Има <span class="hl">поле за търсене</span>, в което се въвежда заявка &mdash; ключови думи или фрази</li>
        <li>Адресното поле на браузъра <span class="hl">също служи за търсене</span></li>
        <li>Работи с <span class="hl">&bdquo;паяци&ldquo; (web crawlers)</span> &mdash; програми, обхождащи уеб страниците и индексиращи съдържанието им</li>
      </ul>
    </div>
    <div class="slide-img">
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:24px;width:240px;text-align:center">
        <div style="font-size:44px;margin-bottom:12px">&#128269;</div>
        <div style="background:var(--bg);border:2px solid var(--accent);border-radius:50px;padding:10px 16px;font-size:12px;color:var(--text-muted);margin-bottom:12px;text-align:left">обяви за работа...</div>
        <div style="font-size:11px;color:var(--text-muted);line-height:1.7">Около 8 630 000 резултата<br>(0.42 секунди)</div>
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 15: ПОПУЛЯРНИ ТЪРСАЧКИ
parts.append("""<div class="slide slide-content">
  <h2>Популярни търсещи машини</h2>
  <div class="slide-body" style="flex-direction:column">
    <div style="width:100%" class="animate-children">
      <div class="cards c2">
        <div class="card" style="display:flex;gap:16px;align-items:center">
          <div style="font-size:40px">&#128269;</div>
          <div><h3>Google</h3><p>https://www.google.com/ &mdash; Гугъл<br>Над 90% пазарен дял в световен мащаб</p></div>
        </div>
        <div class="card" style="display:flex;gap:16px;align-items:center">
          <div style="font-size:40px">&#128309;</div>
          <div><h3>Bing</h3><p>https://www.bing.com/ &mdash; Бинг<br>Разработен от Microsoft</p></div>
        </div>
        <div class="card" style="display:flex;gap:16px;align-items:center">
          <div style="font-size:40px">&#128995;</div>
          <div><h3>Yahoo!</h3><p>https://search.yahoo.com/ &mdash; Яху!<br>Един от първите популярни интернет портали</p></div>
        </div>
        <div class="card" style="display:flex;gap:16px;align-items:center">
          <div style="font-size:40px">&#129414;</div>
          <div><h3>DuckDuckGo</h3><p>https://duckduckgo.com/ &mdash; Дъкдъкгоу<br>Акцент върху поверителността на потребителя</p></div>
        </div>
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 16: GOOGLE vs BING (screenshots)
parts.append('<div class="slide slide-content">\n  <h2>Google и Bing &mdash; Задача 3</h2>\n  <div class="slide-body" style="gap:16px">\n    <div style="flex:1;text-align:center" class="animate-children">\n      ' + img_tag(lec[8], 'Google', style='max-width:100%;max-height:38vh;border-radius:var(--radius);box-shadow:var(--shadow);object-fit:contain') + '\n      <p class="img-caption" style="margin-top:6px">Google &mdash; https://www.google.com</p>\n    </div>\n    <div style="flex:1;text-align:center" class="animate-children">\n      ' + img_tag(lec[5], 'Bing', style='max-width:100%;max-height:38vh;border-radius:var(--radius);box-shadow:var(--shadow);object-fit:contain') + '\n      <p class="img-caption" style="margin-top:6px">Bing &mdash; https://www.bing.com</p>\n    </div>\n  </div>\n  <div class="tip-box" style="width:100%;margin-top:14px">\n    <strong>&#128204; Задача 3:</strong> Отворете двете търсачки в два нови раздела. Намерете приликите и разликите в дизайна им.\n  </div>\n</div>\n')

# SLIDE 17: НАЧИНИ ЗА ТЪРСЕНЕ
parts.append("""<div class="slide slide-content">
  <h2>Начини за ефективно търсене</h2>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Изберете <span class="hl">ключови думи</span>, вероятно употребявани в търсения сайт</li>
        <li>Започнете с <span class="hl">обща заявка</span> (1 дума), после добавяйте пояснения:
          <ul class="bullets" style="margin-top:8px">
            <li class="sub"><em>обяви</em> &rarr; <em>обяви за работа</em> &rarr; <em>обяви за работа Пловдив</em></li>
          </ul>
        </li>
        <li>Заявката <span class="hl">не различава главни от малки</span> букви:
          <ul class="bullets" style="margin-top:8px">
            <li class="sub"><em>обяви за работа плевен</em> = <em>Обяви за Работа Плевен</em></li>
          </ul>
        </li>
        <li>Търсачката <span class="hl">автоматично коригира</span> грешки:
          <ul class="bullets" style="margin-top:8px">
            <li class="sub"><em>убяви за рабута</em> &rarr; <em>обяви за работа</em></li>
          </ul>
        </li>
        <li>При търсене на продукт в <span class="hl">регион</span> &mdash; добавете населеното място</li>
      </ul>
    </div>
  </div>
</div>
""")

# SLIDE 18: ДЕМОНСТРАЦИЯ GOOGLE
parts.append('<div class="slide slide-content">\n  <h2>Демонстрация &mdash; търсене с Google</h2>\n  <div class="slide-body" style="flex-direction:column;align-items:center">\n    <div style="width:100%;max-width:700px;text-align:center" class="animate-children">\n      ' + img_tag(google_demo, 'Google demo') + '\n      <p class="img-caption">Стъпки: 1) Отваря се google.com в браузъра &rarr; 2) В полето за търсене се изписва заявката &rarr; 3) Натиска се Enter или бутонът за търсене</p>\n    </div>\n  </div>\n</div>\n')

# SLIDE 19: РЕЗУЛТАТИ (mock)
parts.append("""<div class="slide slide-content">
  <h2>Резултати от търсенето</h2>
  <div class="slide-body">
    <div class="slide-text animate-children">
      <ul class="bullets">
        <li>Показва се <span class="hl">списък от имена на страници</span> и хипервръзки към тях</li>
        <li>Страниците, <span class="hl">най-точно отговарящи</span> на заявката, са класирани напред</li>
        <li>Показва се <span class="hl">общ брой резултати</span> и времето за търсене</li>
        <li>Резултатите се отварят <span class="hl">в същия раздел</span> при клик с ляв бутон</li>
        <li>Адресното поле на браузъра <span class="hl">работи и като търсачка</span></li>
      </ul>
      <div class="tip-box" style="margin-top:16px">
        <strong>&#128204; ЗАДАЧА 4:</strong> Потърсете &bdquo;обяви за работа&ldquo; в Google. Наблюдавайте броя резултати. После добавете вашия град и сравнете.
      </div>
    </div>
    <div class="slide-img" style="flex:0 0 280px">
      <div style="width:280px">
        <div class="result-item ad">
          <div class="r-url">https://rabota.bg</div>
          <div class="r-title">Обяви за работа &mdash; Работа.bg</div>
          <div class="r-desc">Намери своята следваща работа сред хиляди обяви...</div>
        </div>
        <div class="result-item">
          <div class="r-url">https://jobs.bg &rsaquo; обяви</div>
          <div class="r-title">Jobs.bg &mdash; Обяви за работа</div>
          <div class="r-desc">Разгледайте над 10,000 актуални обяви за работа...</div>
        </div>
        <div class="result-item">
          <div class="r-url">https://zaplata.bg</div>
          <div class="r-title">Zaplata.bg &mdash; Търсене на работа</div>
          <div class="r-desc">Намерете подходяща работа с добро заплащане...</div>
        </div>
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 20: РЕАЛНИ РЕЗУЛТАТИ
parts.append('<div class="slide slide-content">\n  <h2>Реални резултати от търсенето</h2>\n  <div class="slide-body" style="flex-direction:column;align-items:center">\n    <div style="width:100%;text-align:center" class="animate-children">\n      ' + img_tag(lec[2], 'Google results') + '\n      <p class="img-caption">Фигура 5: Страница с резултати от заявката &bdquo;обяви за работа&ldquo; в Google. Обърнете внимание на броя резултати и URL адресите.</p>\n    </div>\n  </div>\n</div>\n')

# SLIDE 20 index, SECTION БЕЗОПАСНОСТ (this is slide index 20)
parts.append("""<div class="slide slide-section">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:12px;position:relative">
    <div class="section-number">04</div>
    <h2>Критично търсене и безопасност</h2>
    <p class="section-desc">Как да разпознаем надеждни резултати и да пазим личните си данни</p>
  </div>
</div>
""")

# SLIDE 21: КРИТИЧЕН ПОДБОР
parts.append("""<div class="slide slide-content">
  <h2>Критичен подбор на резултати</h2>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <div class="warn-box" style="margin-bottom:16px">
        <strong>&#9888;&#65039; Внимание!</strong> Не всички резултати от търсенето са достоверни и полезни!
      </div>
      <ul class="bullets">
        <li>Първите резултати могат да са <span class="hl" style="color:var(--yellow)">реклами</span> &mdash; маркирани с &bdquo;Реклама&ldquo; или &bdquo;Ad&ldquo;; не са непременно неверни, но са платени</li>
        <li>Некачествени сайтове: <span class="hl" style="color:var(--yellow)">граматически лош текст</span> &mdash; признак за машинен превод</li>
        <li>Адреси от вида <span class="hl" style="color:var(--yellow)">bg.website.com</span> не са официални български сайтове</li>
        <li>Адресът в търсачката <span class="hl" style="color:var(--yellow)">не съвпада</span> с реалния адрес след отваряне на страницата</li>
        <li>При съмнение &mdash; <span class="hl">проверявайте</span> в друг надежден независим источник</li>
      </ul>
    </div>
  </div>
</div>
""")

# SLIDE 22: SAFETY RULES
parts.append("""<div class="slide slide-content">
  <h2>Правила за безопасност в Интернет</h2>
  <div class="slide-body" style="flex-direction:column">
    <div style="width:100%" class="animate-children">
      <div class="safety-grid">
        <div class="safety-item"><div class="safety-icon">&#128274;</div><div class="safety-text"><strong>Пазете личните си данни</strong>Не предоставяйте имена, пароли, ЕГН, телефон или банкови данни.</div></div>
        <div class="safety-item"><div class="safety-icon">&#128247;</div><div class="safety-text"><strong>Внимавайте с личните снимки</strong>Не публикувайте публично лични снимки на вас и близките ви.</div></div>
        <div class="safety-item"><div class="safety-icon">&#129309;</div><div class="safety-text"><strong>Избягвайте лични срещи</strong>Хора в Интернет могат да предоставят невярна информация за себе си.</div></div>
        <div class="safety-item"><div class="safety-icon">&#128172;</div><div class="safety-text"><strong>Не изпращайте обидни съобщения</strong>Не отговаряйте на провокации. Не изпращайте анонимни или верижни съобщения.</div></div>
        <div class="safety-item"><div class="safety-icon">&#128206;</div><div class="safety-text"><strong>Внимавайте с файлове и връзки</strong>Не отваряйте файлове и връзки от непознати &mdash; могат да съдържат вируси.</div></div>
        <div class="safety-item"><div class="safety-icon">&#128737;&#65039;</div><div class="safety-text"><strong>Проверявайте информацията</strong>Не всичко в Интернет е достоверно. Търсете потвърждение от надеждни източници.</div></div>
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 23: ОБОБЩЕНИЕ
parts.append("""<div class="slide slide-content">
  <h2>Обобщение на темата</h2>
  <div class="slide-body" style="flex-direction:column">
    <div style="width:100%" class="animate-children">
      <div class="cards c2">
        <div class="card"><div class="ci">&#127760;</div><h3>Интернет</h3><p>Най-голямата мрежа от мрежи. Свързва милиарди потребители. Предоставя достъп до несметна информация.</p></div>
        <div class="card"><div class="ci">&#128187;</div><h3>Браузър</h3><p>Програмата за влизане в Интернет. Chrome, Firefox, Edge, Opera, Safari са браузъри.</p></div>
        <div class="card"><div class="ci">&#128269;</div><h3>Търсачка</h3><p>Уеб страница за търсене на информация. Google, Bing, DuckDuckGo са търсащи машини.</p></div>
        <div class="card"><div class="ci">&#128737;&#65039;</div><h3>Безопасност</h3><p>Критичен подбор на информация. Пазете личните данни. Проверявайте sources.</p></div>
      </div>
      <div class="tip-box" style="margin-top:16px">
        <strong>Готови ли сте за теста?</strong> Проверете дали сте усвоили материала с 3 въпроса.
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 24: QUIZ INTRO
parts.append("""<div class="slide slide-section">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:16px;position:relative">
    <div style="font-size:64px">&#9989;</div>
    <h2 style="font-size:clamp(24px,3.5vw,40px);font-weight:800;text-align:center;background:linear-gradient(135deg,#fff,var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent">Тест за самооценка</h2>
    <p class="section-desc">3 въпроса &middot; Незабавна обратна връзка &middot; Вижте колко сте усвоили</p>
    <button class="quiz-btn primary" onclick="goToSlide(26)" style="margin-top:8px">Започнете теста &rarr;</button>
  </div>
</div>
""")

# SLIDE 25: QUIZ
parts.append("""<div class="slide slide-quiz">
  <div class="quiz-container">
    <div class="quiz-progress">
      <div class="quiz-step current" id="qstep-0"></div>
      <div class="quiz-step" id="qstep-1"></div>
      <div class="quiz-step" id="qstep-2"></div>
    </div>
    <div id="qblock-0" class="question-card">
      <div class="q-number">Въпрос 1 от 3</div>
      <div class="q-text">Какво е Интернет?</div>
      <div class="options" id="opts-0">
        <div class="option" onclick="selectOption(0,0)"><div class="option-letter">А</div><div>Локална мрежа за свързване на два компютъра</div></div>
        <div class="option" onclick="selectOption(0,1)"><div class="option-letter">Б</div><div>Специализирана програма за търсене на информация</div></div>
        <div class="option" onclick="selectOption(0,2)"><div class="option-letter">В</div><div>Глобална мрежа, която свързва други мрежи и техните потребители</div></div>
        <div class="option" onclick="selectOption(0,3)"><div class="option-letter">Г</div><div>Нито едно от изброените</div></div>
      </div>
      <div class="q-feedback" id="qfb-0"></div>
      <div style="margin-top:16px">
        <button class="quiz-btn primary" id="qbtn-check-0" onclick="checkAnswer(0,2,false)" disabled>Провери отговора</button>
      </div>
    </div>
    <div id="qblock-1" class="question-card" style="display:none">
      <div class="q-number">Въпрос 2 от 3</div>
      <div class="q-text">Посочете <u>верните</u> описания (изберете всички верни):</div>
      <div class="q-multi-label">Може да изберете повече от един отговор</div>
      <div class="options" id="opts-1">
        <div class="option" onclick="toggleMultiOption(1,0)"><div class="option-letter">А</div><div><strong>Google</strong> &mdash; търсеща машина</div></div>
        <div class="option" onclick="toggleMultiOption(1,1)"><div class="option-letter">Б</div><div><strong>Firefox</strong> &mdash; интернет браузър</div></div>
        <div class="option" onclick="toggleMultiOption(1,2)"><div class="option-letter">В</div><div><strong>Chrome</strong> &mdash; търсеща машина</div></div>
        <div class="option" onclick="toggleMultiOption(1,3)"><div class="option-letter">Г</div><div><strong>Bing</strong> &mdash; търсеща машина</div></div>
      </div>
      <div class="q-feedback" id="qfb-1"></div>
      <div style="margin-top:16px">
        <button class="quiz-btn primary" id="qbtn-check-1" onclick="checkMultiAnswer(1,[0,1,3])" disabled>Провери отговора</button>
      </div>
    </div>
    <div id="qblock-2" class="question-card" style="display:none">
      <div class="q-number">Въпрос 3 от 3</div>
      <div class="q-text">Кое от следните твърдения за търсене в Интернет е <u>невярно</u>?</div>
      <div class="options" id="opts-2">
        <div class="option" onclick="selectOption(2,0)"><div class="option-letter">А</div><div>Информацията, която намираме в Интернет, не винаги е достоверна</div></div>
        <div class="option" onclick="selectOption(2,1)"><div class="option-letter">Б</div><div>В Интернет можем да търсим само на английски език</div></div>
        <div class="option" onclick="selectOption(2,2)"><div class="option-letter">В</div><div>За да намерим информация в Интернет, трябва да използваме търсеща машина</div></div>
        <div class="option" onclick="selectOption(2,3)"><div class="option-letter">Г</div><div>Търсещата машина работи с ключови думи</div></div>
      </div>
      <div class="q-feedback" id="qfb-2"></div>
      <div style="margin-top:16px">
        <button class="quiz-btn primary" id="qbtn-check-2" onclick="checkAnswer(2,1,true)" disabled>Провери отговора</button>
      </div>
    </div>
    <div class="score-screen" id="score-screen">
      <div class="score-circle">
        <div class="score-num" id="score-num">0</div>
        <div class="score-total">/ 3</div>
      </div>
      <div class="score-msg" id="score-msg"></div>
      <div class="score-detail" id="score-detail"></div>
      <div style="display:flex;gap:12px;margin-top:8px;flex-wrap:wrap;justify-content:center">
        <button class="quiz-btn secondary" onclick="resetQuiz()">&#8635; Опитай отново</button>
        <button class="quiz-btn primary" onclick="goToSlide(27)">Финал &rarr;</button>
      </div>
    </div>
  </div>
</div>
""")

# SLIDE 26: THANK YOU
parts.append("""<div class="slide slide-section" style="background:radial-gradient(ellipse at 50% 50%, #312e81 0%, var(--bg) 65%)">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:0">
    <div style="font-size:72px;margin-bottom:16px">&#127891;</div>
    <h2 style="font-size:clamp(28px,4vw,52px);margin-bottom:8px">Благодаря за вниманието!</h2>
    <p style="color:var(--text-muted);font-size:16px;text-align:center;margin-bottom:32px">Тема 1.1 &mdash; Сърфиране, търсене и филтриране на данни</p>
    <div class="digcomp-badge">Европейска Рамка на дигиталните компетентности &middot; DigComp 2.1 &middot; Нива 1&ndash;2</div>
    <div style="margin-top:40px;display:grid;grid-template-columns:repeat(3,1fr);gap:16px;max-width:600px">
      <div class="card" style="text-align:center"><div style="font-size:28px;margin-bottom:6px">&#128218;</div><div style="font-size:13px;font-weight:700;color:var(--accent2)">Материалът</div><div style="font-size:12px;color:var(--text-muted);margin-top:4px">завършен</div></div>
      <div class="card" style="text-align:center"><div style="font-size:28px;margin-bottom:6px">&#128269;</div><div style="font-size:13px;font-weight:700;color:var(--accent2)">Практиката</div><div style="font-size:12px;color:var(--text-muted);margin-top:4px">4 задачи</div></div>
      <div class="card" style="text-align:center"><div style="font-size:28px;margin-bottom:6px">&#9989;</div><div style="font-size:13px;font-weight:700;color:var(--accent2)">Тестът</div><div style="font-size:12px;color:var(--text-muted);margin-top:4px">попълнен</div></div>
    </div>
    <p style="margin-top:32px;font-size:12px;color:var(--text-muted);max-width:600px;text-align:center;line-height:1.7">
      <strong>Използвана литература:</strong> Wikipedia.org &middot; Николова &amp; Стефанова, ИКТ 5. клас, Просвета &middot; Тужаров, Х. Учебник по Информатика
    </p>
  </div>
</div>
""")

parts.append("""</div><!-- /#slides-wrapper -->
<div id="nav">
  <div id="nav-dots"></div>
  <div id="slide-counter">1 / ?</div>
</div>
<script>
""" + JS + """
</script>
</body>
</html>""")

html = "\n".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = OUT.stat().st_size / 1024
print("Done! " + str(OUT))
print("Size: " + str(round(size_kb)) + " KB (" + str(round(size_kb/1024, 2)) + " MB)")
