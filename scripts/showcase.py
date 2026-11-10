"""Write readable Markdown showcase files from encounters.jsonl and copy sample audio.

Usage: python3 -I showcase.py <repo_dir> <fareez_audio_dir>
"""
import json, os, re, shutil, sys
from collections import defaultdict

REPO, AUDIO = sys.argv[1], sys.argv[2]
recs = [json.loads(l) for l in open(os.path.join(REPO, "data/encounters.jsonl"))]
by_id = {r["id"]: r for r in recs}

PICKS = [
    # Gastroenterology
    "aci-D2N192", "aci-D2N123", "aci-D2N181", "osce-GAS0001", "primock-day1_consultation01",
    # Women's health
    "aci-D2N046", "aci-D2N031",
    # Cardiology
    "aci-D2N164", "aci-D2N161", "osce-CAR0001",
    # Pulmonology
    "aci-D2N059", "osce-RES0181", "osce-RES0036",
    # Orthopedics / MSK
    "aci-D2N186", "aci-D2N195", "osce-MSK0025",
    # Neurology, endocrine, derm, urology, eye
    "aci-D2N197", "aci-D2N178", "aci-D2N183", "aci-D2N118", "aci-D2N203",
    # Primary care
    "aci-D2N007", "primock-day2_consultation03", "primock-day3_consultation05",
]

TITLES = {"osce-GAS0001": "Constant nausea", "osce-CAR0001": "Chest pain", "osce-RES0181": "Sore throat and fever", "osce-RES0036": "Six days of breathlessness", "osce-MSK0025": "Two months of worsening back pain"}

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]

def cap(t):
    return t[:1].upper() + t[1:] if t else t

index = defaultdict(list)
os.makedirs(os.path.join(REPO, "audio-samples"), exist_ok=True)
for pid in PICKS:
    r = by_id.get(pid)
    if not r:
        print("missing", pid); continue
    assert not r["mentions_vendor_product"], pid
    reason = cap((r["visit_reason"] or "").strip())
    if r["source"] == "osce-respiratory":
        reason = TITLES[pid]
    folder = os.path.join(REPO, "transcripts", slug(r["specialty"]))
    os.makedirs(folder, exist_ok=True)
    fn = f"{r['id']}.md"
    lines = [f"# {reason or r['id']}", "",
             f"| | |", "|---|---|",
             f"| Specialty | {r['specialty']} |",
             f"| Source | [{r['source']}]({r['source_url']}) `{r['source_id']}` |",
             f"| License | {r['license']} |",
             f"| How it was recorded | {r['collection_mode']} |",
             f"| Length | {r['word_count']:,} words, {r['turn_count']} turns |"]
    if r["patient"].get("age"):
        lines.append(f"| Patient | {r['patient']['age']}-year-old {r['patient']['gender']} |")
    if r["audio"]:
        if r["source"] == "osce-respiratory":
            src = os.path.join(AUDIO, r["audio"]["file"])
            if os.path.exists(src):
                shutil.copy(src, os.path.join(REPO, "audio-samples", r["audio"]["file"]))
                lines.append(f"| Audio | [`audio-samples/{r['audio']['file']}`](../../audio-samples/{r['audio']['file']}) |")
        else:
            lines.append(f"| Audio | [{r['audio']['channels']}]({r['audio']['url']}) |")
    lines += ["", f"Citation: {r['citation']}", "", "## Transcript", ""]
    for t in r["turns"]:
        who = cap(t["speaker"].replace("_", " "))
        lines.append(f"**{who}:** {cap(t['text'])}  ")
    if r["reference_note"]:
        lines += ["", "## Reference note (written by the dataset authors)", "", r["reference_note"].strip()]
    open(os.path.join(folder, fn), "w").write("\n".join(lines) + "\n")
    index[r["specialty"]].append((reason, f"{slug(r['specialty'])}/{fn}", r))

out = ["| Specialty | Visit | Source | Note | Audio |", "|---|---|---|---|---|"]
for spec in sorted(index):
    for reason, path, r in index[spec]:
        out.append(f"| {spec} | [{reason}]({path}) | {r['source']} | {'yes' if r['reference_note'] else 'no'} | {'yes' if r['audio'] else 'no'} |")
open(os.path.join(REPO, "transcripts/INDEX.md"), "w").write("# Showcase transcripts\n\n" + "\n".join(out) + "\n")
print(len(PICKS), "written")
