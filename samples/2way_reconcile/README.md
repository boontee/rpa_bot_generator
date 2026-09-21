# 2-Way Reconciliation Bot Sample

An automated two-way reconciliation bot implemented in IBM RPA WAL scripting language. It reconciles records between a **Source** Excel spreadsheet and a **Target** Excel spreadsheet, categorizing records and writing a detailed summary report.

---

## Overview

The bot performs a complete two-way key/value comparison between two Excel files:

```
┌──────────────────┐        ┌──────────────────┐
│   Source Excel   │        │   Target Excel   │
│ (Key, Value ...) │        │ (Key, Value ...) │
└────────┬─────────┘        └────────┬─────────┘
         │                           │
         └─────────────┬─────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │ 2-Way Reconcile Logic │
           └───────────┬───────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │      Report Excel     │
           │  • MATCHED            │
           │  • MISMATCH           │
           │  • MISSING IN TARGET  │
           │  • MISSING IN SOURCE  │
           │  • Summary Counts     │
           └───────────────────────┘
```

### Reconciliation Categories

| Status | Condition | Description |
|---|---|---|
| **`MATCHED`** | `Source Key == Target Key` AND `Source Value == Target Value` | Record exists in both files with matching values. |
| **`MISMATCH`** | `Source Key == Target Key` AND `Source Value != Target Value` | Record exists in both files, but values differ. |
| **`MISSING IN TARGET`** | `Source Key` not found in Target | Record exists in Source but missing from Target. |
| **`MISSING IN SOURCE`** | `Target Key` not found in Source | Record exists in Target but missing from Source. |

---

## Files in this Sample

| File | Type | Description |
|---|---|---|
| [`reconcile_bot.wal.txt`](reconcile_bot.wal.txt) | Source | Plain UTF-8 WAL script source (editable). |
| [`reconcile_bot.wal`](reconcile_bot.wal) | Binary | Compiled Protobuf binary script for IBM RPA Studio. |
| [`source.xlsx`](source.xlsx) | Excel Data | Sample Source dataset (Key in Col 1, Value in Col 2). |
| [`target.xlsx`](target.xlsx) | Excel Data | Sample Target dataset (Key in Col 1, Value in Col 2). |
| [`report.xlsx`](report.xlsx) | Excel Report | Generated reconciliation report output with detailed status and summary totals. |

---

## Architecture & Subroutine Flow

The bot follows the standard IBM RPA modular subroutine structure:

1. **`Init`**: Configures file paths (`sourceFile`, `targetFile`, `reportFile`) and resets status counters (`matchedCount`, `mismatchCount`, etc.).
2. **`LoadSourceFile`**: Validates file existence with `ifFile`, opens `source.xlsx`, and loads rows into `sourceTable` via `excelGetTable`.
3. **`LoadTargetFile`**: Validates file existence, opens `target.xlsx`, and loads rows into `targetTable` via `excelGetTable`.
4. **`Reconcile`**: Compares each source row against target rows, categorizing as `MATCHED`, `MISMATCH`, or `MISSING IN TARGET`.
5. **`FlagMissingInSource`**: Scans target rows against source rows to identify items `MISSING IN SOURCE`.
6. **`WriteReportSummary`**: Appends overall summary metrics (Matched, Mismatch, Missing counts) and exports `reportTable` to `report.xlsx` via `excelReport`.
7. **`Cleanup`**: Safely closes all open Excel application handles (`sourceApp`, `targetApp`, `reportApp`) with null-safe checks.
8. **`ErrorHandler`**: Logs errors with `onError` handling and ensures `Cleanup` is always executed before stopping execution.

---

## How to Run

### Option 1: Open in IBM RPA Studio
1. Launch **IBM RPA Studio**.
2. Open [`reconcile_bot.wal`](reconcile_bot.wal).
3. Click **Start Execution** (F5) or debug step-by-step.

### Option 2: Regenerate Binary from Source
If modifying [`reconcile_bot.wal.txt`](reconcile_bot.wal.txt), recompile the binary using `wal_generator.py`:

```powershell
py tools/wal_generator.py --template template/template.wal `
  --script samples/2way_reconcile/reconcile_bot.wal.txt `
  --output samples/2way_reconcile/reconcile_bot.wal
```
