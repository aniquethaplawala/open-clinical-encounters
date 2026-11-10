"""Normalize four openly licensed doctor-patient datasets into one JSONL schema.

Usage: python3 -I normalize.py <raw_dir> <out_dir>
"""
import csv, glob, json, os, re, sys

csv.field_size_limit(10**9)
RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

LIC = {
    "aci-bench": ("CC BY 4.0", "Yim et al. 2023, Scientific Data, doi:10.1038/s41597-023-02487-3", "https://github.com/wyim/aci-bench"),
    "primock57": ("CC BY 4.0", "Papadopoulos Korfiatis et al. 2022, ACL, arXiv:2204.00333", "https://github.com/babylonhealth/primock57"),
    "osce-respiratory": ("CC0 1.0", "Fareez et al. 2022, Scientific Data, doi:10.1038/s41597-022-01423-1", "https://doi.org/10.6084/m9.figshare.16550013"),
    "mts-dialog": ("CC BY 4.0", "Ben Abacha et al. 2023, EACL, aclanthology.org/2023.eacl-main.168", "https://github.com/abachaa/MTS-Dialog"),
}

SPECIALTY_RULES = [
    ("Gastroenterology", r"abdominal|reflux|ibs|hepatitis|swallow|esophag|diarrhea|bowel|liver|anemia"),
    ("Women's health", r"ovarian|breast|mammoplasty|macromastia|ductal|std|pregnan|prenatal"),
    ("Cardiology", r"heart|chf|stemi|stem\b|murmur|mitral|chest pain|palpitation|blood pressure|hypertension|\bbp\b|cholesterol"),
    ("Pulmonology", r"cough|asthma|shortness of breath|dyspnea|lung|respiratory|hemoptysis|smoking"),
    ("Orthopedics & musculoskeletal", r"knee|shoulder|ankle|elbow|wrist|hand|finger|toe|foot|hip|arm|leg|heel|lcl|joint|arthroplasty|arthritis|neck pain|back pain"),
    ("Neurology", r"headache|numbness|hydrocephalus|pituitary|twitch|facial pain"),
    ("Endocrinology", r"diabetes|blood sugar|thyroid|hypogonadism"),
    ("Dermatology", r"acne|dermatitis|melanoma|scalp|psoriatic"),
    ("Nephrology & urology", r"kidney|renal|hematuria|urinat|flank"),
    ("Ophthalmology", r"vision|macular"),
    ("Oncology", r"cancer|carcinoma"),
    ("Primary care", r"annual|chronic problems|follow|er follow|labs|lab finding|exam|sore throat|tick|ulcer|wound|immunoglobulin|lyme|infection"),
]

def specialty(cc):
    c = (cc or "").lower()
    for name, pat in SPECIALTY_RULES:
        if re.search(pat, c):
            return name
    return "Primary care"

def wc(turns):
    return sum(len(t["text"].split()) for t in turns)

def detok(s):
    """ACI-Bench text is lower-cased and space-tokenized; tidy punctuation spacing only."""
    s = re.sub(r" ([,.?!;:%])", r"\1", s)
    s = re.sub(r" (n't|'s|'re|'ve|'ll|'m|'d)\b", r"\1", s)
    return s.strip()

MODE = {"aci": "role-played visit, natural conversation", "virtassist": "role-played visit, clinician cues a voice assistant", "virtscribe": "role-played visit, clinician dictates to a scribe"}

def age(a):
    try: return int(float(a))
    except Exception: return None

records = []

# ---------- ACI-Bench ----------
base = os.path.join(RAW, "aci-bench/data/challenge_data")
for f in sorted(glob.glob(os.path.join(base, "*.csv"))):
    if f.endswith("_metadata.csv"):
        continue
    split = os.path.basename(f)[:-4]
    meta = {r["encounter_id"]: r for r in csv.DictReader(open(os.path.join(base, split + "_metadata.csv")))}
    for r in csv.DictReader(open(f)):
        md = meta.get(r["encounter_id"], {})
        turns = []
        for line in r["dialogue"].split("\n"):
            m = re.match(r"\[(\w+)\]\s*(.*)", line.strip())
            if m:
                turns.append({"speaker": m.group(1).lower(), "text": detok(m.group(2))})
            elif line.strip() and turns:
                turns[-1]["text"] += " " + detok(line)
        cc = (md.get("cc") or "").strip()
        records.append({
            "id": f"aci-{r['encounter_id']}", "source": "aci-bench", "source_id": r["encounter_id"],
            "source_split": split, "collection_mode": MODE.get(r["dataset"], r["dataset"]),
            "specialty": specialty(cc), "visit_reason": cc,
            "patient": {"age": age(md.get("patient_age")), "gender": md.get("patient_gender") or None},
            "turns": turns, "reference_note": r["note"], "note_style": "Full clinical note (CC / HPI / ROS / PE / A&P)",
            "audio": None, "mentions_vendor_product": "dax" in r["dialogue"].lower(),
        })

# ---------- PriMock57 ----------
def textgrid(path):
    txt = open(path, encoding="utf-8").read()
    out = []
    for xmin, xmax, text in re.findall(r'xmin = ([\d.]+)\s*\n\s*xmax = ([\d.]+)\s*\n\s*text = "(.*?)"\s*\n', txt, re.S):
        text = re.sub(r"</?UNSURE>|<UNIN/>|<INAUDIBLE/>|<[A-Z_]+/?>", "", text).replace('""', '"')
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            out.append((float(xmin), float(xmax), text))
    return out

pm = os.path.join(RAW, "primock57")
for nf in sorted(glob.glob(os.path.join(pm, "notes/*.json"))):
    n = json.load(open(nf))
    stem = os.path.basename(nf)[:-5]
    segs = [(a, b, "doctor", t) for a, b, t in textgrid(os.path.join(pm, f"transcripts/{stem}_doctor.TextGrid"))]
    segs += [(a, b, "patient", t) for a, b, t in textgrid(os.path.join(pm, f"transcripts/{stem}_patient.TextGrid"))]
    segs.sort()
    turns = [{"speaker": s, "text": t, "start": round(a, 2), "end": round(b, 2)} for a, b, s, t in segs]
    records.append({
        "id": f"primock-{stem}", "source": "primock57", "source_id": stem, "source_split": "all",
        "collection_mode": "mock consultation, clinician + actor, remote video call",
        "specialty": "Primary care", "visit_reason": n.get("presenting_complaint"),
        "patient": {"age": None, "gender": None},
        "turns": turns, "reference_note": n.get("note"), "note_style": "Clinician-written consultation note (UK primary care shorthand)",
        "audio": {"available": True, "channels": "separate doctor + patient WAV tracks", "url": f"https://github.com/babylonhealth/primock57/tree/main/audio"},
        "mentions_vendor_product": False,
    })

# ---------- OSCE simulated interviews (Fareez et al.) ----------
FZ = {"RES": "Pulmonology", "MSK": "Orthopedics & musculoskeletal", "CAR": "Cardiology", "GAS": "Gastroenterology", "DER": "Dermatology", "GEN": "Primary care"}
for tf in sorted(glob.glob(os.path.join(RAW, "fareez/Data/Clean Transcripts/*.txt"))):
    sid = os.path.basename(tf)[:-4]
    turns = []
    for line in open(tf, encoding="utf-8", errors="replace").read().splitlines():
        line = line.strip()
        m = re.match(r"^([DP])\s*:\s*(.*)", line)
        if m:
            turns.append({"speaker": "doctor" if m.group(1) == "D" else "patient", "text": m.group(2).strip()})
        elif line and turns:
            turns[-1]["text"] += " " + line
    first_patient = next((t["text"] for t in turns if t["speaker"] == "patient"), "")
    records.append({
        "id": f"osce-{sid}", "source": "osce-respiratory", "source_id": sid, "source_split": "all",
        "collection_mode": "simulated OSCE interview, trained actors",
        "specialty": FZ.get(sid[:3], "Primary care"), "visit_reason": first_patient[:160],
        "patient": {"age": None, "gender": None},
        "turns": turns, "reference_note": None, "note_style": None,
        "audio": {"available": True, "channels": "single mixed MP3", "file": f"{sid}.mp3", "url": "https://doi.org/10.6084/m9.figshare.16550013"},
        "mentions_vendor_product": False,
    })

for r in records:
    lic, cite, url = LIC[r["source"]]
    r.update({"license": lic, "citation": cite, "source_url": url, "word_count": wc(r["turns"]), "turn_count": len(r["turns"])})

with open(os.path.join(OUT, "encounters.jsonl"), "w") as fh:
    for r in records:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

# ---------- MTS-Dialog: section-level pairs, kept separate ----------
n = 0
with open(os.path.join(OUT, "mts_dialog_sections.jsonl"), "w") as fh:
    for f in sorted(glob.glob(os.path.join(RAW, "MTS-Dialog/Main-Dataset/*.csv"))):
        split = os.path.basename(f)[:-4]
        for r in csv.DictReader(open(f)):
            turns = []
            for line in r["dialogue"].split("\n"):
                m = re.match(r"^(Doctor|Patient|Guest_family|Guest_clinician|[A-Za-z_]+)\s*:\s*(.*)", line.strip())
                if m:
                    turns.append({"speaker": m.group(1).lower(), "text": m.group(2).strip()})
                elif line.strip() and turns:
                    turns[-1]["text"] += " " + line.strip()
            fh.write(json.dumps({"id": f"mts-{split}-{r['ID']}", "source": "mts-dialog", "source_split": split,
                                 "section_header": r["section_header"], "turns": turns, "reference_section": r["section_text"],
                                 "license": LIC["mts-dialog"][0], "citation": LIC["mts-dialog"][1], "source_url": LIC["mts-dialog"][2]},
                                ensure_ascii=False) + "\n")
            n += 1

from collections import Counter
print("encounters:", len(records), Counter(r["source"] for r in records))
print("specialties:", Counter(r["specialty"] for r in records))
print("mts sections:", n)
print("with audio:", sum(1 for r in records if r["audio"]), "with note:", sum(1 for r in records if r["reference_note"]))
