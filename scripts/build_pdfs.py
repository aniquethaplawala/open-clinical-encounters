"""Render sully-synthetic/*.md into styled HTML files (then PDF via Playwright).

Usage: python3 -I build_pdfs.py <repo_dir> <out_dir> <logo_svg>
"""
import html, os, re, sys, glob

REPO, OUT, LOGO = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
logo = open(LOGO).read()
if "viewBox" not in logo:
    w, h = re.search(r"width=\"([\d.]+)\" height=\"([\d.]+)\"", logo).groups()
    logo = logo.replace("<svg ", f"<svg viewBox=\"0 0 {w} {h}\" ", 1)
GH = "github.com/aniquethaplawala/open-clinical-encounters"

META = {
    "sully-syn-001": ("GI Consultation Sample Transcript", "Gastroenterology", "gi-consultation-sample-transcript", "GI Consultation Note"),
    "sully-syn-002": ("Chronic Pain Evaluation Sample Transcript", "Pain management", "chronic-pain-evaluation-sample-transcript", "Chronic Pain Initial Evaluation"),
    "sully-syn-003": ("Well-Woman Exam Sample Transcript", "Women's health", "well-woman-exam-sample-transcript", "Well-Woman Annual Exam"),
    "sully-syn-004": ("Behavioral Health Telehealth Sample Transcript", "Telehealth", "behavioral-health-telehealth-sample-transcript", "Behavioral Health Telehealth Note"),
    "sully-syn-005": ("Primary Care Visit Sample Transcript", "General", "primary-care-visit-sample-transcript", "SOAP Note"),
}

def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*\((.+?)\)\*", r"<em>(\1)</em>", s)
    return s

def md_note(md):
    out, in_ul, in_ol = [], False, False
    def close():
        nonlocal in_ul, in_ol
        if in_ul: out.append("</ul>"); in_ul = False
        if in_ol: out.append("</ol>"); in_ol = False
    for line in md.splitlines():
        l = line.rstrip()
        if not l.strip():
            close(); continue
        if l.startswith("### "):
            close(); out.append(f"<h4>{inline(l[4:])}</h4>")
        elif re.match(r"^\s*- ", l):
            if not in_ul: close(); out.append("<ul>"); in_ul = True
            out.append(f"<li>{inline(re.sub(r'^\s*- ', '', l))}</li>")
        elif re.match(r"^\d+\. ", l):
            if not in_ol: close(); out.append("<ol>"); in_ol = True
            out.append(f"<li>{inline(re.sub(r'^\d+\. ', '', l))}</li>")
        else:
            close(); out.append(f"<p>{inline(l)}</p>")
    close()
    return "\n".join(out)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Inter:wght@400;500;600;700&display=swap');
@page { size: Letter; margin: 0.55in 0.6in 0.6in; }
:root { --bg:#f7f6f0; --row:#efece8; --navy:#0b345c; --line:#dfdad2; --muted:#8c8881; --ink:#242529; }
* { box-sizing: border-box; }
html, body { background: var(--bg); }
body { margin:0; font-family: Inter, sans-serif; color: var(--ink); font-size: 9.6pt; line-height: 1.5; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.top { display:flex; justify-content:space-between; align-items:flex-start; }
.top svg { width: 86px; height: auto; }
.eyebrow { text-align:right; font-size:7.2pt; letter-spacing:.14em; text-transform:uppercase; color: var(--muted); font-weight:600; line-height:1.6; }
h1 { font-family: Fraunces, serif; font-weight: 500; color: var(--navy); font-size: 25pt; margin: 18px 0 4px; letter-spacing: -.01em; }
.lede { color:#5d5a55; font-size: 10.4pt; margin: 0 0 16px; max-width: 92%; }
table.meta { width:100%; border-collapse: collapse; margin-bottom: 18px; }
table.meta td { border-top: 1px solid var(--line); padding: 7px 10px; vertical-align: top; }
table.meta td:first-child { width: 28%; font-weight: 600; background: var(--row); }
table.meta td:last-child { color:#55524d; }
.sec { display:flex; align-items:center; gap:10px; margin: 18px 0 8px; break-after: avoid; }
.badge { width: 20px; height: 20px; background: var(--navy); color:#fff; font-weight:700; font-size: 8pt; display:flex; align-items:center; justify-content:center; border-radius: 3px; }
.sec h2 { margin:0; font-size: 12.5pt; font-weight: 600; }
.turn { display:grid; grid-template-columns: 74px 1fr; gap: 10px; padding: 4px 10px; border-top: 1px solid var(--line); break-inside: avoid; }
.turn .who { font-weight: 600; color: var(--navy); font-size: 8.4pt; padding-top: 1px; }
.turn.patient .who, .turn.daughter .who { color: #6b5f4f; }
.turn.patient, .turn.daughter { background: rgba(239,236,232,.55); }
.turn em { color: var(--muted); }
.note { border-top: 1px solid var(--line); padding: 8px 10px 4px; }
.note h4 { font-size: 9.8pt; margin: 12px 0 4px; color: var(--navy); break-after: avoid; }
.note p { margin: 0 0 6px; }
.note ul, .note ol { margin: 0 0 8px 0; padding-left: 18px; }
.note li { margin-bottom: 2px; }
.callout { background: var(--row); border-left: 3px solid var(--navy); padding: 11px 14px; margin: 18px 0 10px; break-inside: avoid; font-size: 9pt; }
.callout strong { color: var(--navy); }
.cta { background: var(--navy); color:#fff; border-radius: 6px; padding: 13px 16px; display:flex; justify-content:space-between; align-items:center; gap: 16px; break-inside: avoid; font-size: 9pt; }
.cta strong { font-weight: 700; }
.cta .btn { background:#e9a23b; color:#1b1b1b; font-weight:700; padding: 7px 12px; border-radius: 4px; white-space: nowrap; }
.foot { color: var(--muted); font-size: 7.4pt; margin-top: 10px; }
"""

for f in sorted(glob.glob(os.path.join(REPO, "sully-synthetic/*.md"))):
    s = open(f).read()
    fm = dict(re.findall(r"^(\w+): (.*)$", s.split("---")[1], re.M))
    title, cat, slug, tpl = META[fm["id"]]
    tr = s.split("## Transcript")[1].split("## Reference note")[0]
    note_md = s.split("## Reference note")[1].split("\n", 1)[1].strip()
    note_md = re.sub(r"\n?Synthetic note for teaching\. Not signed\.\s*$", "", note_md)
    note_md = re.sub(r"^### [A-E]\. ", "### ", note_md, flags=re.M)
    note_md = re.sub(r"\n### Attestation\s*$", "", note_md).rstrip()
    turns = []
    for m in re.finditer(r"^\*\*(\w+):\*\* (.*)$", tr, re.M):
        who = m.group(1)
        turns.append(f'<div class="turn {who.lower()}"><div class="who">{who}</div><div>{inline(m.group(2))}</div></div>')
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>Sully.ai: {html.escape(title)}</title><style>{CSS}</style></head><body>
<div class="top">{logo}<div class="eyebrow">{html.escape(cat)}<br>Sample visit transcript · synthetic</div></div>
<h1>{html.escape(fm['title'][0].upper() + fm['title'][1:])}</h1>
<p class="lede">A full doctor-patient conversation and the finished note it should produce, laid out in the Sully {html.escape(tpl)} template. Use it to test an AI scribe, train new scribes, or see what a complete note captures.</p>
<table class="meta">
<tr><td>Patient</td><td>{html.escape(fm['patient'])}</td></tr>
<tr><td>Visit</td><td>{html.escape(fm['visit_type'])}</td></tr>
<tr><td>Length</td><td>About {fm['length_minutes']} minutes, {len(turns)} turns</td></tr>
<tr><td>Matching template</td><td>{html.escape(tpl)} · {html.escape(fm['paired_template'].replace('https://www.', ''))}</td></tr>
</table>
<div class="sec"><div class="badge">A</div><h2>Visit transcript</h2></div>
{''.join(turns)}
<div class="sec"><div class="badge">B</div><h2>Finished note</h2></div>
<div class="note">{md_note(note_md)}</div>
<div class="callout"><strong>How to use this sample.</strong> Run the transcript through your scribe and compare its draft with the finished note. Check the details that are easy to miss: doses, which side of the body, what the patient said no to, and every follow-up step. For 536 more transcripts, many with audio and reference notes, see <a href="https://{GH}" style="color:var(--navy)">{GH}</a>.</div>
<div class="cta"><div><strong>Rather not write the note yourself?</strong> Sully's AI Scribe listens to the visit and drafts the note in your template, ready for you to review and sign.</div><a class="btn" href="https://www.sully.ai/scribe" style="text-decoration:none">sully.ai</a></div>
<p class="foot">Synthetic visit written by Sully.ai for teaching and testing. All people and details are invented. Not medical advice. Licensed CC BY 4.0.</p>
</body></html>"""
    open(os.path.join(OUT, slug + ".html"), "w").write(page)
    print(slug)
