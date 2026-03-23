"""Generate a modern single-file HTML presentation from extracted content."""
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
            "gif": "image/gif", "wmf": "image/x-wmf"}.get(ext, "image/png")
    return f"data:{mime};base64,{data}"

# Load data
with open(BASE / "main_pptx.json", encoding="utf-8") as f:
    main_slides = json.load(f)
with open(BASE / "lecture_docx.json", encoding="utf-8") as f:
    lecture = json.load(f)
with open(BASE / "tests_docx.json", encoding="utf-8") as f:
    tests = json.load(f)

# Preload all images
browser_logos = [img_b64(f"main_slide4_img{i}.png") for i in range(5)]
hyperlink_img = img_b64("main_slide8_img5.png")
safety_img = img_b64("main_slide18_img7.jpg")
google_demo_img = img_b64("demo_slide2_img0.png")
lecture_imgs = [img_b64(f"lecture_doc_img{i}.png") for i in range(14)]

# ---- HTML Template ----
html = f"""<!DOCTYPE html>
<html lang="bg">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Тема 1.1 — Сърфиране, търсене и филтриране на данни</title>
<style>
/* ===== RESET & BASE ===== */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg: #0f172a;
  --surface: #1e293b;
  --surface2: #263147;
  --accent: #6366f1;
  --accent2: #818cf8;
  --accent3: #38bdf8;
  --green: #22c55e;
  --red: #ef4444;
  --yellow: #f59e0b;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --border: #334155;
  --radius: 16px;
  --radius-sm: 8px;
  --shadow: 0 25px 50px rgba(0,0,0,0.5);
}}
html, body {{ height: 100%; overflow: hidden; font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); }}

/* ===== PROGRESS BAR ===== */
#progress-bar {{
  position: fixed; top: 0; left: 0; height: 3px;
  background: linear-gradient(90deg, var(--accent), var(--accent3));
  transition: width 0.5s ease; z-index: 1000;
  box-shadow: 0 0 10px var(--accent);
}}

/* ===== NAV ===== */
#nav {{
  position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
  display: flex; align-items: center; gap: 8px; z-index: 100;
  background: rgba(30,41,59,0.85); backdrop-filter: blur(12px);
  padding: 10px 20px; border-radius: 50px; border: 1px solid var(--border);
}}
.nav-dot {{
  width: 8px; height: 8px; border-radius: 50%; background: var(--border);
  cursor: pointer; transition: all 0.3s ease;
}}
.nav-dot.active {{ background: var(--accent); transform: scale(1.4); box-shadow: 0 0 8px var(--accent); }}
.nav-dot:hover:not(.active) {{ background: var(--accent2); }}
#slide-counter {{
  font-size: 12px; color: var(--text-muted); margin: 0 8px;
  font-variant-numeric: tabular-nums; white-space: nowrap;
}}

/* ===== NAV BUTTONS ===== */
.nav-btn {{
  position: fixed; top: 50%; transform: translateY(-50%);
  width: 48px; height: 48px; border-radius: 50%;
  border: 1px solid var(--border); background: rgba(30,41,59,0.8);
  backdrop-filter: blur(8px); cursor: pointer; color: var(--text);
  font-size: 20px; display: flex; align-items: center; justify-content: center;
  transition: all 0.3s; z-index: 100;
}}
.nav-btn:hover {{ background: var(--accent); border-color: var(--accent); box-shadow: 0 0 20px var(--accent)40; }}
.nav-btn:disabled {{ opacity: 0.2; cursor: not-allowed; }}
#btn-prev {{ left: 16px; }}
#btn-next {{ right: 16px; }}

/* ===== SECTION MENU ===== */
#section-menu {{
  position: fixed; top: 16px; right: 16px; z-index: 200;
  display: flex; gap: 8px; align-items: center;
}}
.section-pill {{
  padding: 5px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;
  border: 1px solid var(--border); background: rgba(30,41,59,0.8);
  backdrop-filter: blur(8px); cursor: pointer; transition: all 0.3s;
  color: var(--text-muted);
}}
.section-pill:hover, .section-pill.active {{
  background: var(--accent); border-color: var(--accent); color: #fff;
  box-shadow: 0 0 16px var(--accent)60;
}}

/* ===== SLIDE CONTAINER ===== */
#slides-wrapper {{
  width: 100%; height: 100%; position: relative; overflow: hidden;
}}
.slide {{
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px 80px 90px;
  opacity: 0; pointer-events: none;
  transform: translateX(60px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}}
.slide.active {{
  opacity: 1; pointer-events: all; transform: translateX(0);
}}
.slide.prev {{
  opacity: 0; transform: translateX(-60px);
}}

/* ===== SLIDE TYPES ===== */
/* TITLE SLIDE */
.slide-title {{
  background: radial-gradient(ellipse at 60% 40%, #312e81 0%, var(--bg) 70%);
}}
.slide-title .kicker {{
  font-size: 13px; font-weight: 600; letter-spacing: 3px; text-transform: uppercase;
  color: var(--accent2); margin-bottom: 20px;
}}
.slide-title h1 {{
  font-size: clamp(24px, 3.5vw, 42px); font-weight: 800; text-align: center;
  line-height: 1.25; max-width: 800px;
  background: linear-gradient(135deg, #fff 30%, var(--accent2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.slide-title .subtitle {{
  margin-top: 24px; color: var(--text-muted); font-size: 15px; text-align: center;
}}
.digcomp-badge {{
  margin-top: 40px; padding: 10px 24px; border-radius: 50px;
  border: 1px solid var(--accent)60; background: var(--accent)10;
  font-size: 12px; color: var(--accent2); text-align: center;
}}

/* SECTION DIVIDER */
.slide-section {{
  background: radial-gradient(ellipse at 50% 50%, #1e1b4b 0%, var(--bg) 65%);
}}
.section-number {{
  font-size: 80px; font-weight: 900; line-height: 1;
  background: linear-gradient(135deg, var(--accent), var(--accent3));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  opacity: 0.15; position: absolute;
}}
.slide-section h2 {{
  font-size: clamp(28px, 4vw, 52px); font-weight: 800; text-align: center;
  background: linear-gradient(135deg, #fff, var(--accent2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  position: relative;
}}
.slide-section .section-desc {{
  color: var(--text-muted); font-size: 16px; text-align: center;
  margin-top: 12px; max-width: 500px; position: relative;
}}

/* CONTENT SLIDE */
.slide-content {{ align-items: flex-start; justify-content: flex-start; padding-top: 80px; }}
.slide-content .slide-header {{ margin-bottom: 32px; width: 100%; }}
.slide-content h2 {{
  font-size: clamp(20px, 2.5vw, 32px); font-weight: 800;
  background: linear-gradient(135deg, #fff 60%, var(--accent2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  padding-bottom: 12px;
  border-bottom: 2px solid; border-image: linear-gradient(90deg, var(--accent), transparent) 1;
}}
.slide-body {{ width: 100%; flex: 1; display: flex; gap: 32px; }}
.slide-text {{ flex: 1; min-width: 0; }}
.slide-img {{ flex: 0 0 auto; display: flex; align-items: center; justify-content: center; }}
.slide-img img {{ max-width: 360px; max-height: 320px; border-radius: var(--radius); box-shadow: var(--shadow); object-fit: contain; }}

/* BULLET LIST */
ul.bullets {{ list-style: none; display: flex; flex-direction: column; gap: 12px; }}
ul.bullets li {{
  display: flex; align-items: flex-start; gap: 12px;
  font-size: clamp(14px, 1.4vw, 17px); line-height: 1.6; color: var(--text);
}}
ul.bullets li::before {{
  content: ''; flex-shrink: 0; width: 8px; height: 8px; border-radius: 50%;
  background: var(--accent); margin-top: 8px;
  box-shadow: 0 0 8px var(--accent);
}}
ul.bullets li.sub::before {{ background: var(--accent3); width: 6px; height: 6px; margin-left: 12px; }}
.highlight {{ color: var(--accent2); font-weight: 600; }}

/* CARDS GRID */
.cards {{ display: grid; gap: 16px; width: 100%; }}
.cards.cols-2 {{ grid-template-columns: repeat(2, 1fr); }}
.cards.cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
.card {{
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 20px; transition: all 0.3s;
}}
.card:hover {{ border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 8px 24px var(--accent)20; }}
.card .card-icon {{ font-size: 32px; margin-bottom: 10px; }}
.card h3 {{ font-size: 16px; font-weight: 700; margin-bottom: 8px; color: var(--accent2); }}
.card p {{ font-size: 14px; color: var(--text-muted); line-height: 1.6; }}

/* BROWSER LOGOS */
.browser-grid {{ display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }}
.browser-card {{
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 20px 28px; transition: all 0.3s; cursor: default;
}}
.browser-card:hover {{ border-color: var(--accent); transform: translateY(-4px); box-shadow: 0 12px 30px var(--accent)20; }}
.browser-card img {{ width: 52px; height: 52px; object-fit: contain; }}
.browser-card span {{ font-size: 13px; color: var(--text-muted); font-weight: 600; }}

/* TIP BOX */
.tip-box {{
  background: linear-gradient(135deg, var(--accent)15, var(--accent3)10);
  border: 1px solid var(--accent)40; border-radius: var(--radius); padding: 16px 20px;
  margin-top: 16px; font-size: 14px; color: var(--text-muted); line-height: 1.6;
}}
.tip-box strong {{ color: var(--accent2); }}
.warning-box {{
  background: linear-gradient(135deg, #f59e0b15, #ef444410);
  border: 1px solid #f59e0b40; border-radius: var(--radius); padding: 16px 20px;
  margin-top: 16px; font-size: 14px; color: var(--text-muted); line-height: 1.6;
}}
.warning-box strong {{ color: #f59e0b; }}

/* SEARCH DEMO ELEMENTS */
.search-bar-demo {{
  background: var(--surface2); border: 2px solid var(--accent); border-radius: 50px;
  padding: 12px 24px; font-size: 16px; color: var(--text); width: 100%;
  max-width: 560px; margin-bottom: 16px; display: flex; align-items: center; gap: 12px;
}}
.search-bar-demo .icon {{ color: var(--text-muted); font-size: 18px; }}
.search-results-demo {{ width: 100%; max-width: 560px; }}
.result-item {{
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm);
  padding: 14px 16px; margin-bottom: 10px; transition: border-color 0.2s;
}}
.result-item:hover {{ border-color: var(--accent); }}
.result-item .r-url {{ font-size: 12px; color: var(--green); margin-bottom: 4px; }}
.result-item .r-title {{ font-size: 15px; font-weight: 600; color: var(--accent2); margin-bottom: 4px; }}
.result-item .r-desc {{ font-size: 13px; color: var(--text-muted); line-height: 1.5; }}
.result-item.ad {{ border-color: #f59e0b40; }}
.result-item.ad .r-url::before {{ content: 'Реклама · '; color: #f59e0b; font-weight: 600; }}

/* TABLE */
.comparison-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
.comparison-table th {{
  background: var(--accent)20; color: var(--accent2); font-weight: 700;
  padding: 12px 16px; text-align: left; border-bottom: 2px solid var(--accent)40;
}}
.comparison-table td {{
  padding: 11px 16px; border-bottom: 1px solid var(--border); color: var(--text);
  line-height: 1.5;
}}
.comparison-table tr:hover td {{ background: var(--surface2); }}
.badge {{
  display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 700;
}}
.badge.browser {{ background: var(--accent)20; color: var(--accent2); border: 1px solid var(--accent)40; }}
.badge.engine {{ background: var(--green)20; color: var(--green); border: 1px solid var(--green)40; }}

/* IMAGE SLIDE */
.img-caption {{
  margin-top: 12px; font-size: 13px; color: var(--text-muted); text-align: center; font-style: italic;
}}
.full-img {{ max-width: 100%; max-height: 55vh; border-radius: var(--radius); box-shadow: var(--shadow); object-fit: contain; }}

/* SAFETY RULES */
.safety-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; width: 100%; }}
.safety-item {{
  display: flex; gap: 12px; align-items: flex-start;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm);
  padding: 14px;
}}
.safety-icon {{ font-size: 24px; flex-shrink: 0; margin-top: 2px; }}
.safety-text {{ font-size: 13px; color: var(--text-muted); line-height: 1.5; }}
.safety-text strong {{ color: var(--text); display: block; margin-bottom: 2px; font-size: 14px; }}

/* ===== QUIZ ===== */
.slide-quiz {{ background: radial-gradient(ellipse at 30% 70%, #1e1b4b 0%, var(--bg) 60%); }}
.quiz-container {{ width: 100%; max-width: 780px; }}
.quiz-progress {{
  display: flex; gap: 6px; margin-bottom: 32px;
}}
.quiz-step {{
  height: 4px; flex: 1; border-radius: 2px; background: var(--border); transition: background 0.4s;
}}
.quiz-step.done {{ background: var(--green); }}
.quiz-step.current {{ background: var(--accent); }}
.question-card {{
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 28px 32px; margin-bottom: 20px;
}}
.q-number {{ font-size: 12px; font-weight: 700; color: var(--accent2); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }}
.q-text {{ font-size: clamp(16px, 2vw, 20px); font-weight: 600; line-height: 1.5; margin-bottom: 24px; }}
.options {{ display: flex; flex-direction: column; gap: 10px; }}
.option {{
  display: flex; align-items: center; gap: 14px;
  background: var(--surface2); border: 2px solid var(--border);
  border-radius: var(--radius-sm); padding: 14px 18px; cursor: pointer;
  transition: all 0.25s; font-size: 15px;
}}
.option:hover:not(.disabled) {{ border-color: var(--accent); background: var(--accent)10; }}
.option.selected {{ border-color: var(--accent); background: var(--accent)15; }}
.option.correct {{ border-color: var(--green) !important; background: var(--green)15 !important; color: var(--green); }}
.option.wrong {{ border-color: var(--red) !important; background: var(--red)10 !important; color: var(--red)cc; }}
.option.disabled {{ cursor: not-allowed; }}
.option-letter {{
  width: 28px; height: 28px; border-radius: 6px; flex-shrink: 0;
  background: var(--border); display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 13px; transition: all 0.25s;
}}
.option.selected .option-letter {{ background: var(--accent); color: #fff; }}
.option.correct .option-letter {{ background: var(--green); color: #fff; }}
.option.wrong .option-letter {{ background: var(--red); color: #fff; }}
.q-feedback {{
  margin-top: 16px; padding: 14px 18px; border-radius: var(--radius-sm);
  font-size: 14px; line-height: 1.6; display: none;
}}
.q-feedback.show {{ display: block; }}
.q-feedback.correct {{ background: var(--green)15; border: 1px solid var(--green)40; color: var(--green); }}
.q-feedback.wrong {{ background: var(--red)10; border: 1px solid var(--red)30; color: #fca5a5; }}

/* Multi-answer quiz */
.q-multi-label {{ font-size: 12px; color: var(--text-muted); margin-bottom: 14px; font-style: italic; }}
.option.multi-correct-marked {{ border-color: var(--green) !important; background: var(--green)15 !important; }}
.option.multi-wrong-marked {{ border-color: var(--red) !important; background: var(--red)10 !important; }}

.quiz-btn {{
  padding: 12px 32px; border-radius: 50px; border: none; cursor: pointer;
  font-size: 15px; font-weight: 700; transition: all 0.3s; margin-top: 8px;
}}
.quiz-btn.primary {{
  background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #fff;
  box-shadow: 0 4px 20px var(--accent)40;
}}
.quiz-btn.primary:hover {{ transform: translateY(-2px); box-shadow: 0 8px 28px var(--accent)60; }}
.quiz-btn.primary:disabled {{ opacity: 0.4; cursor: not-allowed; transform: none; }}
.quiz-btn.secondary {{
  background: var(--surface2); color: var(--text); border: 1px solid var(--border);
}}
.quiz-btn.secondary:hover {{ border-color: var(--accent); color: var(--accent2); }}

/* SCORE SCREEN */
.score-screen {{
  text-align: center; display: none; flex-direction: column; align-items: center; gap: 20px;
}}
.score-screen.show {{ display: flex; }}
.score-circle {{
  width: 120px; height: 120px; border-radius: 50%;
  border: 4px solid var(--accent); display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: radial-gradient(var(--accent)20, transparent);
  box-shadow: 0 0 40px var(--accent)30;
}}
.score-num {{ font-size: 42px; font-weight: 900; color: var(--accent2); }}
.score-total {{ font-size: 14px; color: var(--text-muted); }}
.score-msg {{ font-size: 20px; font-weight: 700; }}
.score-detail {{ font-size: 14px; color: var(--text-muted); max-width: 460px; text-align: center; line-height: 1.7; }}

/* THANK YOU */
.slide-thanks {{ background: radial-gradient(ellipse at 50% 50%, #312e81 0%, var(--bg) 65%); }}

/* ===== ANIMATIONS ===== */
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(20px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.animate-children > * {{
  opacity: 0; animation: fadeUp 0.5s ease forwards;
}}
.animate-children > *:nth-child(1) {{ animation-delay: 0.1s; }}
.animate-children > *:nth-child(2) {{ animation-delay: 0.2s; }}
.animate-children > *:nth-child(3) {{ animation-delay: 0.3s; }}
.animate-children > *:nth-child(4) {{ animation-delay: 0.4s; }}
.animate-children > *:nth-child(5) {{ animation-delay: 0.5s; }}
.animate-children > *:nth-child(6) {{ animation-delay: 0.6s; }}
.animate-children > *:nth-child(7) {{ animation-delay: 0.7s; }}
.animate-children > *:nth-child(8) {{ animation-delay: 0.8s; }}

/* ===== SCROLLABLE CONTENT ===== */
.scrollable {{
  overflow-y: auto; max-height: calc(100vh - 200px);
  scrollbar-width: thin; scrollbar-color: var(--border) transparent;
}}
.scrollable::-webkit-scrollbar {{ width: 4px; }}
.scrollable::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}

/* ===== KEYBOARD HINT ===== */
#keyboard-hint {{
  position: fixed; bottom: 76px; right: 20px; font-size: 11px; color: var(--text-muted);
  display: flex; gap: 6px; align-items: center; opacity: 0.5;
}}
kbd {{
  padding: 2px 5px; border: 1px solid var(--border); border-radius: 4px;
  background: var(--surface); font-size: 11px;
}}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {{
  .slide {{ padding: 50px 24px 90px; }}
  .slide-body {{ flex-direction: column; }}
  .slide-img img {{ max-width: 100%; }}
  .cards.cols-2, .cards.cols-3, .safety-grid {{ grid-template-columns: 1fr; }}
  .browser-grid {{ gap: 12px; }}
  .browser-card {{ padding: 14px 18px; }}
  #section-menu {{ display: none; }}
  .nav-btn {{ width: 38px; height: 38px; font-size: 16px; }}
}}
</style>
</head>
<body>

<!-- Progress bar -->
<div id="progress-bar" style="width:0%"></div>

<!-- Navigation arrows -->
<button class="nav-btn" id="btn-prev" onclick="changeSlide(-1)">&#8592;</button>
<button class="nav-btn" id="btn-next" onclick="changeSlide(1)">&#8594;</button>

<!-- Section pills -->
<div id="section-menu">
  <div class="section-pill" onclick="goToSlide(0)">Начало</div>
  <div class="section-pill" onclick="goToSlide(3)">Интернет</div>
  <div class="section-pill" onclick="goToSlide(8)">Браузър</div>
  <div class="section-pill" onclick="goToSlide(14)">Търсене</div>
  <div class="section-pill" onclick="goToSlide(21)">Безопасност</div>
  <div class="section-pill" onclick="goToSlide(23)">Тест</div>
</div>

<!-- Keyboard hint -->
<div id="keyboard-hint"><kbd>←</kbd><kbd>→</kbd> или <kbd>Space</kbd></div>

<!-- Slides wrapper -->
<div id="slides-wrapper">

<!-- ═══════════════════════════════════════════════════
     SLIDE 0: TITLE
═══════════════════════════════════════════════════ -->
<div class="slide slide-title active" id="slide-0">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:0">
    <div class="kicker">Тема 1.1</div>
    <h1>Сърфиране, търсене и филтриране на данни, информация и дигитално съдържание</h1>
    <p class="subtitle">Мултимедийна презентация-урок</p>
    <div class="digcomp-badge">
      📋 Европейска Рамка на дигиталните компетентности (DigComp 2.1) · Нива 1–2
    </div>
    <div style="margin-top:50px;display:flex;gap:16px;flex-wrap:wrap;justify-content:center">
      <div class="card" style="width:auto;padding:14px 22px;display:flex;gap:10px;align-items:center">
        <span style="font-size:22px">🌐</span>
        <div>
          <div style="font-size:13px;font-weight:700;color:var(--accent2)">4 раздела</div>
          <div style="font-size:12px;color:var(--text-muted)">теоретичен материал</div>
        </div>
      </div>
      <div class="card" style="width:auto;padding:14px 22px;display:flex;gap:10px;align-items:center">
        <span style="font-size:22px">🔍</span>
        <div>
          <div style="font-size:13px;font-weight:700;color:var(--accent2)">Практически задачи</div>
          <div style="font-size:12px;color:var(--text-muted)">интерактивни примери</div>
        </div>
      </div>
      <div class="card" style="width:auto;padding:14px 22px;display:flex;gap:10px;align-items:center">
        <span style="font-size:22px">✅</span>
        <div>
          <div style="font-size:13px;font-weight:700;color:var(--accent2)">Тест за самооценка</div>
          <div style="font-size:12px;color:var(--text-muted)">3 въпроса с обратна връзка</div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════
     SECTION: ИНТЕРНЕТ
═══════════════════════════════════════════════════ -->

<!-- SLIDE 1: SECTION DIVIDER -->
<div class="slide slide-section" id="slide-1">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:12px;position:relative">
    <div class="section-number">01</div>
    <h2>Интернет</h2>
    <p class="section-desc">Какво представлява глобалната мрежа и какво можем да правим с нея</p>
  </div>
</div>

<!-- SLIDE 2: КАКВО Е ИНТЕРНЕТ -->
<div class="slide slide-content" id="slide-2">
  <div class="slide-header"><h2>Какво е Интернет?</h2></div>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Интернет е най-голямата <span class="highlight">компютърна мрежа</span> в световен мащаб</li>
        <li>Представлява <span class="highlight">„мрежа от мрежи"</span> — свързва милиони частни, обществени, университетски, фирмени и държавни мрежи</li>
        <li>Осигурява <span class="highlight">отдалечен достъп</span> до голямо разнообразие от информационни ресурси и услуги</li>
        <li>Използва стандартни комуникационни протоколи като <span class="highlight">TCP/IP</span> за обмен на данни</li>
      </ul>
      <div class="tip-box" style="margin-top:20px">
        <strong>💡 Знаете ли?</strong><br>
        Думата „Интернет" идва от <em>inter</em> (между) + <em>network</em> (мрежа). Накратко се казва и <strong>„нет"</strong>.
      </div>
    </div>
    <div class="slide-img">
      <div style="width:260px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:24px;text-align:center">
        <div style="font-size:64px;margin-bottom:12px">🌐</div>
        <div style="font-size:13px;color:var(--text-muted);line-height:1.7">
          Свързва <strong style="color:var(--accent2)">милиони</strong> мрежи<br>и техните потребители<br>по целия свят
        </div>
      </div>
    </div>
  </div>
</div>

<!-- SLIDE 3: В ИНТЕРНЕТ МОЖЕМ -->
<div class="slide slide-content" id="slide-3">
  <div class="slide-header"><h2>В Интернет можем...</h2></div>
  <div class="slide-body">
    <div class="animate-children" style="width:100%">
      <div class="cards cols-3" style="margin-bottom:20px">
        <div class="card"><div class="card-icon">🌤️</div><h3>Прогноза за времето</h3><p>Проверяваме актуалните метеорологични условия</p></div>
        <div class="card"><div class="card-icon">📰</div><h3>Новини</h3><p>Следим актуалните новини и събития от цял свят</p></div>
        <div class="card"><div class="card-icon">✈️</div><h3>Планиране на ваканция</h3><p>Избираме места, резервираме билети и хотели</p></div>
        <div class="card"><div class="card-icon">💼</div><h3>Обяви за работа</h3><p>Търсим нови възможности за кариерно развитие</p></div>
        <div class="card"><div class="card-icon">💳</div><h3>Онлайн плащания</h3><p>Плащаме сметки за ток, вода и телефон</p></div>
        <div class="card"><div class="card-icon">💬</div><h3>Комуникация</h3><p>Общуваме с близки чрез писмена, аудио и видеовръзка</p></div>
      </div>
      <div class="tip-box">
        <strong>И много, много повече!</strong> Интернет е неразделна част от съвременния свят.
      </div>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════
     SECTION: БРАУЗЪР
═══════════════════════════════════════════════════ -->

<!-- SLIDE 4: SECTION DIVIDER -->
<div class="slide slide-section" id="slide-4">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:12px;position:relative">
    <div class="section-number">02</div>
    <h2>Интернет браузър</h2>
    <p class="section-desc">Програмата, чрез която влизаме в Интернет</p>
  </div>
</div>

<!-- SLIDE 5: КАКВО Е БРАУЗЪР -->
<div class="slide slide-content" id="slide-5">
  <div class="slide-header"><h2>Интернет браузър</h2></div>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Специална програма за <span class="highlight">влизане и сърфиране</span> в Интернет</li>
        <li>Служи за <span class="highlight">отваряне и разглеждане</span> на уеб страници</li>
        <li>Осигурява <span class="highlight">връзката</span> между потребителя и информацията в глобалната мрежа</li>
        <li>За влизане в Интернет трябва браузърът да е <span class="highlight">инсталиран</span> на компютъра</li>
      </ul>
    </div>
  </div>
</div>

<!-- SLIDE 6: ПОПУЛЯРНИ БРАУЗЪРИ (with logos) -->
<div class="slide slide-content" id="slide-6">
  <div class="slide-header"><h2>Популярни браузъри</h2></div>
  <div class="slide-body">
    <div style="width:100%" class="animate-children">
      <div class="browser-grid">
        <div class="browser-card">
          {'<img src="' + browser_logos[0] + '" alt="Chrome">' if browser_logos[0] else '<div style="font-size:52px">🔵</div>'}
          <span>Google Chrome</span>
          <span style="font-size:11px;color:var(--accent2)">Хром</span>
        </div>
        <div class="browser-card">
          {'<img src="' + browser_logos[1] + '" alt="Firefox">' if browser_logos[1] else '<div style="font-size:52px">🦊</div>'}
          <span>Mozilla Firefox</span>
          <span style="font-size:11px;color:var(--accent2)">Файърфокс</span>
        </div>
        <div class="browser-card">
          {'<img src="' + browser_logos[3] + '" alt="Edge">' if browser_logos[3] else '<div style="font-size:52px">🔷</div>'}
          <span>Microsoft Edge</span>
          <span style="font-size:11px;color:var(--accent2)">Едж</span>
        </div>
        <div class="browser-card">
          {'<img src="' + browser_logos[2] + '" alt="Opera">' if browser_logos[2] else '<div style="font-size:52px">🅾️</div>'}
          <span>Opera</span>
          <span style="font-size:11px;color:var(--accent2)">Опера</span>
        </div>
        <div class="browser-card">
          {'<img src="' + browser_logos[4] + '" alt="Safari">' if browser_logos[4] else '<div style="font-size:52px">🧭</div>'}
          <span>Safari</span>
          <span style="font-size:11px;color:var(--accent2)">Сафари</span>
        </div>
      </div>
      <div class="tip-box" style="margin-top:20px">
        <strong>💡 Важно:</strong> Браузърът <strong>НЕ е</strong> търсещата машина! Chrome е браузър, докато Google е търсачка.
      </div>
    </div>
  </div>
</div>

<!-- SLIDE 7: СТРУКТУРА НА БРАУЗЪР -->
<div class="slide slide-content" id="slide-7">
  <div class="slide-header"><h2>Структура на браузъра</h2></div>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li><span class="highlight">Прозорец</span> — браузърът се отваря в отделен прозорец, като всяка друга програма</li>
        <li><span class="highlight">Раздел (таб)</span> — всяка отделна уеб страница, отворена в прозореца; може да отваряте много раздели едновременно</li>
        <li><span class="highlight">Начална страница</span> — разделът, който се зарежда автоматично при стартиране на браузъра</li>
        <li><span class="highlight">Адресно поле</span> — полето, в което се изписва адресът на уеб страницата</li>
        <li><span class="highlight">Бутони за навигация</span> — напред, назад, презареждане на страница</li>
      </ul>
    </div>
    <div class="slide-img">
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;width:280px">
        <div style="background:var(--surface2);border-radius:6px;padding:8px 12px;margin-bottom:8px;display:flex;gap:6px;align-items:center">
          <div style="width:10px;height:10px;border-radius:50%;background:#ef4444"></div>
          <div style="width:10px;height:10px;border-radius:50%;background:#f59e0b"></div>
          <div style="width:10px;height:10px;border-radius:50%;background:#22c55e"></div>
        </div>
        <div style="background:var(--bg);border-radius:4px;padding:6px 10px;margin-bottom:8px;font-size:11px;color:var(--text-muted);display:flex;gap:6px;align-items:center">
          <span>&#8592;</span><span>&#8594;</span>
          <div style="flex:1;background:var(--surface);border-radius:3px;padding:3px 8px;font-size:10px">https://www.wikipedia.org</div>
        </div>
        <div style="background:var(--bg);border-radius:4px;padding:16px;font-size:12px;color:var(--text-muted);text-align:center;min-height:80px;display:flex;align-items:center;justify-content:center">
          🌐 Съдържание на уеб страницата
        </div>
      </div>
    </div>
  </div>
</div>

<!-- SLIDE 8: ИНТЕРНЕТ СТРАНИЦА -->
<div class="slide slide-content" id="slide-8">
  <div class="slide-header"><h2>Интернет страница (Уеб страница)</h2></div>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Специален файл, съдържащ информация под формата на <span class="highlight">текст, изображения, видео и аудио</span></li>
        <li>Има <span class="highlight">уникален адрес (URL)</span> — указва точното място в Интернет</li>
        <li>Адресът се изписва в <span class="highlight">адресното поле</span> на браузъра</li>
        <li>Групата от свързани уеб страници, собственост на един автор или организация, се казва <span class="highlight">уеб сайт</span></li>
        <li>При отваряне на последователни страници в един раздел потребителят може да се <span class="highlight">придвижва назад и напред</span></li>
      </ul>
      <div class="tip-box" style="margin-top:16px">
        <strong>📌 ЗАДАЧА 1:</strong> Потърсете кои браузъри са инсталирани на вашия компютър. Отворете един от тях и разгледайте началната страница.
      </div>
    </div>
  </div>
</div>

<!-- SLIDE 9: ХИПЕРВРЪЗКИ -->
<div class="slide slide-content" id="slide-9">
  <div class="slide-header"><h2>Хипервръзки (Линкове)</h2></div>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Интерактивен обект, който <span class="highlight">води до друга уеб страница</span></li>
        <li>Може да бъде <span class="highlight">текст</span> (обикновено подчертан и оцветен в синьо) или <span class="highlight">изображение</span></li>
        <li>При посочване с мишка се появява символът <span class="highlight" style="font-size:18px">👆</span></li>
        <li>Чрез хипервръзките се осъществява <span class="highlight">навигацията</span> между уеб страниците</li>
        <li>Разговорно се казва <span class="highlight">„линк"</span> (от англ. <em>hyperlink</em>)</li>
      </ul>
      <div class="tip-box" style="margin-top:16px">
        <strong>📌 ЗАДАЧА 2:</strong> Отворете <a href="https://www.wikipedia.org" target="_blank" style="color:var(--accent2)">wikipedia.org</a> и намерете хипервръзката за български език. Последвайте я и се върнете назад с бутона ←
      </div>
    </div>
    <div class="slide-img" style="flex:0 0 200px">
      {'<img src="' + hyperlink_img + '" alt="Хипервръзка пример" style="max-width:200px;max-height:180px;border-radius:var(--radius);box-shadow:var(--shadow);object-fit:contain;background:white;padding:8px">' if hyperlink_img else '<div style="width:200px;height:150px;display:flex;align-items:center;justify-content:center;background:var(--surface);border-radius:var(--radius);font-size:48px">🔗</div>'}
    </div>
  </div>
</div>

<!-- SLIDE 10: WIKIPEDIA DEMO -->
<div class="slide slide-content" id="slide-10">
  <div class="slide-header"><h2>Пример: Началната страница на Уикипедия</h2></div>
  <div class="slide-body" style="flex-direction:column;align-items:center">
    <div style="width:100%;text-align:center" class="animate-children">
      <p style="color:var(--text-muted);margin-bottom:16px;font-size:14px">Показани са основните инструменти на браузъра и елементите в страницата</p>
      {'<img src="' + lecture_imgs[1] + '" alt="Wikipedia начална страница" class="full-img">' if lecture_imgs[1] else '<div style="height:300px;display:flex;align-items:center;justify-content:center;background:var(--surface);border-radius:var(--radius);font-size:48px;color:var(--text-muted)">🌐</div>'}
      <p class="img-caption">Фигура 3: Интерфейс на браузъра Firefox с отворена началната страница на Уикипедия</p>
    </div>
  </div>
</div>

<!-- SLIDE 11: СРАВНЕНИЕ БРАУЗЪРИ (with images) -->
<div class="slide slide-content" id="slide-11">
  <div class="slide-header"><h2>Chrome, Firefox и Edge — сравнение</h2></div>
  <div class="slide-body" style="flex-direction:column">
    <div style="width:100%;text-align:center" class="animate-children">
      {'<img src="' + lecture_imgs[3] + '" alt="Сравнение браузъри" class="full-img">' if lecture_imgs[3] else ''}
      <p class="img-caption">Фигура 2: Сравнение между Chrome, Firefox и Edge — всички отварят едни и същи два раздела (Уикипедия и нов раздел)</p>
    </div>
    <div class="tip-box" style="margin-top:16px">
      <strong>💡 Забележете:</strong> Въпреки визуалните разлики, всички браузъри изпълняват едни и същи основни функции.
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════
     SECTION: ТЪРСЕНЕ
═══════════════════════════════════════════════════ -->

<!-- SLIDE 12: SECTION DIVIDER -->
<div class="slide slide-section" id="slide-12">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:12px;position:relative">
    <div class="section-number">03</div>
    <h2>Търсене в Интернет</h2>
    <p class="section-desc">Търсачки, техники за търсене и критична оценка на резултатите</p>
  </div>
</div>

<!-- SLIDE 13: ТЪРСЕЩА МАШИНА -->
<div class="slide slide-content" id="slide-13">
  <div class="slide-header"><h2>Търсеща машина (търсачка)</h2></div>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Специализиран <span class="highlight">софтуер за търсене</span> на информация в Интернет</li>
        <li>Отваря се в браузъра като уеб страница и има собствен <span class="highlight">адрес (URL)</span></li>
        <li>Има <span class="highlight">поле за търсене</span>, в което се попълва заявка — ключови думи</li>
        <li>Адресното поле на браузъра <span class="highlight">също играе роля на търсачка</span></li>
        <li>Работи с <span class="highlight">„паяци"</span> (web crawlers) — програми, които обхождат уеб страниците и индексират съдържанието им</li>
      </ul>
    </div>
    <div class="slide-img">
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:24px;width:260px;text-align:center">
        <div style="font-size:48px;margin-bottom:12px">🔍</div>
        <div style="background:var(--bg);border:2px solid var(--accent);border-radius:50px;padding:10px 16px;font-size:13px;color:var(--text-muted);margin-bottom:12px;text-align:left">обяви за работа...</div>
        <div style="font-size:11px;color:var(--text-muted);line-height:1.6">Резултати: 4 760 000,000<br>Времe: 0.45 сек.</div>
      </div>
    </div>
  </div>
</div>

<!-- SLIDE 14: НАЙ-ПОПУЛЯРНИ ТЪРСАЧКИ -->
<div class="slide slide-content" id="slide-14">
  <div class="slide-header"><h2>Популярни търсещи машини</h2></div>
  <div class="slide-body" style="flex-direction:column">
    <div style="width:100%" class="animate-children">
      <div class="cards cols-2">
        <div class="card" style="display:flex;gap:16px;align-items:center">
          <div style="font-size:40px">🔍</div>
          <div><h3>Google</h3><p>https://www.google.com/ — Гугъл<br>Над 90% пазарен дял в световен мащаб</p></div>
        </div>
        <div class="card" style="display:flex;gap:16px;align-items:center">
          <div style="font-size:40px">🔵</div>
          <div><h3>Bing</h3><p>https://www.bing.com/ — Бинг<br>Разработен от Microsoft</p></div>
        </div>
        <div class="card" style="display:flex;gap:16px;align-items:center">
          <div style="font-size:40px">🟣</div>
          <div><h3>Yahoo!</h3><p>https://search.yahoo.com/ — Яхуу<br>Един от първите популярни портали</p></div>
        </div>
        <div class="card" style="display:flex;gap:16px;align-items:center">
          <div style="font-size:40px">🦆</div>
          <div><h3>DuckDuckGo</h3><p>https://duckduckgo.com/ — Дъкдъкгоу<br>Поставя акцент върху поверителността</p></div>
        </div>
      </div>
      <div class="tip-box" style="margin-top:14px">
        <strong>📌 ЗАДАЧА 3:</strong> Отворете два нови раздела и сравнете началните страници на Google и Bing. Намерете полетата за търсене и бутоните.
      </div>
    </div>
  </div>
</div>

<!-- SLIDE 15: СРАВНЕНИЕ ТЪРСАЧКИ (with images) -->
<div class="slide slide-content" id="slide-15b">
  <div class="slide-header"><h2>Google и Bing — сравнение (Задача 3)</h2></div>
  <div class="slide-body" style="gap:16px">
    <div style="flex:1;text-align:center" class="animate-children">
      {'<img src="' + lecture_imgs[8] + '" alt="Google" style="max-width:100%;max-height:42vh;border-radius:var(--radius);box-shadow:var(--shadow);object-fit:contain">' if lecture_imgs[8] else ''}
      <p class="img-caption" style="margin-top:6px">Google — https://www.google.com</p>
    </div>
    <div style="flex:1;text-align:center" class="animate-children">
      {'<img src="' + lecture_imgs[5] + '" alt="Bing" style="max-width:100%;max-height:42vh;border-radius:var(--radius);box-shadow:var(--shadow);object-fit:contain">' if lecture_imgs[5] else ''}
      <p class="img-caption" style="margin-top:6px">Bing — https://www.bing.com</p>
    </div>
  </div>
</div>

<!-- SLIDE 15: НАЧИНИ ЗА ТЪРСЕНЕ -->
<div class="slide slide-content" id="slide-15">
  <div class="slide-header"><h2>Начини за търсене — добри практики</h2></div>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <ul class="bullets">
        <li>Изберете <span class="highlight">ключови думи</span>, вероятно използвани в търсения сайт</li>
        <li>Започнете с <span class="highlight">обикновена заявка</span> от една дума, после добавете пояснителни думи</li>
        <li>Ако търсите в <span class="highlight">определен регион</span>, добавете го към заявката
          <ul class="bullets" style="margin-top:8px"><li class="sub">Пример: <em>обяви</em> → <em>обяви за работа</em> → <em>обяви за работа Пловдив</em></li></ul>
        </li>
        <li>Заявката <span class="highlight">не различава главни и малки букви</span>
          <ul class="bullets" style="margin-top:8px"><li class="sub">Пример: <em>обяви за работа плевен</em> = <em>Обяви за Работа Плевен</em></li></ul>
        </li>
        <li>Търсачката <span class="highlight">автоматично коригира</span> грешно изписани думи
          <ul class="bullets" style="margin-top:8px"><li class="sub">Пример: <em>убяви за рабута</em> → <em>обяви за работа</em></li></ul>
        </li>
      </ul>
    </div>
  </div>
</div>

<!-- SLIDE 16: ДЕМОНСТРАЦИЯ НА ТЪРСЕНЕ -->
<div class="slide slide-content" id="slide-16">
  <div class="slide-header"><h2>Демонстрация — Търсене с Google</h2></div>
  <div class="slide-body" style="flex-direction:column;align-items:center">
    <div style="width:100%;max-width:680px;text-align:center" class="animate-children">
      {'<img src="' + google_demo_img + '" alt="Google търсене" class="full-img">' if google_demo_img else ''}
      <p class="img-caption">Стъпки: 1) Отваря се google.com → 2) Изписва се заявката → 3) Натиска се „Google Търсене" или Enter</p>
    </div>
  </div>
</div>

<!-- SLIDE 17: РЕЗУЛТАТИ -->
<div class="slide slide-content" id="slide-17">
  <div class="slide-header"><h2>Резултати от търсенето</h2></div>
  <div class="slide-body">
    <div class="slide-text animate-children">
      <ul class="bullets">
        <li>Показва се <span class="highlight">списък от имена на страници</span> и хипервръзки към тях</li>
        <li>Страниците, <span class="highlight">най-точно отговарящи</span> на заявката, са класирани най-напред</li>
        <li>Показва се <span class="highlight">брой резултати</span> и времето за търсене</li>
        <li>Резултатите се отварят <span class="highlight">в същия раздел</span> (при клик с ляв бутон)</li>
        <li>Адресното поле на браузъра <span class="highlight">също работи като търсачка</span></li>
      </ul>
    </div>
    <div class="slide-img" style="flex:0 0 280px">
      <div style="width:280px">
        <div class="result-item ad">
          <div class="r-url">https://rabotа.bg</div>
          <div class="r-title">Обяви за работа — Работа.bg</div>
          <div class="r-desc">Намери своята следваща работа сред хиляди обяви...</div>
        </div>
        <div class="result-item">
          <div class="r-url">https://jobs.bg › обяви</div>
          <div class="r-title">Jobs.bg — Обяви за работа</div>
          <div class="r-desc">Разгледайте над 10,000 актуални обяви за работа в България...</div>
        </div>
        <div class="result-item">
          <div class="r-url">https://zaplata.bg</div>
          <div class="r-title">Zaplata.bg — Търсене на работа</div>
          <div class="r-desc">Намерете подходяща работа с добро заплащане...</div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- SLIDE 18: ПРИМЕРИ ЗА ТЪРСЕНЕ (images from lecture) -->
<div class="slide slide-content" id="slide-18">
  <div class="slide-header"><h2>Примери за търсене с резултати</h2></div>
  <div class="slide-body" style="flex-direction:column;align-items:center">
    <div style="width:100%;text-align:center" class="animate-children">
      {'<img src="' + lecture_imgs[2] + '" alt="Примери търсене" class="full-img">' if lecture_imgs[2] else '<div style="font-size:48px;text-align:center;padding:40px">🔍</div>'}
      <p class="img-caption">Фигура 5: Страница с първите резултати от заявката „обяви за работа" в търсачката Google</p>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════
     SECTION: БЕЗОПАСНОСТ
═══════════════════════════════════════════════════ -->

<!-- SLIDE 19: SECTION DIVIDER -->
<div class="slide slide-section" id="slide-19">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:12px;position:relative">
    <div class="section-number">04</div>
    <h2>Критично търсене и безопасност</h2>
    <p class="section-desc">Как да разпознаем надеждни резултати и да пазим личните си данни</p>
  </div>
</div>

<!-- SLIDE 20: КРИТИЧЕН ПОДБОР -->
<div class="slide slide-content" id="slide-20">
  <div class="slide-header"><h2>Критичен подбор на резултати</h2></div>
  <div class="slide-body">
    <div class="slide-text scrollable animate-children">
      <div class="warning-box" style="margin-bottom:16px">
        <strong>⚠️ Внимание!</strong> Не всички резултати са достоверни и полезни!
      </div>
      <ul class="bullets">
        <li>Първите резултати могат да са <span class="highlight" style="color:#f59e0b">реклами</span> — маркирани с „Реклама" или „Ad"; не са непременно неверни, но са платени</li>
        <li>Некачествени сайтове: <span class="highlight" style="color:#f59e0b">граматически лош текст</span> — признак за машинен превод</li>
        <li>Адресите <span class="highlight" style="color:#f59e0b">bg.website.com</span> или <span class="highlight" style="color:#f59e0b">website.com/bg</span> не са официални български сайтове</li>
        <li>Адресът в търсачката <span class="highlight" style="color:#f59e0b">не съвпада</span> с адреса в браузъра след отваряне</li>
        <li>При съмнение — <span class="highlight">потърсете повторно</span> информацията в друг надежден источник</li>
      </ul>
    </div>
  </div>
</div>

<!-- SLIDE 21: БЕЗОПАСНОСТ В ИНТЕРНЕТ -->
<div class="slide slide-content" id="slide-21">
  <div class="slide-header"><h2>Правила за безопасност в Интернет</h2></div>
  <div class="slide-body" style="flex-direction:column">
    <div style="width:100%" class="animate-children">
      <div class="safety-grid">
        <div class="safety-item">
          <div class="safety-icon">🔒</div>
          <div class="safety-text"><strong>Пазете личните си данни</strong>Не предоставяйте имена, пароли, ЕГН, телефон или банкови данни — крие риск от злоупотреба.</div>
        </div>
        <div class="safety-item">
          <div class="safety-icon">📷</div>
          <div class="safety-text"><strong>Внимавайте с личните снимки</strong>Не публикувайте публично лични снимки на вас и близките ви.</div>
        </div>
        <div class="safety-item">
          <div class="safety-icon">🤝</div>
          <div class="safety-text"><strong>Избягвайте лични срещи</strong>Хора в Интернет може да предоставят невярна информация за себе си. Избягвайте срещи с непознати.</div>
        </div>
        <div class="safety-item">
          <div class="safety-icon">💬</div>
          <div class="safety-text"><strong>Не изпращайте обидни съобщения</strong>Не отговаряйте на провокации. Не изпращайте анонимни или верижни съобщения.</div>
        </div>
        <div class="safety-item">
          <div class="safety-icon">📎</div>
          <div class="safety-text"><strong>Внимавайте с прикачени файлове</strong>Не отваряйте файлове и връзки от непознати — могат да съдържат вируси.</div>
        </div>
        <div class="safety-item">
          <div class="safety-icon">🛡️</div>
          <div class="safety-text"><strong>Проверявайте информацията</strong>Не всичко в Интернет е достоверно. Търсете потвърждение от надеждни източници.</div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- SLIDE 22: SAFETY IMAGE -->
<div class="slide slide-content" id="slide-22">
  <div class="slide-header"><h2>Обобщение — Безопасност в Интернет</h2></div>
  <div class="slide-body" style="flex-direction:column;align-items:center">
    <div style="width:100%;text-align:center" class="animate-children">
      {'<img src="' + safety_img + '" alt="Безопасност" class="full-img">' if safety_img else ''}
      <p class="img-caption" style="margin-top:16px">Основните правила за безопасно поведение в Интернет</p>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════
     QUIZ
═══════════════════════════════════════════════════ -->

<!-- SLIDE 23: QUIZ INTRO -->
<div class="slide slide-section" id="slide-23">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:16px;position:relative">
    <div style="font-size:64px">✅</div>
    <h2 style="font-size:clamp(24px,3.5vw,40px);font-weight:800;text-align:center;background:linear-gradient(135deg,#fff,var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent">Тест за самооценка</h2>
    <p class="section-desc">3 въпроса · Незабавна обратна връзка · Вижте колко сте усвоили</p>
    <button class="quiz-btn primary" onclick="goToSlide(24)" style="margin-top:8px">Започнете теста →</button>
  </div>
</div>

<!-- SLIDE 24: QUIZ -->
<div class="slide slide-quiz" id="slide-24">
  <div class="quiz-container" id="quiz-container">
    <!-- Quiz progress -->
    <div class="quiz-progress" id="quiz-progress">
      <div class="quiz-step current" id="qstep-0"></div>
      <div class="quiz-step" id="qstep-1"></div>
      <div class="quiz-step" id="qstep-2"></div>
    </div>

    <!-- Q1 -->
    <div id="qblock-0" class="question-card">
      <div class="q-number">Въпрос 1 от 3</div>
      <div class="q-text">Какво е Интернет?</div>
      <div class="options" id="opts-0">
        <div class="option" onclick="selectOption(0, 0, false)" id="opt-0-0">
          <div class="option-letter">А</div>
          <div>Локална мрежа за свързване на два компютъра</div>
        </div>
        <div class="option" onclick="selectOption(0, 1, false)" id="opt-0-1">
          <div class="option-letter">Б</div>
          <div>Специализирана програма за търсене на информация</div>
        </div>
        <div class="option" onclick="selectOption(0, 2, true)" id="opt-0-2">
          <div class="option-letter">В</div>
          <div>Глобална мрежа, която свързва други мрежи и техните потребители</div>
        </div>
        <div class="option" onclick="selectOption(0, 3, false)" id="opt-0-3">
          <div class="option-letter">Г</div>
          <div>Нито едно от изброените</div>
        </div>
      </div>
      <div class="q-feedback" id="qfb-0"></div>
      <div style="margin-top:16px;display:flex;gap:12px">
        <button class="quiz-btn primary" id="qbtn-check-0" onclick="checkAnswer(0, 2, false)" disabled>Провери отговора</button>
      </div>
    </div>

    <!-- Q2 -->
    <div id="qblock-1" class="question-card" style="display:none">
      <div class="q-number">Въпрос 2 от 3</div>
      <div class="q-text">Посочете кои от изброените са интернет браузъри и кои са търсещи машини:</div>
      <div class="q-multi-label">Изберете правилните отговори (може да изберете повече от един)</div>
      <div class="options" id="opts-1">
        <div class="option" onclick="toggleMultiOption(1, 0)" id="opt-1-0">
          <div class="option-letter">А</div>
          <div><strong>Google</strong> — търсеща машина</div>
        </div>
        <div class="option" onclick="toggleMultiOption(1, 1)" id="opt-1-1">
          <div class="option-letter">Б</div>
          <div><strong>Firefox</strong> — интернет браузър</div>
        </div>
        <div class="option" onclick="toggleMultiOption(1, 2)" id="opt-1-2">
          <div class="option-letter">В</div>
          <div><strong>Chrome</strong> — търсеща машина</div>
        </div>
        <div class="option" onclick="toggleMultiOption(1, 3)" id="opt-1-3">
          <div class="option-letter">Г</div>
          <div><strong>Bing</strong> — търсеща машина</div>
        </div>
      </div>
      <div class="q-feedback" id="qfb-1"></div>
      <div style="margin-top:16px;display:flex;gap:12px">
        <button class="quiz-btn primary" id="qbtn-check-1" onclick="checkMultiAnswer(1, [0,1,3])" disabled>Провери отговора</button>
      </div>
    </div>

    <!-- Q3 -->
    <div id="qblock-2" class="question-card" style="display:none">
      <div class="q-number">Въпрос 3 от 3</div>
      <div class="q-text">Кое от следните твърдения за търсене в Интернет е <u>невярно</u>?</div>
      <div class="options" id="opts-2">
        <div class="option" onclick="selectOption(2, 0, false)" id="opt-2-0">
          <div class="option-letter">А</div>
          <div>Информацията, която намираме в Интернет, не винаги е достоверна</div>
        </div>
        <div class="option" onclick="selectOption(2, 1, true)" id="opt-2-1">
          <div class="option-letter">Б</div>
          <div>В Интернет можем да търсим само на английски език</div>
        </div>
        <div class="option" onclick="selectOption(2, 2, false)" id="opt-2-2">
          <div class="option-letter">В</div>
          <div>За да намерим информация в Интернет, трябва да използваме търсеща машина</div>
        </div>
        <div class="option" onclick="selectOption(2, 3, false)" id="opt-2-3">
          <div class="option-letter">Г</div>
          <div>Търсещата машина работи с ключови думи</div>
        </div>
      </div>
      <div class="q-feedback" id="qfb-2"></div>
      <div style="margin-top:16px;display:flex;gap:12px">
        <button class="quiz-btn primary" id="qbtn-check-2" onclick="checkAnswer(2, 1, true)" disabled>Провери отговора</button>
      </div>
    </div>

    <!-- Score screen -->
    <div class="score-screen" id="score-screen">
      <div class="score-circle">
        <div class="score-num" id="score-num">0</div>
        <div class="score-total">/ 3</div>
      </div>
      <div class="score-msg" id="score-msg"></div>
      <div class="score-detail" id="score-detail"></div>
      <div style="display:flex;gap:12px;margin-top:8px">
        <button class="quiz-btn secondary" onclick="resetQuiz()">🔄 Опитай отново</button>
        <button class="quiz-btn primary" onclick="goToSlide(25)">Финал →</button>
      </div>
    </div>
  </div>
</div>

<!-- SLIDE 25: БЛАГОДАРЯ -->
<div class="slide slide-thanks" id="slide-25">
  <div class="animate-children" style="display:flex;flex-direction:column;align-items:center;gap:0">
    <div style="font-size:72px;margin-bottom:16px;animation:fadeUp 1s ease">🎓</div>
    <h2 style="font-size:clamp(28px,4vw,52px);font-weight:900;text-align:center;background:linear-gradient(135deg,#fff,var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px">Благодаря за вниманието!</h2>
    <p style="color:var(--text-muted);font-size:16px;text-align:center;margin-bottom:32px">Тема 1.1 — Сърфиране, търсене и филтриране на данни</p>
    <div class="digcomp-badge">Европейска Рамка на дигиталните компетентности · DigComp 2.1 · Нива 1–2</div>
    <div style="margin-top:40px;display:grid;grid-template-columns:repeat(3,1fr);gap:16px;max-width:600px">
      <div class="card" style="text-align:center">
        <div style="font-size:28px;margin-bottom:6px">📚</div>
        <div style="font-size:13px;font-weight:700;color:var(--accent2)">Материалът</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px">завършен</div>
      </div>
      <div class="card" style="text-align:center">
        <div style="font-size:28px;margin-bottom:6px">🔍</div>
        <div style="font-size:13px;font-weight:700;color:var(--accent2)">Практиката</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px">4 задачи</div>
      </div>
      <div class="card" style="text-align:center">
        <div style="font-size:28px;margin-bottom:6px">✅</div>
        <div style="font-size:13px;font-weight:700;color:var(--accent2)">Тестът</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px">попълнен</div>
      </div>
    </div>
    <p style="margin-top:32px;font-size:13px;color:var(--text-muted)">
      Използвана литература: Wikipedia.org · Николова & Стефанова, ИКТ 5. клас, Просвета · Тужаров, Учебник по Информатика
    </p>
  </div>
</div>

</div><!-- /#slides-wrapper -->

<!-- Bottom nav dots -->
<div id="nav">
  <div id="nav-dots"></div>
  <div id="slide-counter">1 / 26</div>
</div>

<script>
// ===== SLIDE ENGINE =====
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
  setTimeout(() => prev.classList.remove('prev'), 600);
  // Re-trigger animations
  next.querySelectorAll('.animate-children').forEach(el => {
    el.querySelectorAll(':scope > *').forEach(c => {
      c.style.animation = 'none';
      c.offsetHeight;
      c.style.animation = '';
    });
  });
  next.classList.add('active');
  current = n;
  updateNav();
}

function changeSlide(dir) { goToSlide(current + dir); }

function updateNav() {
  const pct = TOTAL <= 1 ? 100 : (current / (TOTAL - 1)) * 100;
  document.getElementById('progress-bar').style.width = pct + '%';
  document.getElementById('slide-counter').textContent = (current + 1) + ' / ' + TOTAL;
  document.querySelectorAll('.nav-dot').forEach((d, i) => d.classList.toggle('active', i === current));
  document.getElementById('btn-prev').disabled = current === 0;
  document.getElementById('btn-next').disabled = current === TOTAL - 1;
  // Section pills - find index of each anchor slide
  const anchors = [0,1,4,12,19,23];
  const pills = document.querySelectorAll('.section-pill');
  let activeSection = 0;
  anchors.forEach((s, i) => { if (current >= s) activeSection = i; });
  pills.forEach((p, i) => p.classList.toggle('active', i === activeSection));
}

// Build nav dots
(function() {
  const c = document.getElementById('nav-dots');
  for (let i = 0; i < TOTAL; i++) {
    const d = document.createElement('div');
    d.className = 'nav-dot' + (i === 0 ? ' active' : '');
    d.onclick = () => goToSlide(i);
    d.title = 'Слайд ' + (i + 1);
    c.appendChild(d);
  }
})();
updateNav();

// Keyboard navigation
document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); changeSlide(1); }}
  if (e.key === 'ArrowLeft') {{ e.preventDefault(); changeSlide(-1); }}
  if (e.key === 'Home') goToSlide(0);
  if (e.key === 'End') goToSlide(TOTAL - 1);
}});

// Touch/swipe
let touchStartX = 0;
document.addEventListener('touchstart', e => {{ touchStartX = e.touches[0].clientX; }}, {{passive:true}});
document.addEventListener('touchend', e => {{
  const dx = e.changedTouches[0].clientX - touchStartX;
  if (Math.abs(dx) > 50) changeSlide(dx < 0 ? 1 : -1);
}}, {{passive:true}});

// ===== QUIZ ENGINE =====
let quizAnswers = [null, [], null];
let quizChecked = [false, false, false];
let quizCorrect = [false, false, false];
let currentQ = 0;

function selectOption(qIdx, optIdx, isCorrect) {{
  if (quizChecked[qIdx]) return;
  quizAnswers[qIdx] = optIdx;
  document.querySelectorAll('#opts-' + qIdx + ' .option').forEach((o, i) => {{
    o.classList.toggle('selected', i === optIdx);
  }});
  document.getElementById('qbtn-check-' + qIdx).disabled = false;
}}

function toggleMultiOption(qIdx, optIdx) {{
  if (quizChecked[qIdx]) return;
  const idx = quizAnswers[qIdx].indexOf(optIdx);
  if (idx === -1) quizAnswers[qIdx].push(optIdx);
  else quizAnswers[qIdx].splice(idx, 1);
  document.querySelectorAll('#opts-' + qIdx + ' .option').forEach((o, i) => {{
    o.classList.toggle('selected', quizAnswers[qIdx].includes(i));
  }});
  document.getElementById('qbtn-check-' + qIdx).disabled = quizAnswers[qIdx].length === 0;
}}

function checkAnswer(qIdx, correctIdx, isLastQ) {{
  if (quizAnswers[qIdx] === null) return;
  quizChecked[qIdx] = true;
  document.getElementById('qbtn-check-' + qIdx).disabled = true;
  const opts = document.querySelectorAll('#opts-' + qIdx + ' .option');
  opts.forEach(o => o.classList.add('disabled'));
  const chosen = quizAnswers[qIdx];
  const isRight = chosen === correctIdx;
  quizCorrect[qIdx] = isRight;
  opts[correctIdx].classList.add('correct');
  if (!isRight) opts[chosen].classList.add('wrong');
  const fb = document.getElementById('qfb-' + qIdx);
  fb.className = 'q-feedback show ' + (isRight ? 'correct' : 'wrong');
  if (qIdx === 0) {{
    fb.innerHTML = isRight
      ? '✅ <strong>Правилно!</strong> Интернет е глобална мрежа от мрежи, която свързва милиони потребители по целия свят.'
      : '❌ <strong>Неправилно.</strong> Правилният отговор е <strong>В)</strong>. Интернет е <em>глобална</em> мрежа от мрежи — не локална и не е само програма.';
  }} else if (qIdx === 2) {{
    fb.innerHTML = isRight
      ? '✅ <strong>Правилно!</strong> Твърдението „можем да търсим само на английски" е невярно — търсачките поддържат всички езици, включително български.'
      : '❌ <strong>Неправилно.</strong> Отговор <strong>Б)</strong> е невярното твърдение — в Интернет можем да търсим на всякакъв език.';
  }}
  setTimeout(() => {{
    if (!isLastQ) {{
      currentQ = qIdx + 1;
      document.getElementById('qblock-' + qIdx).style.display = 'none';
      document.getElementById('qblock-' + currentQ).style.display = 'block';
      document.getElementById('qstep-' + qIdx).className = 'quiz-step done';
      if (currentQ < 3) document.getElementById('qstep-' + currentQ).className = 'quiz-step current';
    }} else {{
      showScore();
    }}
  }}, 1800);
}}

function checkMultiAnswer(qIdx, correctIndices) {{
  if (quizAnswers[qIdx].length === 0) return;
  quizChecked[qIdx] = true;
  document.getElementById('qbtn-check-' + qIdx).disabled = true;
  const opts = document.querySelectorAll('#opts-' + qIdx + ' .option');
  opts.forEach(o => o.classList.add('disabled'));
  // Correct answers: 0 (Google=search), 1 (Firefox=browser), 3 (Bing=search)
  // Wrong answer: 2 (Chrome is a BROWSER, not a search engine)
  const chosen = quizAnswers[qIdx];
  const isRight = correctIndices.every(i => chosen.includes(i)) && !chosen.includes(2);
  quizCorrect[qIdx] = isRight;
  opts.forEach((o, i) => {{
    if (correctIndices.includes(i)) o.classList.add('multi-correct-marked');
    else if (chosen.includes(i)) o.classList.add('multi-wrong-marked');
  }});
  const fb = document.getElementById('qfb-' + qIdx);
  fb.className = 'q-feedback show ' + (isRight ? 'correct' : 'wrong');
  fb.innerHTML = isRight
    ? '✅ <strong>Правилно!</strong> Google и Bing са търсещи машини, Firefox и Chrome са браузъри.'
    : '❌ <strong>Внимание:</strong> <strong>Chrome е браузър</strong>, а не търсеща машина! Google и Bing са търсачки; Firefox и Chrome са браузъри.';
  setTimeout(() => {{
    currentQ = qIdx + 1;
    document.getElementById('qblock-' + qIdx).style.display = 'none';
    document.getElementById('qblock-' + currentQ).style.display = 'block';
    document.getElementById('qstep-' + qIdx).className = 'quiz-step done';
    document.getElementById('qstep-' + currentQ).className = 'quiz-step current';
  }}, 1800);
}}

function showScore() {{
  document.querySelectorAll('[id^=qblock-]').forEach(b => b.style.display = 'none');
  document.getElementById('score-screen').classList.add('show');
  document.querySelectorAll('.quiz-step').forEach(s => s.className = 'quiz-step done');
  const score = quizCorrect.filter(Boolean).length;
  document.getElementById('score-num').textContent = score;
  const msgs = ['Опитайте отново! 💪', 'Добър старт! 📚', 'Много добре! 👍', 'Отличен резултат! 🏆'];
  document.getElementById('score-msg').textContent = msgs[score];
  const details = [
    'Прегледайте материала и опитайте отново — ще се справите!',
    'Прочетете повторно разделите, при които имате грешки.',
    'Почти перфектно! Прегледайте въпросите с грешки за пълно разбиране.',
    'Усвоили сте материала отлично! Готови сте за следващата тема.'
  ];
  document.getElementById('score-detail').textContent = details[score];
}}

function resetQuiz() {{
  quizAnswers = [null, [], null];
  quizChecked = [false, false, false];
  quizCorrect = [false, false, false];
  currentQ = 0;
  for (let i = 0; i < 3; i++) {{
    document.getElementById('qblock-' + i).style.display = i === 0 ? 'block' : 'none';
    document.querySelectorAll('#opts-' + i + ' .option').forEach(o => {{
      o.className = 'option';
    }});
    document.getElementById('qfb-' + i).className = 'q-feedback';
    document.getElementById('qbtn-check-' + i).disabled = true;
    document.getElementById('qstep-' + i).className = 'quiz-step' + (i === 0 ? ' current' : '');
  }}
  document.getElementById('score-screen').classList.remove('show');
}}
</script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = OUT.stat().st_size / 1024
print(f"✅ Done! Output: {OUT}")
print(f"   Size: {size_kb:.1f} KB")
