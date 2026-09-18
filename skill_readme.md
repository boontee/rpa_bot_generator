# IBM RPA Skill — PPT Deck Generation Guide

This file tells Bob how to generate a PowerPoint presentation from the
[`ibm-rpa` skill](.bob/skills/ibm-rpa/SKILL.md). Use it as the prompt
scaffold whenever you want a slide deck that explains, demos, or pitches
IBM RPA WAL scripting.

---

## How to Ask Bob to Generate a PPT

Paste one of the ready-made prompts below into Bob, or adapt the template
at the end of this file for a custom deck.

---

## Ready-Made Prompts

### 1 — Overview / Intro Deck
> Create a PowerPoint presentation that introduces IBM RPA and WAL scripting.
> Cover: what IBM RPA is, the WAL language basics, script structure, key
> automation types (Web, Java, Excel, SAP, Queue), and security rules.
> Use the ibm-rpa skill for all technical content.
> Save the file as `IBM_RPA_Overview.pptx`.

### 2 — Java App Automation Deck (MAG / RAPID use case)
> Create a PowerPoint presentation on automating Java Swing desktop
> applications with IBM RPA. Include: Java driver prerequisites (JAB),
> recorder workflow, selector structure, key WAL commands, and a concrete
> example targeting MAG's RAPID cargo revenue accounting system.
> Save as `IBM_RPA_Java_Automation.pptx`.

### 3 — Vision Driver / Surface Automation Deck
> Create a PowerPoint presentation on IBM RPA surface automation using the
> Vision driver. Cover: when to use it, pixel-comparison vs OCR mechanics,
> environment setup, key WAL commands (findImageBySimilarity, waitForImage,
> clickByOCR, getControlTextByOCR), best practices, and Citrix/VDI usage.
> Save as `IBM_RPA_Vision_Driver.pptx`.

### 4 — Full Technical Reference Deck (all categories)
> Create a comprehensive PowerPoint reference deck for IBM RPA WAL scripting.
> One section per command category: Variables & Data, Control Flow, Web
> Automation (Classic + Smart), Java App, Excel/Office, File & Folder,
> Database, Queue, SAP, PDF/OCR, Email, and System/OS.
> Include WAL code snippets on relevant slides.
> Save as `IBM_RPA_WAL_Reference.pptx`.

### 5 — Security & Best Practices Deck
> Create a PowerPoint deck focused on IBM RPA WAL scripting security and
> coding best practices: no hardcoded credentials, vault/asset usage,
> mandatory script structure, selector strategy, error handling patterns,
> and the pre-output checklist.
> Save as `IBM_RPA_Best_Practices.pptx`.

---

## Slide Structure Template

When Bob generates a deck, it uses this default slide structure unless
you specify otherwise:

| Slide # | Purpose | Content drawn from |
|---|---|---|
| 1 | **Title slide** | Deck title, subtitle, date |
| 2 | **Agenda** | Section names as bullet list |
| 3–N | **Content slides** | One topic per slide (see below) |
| Last | **Summary / Next Steps** | Key takeaways, call to action |

### Content slide format (default)
- **Heading** — topic name
- **3–5 bullet points** — key facts or rules
- **Code block** (if applicable) — WAL snippet showing the pattern
- **Speaker notes** — expanded explanation for the presenter

---

## Deck Content Map

The table below maps each skill file to the slides it should produce.
Reference this when customising which sections to include or exclude.

| Skill file | Topics / Slides generated |
|---|---|
| [`SKILL.md`](.bob/skills/ibm-rpa/SKILL.md) | WAL language essentials, mandatory script structure, non-negotiable rules, pre-output checklist |
| [`wal-reference.md`](.bob/skills/ibm-rpa/wal-reference.md) | Data types, Variables & Data, Control Flow, Web Automation (Classic), Smart Web, Excel, File/Folder, Database, Queue, PDF/OCR, Email, SAP, System/OS, Selector quick reference |
| [`conventions.md`](.bob/skills/ibm-rpa/conventions.md) | Naming conventions, file structure template, subroutine guidelines, security rules, retry pattern, error handling patterns, queue dispatcher-performer pattern, BAW integration |
| [`examples/web-login.wal`](.bob/skills/ibm-rpa/examples/web-login.wal) | Web authentication demo slide |
| [`examples/excel-reader.wal`](.bob/skills/ibm-rpa/examples/excel-reader.wal) | Excel read/loop/write demo slide |
| [`examples/excel-reconcile.wal`](.bob/skills/ibm-rpa/examples/excel-reconcile.wal) | Data reconciliation demo slide |
| [`examples/queue-processor.wal`](.bob/skills/ibm-rpa/examples/queue-processor.wal) | Queue performer pattern demo slide |
| [`examples/python_list_bridge.wal`](.bob/skills/ibm-rpa/examples/python_list_bridge.wal) | Python→WAL List bridge pattern (pipe-delimited string + textSplit) |
| [`README.md`](README.md) — Java section | Java driver setup, JAB, Java WAL commands, selectors |
| [`README.md`](README.md) — Vision section | Vision driver, surface automation, OCR, best practices |
| [`README.md`](README.md) — MAG/RAPID section | Customer use-case slide: RAPID platform, MAG automation opportunity |

---

## Customisation Options

Include any of the following in your prompt to control the output:

| Option | Example instruction |
|---|---|
| **Slide count** | "Keep the deck to 12 slides maximum." |
| **Audience** | "Audience is non-technical managers." / "Audience is IBM RPA developers." |
| **Branding** | "Use IBM blue (#0062FF) as the accent colour." |
| **Code depth** | "Show full WAL code examples on every applicable slide." / "Keep code snippets minimal — one line per slide." |
| **Use case focus** | "Focus on the MAG RAPID cargo accounting automation scenario." |
| **Output filename** | "Save as `RPA_Deck_v1.pptx`." |
| **Section exclusions** | "Exclude the SAP and Terminal sections." |
| **Speaker notes** | "Add detailed speaker notes on every slide." / "No speaker notes needed." |

---

## Full Custom Prompt Template

Copy, fill in the `[…]` placeholders, and paste into Bob:

```
Create a PowerPoint presentation on [TOPIC].

Audience: [e.g. IBM RPA developers / business stakeholders / solution architects]
Slide count: [e.g. 10–15 slides]
Sections to include: [list from the Deck Content Map above]
Sections to exclude: [list, or "none"]
Code examples: [full / minimal / none]
Speaker notes: [yes / no]
Accent colour: [e.g. IBM blue #0062FF]
Output filename: [e.g. My_RPA_Deck.pptx]

Use the ibm-rpa skill (@.bob/skills/ibm-rpa/SKILL.md) for all
technical content. Follow the slide structure template in skill_readme.md.
```

---

## Skill Reference

| File | Purpose |
|---|---|
| [`.bob/skills/ibm-rpa/SKILL.md`](.bob/skills/ibm-rpa/SKILL.md) | Core skill — WAL rules, script structure, checklist |
| [`.bob/skills/ibm-rpa/wal-reference.md`](.bob/skills/ibm-rpa/wal-reference.md) | Full WAL command reference by category |
| [`.bob/skills/ibm-rpa/conventions.md`](.bob/skills/ibm-rpa/conventions.md) | Naming, patterns, security, BAW integration |
| [`.bob/skills/ibm-rpa/examples/`](.bob/skills/ibm-rpa/examples/) | Working WAL script examples |
| [`README.md`](README.md) | Java driver, Vision driver, MAG/RAPID research |
| [`skill_readme.md`](skill_readme.md) | This file — PPT generation guide |
