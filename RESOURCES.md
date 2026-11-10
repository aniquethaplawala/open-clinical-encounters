# What you need to build and evaluate a clinical documentation product

A working map of the resources behind an AI scribe, from raw audio to a signed note in the EHR. Each section says what the resource is for, gives public options, and notes the license. Licenses marked **verified** were checked against the source on 10 Nov 2026. Everything else: check the terms before you reuse it.

---

## 1. Doctor-patient conversations (transcripts and audio)

The input side. You need volume, variety across specialties, and realistic speech: interruptions, filler words, family members talking, and mid-visit topic changes.

| Resource | What it is | Audio | Paired note | License |
|---|---|---|---|---|
| [ACI-Bench](https://github.com/wyim/aci-bench) | 207 role-played visits, mostly outpatient, three recording styles | No | Yes, full note | CC BY 4.0 (verified) |
| [PriMock57](https://github.com/babylonhealth/primock57) | 57 mock primary care video consults with clinicians and actors | Yes, separate doctor and patient tracks | Yes, clinician-written | CC BY 4.0 (verified) |
| [Simulated OSCE interviews](https://doi.org/10.6084/m9.figshare.16550013) (Fareez et al. 2022) | 272 interviews, mostly respiratory and musculoskeletal | Yes, MP3 | No | CC0 (verified) |
| [MTS-Dialog](https://github.com/abachaa/MTS-Dialog) | 1,701 short dialogue snippets, each paired with one note section | No | Section only | CC BY 4.0 (verified) |
| [MedSynth](https://huggingface.co/datasets/Ahmad0067/MedSynth) | 10,000+ LLM-generated dialogue and SOAP note pairs across 2,000+ ICD-10 codes | No | Yes | Not stated on the card |
| [NoteChat](https://arxiv.org/abs/2310.15959) / [Augmented Clinical Notes](https://huggingface.co/datasets/AGBonnet/augmented-clinical-notes) | Synthetic dialogues generated from PubMed case reports | No | Yes | Card says MIT, source notes are CC BY-NC-SA |
| [AfriSpeech-200](https://huggingface.co/datasets/intronhealth/afrispeech-200) | 200 hours of African-accented English, clinical and general | Yes | No | CC BY-NC-SA 4.0, non-commercial (verified) |
| [AfriSpeech-Dialog](https://huggingface.co/datasets/intronhealth/afrispeech-dialog) | Long-form accented conversations, medical and general | Yes | No | CC BY-NC-SA 4.0, non-commercial (verified) |
| **This repo, `sully-synthetic/`** | 5 Sully-written visits matched to Sully templates | Not yet | Yes | CC BY 4.0, Sully.ai |

**What public data won't give you:** real exam-room acoustics, more than two speakers, interpreters, long visits (40+ minutes), pediatrics with a parent talking, procedures, and inpatient rounds. Plan to generate or record these yourself (see section 10).

## 2. Clinical note corpora (the output side)

What good notes look like, by specialty and note type.

- [MIMIC-IV-Note](https://physionet.org/content/mimic-iv-note/): about 330,000 discharge summaries and radiology reports. Credentialed access, no redistribution.
- [n2c2 / i2b2 datasets](https://n2c2.dbmi.hms.harvard.edu/): annotated notes for NLP tasks. Data use agreement required.
- [MEDEC](https://github.com/abachaa/MEDEC): clinical notes with injected medical errors, for error-detection tests. CC BY 4.0 (verified).
- Note templates: [Sully templates](https://www.sully.ai/templates) (SOAP, GI, pain, women's health, behavioral health), plus the HL7 C-CDA document types (H&P, Progress Note, Consult Note, Discharge Summary).

## 3. Synthetic patients and charts

The context a scribe needs: problem lists, meds, allergies, prior visits.

- [Synthea](https://github.com/synthetichealth/synthea): synthetic patient histories exported as FHIR, C-CDA or CSV. Apache 2.0 (verified).
- [CMS synthetic claims (SynPUF)](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files): synthetic Medicare claims for coding and billing tests.
- Pair a Synthea chart with a generated conversation to test "pull from the chart, don't re-ask" behavior.

## 4. Medical vocabularies and code sets

Needed for speech recognition word lists, structured output, and coding.

| Set | Use | Access |
|---|---|---|
| ICD-10-CM | Diagnoses | Free from CMS and CDC |
| RxNorm | Drug names, doses, forms | Free through NLM (UMLS account) |
| SNOMED CT | Problems, findings | Free in the US through the UMLS license |
| LOINC | Labs, vitals, note section and document types | Free with a license agreement |
| CPT | Procedures and E/M codes | **Paid AMA license** |
| HCPCS | Supplies, drugs, non-physician services | Free from CMS |
| FDA NDC directory | Brand and generic drug names | Free |

Build a drug and condition word list from RxNorm and the NDC directory to measure **medical term error rate**, not just overall word error rate.

## 5. Evaluation benchmarks and quality scales

- **ACI-Bench metrics**: ROUGE, BERTScore, BLEURT and fact-based scores for note generation.
- **[MEDIQA-Chat 2023](https://sites.google.com/view/mediqa2023) / MEDIQA-Sum** shared tasks: standard splits for dialogue-to-note.
- **PDQI-9** (Stetson et al. 2012): a 9-item physician rating scale for note quality (accurate, thorough, useful, organized, comprehensible, succinct, synthesized, internally consistent, up to date). The standard human-review rubric for scribe notes.
- **[HealthBench](https://github.com/openai/simple-evals)**: physician-written rubrics for health conversations. MIT.
- **[MedHELM](https://crfm.stanford.edu/helm/medhelm/latest/)**: Stanford's clinical task leaderboard, includes note generation.
- **Error taxonomy**: track omissions, hallucinations (fact not in the transcript), wrong speaker, negation flips ("no chest pain" becomes "chest pain"), wrong laterality, wrong dose, and stale chart facts. Score each by clinical risk, not just count.

## 6. Speech and audio tooling

- **Background noise for augmentation**: [MUSAN](https://www.openslr.org/17/) and [DEMAND](https://zenodo.org/record/1227121) to simulate HVAC, hallway, monitors, and keyboard noise.
- **Speaker diarization tests**: PriMock57's separate tracks give you ground truth for who said what.
- **Text-to-speech with varied voices** to turn synthetic transcripts into audio, including accents, older voices, and children.
- **Medical word lists** (section 4) for keyword boosting and term-level scoring.

## 7. EHR integration and standards

- **FHIR R4 and US Core**: DocumentReference and Composition for notes; Condition, MedicationRequest, AllergyIntolerance and Observation for structured data.
- **Sandboxes**: [Epic on FHIR](https://fhir.epic.com/), [Oracle Health code console](https://code-console.cerner.com/), [athenahealth developer portal](https://docs.athenahealth.com/api/), eClinicalWorks FHIR developer program, [SMART Health IT sandbox](https://launch.smarthealthit.org/).
- **HL7 v2 MDM messages** for sending notes to older EHRs.
- **C-CDA** for document exchange.

## 8. Compliance and governance

- **HIPAA**: business associate agreements with every vendor that touches audio or text (speech recognition, LLM, storage).
- **Recording consent**: state laws differ. A dozen or so states require every party to agree to a recording. Have a patient consent script and a log of consent.
- **ONC HTI-1**: source and transparency requirements for decision support shown inside certified EHRs.
- **FDA clinical decision support guidance**: where a documentation tool ends and a regulated device begins (for example, suggesting diagnoses).
- **[CHAI](https://chai.org/) assurance standards** and **Joint Commission and CHAI guidance on responsible AI use in health care**: what health systems will ask for in procurement.
- **SOC 2 Type II and HITRUST**: what IT security teams ask for.

## 9. Real-world outcome measures

How health systems judge a scribe after go-live:

- Time in notes per visit and after-hours EHR time ("pajama time"), from EHR audit logs such as Epic Signal.
- Note edit rate: share of the AI note the clinician changed before signing.
- Clinician burnout surveys (Mini-Z, Stanford Professional Fulfillment Index).
- Visit volume, same-day note closure, coding level shifts.
- Patient experience scores.
- Published ambient scribe studies (Kaiser Permanente, academic health systems) give baselines to compare against.

## 10. Things you have to make yourself

No public dataset covers these well:

1. **Gold notes by specialty**, written or approved by clinicians in that specialty, in your own templates.
2. **Hard-case transcripts**: interpreters, three or more speakers, a wrong patient name, the patient correcting the doctor, contradictions with the chart, sensitive topics the patient asks to keep out of the note, and a visit that switches topic halfway.
3. **Long and noisy audio**: 30 to 60 minute visits, exam rooms, telehealth with lag and dropouts.
4. **Clinician style profiles**: the same visit written three ways, for testing personalization.
5. **Consented real recordings** from design partners, with a de-identification pipeline.
6. **A red-team set** for safety: prompts hidden in speech, unsafe dose statements, and self-harm disclosures that must reach the note.
