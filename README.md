# IBM RPA — Java App UI Automation & Vision Driver

---

## Malaysia Aviation Group (MAG) — RAPID Application Research

> **Summary:** RAPID is **Mercator's airline cargo & passenger revenue accounting platform** — a commercial enterprise product originally built by Emirates' IT division (Mercator) in 1994, now maintained under **Accelya** (post-2017 merger). Malaysia Airlines (MAB) and MASkargo use RAPID to manage all cargo air waybill revenue recognition, billing, interline settlement, and financial reporting. The UI is a **Java Swing thick-client desktop application**, making it an ideal candidate for IBM RPA's **Java driver** (via Java Access Bridge).

### What Is RAPID?

| Attribute | Detail |
|---|---|
| **Product name** | RAPID (Revenue Accounting Platform for Airlines) |
| **Vendor** | Mercator (Emirates IT division, est. 1995) → acquired/merged into **Accelya** (2017) |
| **Product family** | RAPID Cargo, RAPID Passenger |
| **First go-live** | 20 November 1994 at Emirates Airlines (25+ years in production) |
| **Customer count** | 60+ air carriers worldwide (at its peak under Mercator) |
| **Successor** | Accelya RA V20 (airlines are being migrated off RAPID to RA V20) |
| **MAG usage** | Malaysia Airlines Berhad (MAB) cargo revenue accounting; used alongside SAP S/4HANA |

### How MAG Uses RAPID

From multiple Malaysia Airlines job postings, RAPID is used for **cargo revenue accounting** across these functional areas:

| Function | RAPID Activities |
|---|---|
| **Flown revenue recognition** | Weekly/monthly AWB flown accounting, flown deletions, batch error resolution |
| **Mail & truck accounting** | MAI2010, MAI2018, MAI5011 (mail closing); MAI2014, MAI2012 (mail accounting); FLC2004 (truck revenue) |
| **Sales suspense clearing** | SLC5435 forward sales suspense; AVL AWB resolution |
| **RDI (Rapid Data Interface)** | Daily monitoring and clearing of RDI screen exceptions and flown batch errors |
| **Billing & invoicing** | Charges Correction Advice (CCA); invoices, credit notes, journal vouchers (JVs) |
| **Warehouse revenue** | Other charges, fuel surcharges, security surcharges, tonnage verification |
| **Interline & mail** | Interline charge reconciliation; forwarded to SAP for JV posting |

**Complementary systems used alongside RAPID at MAG:**
- **SAP S/4HANA** — manual journal vouchers (JVs), notional commission entries, suspense reconciliation
- **Esker** — ORC (Overriding Commission) payment vouchers for charter operations
- **Unisys Cargo Solutions (KeRIS)** — MASkargo's separate cargo management system for operations, sales, ground handling

### RAPID Platform Architecture & UI Technology

| Attribute | Assessment |
|---|---|
| **UI type** | **Java Swing thick-client desktop application** |
| **Why Java Swing** | RAPID originated in the mid-1990s at Emirates as an in-house system; Java Swing was the dominant enterprise GUI framework at that time |
| **Screen code style** | Module codes like `MAI2010`, `SLC5435`, `FLC2004` are characteristic of a form-based thick-client menu navigation |
| **Backend** | Oracle database (industry standard for enterprise aviation systems of this era) |
| **Deployment** | Client-server; installed locally on analyst/accountant workstations |
| **IBM RPA driver needed** | **Java driver** (via Java Access Bridge) for standard controls; **Vision driver** as fallback for any non-accessible custom panels |

> The screen module code naming convention (`MAI`, `SLC`, `FLC` prefixes followed by 4-digit numbers) is typical of Java Swing enterprise applications where each 4-digit code opens a specific data-entry or reporting form.

### IBM RPA Automation Opportunity at MAG

The job postings explicitly mention:
> *"Participate in Robotic Process Automation projects alongside another executive as a backup."*

This confirms MAG is actively automating RAPID workflows with RPA. Candidate processes:

| Process | Automation Potential |
|---|---|
| Weekly/monthly flown AWB closures | High — repetitive, rule-based, date-triggered |
| RDI exception monitoring & clearing | High — daily batch monitoring loop |
| Mail closing sequence (MAI2010 → MAI2018 → MAI5011) | High — fixed sequence of form submissions |
| Forward sales suspense report (SLC5435) | Medium — requires conditional logic per AWB status |
| CCA verification and approval | Medium — document validation + approval workflow |
| Suspense account aging reports | High — data extraction + Excel/SAP posting |

---


Research notes on automating **Java (Swing/AWT) desktop applications** and using
the **Vision driver (Surface Automation)** in IBM RPA Studio.

---

## Table of Contents

1. [Recorder Overview](#1-recorder-overview)
2. [Driver Types](#2-driver-types)
3. [Java Driver — Automating Java Applications](#3-java-driver--automating-java-applications)
   - [Prerequisites & Setup](#prerequisites--setup)
   - [Launching the Java Driver in the Recorder](#launching-the-java-driver-in-the-recorder)
   - [Key WAL Commands for Java Automation](#key-wal-commands-for-java-automation)
   - [Selectors for Java Controls](#selectors-for-java-controls)
4. [Vision Driver — Surface Automation](#4-vision-driver--surface-automation)
   - [When to Use the Vision Driver](#when-to-use-the-vision-driver)
   - [How It Works](#how-it-works)
   - [Environment Setup for Reliable Results](#environment-setup-for-reliable-results)
   - [Key WAL Commands for Surface Automation](#key-wal-commands-for-surface-automation)
   - [OCR Commands](#ocr-commands)
   - [Best Practices & Guidelines](#best-practices--guidelines)
5. [Java Driver vs Vision Driver — Decision Guide](#5-java-driver-vs-vision-driver--decision-guide)
6. [References](#6-references)

---

## 1. Recorder Overview

IBM RPA Studio's **Recorder** is the primary tool for capturing interactions with
desktop, web, and terminal applications. It:

- Maps application UI elements (called **controls**) and reads their attributes.
- Generates **selectors** — attribute combinations that uniquely identify each control.
- Auto-generates WAL script commands as you interact with the application.
- Supports both *automatic* (click-to-record) and *manual* (inspector-based) mapping.

The recorder operates through **drivers**, each tailored to a specific UI technology.

---

## 2. Driver Types

| Driver | Technology | Typical Use |
|---|---|---|
| **Windows** | Microsoft UI Automation v3 | Native Win32/WPF/WinForms apps |
| **Java** | Java Access Bridge (JAB) | Java Swing/AWT desktop apps |
| **SAP** | SAP GUI Scripting | SAP GUI for Windows |
| **Web** | Browser DevTools / DOM | Chrome, Edge, Firefox |
| **Terminal** | HLLAPI / 3270/5250 emulation | Mainframe/AS400 green-screen |
| **Vision** | Proprietary pixel comparison + OCR | Any visible UI — fallback driver |

> **Note (from C1000-123 exam):** SAP automation requires activating the **Vision
> driver** in the Recorder, while control selectors for Windows applications can be
> identified directly without it.

---

## 3. Java Driver — Automating Java Applications

### Prerequisites & Setup

1. **IBM RPA Client must be installed** with the *Java Manager* component enabled.
   During the installer, ensure the **Java Manager** option is checked (it is not
   enabled by default — you must reinstall if it was missed).

2. **Java Access Bridge (JAB)** must be enabled on the target machine:
   - JAB is a Windows DLL that exposes the Java Accessibility API to external
     tools including IBM RPA.
   - Enable via `jabswitch -enable` in a command prompt, **or** through
     `Java Control Panel → Advanced → Accessibility → Enable Java Access Bridge`.
   - A system restart may be required after enabling.

3. **Java Runtime Environment (JRE/JDK)** — the target Java application and the
   IBM RPA agent machine must have a compatible 64-bit JRE installed.
   IBM RPA ships with **IBM Java SRE 8 x64** and keeps it updated with the latest
   security fixes.

4. The target application must implement the **Java Accessibility API** — standard
   Swing and AWT components do this automatically.

### Launching the Java Driver in the Recorder

1. Open IBM RPA Studio and open or create a WAL script.
2. Click **Recorder** in the toolbar.
3. In the *Start Recorder* dialog, select **Java** as the driver.
4. Launch or select the target Java application.
5. The recorder bar appears — hover over Java controls to highlight them and
   click to capture their selectors and generate commands.

### Key WAL Commands for Java Automation

Commands generated by the Java driver follow the same pattern as Windows driver
commands but use Java-specific selectors. Common commands:

| WAL Command | Purpose |
|---|---|
| `click` | Click a Java UI control (button, menu item, etc.) |
| `setText` | Type text into a Java text field or text area |
| `getText` | Read the current value of a Java text control |
| `check` / `uncheck` | Toggle a Java checkbox |
| `select` | Choose an item in a combo box / list |
| `waitForControl` | Wait until a Java control becomes available |
| `executeJavaScript` | Run JavaScript inside embedded browser panes |

> The exact command names generated depend on the recorder action; IBM RPA uses
> a unified command set across drivers (e.g., `click`, `getText`, `setText`).
> The *selector* string distinguishes Java controls from Windows controls.

### Selectors for Java Controls

Java selectors are built from accessibility attributes exposed via JAB, such as:

```
selector: "role=push button;name=Submit"
selector: "role=text;name=Username"
selector: "role=combo box;name=Country"
```

Attributes commonly available in Java selectors:

- `role` — control type (push button, text, combo box, check box, list, …)
- `name` — accessible name of the control (set via `setAccessibleName()`)
- `description` — accessible description
- `index` — position-based fallback when names are not unique

---

## 4. Vision Driver — Surface Automation

### When to Use the Vision Driver

The Vision driver (also called **Surface Automation**) is the fallback approach
when:

- The application is **not natively supported** by any other driver.
- The application runs inside a **virtual machine / Citrix / RDP** session.
- Selectors are **dynamic or unreliable** (e.g., controls change attributes at runtime).
- You need to automate a **legacy or proprietary** application with no accessibility API.
- You need to interact with **image-only content** (scanned PDFs, screenshots).

> IBM Support explicitly states: *"IBM RPA allows users to interact with elements
> by using images instead of selectors. This is useful when the selectors are
> dynamic or interacting with applications the recorder does not support."*

### How It Works

IBM RPA's proprietary Vision driver uses two core technologies:

1. **Pixel-by-pixel image comparison** — An *anchor image* (a screenshot of a UI
   element captured at record time) is compared against the live screen to locate
   the control. A **similarity threshold** (0–100%) controls how strict the match is.

2. **OCR (Optical Character Recognition)** — Text visible on screen is recognised
   without needing a selector. Useful for reading values in non-accessible controls
   or clicking buttons by their label text.

### Environment Setup for Reliable Results

Screen conditions directly affect image matching accuracy. IBM recommends:

| Setting | Recommended Value |
|---|---|
| Screen resolution | Match the resolution used during anchor image capture |
| Display scale (DPI) | 100% (do not use 125% / 150%) |
| Color depth | 32-bit |
| Window zoom | 100% |
| Window state | Always-on-top / in focus (use `setFocus` / `bringToFront`) |
| Theme | Consistent — do not allow Windows theme changes between record and run |

### Key WAL Commands for Surface Automation

| WAL Command | Purpose |
|---|---|
| `findImageBySimilarity` | Scan the screen (or a region/window) for an anchor image; returns coordinates |
| `waitForImage` | Block execution until an anchor image appears on screen (with timeout) |
| `clickImage` | Find an anchor image and click its centre |
| `clickImageByOCR` | Find visible text on screen using OCR and click it |
| `getControlTextByOCR` | Read text from a screen region using OCR and return it as a string |
| `recognizeImageTextOrPdf` | Extract all text from an image file or a PDF page using OCR |
| `waitForWindow` / `findWindow` | Locate a specific application window (used to scope image searches) |

> **Region scoping:** For image commands, you can scope the search to a specific
> window handle (via `waitForWindow`) to avoid false positives when the same image
> appears elsewhere on the screen (e.g., in a local vs. remote desktop session).

### OCR Commands

| WAL Command | Purpose |
|---|---|
| `clickByOCR` | Click a UI control identified by its visible text label |
| `getControlTextByOCR` | Extract text near an anchor image (anchor + offset region) |
| `recognizeImageTextOrPdf` | Batch OCR on a file; returns the full text |

**OCR accuracy tips:**
- Use high-contrast, legible fonts.
- Ensure the target text is not partially obscured or anti-aliased at small sizes.
- Set screen scale to 100% and avoid ClearType distortion at non-native resolutions.
- For PDF automation, prefer text-layer PDFs over image-only PDFs; use OCR only
  when the PDF has no selectable text layer.

### Best Practices & Guidelines

1. **Prefer native drivers first.** Use the Vision driver only when other drivers
   cannot map the control. Native selector-based automation is faster, more reliable,
   and resilient to layout changes.

2. **Capture clean anchor images.** Use a stable state of the application, with
   no transient highlights or tooltips. The anchor image should contain enough
   surrounding pixels to be unique on screen.

3. **Set an appropriate similarity threshold.** A threshold that is too high
   (e.g., 99%) causes fragile matches that break on minor pixel changes.
   A threshold that is too low (e.g., 60%) can produce false positives.
   Start at 85–90% and tune from there.

4. **Always focus the target window before image operations.** Use
   `setFocus` or `bringWindowToFront` to ensure the application is not
   obscured by other windows.

5. **Use `waitForImage` instead of `findImageBySimilarity` + manual sleep.**
   `waitForImage` handles timing natively and will retry until the image appears
   or the timeout expires, making scripts more resilient.

6. **Scope searches to a window/region.** Rather than scanning the full screen,
   pass a window context to image commands to reduce matching time and avoid
   false matches on multi-monitor setups.

7. **Citrix / RDP / VDI environments.** Surface automation is commonly the *only*
   viable option in virtualised desktops. In these cases, ensure the remote session
   resolution and DPI exactly match what was used during recording.

---

## 5. Java Driver vs Vision Driver — Decision Guide

```
Target application is a Java Swing/AWT app?
│
├─ YES ─► Does it use standard Swing/AWT controls?
│         │
│         ├─ YES ─► Use JAVA DRIVER
│         │         (JAB + recorder; reliable selectors)
│         │
│         └─ NO  ─► Does it embed non-accessible custom controls
│                   (e.g., canvas-drawn, WebView panes)?
│                   │
│                   ├─ YES ─► Use VISION DRIVER for those controls,
│                   │         JAVA DRIVER for standard controls
│                   └─ NO  ─► Use JAVA DRIVER
│
└─ NO  ─► Is the app running in Citrix/RDP/VDI?
          │
          ├─ YES ─► VISION DRIVER (only option in virtualised sessions)
          └─ NO  ─► Choose driver by technology:
                    Windows / SAP / Web / Terminal
```

---

## 6. References

| Source | URL |
|---|---|
| IBM Docs — Supported applications (23.0.x) | https://www.ibm.com/docs/en/rpa/23.0.x?topic=recorder-supported-applications |
| IBM Docs — Surface automation (21.0.x) | https://www.ibm.com/docs/en/rpa/21.0.x?topic=automation-surface |
| IBM Docs — Overview of surface automation (21.0.x) | https://www.ibm.com/docs/en/rpa/21.0.x?topic=automation-overview-surface |
| IBM Docs — Actions for surface automation (30.0.x) | https://www.ibm.com/docs/en/rpa/30.0.x?topic=automation-actions-surface |
| IBM Docs — Finding an image in the screen (23.0.x) | https://www.ibm.com/docs/en/rpa/23.0.x?topic=automation-finding-image-in-screen |
| IBM Docs — Click by OCR (30.0.x) | https://www.ibm.com/docs/en/rpa/30.0.x?topic=ocr-click-by |
| IBM Docs — Get control text by OCR (23.0.x) | https://www.ibm.com/docs/en/rpa/23.0.x?topic=automation-get-image-text |
| IBM Docs — WAL Commands reference (23.0.x) | https://www.ibm.com/docs/en/rpa/23.0.x?topic=commands |
| IBM Docs — Selectors (23.0.x) | https://www.ibm.com/docs/en/rpa/23.0.x?topic=automation-selectors |
| IBM Support — Vision driver instructions | https://www.ibm.com/support/pages/ibm-rpa-instructions-using-vision-driver |
| IBM Docs — Recorder overview (23.0.x) | https://www.ibm.com/docs/en/rpa/23.0.x?topic=recorder-overview |
| CP4BA Jam-in-a-Box — RPA Lab (Java Swing + Web) | https://ibm.github.io/cp4ba-jam-in-a-box/24.0.0/Robotic%20Process%20Automation/ |
| IBM CP4BA Labs GitHub (25.0.1) | https://github.com/IBM/cp4ba-labs/blob/main/25.0.1/Robotic%20Process%20Automation/README.md |
