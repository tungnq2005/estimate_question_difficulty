"""
Generic verification form generator.
Takes a subject config and produces a self-contained HTML file.
"""
import json


FORM_TEMPLATE = '''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --paper:      #FAF7F2;
    --paper-2:    #F3EEE4;
    --ink:        #1A1D1E;
    --ink-soft:   #4A4F52;
    --ink-mute:   #8B8E90;
    --rule:       #D9D2C4;
    --rule-soft:  #E8E3D6;
    --accent:     {accent};
    --accent-2:   {accent2};
    --warm:       #C2410C;
    --red:        #991B1B;
    --green:      #15803D;
    --amber:      #92400E;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    background: var(--paper);
    color: var(--ink);
    font-family: 'IBM Plex Sans', -apple-system, sans-serif;
    font-size: 15px;
    line-height: 1.55;
    min-height: 100vh;
  }}
  header {{
    background: var(--paper);
    border-bottom: 1px solid var(--rule);
    padding: 22px 32px;
    position: sticky; top: 0;
    z-index: 50;
    backdrop-filter: blur(6px);
  }}
  .header-inner {{
    display: flex; align-items: center; gap: 32px;
    max-width: 1400px; margin: 0 auto;
  }}
  .brand {{
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 500;
    font-size: 22px;
    letter-spacing: -0.01em;
    line-height: 1.1;
  }}
  .brand small {{
    display: block;
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 400;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-mute);
    margin-top: 2px;
  }}
  .teacher-input {{
    flex: 1;
    max-width: 340px;
  }}
  .teacher-input label {{
    display: block;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-mute);
    margin-bottom: 4px;
  }}
  .teacher-input input {{
    width: 100%;
    padding: 6px 10px;
    border: 1px solid var(--rule);
    background: white;
    font-family: inherit;
    font-size: 14px;
    color: var(--ink);
    border-radius: 2px;
  }}
  .teacher-input input:focus {{
    outline: 2px solid var(--accent);
    outline-offset: -1px;
  }}
  .progress-wrap {{
    flex: 1;
    max-width: 320px;
  }}
  .progress-label {{
    display: flex; justify-content: space-between;
    font-size: 11px;
    letter-spacing: 0.05em;
    color: var(--ink-mute);
    margin-bottom: 6px;
  }}
  .progress-bar {{
    height: 6px;
    background: var(--rule-soft);
    border-radius: 3px;
    overflow: hidden;
  }}
  .progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
    transition: width 0.3s;
    width: 0%;
  }}
  .save-status {{
    font-size: 11px;
    color: var(--ink-mute);
    font-family: 'JetBrains Mono', monospace;
  }}
  .save-status.saving {{ color: var(--amber); }}
  .save-status.saved {{ color: var(--green); }}
  .layout {{
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 0;
    max-width: 1400px;
    margin: 0 auto;
    min-height: calc(100vh - 85px);
  }}
  nav.sidebar {{
    border-right: 1px solid var(--rule);
    padding: 28px 20px 28px 32px;
    position: sticky;
    top: 85px;
    align-self: start;
    max-height: calc(100vh - 85px);
    overflow-y: auto;
  }}
  .sidebar-title {{
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--ink-mute);
    font-weight: 600;
    margin-bottom: 14px;
  }}
  .nav-item {{
    display: block;
    width: 100%;
    text-align: left;
    padding: 9px 12px;
    margin: 2px 0;
    background: none;
    border: none;
    font-family: inherit;
    font-size: 13.5px;
    color: var(--ink-soft);
    cursor: pointer;
    border-radius: 2px;
    border-left: 2px solid transparent;
    transition: background 0.15s, border-color 0.15s;
  }}
  .nav-item:hover {{
    background: var(--paper-2);
    color: var(--ink);
  }}
  .nav-item.active {{
    background: var(--paper-2);
    color: var(--ink);
    border-left-color: var(--accent);
    font-weight: 500;
  }}
  .nav-meta {{
    display: block;
    font-size: 11px;
    color: var(--ink-mute);
    margin-top: 2px;
    font-family: 'JetBrains Mono', monospace;
  }}
  .nav-complete-dot {{
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--green);
    margin-right: 6px;
    vertical-align: middle;
  }}
  main.content {{
    padding: 32px 56px 80px 48px;
    max-width: 900px;
  }}
  .section-header {{
    margin-bottom: 28px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--rule-soft);
  }}
  .section-title {{
    font-family: 'Fraunces', serif;
    font-size: 30px;
    font-weight: 500;
    letter-spacing: -0.015em;
    margin: 0 0 8px;
    line-height: 1.2;
  }}
  .section-desc {{
    color: var(--ink-soft);
    font-size: 14.5px;
    margin: 0;
    max-width: 680px;
  }}
  .section-count {{
    display: inline-block;
    margin-top: 12px;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-mute);
    font-family: 'JetBrains Mono', monospace;
  }}
  .item {{
    padding: 18px 22px;
    margin: 12px 0;
    background: white;
    border: 1px solid var(--rule-soft);
    border-radius: 3px;
    transition: border-color 0.15s;
  }}
  .item.answered-yes {{ border-left: 3px solid var(--green); }}
  .item.answered-no  {{ border-left: 3px solid var(--red); }}
  .item.answered-maybe {{ border-left: 3px solid var(--amber); }}
  .item-claim {{
    font-size: 15.5px;
    line-height: 1.5;
    color: var(--ink);
    margin-bottom: 4px;
  }}
  .item-claim b {{
    font-weight: 600;
    color: var(--accent);
  }}
  .item-context {{
    font-size: 12px;
    color: var(--ink-mute);
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.01em;
    margin-bottom: 14px;
  }}
  .radios {{
    display: flex;
    gap: 0;
    margin-bottom: 12px;
    border: 1px solid var(--rule);
    border-radius: 3px;
    overflow: hidden;
    width: fit-content;
  }}
  .radios label {{
    padding: 7px 16px;
    cursor: pointer;
    font-size: 13.5px;
    color: var(--ink-soft);
    background: white;
    border-right: 1px solid var(--rule);
    transition: all 0.12s;
    user-select: none;
  }}
  .radios label:last-child {{ border-right: none; }}
  .radios input {{ display: none; }}
  .radios label:hover {{ background: var(--paper-2); }}
  .radios input:checked + span {{ font-weight: 500; }}
  .radios label.sel-yes:has(input:checked)  {{ background: #DCFCE7; color: var(--green); }}
  .radios label.sel-no:has(input:checked)   {{ background: #FEE2E2; color: var(--red); }}
  .radios label.sel-maybe:has(input:checked){{ background: #FEF3C7; color: var(--amber); }}
  .comment {{
    width: 100%;
    padding: 8px 10px;
    border: 1px solid var(--rule);
    font-family: inherit;
    font-size: 13.5px;
    color: var(--ink);
    background: var(--paper);
    border-radius: 2px;
    min-height: 36px;
    resize: vertical;
  }}
  .comment:focus {{
    outline: 2px solid var(--accent);
    outline-offset: -1px;
    background: white;
  }}
  .comment::placeholder {{
    color: var(--ink-mute);
    font-style: italic;
  }}
  .footer-actions {{
    margin-top: 48px;
    padding: 24px;
    background: var(--paper-2);
    border-radius: 3px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
  }}
  .footer-info {{
    flex: 1;
    min-width: 280px;
    font-size: 13px;
    color: var(--ink-soft);
  }}
  .btn {{
    padding: 9px 18px;
    font-family: inherit;
    font-size: 13.5px;
    font-weight: 500;
    cursor: pointer;
    border-radius: 2px;
    border: 1px solid var(--rule);
    background: white;
    color: var(--ink);
    transition: all 0.15s;
  }}
  .btn:hover {{ background: var(--paper); border-color: var(--ink-soft); }}
  .btn-primary {{
    background: var(--ink);
    color: var(--paper);
    border-color: var(--ink);
  }}
  .btn-primary:hover {{
    background: var(--accent);
    border-color: var(--accent);
    color: white;
  }}
  .btn-danger {{
    color: var(--red);
    border-color: #FCA5A5;
  }}
  .btn-danger:hover {{
    background: #FEE2E2;
  }}
  .intro {{
    padding: 28px 32px;
    background: var(--paper-2);
    border-radius: 3px;
    margin-bottom: 24px;
    border-left: 3px solid var(--accent);
  }}
  .intro h2 {{
    font-family: 'Fraunces', serif;
    font-weight: 500;
    margin: 0 0 10px;
    font-size: 20px;
  }}
  .intro p {{ margin: 6px 0; font-size: 14px; color: var(--ink-soft); }}
  .intro ul {{ margin: 10px 0 0; padding-left: 22px; font-size: 14px; color: var(--ink-soft); }}
  .intro li {{ margin: 4px 0; }}
  .intro .highlight {{ color: var(--warm); font-weight: 500; }}
  @media (max-width: 900px) {{
    .layout {{ grid-template-columns: 1fr; }}
    nav.sidebar {{ position: relative; top: 0; border-right: none; border-bottom: 1px solid var(--rule); max-height: none; }}
    main.content {{ padding: 24px; }}
    .header-inner {{ flex-wrap: wrap; gap: 16px; }}
  }}
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="brand">
      Phiếu thẩm định Ontology
      <small>{subject_label} — Bản 0.1</small>
    </div>
    <div class="teacher-input">
      <label>Họ tên giáo viên (để ghi nhận)</label>
      <input type="text" id="teacher-name" placeholder="VD: Nguyễn Văn A — Trường THCS X">
    </div>
    <div class="progress-wrap">
      <div class="progress-label">
        <span><span id="done-count">0</span> / {total_items} câu đã trả lời</span>
        <span class="save-status" id="save-status">—</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
    </div>
  </div>
</header>

<div class="layout">
  <nav class="sidebar" id="sidebar"></nav>
  <main class="content" id="content"></main>
</div>

<script>
const DATA = {data_json};
const SUBJECT = "{subject_code}";
const STORAGE_KEY = "{subject_code}_verify_responses_v1";
const INTRO_NOTE = {intro_note};

function loadResponses() {{
  try {{
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  }} catch(e) {{}}
  return {{ teacher: '', responses: {{}} }};
}}

let state = loadResponses();

function saveResponses() {{
  const status = document.getElementById('save-status');
  status.textContent = 'saving...';
  status.className = 'save-status saving';
  try {{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    setTimeout(() => {{
      status.textContent = '✓ saved ' + new Date().toLocaleTimeString('vi-VN');
      status.className = 'save-status saved';
    }}, 180);
  }} catch(e) {{
    status.textContent = '✗ save error';
    status.className = 'save-status';
  }}
}}

function updateProgress() {{
  let total = 0, done = 0;
  DATA.forEach(s => {{
    s.items.forEach(it => {{
      total++;
      if (state.responses[it.id] && state.responses[it.id].verdict) done++;
    }});
  }});
  document.getElementById('done-count').textContent = done;
  document.getElementById('progress-fill').style.width = (total ? (done/total*100) : 0) + '%';
}}

function sectionCount(section) {{
  return section.items.filter(it => state.responses[it.id] && state.responses[it.id].verdict).length;
}}

let activeSection = DATA[0].id;

function renderSidebar() {{
  const nav = document.getElementById('sidebar');
  const html = ['<div class="sidebar-title">Các phần thẩm định</div>'];
  DATA.forEach(s => {{
    const done = sectionCount(s);
    const total = s.items.length;
    const complete = done === total;
    html.push(`<button class="nav-item ${{s.id===activeSection?'active':''}}" data-sec="${{s.id}}">
      ${{complete ? '<span class="nav-complete-dot"></span>' : ''}}${{s.title}}
      <span class="nav-meta">${{done}} / ${{total}}</span>
    </button>`);
  }});
  nav.innerHTML = html.join('');
  nav.querySelectorAll('.nav-item').forEach(b => {{
    b.addEventListener('click', () => {{
      activeSection = b.dataset.sec;
      renderSidebar();
      renderContent();
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }});
  }});
}}

function renderContent() {{
  const s = DATA.find(x => x.id === activeSection);
  const main = document.getElementById('content');
  const isFirst = DATA.indexOf(s) === 0;
  const intro = isFirst ? `
    <div class="intro">
      <h2>Hướng dẫn cho giáo viên</h2>
      <p>Đây là phiếu thẩm định tri thức của một ontology (bản đồ tri thức có cấu trúc) về môn {subject_vn},
      dùng cho nghiên cứu về ước lượng độ khó câu hỏi.</p>
      <p>${{INTRO_NOTE}}</p>
      <p>Mỗi mục là một <b>khẳng định</b> về kiến thức {subject_vn}. Thầy/cô đánh giá:</p>
      <ul>
        <li><b style="color: var(--green);">Đúng</b> — khẳng định chính xác theo SGK/thực tế</li>
        <li><b style="color: var(--red);">Sai</b> — khẳng định không đúng (ghi rõ lý do ở ô bình luận)</li>
        <li><b style="color: var(--amber);">Không chắc</b> — cần xem lại hoặc có thể đúng/sai tùy cách hiểu</li>
      </ul>
      <p class="highlight">💾 Câu trả lời được tự lưu vào trình duyệt. Có thể đóng tab và quay lại sau.</p>
      <p>Hoàn thành xong, bấm <b>Export JSON</b> ở cuối trang và gửi file cho người thu thập.</p>
    </div>
  ` : '';

  const items = s.items.map(it => {{
    const r = state.responses[it.id] || {{}};
    const cls = r.verdict === 'yes' ? 'answered-yes' :
                r.verdict === 'no' ? 'answered-no' :
                r.verdict === 'maybe' ? 'answered-maybe' : '';
    return `<div class="item ${{cls}}" data-id="${{it.id}}">
      <div class="item-claim">${{it.claim}}</div>
      <div class="item-context">${{it.context}}</div>
      <div class="radios">
        <label class="sel-yes"><input type="radio" name="v_${{it.id}}" value="yes" ${{r.verdict==='yes'?'checked':''}}><span>✓ Đúng</span></label>
        <label class="sel-no"><input type="radio" name="v_${{it.id}}" value="no" ${{r.verdict==='no'?'checked':''}}><span>✗ Sai</span></label>
        <label class="sel-maybe"><input type="radio" name="v_${{it.id}}" value="maybe" ${{r.verdict==='maybe'?'checked':''}}><span>? Không chắc</span></label>
      </div>
      <textarea class="comment" placeholder="Bình luận (không bắt buộc) — lý do sai, cần bổ sung, ghi chú..." data-id="${{it.id}}">${{r.comment || ''}}</textarea>
    </div>`;
  }}).join('');

  main.innerHTML = `
    ${{intro}}
    <div class="section-header">
      <h1 class="section-title">${{s.title}}</h1>
      <p class="section-desc">${{s.desc}}</p>
      <div class="section-count">${{s.items.length}} mục • ${{sectionCount(s)}} đã trả lời</div>
    </div>
    ${{items}}
    <div class="footer-actions">
      <div class="footer-info">
        <b>Hoàn thành</b> — Bấm Export để tải file JSON gửi lại cho người tổ chức.
        Có thể gửi file ngay cả khi chưa trả lời hết toàn bộ.
      </div>
      <button class="btn btn-primary" id="export-btn">📥 Export JSON</button>
      <button class="btn btn-danger" id="clear-btn">Xóa toàn bộ</button>
    </div>
  `;

  main.querySelectorAll('input[type="radio"]').forEach(r => {{
    r.addEventListener('change', e => {{
      const id = e.target.name.slice(2);
      state.responses[id] = state.responses[id] || {{}};
      state.responses[id].verdict = e.target.value;
      state.responses[id].ts = new Date().toISOString();
      saveResponses();
      updateProgress();
      renderSidebar();
      const item = e.target.closest('.item');
      item.classList.remove('answered-yes','answered-no','answered-maybe');
      item.classList.add('answered-' + e.target.value);
    }});
  }});

  let commentTimer;
  main.querySelectorAll('.comment').forEach(c => {{
    c.addEventListener('input', e => {{
      const id = e.target.dataset.id;
      state.responses[id] = state.responses[id] || {{}};
      state.responses[id].comment = e.target.value;
      clearTimeout(commentTimer);
      commentTimer = setTimeout(saveResponses, 400);
    }});
  }});

  document.getElementById('export-btn').addEventListener('click', exportJson);
  document.getElementById('clear-btn').addEventListener('click', () => {{
    if (confirm('Xóa toàn bộ câu trả lời? Không thể hoàn tác.')) {{
      state = {{ teacher: document.getElementById('teacher-name').value, responses: {{}} }};
      saveResponses();
      updateProgress();
      renderSidebar();
      renderContent();
    }}
  }});
}}

function exportJson() {{
  const teacher = document.getElementById('teacher-name').value.trim() || 'anonymous';
  state.teacher = teacher;
  const payload = {{
    subject: SUBJECT,
    ontology_version: SUBJECT + ' v0.1',
    teacher: teacher,
    exported_at: new Date().toISOString(),
    summary: {{
      total_items: DATA.reduce((a,s) => a + s.items.length, 0),
      answered: Object.values(state.responses).filter(r => r.verdict).length,
      by_verdict: {{
        yes: Object.values(state.responses).filter(r => r.verdict === 'yes').length,
        no: Object.values(state.responses).filter(r => r.verdict === 'no').length,
        maybe: Object.values(state.responses).filter(r => r.verdict === 'maybe').length,
      }},
    }},
    responses: state.responses,
  }};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const safe = teacher.replace(/[^a-zA-Z0-9_.-]/g, '_').slice(0, 40) || 'anon';
  a.href = url;
  a.download = SUBJECT + '_review_' + safe + '_' + new Date().toISOString().slice(0,10) + '.json';
  a.click();
  URL.revokeObjectURL(url);
}}

document.getElementById('teacher-name').addEventListener('input', e => {{
  state.teacher = e.target.value;
  saveResponses();
}});
document.getElementById('teacher-name').value = state.teacher || '';

renderSidebar();
renderContent();
updateProgress();
</script>
</body>
</html>
'''


# Accent color palette per subject
ACCENTS = {
    'geo9':  ('#556B2F', '#879F52'),   # olive green (for Địa)
    'math9': ('#4A5D8F', '#7A93BD'),   # deep blue (for Toán)
    'chem9': ('#8B2D4F', '#B8547A'),   # burgundy (for Hóa)
    'su9':   ('#7A4B2F', '#A67B5B'),   # warm brown (for Sử)
}


def generate_form(
    subject_code,       # 'math9', 'chem9', etc.
    subject_label,      # 'TOÁN 9' — displayed in header
    subject_vn,         # 'Toán lớp 9' — displayed in intro prose
    title,              # full page title
    sections,           # list of {id, title, desc, items: [{id, claim, context}]}
    intro_note="",      # extra intro paragraph (subject-specific guidance)
):
    total_items = sum(len(s['items']) for s in sections)
    accent, accent2 = ACCENTS.get(subject_code, ('#556B2F', '#879F52'))

    return FORM_TEMPLATE.format(
        title=title,
        subject_label=subject_label,
        subject_code=subject_code,
        subject_vn=subject_vn,
        total_items=total_items,
        data_json=json.dumps(sections, ensure_ascii=False),
        intro_note=json.dumps(intro_note, ensure_ascii=False),
        accent=accent,
        accent2=accent2,
    )


DIFFICULTY_FORM_TEMPLATE = '''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --paper:      #FAF7F2;
    --paper-2:    #F3EEE4;
    --ink:        #1A1D1E;
    --ink-soft:   #4A4F52;
    --ink-mute:   #8B8E90;
    --rule:       #D9D2C4;
    --rule-soft:  #E8E3D6;
    --accent:     {accent};
    --accent-2:   {accent2};
    --warm:       #C2410C;
    --easy:       #15803D;
    --medium:     #92400E;
    --hard:       #991B1B;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    background: var(--paper);
    color: var(--ink);
    font-family: 'IBM Plex Sans', -apple-system, sans-serif;
    font-size: 15px;
    line-height: 1.55;
    min-height: 100vh;
  }}
  header {{
    background: var(--paper);
    border-bottom: 1px solid var(--rule);
    padding: 22px 32px;
    position: sticky; top: 0;
    z-index: 50;
    backdrop-filter: blur(6px);
  }}
  .header-inner {{
    display: flex; align-items: center; gap: 32px;
    max-width: 1400px; margin: 0 auto;
  }}
  .brand {{
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 500;
    font-size: 22px;
    letter-spacing: -0.01em;
    line-height: 1.1;
  }}
  .brand small {{
    display: block;
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 400;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-mute);
    margin-top: 2px;
  }}
  .teacher-input {{ flex: 1; max-width: 340px; }}
  .teacher-input label {{
    display: block; font-size: 10px; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--ink-mute); margin-bottom: 4px;
  }}
  .teacher-input input {{
    width: 100%; padding: 6px 10px; border: 1px solid var(--rule);
    background: white; font-family: inherit; font-size: 14px;
    color: var(--ink); border-radius: 2px;
  }}
  .teacher-input input:focus {{ outline: 2px solid var(--accent); outline-offset: -1px; }}
  .progress-wrap {{ flex: 1; max-width: 320px; }}
  .progress-label {{
    display: flex; justify-content: space-between; font-size: 11px;
    letter-spacing: 0.05em; color: var(--ink-mute); margin-bottom: 6px;
  }}
  .progress-bar {{ height: 6px; background: var(--rule-soft); border-radius: 3px; overflow: hidden; }}
  .progress-fill {{
    height: 100%; background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
    transition: width 0.3s; width: 0%;
  }}
  .save-status {{ font-size: 11px; color: var(--ink-mute); font-family: 'JetBrains Mono', monospace; }}
  .save-status.saving {{ color: var(--medium); }}
  .save-status.saved {{ color: var(--easy); }}
  .layout {{
    display: grid; grid-template-columns: 300px 1fr; gap: 0;
    max-width: 1400px; margin: 0 auto; min-height: calc(100vh - 85px);
  }}
  nav.sidebar {{
    border-right: 1px solid var(--rule); padding: 28px 20px 28px 32px;
    position: sticky; top: 85px; align-self: start;
    max-height: calc(100vh - 85px); overflow-y: auto;
  }}
  .sidebar-title {{
    font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--ink-mute); font-weight: 600; margin-bottom: 14px;
  }}
  .nav-item {{
    display: block; width: 100%; text-align: left; padding: 9px 12px; margin: 2px 0;
    background: none; border: none; font-family: inherit; font-size: 13.5px;
    color: var(--ink-soft); cursor: pointer; border-radius: 2px;
    border-left: 2px solid transparent; transition: background 0.15s, border-color 0.15s;
  }}
  .nav-item:hover {{ background: var(--paper-2); color: var(--ink); }}
  .nav-item.active {{
    background: var(--paper-2); color: var(--ink);
    border-left-color: var(--accent); font-weight: 500;
  }}
  .nav-meta {{
    display: block; font-size: 11px; color: var(--ink-mute);
    margin-top: 2px; font-family: 'JetBrains Mono', monospace;
  }}
  .nav-complete-dot {{
    display: inline-block; width: 6px; height: 6px; border-radius: 50%;
    background: var(--easy); margin-right: 6px; vertical-align: middle;
  }}
  main.content {{ padding: 32px 56px 80px 48px; max-width: 900px; }}
  .section-header {{
    margin-bottom: 28px; padding-bottom: 16px; border-bottom: 1px solid var(--rule-soft);
  }}
  .section-title {{
    font-family: 'Fraunces', serif; font-size: 30px; font-weight: 500;
    letter-spacing: -0.015em; margin: 0 0 8px; line-height: 1.2;
  }}
  .section-desc {{ color: var(--ink-soft); font-size: 14.5px; margin: 0; max-width: 680px; }}
  .section-count {{
    display: inline-block; margin-top: 12px; font-size: 11px; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--ink-mute); font-family: 'JetBrains Mono', monospace;
  }}
  .item {{
    padding: 18px 22px; margin: 12px 0; background: white;
    border: 1px solid var(--rule-soft); border-radius: 3px; transition: border-color 0.15s;
  }}
  .item.answered-easy   {{ border-left: 3px solid var(--easy); }}
  .item.answered-medium {{ border-left: 3px solid var(--medium); }}
  .item.answered-hard   {{ border-left: 3px solid var(--hard); }}
  .item-stem {{ font-size: 15.5px; line-height: 1.5; color: var(--ink); margin-bottom: 10px; font-weight: 500; }}
  .item-options {{ margin-bottom: 12px; }}
  .item-option {{
    display: flex; gap: 8px; padding: 5px 0; font-size: 14px; color: var(--ink-soft);
  }}
  .item-option .letter {{ font-family: 'JetBrains Mono', monospace; color: var(--ink-mute); flex-shrink: 0; }}
  .item-option.is-correct {{ color: var(--ink); font-weight: 500; }}
  .item-option.is-correct .letter {{ color: var(--easy); }}
  .item-option .correct-tag {{
    font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase;
    color: var(--easy); border: 1px solid var(--easy); border-radius: 2px;
    padding: 1px 5px; margin-left: 6px;
  }}
  .item-context {{
    font-size: 12px; color: var(--ink-mute); font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.01em; margin-bottom: 14px;
  }}
  .radios {{
    display: flex; gap: 0; margin-bottom: 12px; border: 1px solid var(--rule);
    border-radius: 3px; overflow: hidden; width: fit-content;
  }}
  .radios label {{
    padding: 7px 16px; cursor: pointer; font-size: 13.5px; color: var(--ink-soft);
    background: white; border-right: 1px solid var(--rule); transition: all 0.12s; user-select: none;
  }}
  .radios label:last-child {{ border-right: none; }}
  .radios input {{ display: none; }}
  .radios label:hover {{ background: var(--paper-2); }}
  .radios input:checked + span {{ font-weight: 500; }}
  .radios label.sel-easy:has(input:checked)   {{ background: #DCFCE7; color: var(--easy); }}
  .radios label.sel-medium:has(input:checked) {{ background: #FEF3C7; color: var(--medium); }}
  .radios label.sel-hard:has(input:checked)   {{ background: #FEE2E2; color: var(--hard); }}
  .comment {{
    width: 100%; padding: 8px 10px; border: 1px solid var(--rule); font-family: inherit;
    font-size: 13.5px; color: var(--ink); background: var(--paper); border-radius: 2px;
    min-height: 36px; resize: vertical;
  }}
  .comment:focus {{ outline: 2px solid var(--accent); outline-offset: -1px; background: white; }}
  .comment::placeholder {{ color: var(--ink-mute); font-style: italic; }}
  .footer-actions {{
    margin-top: 48px; padding: 24px; background: var(--paper-2); border-radius: 3px;
    display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
  }}
  .footer-info {{ flex: 1; min-width: 280px; font-size: 13px; color: var(--ink-soft); }}
  .btn {{
    padding: 9px 18px; font-family: inherit; font-size: 13.5px; font-weight: 500;
    cursor: pointer; border-radius: 2px; border: 1px solid var(--rule);
    background: white; color: var(--ink); transition: all 0.15s;
  }}
  .btn:hover {{ background: var(--paper); border-color: var(--ink-soft); }}
  .btn-primary {{ background: var(--ink); color: var(--paper); border-color: var(--ink); }}
  .btn-primary:hover {{ background: var(--accent); border-color: var(--accent); color: white; }}
  .btn-danger {{ color: var(--hard); border-color: #FCA5A5; }}
  .btn-danger:hover {{ background: #FEE2E2; }}
  .intro {{
    padding: 28px 32px; background: var(--paper-2); border-radius: 3px;
    margin-bottom: 24px; border-left: 3px solid var(--accent);
  }}
  .intro h2 {{ font-family: 'Fraunces', serif; font-weight: 500; margin: 0 0 10px; font-size: 20px; }}
  .intro p {{ margin: 6px 0; font-size: 14px; color: var(--ink-soft); }}
  .intro ul {{ margin: 10px 0 0; padding-left: 22px; font-size: 14px; color: var(--ink-soft); }}
  .intro li {{ margin: 4px 0; }}
  .intro .highlight {{ color: var(--warm); font-weight: 500; }}
  @media (max-width: 900px) {{
    .layout {{ grid-template-columns: 1fr; }}
    nav.sidebar {{ position: relative; top: 0; border-right: none; border-bottom: 1px solid var(--rule); max-height: none; }}
    main.content {{ padding: 24px; }}
    .header-inner {{ flex-wrap: wrap; gap: 16px; }}
  }}
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="brand">
      Phiếu chấm độ khó câu hỏi
      <small>{subject_label} — khảo sát đối chiếu p-value</small>
    </div>
    <div class="teacher-input">
      <label>Họ tên giáo viên (để ghi nhận)</label>
      <input type="text" id="teacher-name" placeholder="VD: Nguyễn Văn A — Trường THCS X">
    </div>
    <div class="progress-wrap">
      <div class="progress-label">
        <span><span id="done-count">0</span> / {total_items} câu đã chấm</span>
        <span class="save-status" id="save-status">—</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
    </div>
  </div>
</header>

<div class="layout">
  <nav class="sidebar" id="sidebar"></nav>
  <main class="content" id="content"></main>
</div>

<script>
const DATA = {data_json};
const SUBJECT = "{subject_code}";
const STORAGE_KEY = "{subject_code}_difficulty_responses_v1";
const INTRO_NOTE = {intro_note};

function loadResponses() {{
  try {{
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  }} catch(e) {{}}
  return {{ teacher: '', responses: {{}} }};
}}

let state = loadResponses();

function saveResponses() {{
  const status = document.getElementById('save-status');
  status.textContent = 'saving...';
  status.className = 'save-status saving';
  try {{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    setTimeout(() => {{
      status.textContent = '✓ saved ' + new Date().toLocaleTimeString('vi-VN');
      status.className = 'save-status saved';
    }}, 180);
  }} catch(e) {{
    status.textContent = '✗ save error';
    status.className = 'save-status';
  }}
}}

function updateProgress() {{
  let total = 0, done = 0;
  DATA.forEach(s => {{
    s.items.forEach(it => {{
      total++;
      if (state.responses[it.id] && state.responses[it.id].verdict) done++;
    }});
  }});
  document.getElementById('done-count').textContent = done;
  document.getElementById('progress-fill').style.width = (total ? (done/total*100) : 0) + '%';
}}

function sectionCount(section) {{
  return section.items.filter(it => state.responses[it.id] && state.responses[it.id].verdict).length;
}}

let activeSection = DATA[0].id;

function renderSidebar() {{
  const nav = document.getElementById('sidebar');
  const html = ['<div class="sidebar-title">Các phần chấm</div>'];
  DATA.forEach(s => {{
    const done = sectionCount(s);
    const total = s.items.length;
    const complete = done === total;
    html.push(`<button class="nav-item ${{s.id===activeSection?'active':''}}" data-sec="${{s.id}}">
      ${{complete ? '<span class="nav-complete-dot"></span>' : ''}}${{s.title}}
      <span class="nav-meta">${{done}} / ${{total}}</span>
    </button>`);
  }});
  nav.innerHTML = html.join('');
  nav.querySelectorAll('.nav-item').forEach(b => {{
    b.addEventListener('click', () => {{
      activeSection = b.dataset.sec;
      renderSidebar();
      renderContent();
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }});
  }});
}}

function renderContent() {{
  const s = DATA.find(x => x.id === activeSection);
  const main = document.getElementById('content');
  const isFirst = DATA.indexOf(s) === 0;
  const intro = isFirst ? `
    <div class="intro">
      <h2>Hướng dẫn cho giáo viên</h2>
      <p>Đây là phiếu chấm ĐỘ KHÓ cho một bộ câu hỏi trắc nghiệm {subject_vn}, dùng làm
      nguồn nhãn thứ ba (bên cạnh nhãn AI và tỉ lệ trả lời đúng thật của học sinh) cho nghiên cứu
      về ước lượng độ khó câu hỏi.</p>
      <p>${{INTRO_NOTE}}</p>
      <p>Với MỖI câu, đọc đề + 4 phương án (đáp án đúng được đánh dấu ✓ để thầy/cô tham chiếu),
      rồi đánh giá ĐỘ KHÓ đối với học sinh lớp 9 trung bình:</p>
      <ul>
        <li><b style="color: var(--easy);">Dễ</b> — đa số học sinh trả lời đúng, kiến thức cơ bản/trực tiếp trong SGK</li>
        <li><b style="color: var(--medium);">Trung bình</b> — cần suy luận hoặc nhớ chi tiết, một bộ phận học sinh sẽ sai</li>
        <li><b style="color: var(--hard);">Khó</b> — đòi hỏi so sánh/phân tích sâu hoặc kiến thức ít trọng tâm, đa số dễ nhầm</li>
      </ul>
      <p class="highlight">💾 Câu trả lời được tự lưu vào trình duyệt. Có thể đóng tab và quay lại sau.</p>
      <p>Hoàn thành xong, bấm <b>Export JSON</b> ở cuối trang và gửi file cho người thu thập.</p>
    </div>
  ` : '';

  const items = s.items.map(it => {{
    const r = state.responses[it.id] || {{}};
    const cls = r.verdict === 'easy' ? 'answered-easy' :
                r.verdict === 'medium' ? 'answered-medium' :
                r.verdict === 'hard' ? 'answered-hard' : '';
    const opts = it.options.map(o => `<div class="item-option ${{o.is_correct ? 'is-correct' : ''}}">
        <span class="letter">${{o.letter}}.</span><span>${{o.text}}</span>
        ${{o.is_correct ? '<span class="correct-tag">✓ đáp án đúng</span>' : ''}}
      </div>`).join('');
    return `<div class="item ${{cls}}" data-id="${{it.id}}">
      <div class="item-stem">${{it.stem}}</div>
      <div class="item-options">${{opts}}</div>
      ${{it.context ? `<div class="item-context">${{it.context}}</div>` : ''}}
      <div class="radios">
        <label class="sel-easy"><input type="radio" name="v_${{it.id}}" value="easy" ${{r.verdict==='easy'?'checked':''}}><span>Dễ</span></label>
        <label class="sel-medium"><input type="radio" name="v_${{it.id}}" value="medium" ${{r.verdict==='medium'?'checked':''}}><span>Trung bình</span></label>
        <label class="sel-hard"><input type="radio" name="v_${{it.id}}" value="hard" ${{r.verdict==='hard'?'checked':''}}><span>Khó</span></label>
      </div>
      <textarea class="comment" placeholder="Bình luận (không bắt buộc) — vì sao khó/dễ, câu có vấn đề..." data-id="${{it.id}}">${{r.comment || ''}}</textarea>
    </div>`;
  }}).join('');

  main.innerHTML = `
    ${{intro}}
    <div class="section-header">
      <h1 class="section-title">${{s.title}}</h1>
      <p class="section-desc">${{s.desc}}</p>
      <div class="section-count">${{s.items.length}} câu • ${{sectionCount(s)}} đã chấm</div>
    </div>
    ${{items}}
    <div class="footer-actions">
      <div class="footer-info">
        <b>Hoàn thành</b> — Bấm Export để tải file JSON gửi lại cho người tổ chức.
        Có thể gửi file ngay cả khi chưa chấm hết toàn bộ.
      </div>
      <button class="btn btn-primary" id="export-btn">📥 Export JSON</button>
      <button class="btn btn-danger" id="clear-btn">Xóa toàn bộ</button>
    </div>
  `;

  main.querySelectorAll('input[type="radio"]').forEach(r => {{
    r.addEventListener('change', e => {{
      const id = e.target.name.slice(2);
      state.responses[id] = state.responses[id] || {{}};
      state.responses[id].verdict = e.target.value;
      state.responses[id].ts = new Date().toISOString();
      saveResponses();
      updateProgress();
      renderSidebar();
      const item = e.target.closest('.item');
      item.classList.remove('answered-easy','answered-medium','answered-hard');
      item.classList.add('answered-' + e.target.value);
    }});
  }});

  let commentTimer;
  main.querySelectorAll('.comment').forEach(c => {{
    c.addEventListener('input', e => {{
      const id = e.target.dataset.id;
      state.responses[id] = state.responses[id] || {{}};
      state.responses[id].comment = e.target.value;
      clearTimeout(commentTimer);
      commentTimer = setTimeout(saveResponses, 400);
    }});
  }});

  document.getElementById('export-btn').addEventListener('click', exportJson);
  document.getElementById('clear-btn').addEventListener('click', () => {{
    if (confirm('Xóa toàn bộ câu trả lời? Không thể hoàn tác.')) {{
      state = {{ teacher: document.getElementById('teacher-name').value, responses: {{}} }};
      saveResponses();
      updateProgress();
      renderSidebar();
      renderContent();
    }}
  }});
}}

function exportJson() {{
  const teacher = document.getElementById('teacher-name').value.trim() || 'anonymous';
  state.teacher = teacher;
  const payload = {{
    subject: SUBJECT,
    teacher: teacher,
    exported_at: new Date().toISOString(),
    summary: {{
      total_items: DATA.reduce((a,s) => a + s.items.length, 0),
      answered: Object.values(state.responses).filter(r => r.verdict).length,
      by_verdict: {{
        easy: Object.values(state.responses).filter(r => r.verdict === 'easy').length,
        medium: Object.values(state.responses).filter(r => r.verdict === 'medium').length,
        hard: Object.values(state.responses).filter(r => r.verdict === 'hard').length,
      }},
    }},
    responses: state.responses,
  }};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const safe = teacher.replace(/[^a-zA-Z0-9_.-]/g, '_').slice(0, 40) || 'anon';
  a.href = url;
  a.download = SUBJECT + '_difficulty_' + safe + '_' + new Date().toISOString().slice(0,10) + '.json';
  a.click();
  URL.revokeObjectURL(url);
}}

document.getElementById('teacher-name').addEventListener('input', e => {{
  state.teacher = e.target.value;
  saveResponses();
}});
document.getElementById('teacher-name').value = state.teacher || '';

renderSidebar();
renderContent();
updateProgress();
</script>
</body>
</html>
'''


def generate_difficulty_form(
    subject_code,       # 'su9'
    subject_label,      # 'LỊCH SỬ 9'
    subject_vn,         # 'Lịch sử lớp 9'
    title,              # full page title
    sections,           # list of {id, title, desc, items: [{id, stem, context, options:[{letter,text,is_correct}]}]}
    intro_note="",      # extra intro paragraph (subject-specific guidance)
):
    """Sinh form HTML để giáo viên chấm Dễ/Trung bình/Khó cho một bộ MCQ —
    nguồn nhãn thứ 3 (T7 trong kế hoạch Cold->Warm), độc lập với nhãn LLM và
    p-value thực nghiệm. KHÔNG được đưa nhãn LLM vào `sections` — lộ nhãn LLM
    cho giáo viên sẽ làm hỏng tính độc lập của nguồn nhãn thứ 3 này."""
    total_items = sum(len(s['items']) for s in sections)
    accent, accent2 = ACCENTS.get(subject_code, ('#556B2F', '#879F52'))

    return DIFFICULTY_FORM_TEMPLATE.format(
        title=title,
        subject_label=subject_label,
        subject_code=subject_code,
        subject_vn=subject_vn,
        total_items=total_items,
        data_json=json.dumps(sections, ensure_ascii=False),
        intro_note=json.dumps(intro_note, ensure_ascii=False),
        accent=accent,
        accent2=accent2,
    )


def generate_difficulty_apps_script(subject_label, subject_code, items_by_section, total_items):
    """Generate Google Apps Script that creates a difficulty-rating Form.

    items_by_section: dict of section_name -> list of {stem, options:[(letter,text,is_correct)]}
    """
    gs_lines = [f'''/**
 * Google Apps Script: Tao Google Form cham do kho MCQ {subject_label}
 *
 * CACH DUNG: giong het form tham dinh ontology — xem huong dan trong file
 * do (Extensions > Apps Script > dan file nay > Run > createForm).
 */

function createForm() {{
  var form = FormApp.create("Phieu cham do kho cau hoi {subject_label}");

  form.setTitle("Phieu cham do kho cau hoi {subject_label}");
  form.setDescription(
    "Cam on thay/co tham gia cham do kho!\\n\\n" +
    "Voi MOI cau hoi, doc de + 4 phuong an (dap an dung duoc ghi trong ngoac), " +
    "roi danh gia DO KHO doi voi hoc sinh lop 9 trung binh: De / Trung binh / Kho.\\n\\n" +
    "Tong cong co khoang {total_items} cau."
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(true);
  form.setShowLinkToRespondAgain(false);

  form.addTextItem()
    .setTitle("Ho ten giao vien")
    .setRequired(true);

  form.addTextItem()
    .setTitle("Truong / don vi cong tac")
    .setRequired(false);
''']

    for sec_name, items in items_by_section.items():
        gs_lines.append(f'\n  // --- SECTION: {sec_name} ---')
        gs_lines.append(f'  form.addPageBreakItem()\n'
                        f'    .setTitle({json.dumps(sec_name, ensure_ascii=False)});')
        for it in items:
            opts_txt = " | ".join(
                f"{letter}. {text}" + (" (DAP AN DUNG)" if is_correct else "")
                for letter, text, is_correct in it['options'])
            full_q = it['stem'] + "\n" + opts_txt
            gs_lines.append(f'  form.addMultipleChoiceItem()\n'
                            f'    .setTitle({json.dumps(full_q, ensure_ascii=False)})\n'
                            f'    .setChoiceValues(["De", "Trung binh", "Kho"])\n'
                            f'    .setRequired(false);')

    gs_lines.append(f'''
  var ss = SpreadsheetApp.create("Phieu cham do kho {subject_label} — Responses");
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log("Form da tao thanh cong!");
  Logger.log("PUBLISHED URL: " + form.getPublishedUrl());
  Logger.log("EDIT URL: " + form.getEditUrl());
  Logger.log("RESPONSE SHEET: " + ss.getUrl());
}}
''')

    return '\n'.join(gs_lines)


SELF_ASSESS_TEMPLATE = '''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --paper: #FAF7F2; --paper-2: #F3EEE4; --ink: #1A1D1E; --ink-soft: #4A4F52;
    --ink-mute: #8B8E90; --rule: #D9D2C4; --rule-soft: #E8E3D6;
    --accent: {accent}; --accent-2: {accent2};
    --easy: #15803D; --medium: #92400E; --hard: #991B1B; --pick: #1D4ED8;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{ background: var(--paper); color: var(--ink); font-family: 'IBM Plex Sans', -apple-system, sans-serif; font-size: 15px; line-height: 1.55; min-height: 100vh; }}
  header {{ background: var(--paper); border-bottom: 1px solid var(--rule); padding: 22px 32px; position: sticky; top: 0; z-index: 50; backdrop-filter: blur(6px); }}
  .header-inner {{ display: flex; align-items: center; gap: 32px; max-width: 1400px; margin: 0 auto; flex-wrap: wrap; }}
  .brand {{ font-family: 'Fraunces', Georgia, serif; font-weight: 500; font-size: 22px; letter-spacing: -0.01em; line-height: 1.1; }}
  .brand small {{ display: block; font-family: 'IBM Plex Sans', sans-serif; font-weight: 400; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-mute); margin-top: 2px; }}
  .rater-input {{ flex: 1; max-width: 300px; }}
  .rater-input label {{ display: block; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-mute); margin-bottom: 4px; }}
  .rater-input input {{ width: 100%; padding: 6px 10px; border: 1px solid var(--rule); background: white; font-family: inherit; font-size: 14px; color: var(--ink); border-radius: 2px; }}
  .rater-input input:focus {{ outline: 2px solid var(--accent); outline-offset: -1px; }}
  .progress-wrap {{ flex: 1; max-width: 320px; }}
  .progress-label {{ display: flex; justify-content: space-between; font-size: 11px; letter-spacing: 0.05em; color: var(--ink-mute); margin-bottom: 6px; }}
  .progress-bar {{ height: 6px; background: var(--rule-soft); border-radius: 3px; overflow: hidden; }}
  .progress-fill {{ height: 100%; background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%); transition: width 0.3s; width: 0%; }}
  .save-status {{ font-size: 11px; color: var(--ink-mute); font-family: 'JetBrains Mono', monospace; }}
  .save-status.saving {{ color: var(--medium); }}
  .save-status.saved {{ color: var(--easy); }}
  .layout {{ display: grid; grid-template-columns: 300px 1fr; gap: 0; max-width: 1400px; margin: 0 auto; min-height: calc(100vh - 85px); }}
  nav.sidebar {{ border-right: 1px solid var(--rule); padding: 28px 20px 28px 32px; position: sticky; top: 85px; align-self: start; max-height: calc(100vh - 85px); overflow-y: auto; }}
  .sidebar-title {{ font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-mute); font-weight: 600; margin-bottom: 14px; }}
  .nav-item {{ display: block; width: 100%; text-align: left; padding: 9px 12px; margin: 2px 0; background: none; border: none; font-family: inherit; font-size: 13.5px; color: var(--ink-soft); cursor: pointer; border-radius: 2px; border-left: 2px solid transparent; transition: background 0.15s, border-color 0.15s; }}
  .nav-item:hover {{ background: var(--paper-2); color: var(--ink); }}
  .nav-item.active {{ background: var(--paper-2); color: var(--ink); border-left-color: var(--accent); font-weight: 500; }}
  .nav-meta {{ display: block; font-size: 11px; color: var(--ink-mute); margin-top: 2px; font-family: 'JetBrains Mono', monospace; }}
  .nav-complete-dot {{ display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--easy); margin-right: 6px; vertical-align: middle; }}
  main.content {{ padding: 32px 56px 80px 48px; max-width: 900px; }}
  .section-header {{ margin-bottom: 28px; padding-bottom: 16px; border-bottom: 1px solid var(--rule-soft); }}
  .section-title {{ font-family: 'Fraunces', serif; font-size: 30px; font-weight: 500; letter-spacing: -0.015em; margin: 0 0 8px; line-height: 1.2; }}
  .section-desc {{ color: var(--ink-soft); font-size: 14.5px; margin: 0; max-width: 680px; }}
  .section-count {{ display: inline-block; margin-top: 12px; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-mute); font-family: 'JetBrains Mono', monospace; }}
  .item {{ padding: 18px 22px; margin: 12px 0; background: white; border: 1px solid var(--rule-soft); border-radius: 3px; transition: border-color 0.15s; }}
  .item.done {{ border-left: 3px solid var(--easy); }}
  .item.partial {{ border-left: 3px solid var(--medium); }}
  .item-stem {{ font-size: 15.5px; line-height: 1.5; color: var(--ink); margin-bottom: 10px; font-weight: 500; }}
  .step-label {{ font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-mute); margin: 12px 0 6px; }}
  .options {{ display: flex; flex-direction: column; gap: 4px; margin-bottom: 4px; }}
  .opt-label {{ display: flex; gap: 8px; padding: 6px 10px; border: 1px solid var(--rule); border-radius: 3px; cursor: pointer; font-size: 14px; color: var(--ink-soft); background: white; transition: all 0.12s; }}
  .opt-label:hover {{ background: var(--paper-2); }}
  .opt-label input {{ display: none; }}
  .opt-label .letter {{ font-family: 'JetBrains Mono', monospace; color: var(--ink-mute); flex-shrink: 0; }}
  .opt-label:has(input:checked) {{ background: #DBEAFE; border-color: var(--pick); color: var(--ink); font-weight: 500; }}
  .opt-label:has(input:checked) .letter {{ color: var(--pick); }}
  .radios {{ display: flex; gap: 0; margin-bottom: 4px; border: 1px solid var(--rule); border-radius: 3px; overflow: hidden; width: fit-content; }}
  .radios label {{ padding: 7px 16px; cursor: pointer; font-size: 13.5px; color: var(--ink-soft); background: white; border-right: 1px solid var(--rule); transition: all 0.12s; user-select: none; }}
  .radios label:last-child {{ border-right: none; }}
  .radios input {{ display: none; }}
  .radios label:hover {{ background: var(--paper-2); }}
  .radios label.sel-easy:has(input:checked)   {{ background: #DCFCE7; color: var(--easy); font-weight: 500; }}
  .radios label.sel-medium:has(input:checked) {{ background: #FEF3C7; color: var(--medium); font-weight: 500; }}
  .radios label.sel-hard:has(input:checked)   {{ background: #FEE2E2; color: var(--hard); font-weight: 500; }}
  .footer-actions {{ margin-top: 48px; padding: 24px; background: var(--paper-2); border-radius: 3px; display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }}
  .footer-info {{ flex: 1; min-width: 280px; font-size: 13px; color: var(--ink-soft); }}
  .btn {{ padding: 9px 18px; font-family: inherit; font-size: 13.5px; font-weight: 500; cursor: pointer; border-radius: 2px; border: 1px solid var(--rule); background: white; color: var(--ink); transition: all 0.15s; }}
  .btn:hover {{ background: var(--paper); border-color: var(--ink-soft); }}
  .btn-primary {{ background: var(--ink); color: var(--paper); border-color: var(--ink); }}
  .btn-primary:hover {{ background: var(--accent); border-color: var(--accent); color: white; }}
  .btn-danger {{ color: var(--hard); border-color: #FCA5A5; }}
  .btn-danger:hover {{ background: #FEE2E2; }}
  .intro {{ padding: 28px 32px; background: var(--paper-2); border-radius: 3px; margin-bottom: 24px; border-left: 3px solid var(--accent); }}
  .intro h2 {{ font-family: 'Fraunces', serif; font-weight: 500; margin: 0 0 10px; font-size: 20px; }}
  .intro p {{ margin: 6px 0; font-size: 14px; color: var(--ink-soft); }}
  .intro .highlight {{ color: var(--warm, #C2410C); font-weight: 500; }}
  @media (max-width: 900px) {{
    .layout {{ grid-template-columns: 1fr; }}
    nav.sidebar {{ position: relative; top: 0; border-right: none; border-bottom: 1px solid var(--rule); max-height: none; }}
    main.content {{ padding: 24px; }}
  }}
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="brand">Tự làm bài + tự chấm độ khó<small>{subject_label} — không cần Google Form, lưu ngay trên máy</small></div>
    <div class="rater-input">
      <label>Mã người đánh giá (tên/nickname)</label>
      <input type="text" id="rater-id" placeholder="VD: minh, an_dhbk...">
    </div>
    <div class="progress-wrap">
      <div class="progress-label"><span><span id="done-count">0</span> / {total_items} câu xong CẢ HAI bước</span><span class="save-status" id="save-status">—</span></div>
      <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
    </div>
  </div>
</header>

<div class="layout">
  <nav class="sidebar" id="sidebar"></nav>
  <main class="content" id="content"></main>
</div>

<script>
const DATA = {data_json};
const SUBJECT = "{subject_code}";
const STORAGE_KEY = "{subject_code}_self_assess_v1";
const INTRO_NOTE = {intro_note};

function loadResponses() {{
  try {{ const raw = localStorage.getItem(STORAGE_KEY); if (raw) return JSON.parse(raw); }} catch(e) {{}}
  return {{ rater: '', responses: {{}} }};
}}
let state = loadResponses();

function saveResponses() {{
  const status = document.getElementById('save-status');
  status.textContent = 'saving...'; status.className = 'save-status saving';
  try {{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    setTimeout(() => {{ status.textContent = '✓ saved ' + new Date().toLocaleTimeString('vi-VN'); status.className = 'save-status saved'; }}, 180);
  }} catch(e) {{ status.textContent = '✗ save error'; status.className = 'save-status'; }}
}}

function isDone(r) {{ return r && r.answer && r.verdict; }}
function isPartial(r) {{ return r && (r.answer || r.verdict) && !isDone(r); }}

function updateProgress() {{
  let total = 0, done = 0;
  DATA.forEach(s => s.items.forEach(it => {{ total++; if (isDone(state.responses[it.id])) done++; }}));
  document.getElementById('done-count').textContent = done;
  document.getElementById('progress-fill').style.width = (total ? (done/total*100) : 0) + '%';
}}
function sectionCount(section) {{ return section.items.filter(it => isDone(state.responses[it.id])).length; }}

let activeSection = DATA[0].id;

function renderSidebar() {{
  const nav = document.getElementById('sidebar');
  const html = ['<div class="sidebar-title">Các nhóm câu</div>'];
  DATA.forEach(s => {{
    const done = sectionCount(s), total = s.items.length, complete = done === total;
    html.push(`<button class="nav-item ${{s.id===activeSection?'active':''}}" data-sec="${{s.id}}">
      ${{complete ? '<span class="nav-complete-dot"></span>' : ''}}${{s.title}}
      <span class="nav-meta">${{done}} / ${{total}}</span></button>`);
  }});
  nav.innerHTML = html.join('');
  nav.querySelectorAll('.nav-item').forEach(b => {{
    b.addEventListener('click', () => {{ activeSection = b.dataset.sec; renderSidebar(); renderContent(); window.scrollTo({{top:0,behavior:'smooth'}}); }});
  }});
}}

function renderContent() {{
  const s = DATA.find(x => x.id === activeSection);
  const main = document.getElementById('content');
  const isFirst = DATA.indexOf(s) === 0;
  const intro = isFirst ? `
    <div class="intro">
      <h2>Hướng dẫn</h2>
      <p>Với MỖI câu: (1) đọc đề + 4 phương án, CHỌN đáp án bạn nghĩ đúng như đang làm bài thật
      (đáp án đúng KHÔNG hiển thị trước); (2) sau đó đánh giá ĐỘ KHÓ bạn cảm nhận khi làm câu đó.</p>
      <p>${{INTRO_NOTE}}</p>
      <p class="highlight">💾 Tự lưu vào trình duyệt máy này. Đóng tab quay lại vẫn còn. Xong (hoặc làm dở) bấm Export JSON gửi lại.</p>
    </div>` : '';

  const items = s.items.map(it => {{
    const r = state.responses[it.id] || {{}};
    const cls = isDone(r) ? 'done' : (isPartial(r) ? 'partial' : '');
    const opts = it.options.map(o => `<label class="opt-label">
        <input type="radio" name="ans_${{it.id}}" value="${{o.letter}}" ${{r.answer===o.letter?'checked':''}}>
        <span class="letter">${{o.letter}}.</span><span>${{o.text}}</span></label>`).join('');
    return `<div class="item ${{cls}}" data-id="${{it.id}}">
      <div class="item-stem">${{it.stem}}</div>
      <div class="step-label">Bước 1 — chọn đáp án</div>
      <div class="options">${{opts}}</div>
      <div class="step-label">Bước 2 — độ khó bạn cảm nhận</div>
      <div class="radios">
        <label class="sel-easy"><input type="radio" name="diff_${{it.id}}" value="easy" ${{r.verdict==='easy'?'checked':''}}><span>Dễ</span></label>
        <label class="sel-medium"><input type="radio" name="diff_${{it.id}}" value="medium" ${{r.verdict==='medium'?'checked':''}}><span>Trung bình</span></label>
        <label class="sel-hard"><input type="radio" name="diff_${{it.id}}" value="hard" ${{r.verdict==='hard'?'checked':''}}><span>Khó</span></label>
      </div>
    </div>`;
  }}).join('');

  main.innerHTML = `${{intro}}
    <div class="section-header"><h1 class="section-title">${{s.title}}</h1><p class="section-desc">${{s.desc}}</p>
      <div class="section-count">${{s.items.length}} câu • ${{sectionCount(s)}} xong cả hai bước</div></div>
    ${{items}}
    <div class="footer-actions">
      <div class="footer-info"><b>Hoàn thành</b> — Export JSON rồi gửi lại. Có thể gửi dở, không cần xong hết.</div>
      <button class="btn btn-primary" id="export-btn">📥 Export JSON</button>
      <button class="btn btn-danger" id="clear-btn">Xóa toàn bộ</button>
    </div>`;

  main.querySelectorAll('input[name^="ans_"]').forEach(r => {{
    r.addEventListener('change', e => {{
      const id = e.target.name.slice(4);
      state.responses[id] = state.responses[id] || {{}};
      state.responses[id].answer = e.target.value;
      state.responses[id].ts = new Date().toISOString();
      saveResponses(); updateProgress(); renderSidebar();
      const item = e.target.closest('.item');
      item.className = 'item ' + (isDone(state.responses[id]) ? 'done' : 'partial');
    }});
  }});
  main.querySelectorAll('input[name^="diff_"]').forEach(r => {{
    r.addEventListener('change', e => {{
      const id = e.target.name.slice(5);
      state.responses[id] = state.responses[id] || {{}};
      state.responses[id].verdict = e.target.value;
      state.responses[id].ts = new Date().toISOString();
      saveResponses(); updateProgress(); renderSidebar();
      const item = e.target.closest('.item');
      item.className = 'item ' + (isDone(state.responses[id]) ? 'done' : 'partial');
    }});
  }});

  document.getElementById('export-btn').addEventListener('click', exportJson);
  document.getElementById('clear-btn').addEventListener('click', () => {{
    if (confirm('Xóa toàn bộ câu trả lời? Không thể hoàn tác.')) {{
      state = {{ rater: document.getElementById('rater-id').value, responses: {{}} }};
      saveResponses(); updateProgress(); renderSidebar(); renderContent();
    }}
  }});
}}

function exportJson() {{
  const rater = document.getElementById('rater-id').value.trim() || 'anonymous';
  state.rater = rater;
  const payload = {{
    subject: SUBJECT, rater: rater, exported_at: new Date().toISOString(),
    summary: {{
      total_items: DATA.reduce((a,s) => a + s.items.length, 0),
      done_both: Object.values(state.responses).filter(isDone).length,
      answered_only: Object.values(state.responses).filter(r => r.answer).length,
      rated_only: Object.values(state.responses).filter(r => r.verdict).length,
    }},
    responses: state.responses,
  }};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const safe = rater.replace(/[^a-zA-Z0-9_.-]/g, '_').slice(0, 40) || 'anon';
  a.href = url;
  a.download = SUBJECT + '_self_' + safe + '_' + new Date().toISOString().slice(0,10) + '.json';
  a.click(); URL.revokeObjectURL(url);
}}

document.getElementById('rater-id').addEventListener('input', e => {{ state.rater = e.target.value; saveResponses(); }});
document.getElementById('rater-id').value = state.rater || '';

renderSidebar(); renderContent(); updateProgress();
</script>
</body>
</html>
'''


def generate_self_assessment_form(
    subject_code, subject_label, subject_vn, title, sections, intro_note="",
):
    """Sinh form HTML TỰ ĐÁNH GIÁ — người dùng vừa TỰ TRẢ LỜI (chọn đáp án,
    không hiện đáp án đúng trước) vừa TỰ CHẤM ĐỘ KHÓ cho từng câu, chạy hoàn
    toàn local (mở file .html trực tiếp), không cần Google Form/Apps Script.
    Dùng khi không tiếp cận được học sinh/giáo viên thật — người dùng (vd.
    chính tác giả + vài người quen) tạo một nguồn ĐỘC LẬP THẬT (không phải mô
    phỏng LLM) để đối chiếu với nhãn LLM, dù không đại diện học sinh lớp 9."""
    total_items = sum(len(s['items']) for s in sections)
    accent, accent2 = ACCENTS.get(subject_code, ('#556B2F', '#879F52'))
    return SELF_ASSESS_TEMPLATE.format(
        title=title, subject_label=subject_label, subject_code=subject_code,
        subject_vn=subject_vn, total_items=total_items,
        data_json=json.dumps(sections, ensure_ascii=False),
        intro_note=json.dumps(intro_note, ensure_ascii=False),
        accent=accent, accent2=accent2,
    )


def generate_apps_script(subject_label, subject_code, items_by_section, total_items):
    """Generate Google Apps Script that creates a Form.

    items_by_section: dict of section_name -> list of plain-text claims
    """
    gs_lines = [f'''/**
 * Google Apps Script: Tao Google Form tham dinh Ontology {subject_label}
 *
 * CACH DUNG:
 *   1. Mo https://script.google.com/ (dang nhap bang Google Account cua ban)
 *   2. New project -> dan TOAN BO file nay vao editor
 *   3. Bam Save (Ctrl+S), dat ten project tuy y
 *   4. Bam RUN (bieu tuong ▶) -> chay function "createForm"
 *   5. Lan dau se yeu cau grant permission (Drive, Forms) — cu dong y
 *   6. Sau khi chay xong, mo tab "Execution log" de xem URL cua Form
 *   7. Mo link "PUBLISHED URL" de chia se cho giao vien
 *   8. Response se duoc ghi vao Google Sheets (link in ra o log)
 */

function createForm() {{
  var form = FormApp.create("Phieu tham dinh Ontology {subject_label} — Ban 0.1");

  form.setTitle("Phieu tham dinh Ontology {subject_label}");
  form.setDescription(
    "Cam on thay/co tham gia tham dinh!\\n\\n" +
    "Day la phieu khao sat cac khang dinh ve kien thuc {subject_label}, phuc vu cho nghien cuu " +
    "ve uoc luong do kho cau hoi trac nghiem.\\n\\n" +
    "Voi MOI khang dinh, xin danh gia: DUNG / SAI / KHONG CHAC. " +
    "Neu co binh luan (dac biet khi chon SAI), xin ghi vao o binh luan o cuoi moi phan.\\n\\n" +
    "Tong cong co khoang {total_items} muc, chia theo chu de. Co the luu va lam tiep sau."
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(true);
  form.setShowLinkToRespondAgain(false);

  form.addTextItem()
    .setTitle("Ho ten giao vien")
    .setHelpText("De ghi nhan dong gop. Co the ghi 'An danh' neu khong muon neu ten.")
    .setRequired(true);

  form.addTextItem()
    .setTitle("Truong / don vi cong tac")
    .setRequired(false);
''']

    for sec_name, claims in items_by_section.items():
        gs_lines.append(f'\n  // --- SECTION: {sec_name} ---')
        # strip HTML from section name for Apps Script title
        clean_name = sec_name.replace('<b>', '').replace('</b>', '')
        gs_lines.append(f'  form.addPageBreakItem()\n'
                        f'    .setTitle({json.dumps(clean_name, ensure_ascii=False)})\n'
                        f'    .setHelpText("Phan nay co {len(claims)} muc. Voi moi muc, chon Dung / Sai / Khong chac.");')
        for claim in claims:
            c = claim.replace('<b>', '').replace('</b>', '')
            gs_lines.append(f'  form.addMultipleChoiceItem()\n'
                            f'    .setTitle({json.dumps(c, ensure_ascii=False)})\n'
                            f'    .setChoiceValues(["Dung", "Sai", "Khong chac"])\n'
                            f'    .setRequired(false);')
        gs_lines.append(f'  form.addParagraphTextItem()\n'
                        f'    .setTitle({json.dumps(f"Binh luan cho phan: {clean_name} (khong bat buoc)", ensure_ascii=False)})\n'
                        f'    .setHelpText("Neu co muc nao Sai hoac can bo sung, xin ghi ro o day.")\n'
                        f'    .setRequired(false);')

    gs_lines.append(f'''
  var ss = SpreadsheetApp.create("Phieu tham dinh {subject_label} — Responses");
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log("===========================================");
  Logger.log("Form da tao thanh cong!");
  Logger.log("");
  Logger.log("PUBLISHED URL (share cho giao vien):");
  Logger.log(form.getPublishedUrl());
  Logger.log("");
  Logger.log("EDIT URL (link de sua form):");
  Logger.log(form.getEditUrl());
  Logger.log("");
  Logger.log("RESPONSE SHEET (xem response):");
  Logger.log(ss.getUrl());
  Logger.log("===========================================");
}}
''')

    return '\n'.join(gs_lines)
