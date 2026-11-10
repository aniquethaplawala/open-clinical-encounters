# Open Clinical Encounters

**536 doctor-patient visit transcripts, 329 with audio and 264 with a matching clinical note, in one format.** Built by [Sully.ai](https://www.sully.ai) for anyone testing or teaching AI medical scribes and clinical documentation.

The data comes from four openly licensed research datasets. We converted all of them to the same schema, so you can load one file instead of four. We also added five synthetic visits written by Sully, each paired with a note in one of our [free note templates](https://www.sully.ai/templates).

## What's inside

| Folder | Contents |
|---|---|
| [`data/encounters.jsonl`](data/encounters.jsonl) | All 536 full visits, one per line, same schema |
| [`data/mts_dialog_sections.jsonl`](data/mts_dialog_sections.jsonl) | 1,701 short dialogue snippets, each paired with one note section |
| [`data/catalog.csv`](data/catalog.csv) | One row per visit: specialty, reason for visit, length, note and audio flags |
| [`transcripts/`](transcripts/INDEX.md) | 24 hand-picked visits across 11 specialties, formatted for reading |
| [`audio-samples/`](audio-samples/) | 5 MP3 recordings that match showcase transcripts |
| [`sully-synthetic/`](sully-synthetic/) | 5 Sully-written visits with notes: GI, pain, women's health, telehealth behavioral health, primary care. Also in [`data/sully_synthetic.jsonl`](data/sully_synthetic.jsonl) and as print-ready PDFs in [`sully-synthetic/pdf/`](sully-synthetic/pdf/) |
| [`RESOURCES.md`](RESOURCES.md) | A map of everything else you need to build and evaluate a scribe |
| [`scripts/`](scripts/) | The code that builds this repo from the original sources |

## By the numbers

| Source | Visits | Audio | Note | License |
|---|---|---|---|---|
| [ACI-Bench](https://github.com/wyim/aci-bench) | 207 | No | Yes | CC BY 4.0 |
| [Simulated OSCE interviews](https://doi.org/10.6084/m9.figshare.16550013) | 272 | Yes | No | CC0 |
| [PriMock57](https://github.com/babylonhealth/primock57) | 57 | Yes | Yes | CC BY 4.0 |
| [MTS-Dialog](https://github.com/abachaa/MTS-Dialog) | 1,701 snippets | No | Section | CC BY 4.0 |
| Sully synthetic | 5 | Not yet | Yes | CC BY 4.0 |

Specialties across the 536 full visits: pulmonology 232, orthopedics and musculoskeletal 138, primary care 92, cardiology 21, gastroenterology 20, neurology 7, nephrology and urology 7, dermatology 6, women's health 6, endocrinology 5, ophthalmology 2. Specialty labels come from the visit reason using simple keyword rules (see `scripts/normalize.py`), so treat them as a starting point.

## Schema

```json
{
  "id": "aci-D2N192",
  "source": "aci-bench",
  "source_id": "D2N192",
  "specialty": "Gastroenterology",
  "visit_reason": "abdominal pain",
  "collection_mode": "role-played visit, natural conversation",
  "patient": {"age": 34, "gender": "female"},
  "turns": [{"speaker": "doctor", "text": "..."}, {"speaker": "patient", "text": "..."}],
  "reference_note": "CHIEF COMPLAINT\n\nAbdominal pain...",
  "note_style": "Full clinical note (CC / HPI / ROS / PE / A&P)",
  "audio": null,
  "license": "CC BY 4.0",
  "citation": "Yim et al. 2023, Scientific Data, doi:10.1038/s41597-023-02487-3",
  "source_url": "https://github.com/wyim/aci-bench",
  "word_count": 1598,
  "turn_count": 54,
  "mentions_vendor_product": false
}
```

PriMock57 turns also carry `start` and `end` times in seconds. `mentions_vendor_product` flags ACI-Bench visits where the clinician addresses a commercial voice assistant by name; filter these out if you want neutral text.

## Quick start

```python
import json
visits = [json.loads(line) for line in open("data/encounters.jsonl")]

with_notes = [v for v in visits if v["reference_note"]]
gi = [v for v in visits if v["specialty"] == "Gastroenterology"]

def as_text(v):
    return "\n".join(f"{t['speaker'].upper()}: {t['text']}" for t in v["turns"])

print(as_text(gi[0])[:500])
```

## Ideas for use

- **Test an AI scribe**: send each transcript through your system and compare the output with `reference_note`, using a clinician rating scale such as PDQI-9.
- **Test speech recognition**: run the OSCE and PriMock57 audio through a speech-to-text engine and compare it with the human transcripts. PriMock57 has separate doctor and patient tracks, so you can test who-said-what too.
- **Teach note writing**: use the showcase transcripts and Sully templates in residency or scribe training.
- **Blog and demo material**: every visit is role-played or synthetic, so there's no real patient data.

## Audio

Five MP3 samples are in `audio-samples/`. The full sets are:

- **Simulated OSCE interviews**: 272 MP3s, about 1 GB, at [figshare](https://doi.org/10.6084/m9.figshare.16550013).
- **PriMock57**: 57 visits with separate doctor and patient WAV tracks, stored with Git LFS at [babylonhealth/primock57](https://github.com/babylonhealth/primock57).

## Rebuild from source

```bash
python3 scripts/normalize.py raw/ data/      # raw/ holds the four source datasets
python3 scripts/showcase.py . "raw/fareez/Data/Audio Recordings"
```

## License and credit

- Sully's own work in this repo (the synthetic visits, the scripts, the docs and the schema) is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Each converted visit keeps its original license, listed in its `license` field. We changed formatting only: speaker labels, spacing, and the removal of transcription tags such as `<UNSURE>`. The words are unchanged.
- **Please cite the original authors.** Full citations are in [ATTRIBUTION.md](ATTRIBUTION.md).

All visits are role-played or synthetic. None contain real patient information. This repo is for research, testing and teaching, not for clinical care.
