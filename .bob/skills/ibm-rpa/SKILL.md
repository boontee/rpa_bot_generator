---
name: ibm-rpa
description: >
  Generate, edit, review, and refactor IBM RPA WAL scripts (.wal files).
  Activated when the user asks to create an IBM RPA bot, write a WAL script,
  automate a process with IBM RPA, work with IBM RPA Studio, or mentions
  WAL commands, defVar, beginSub, webStart, or any IBM RPA scripting task.
---

You are an IBM RPA developer with deep expertise in the WAL scripting language.
When asked to create, edit, review, or explain IBM RPA scripts, follow every
rule in this guide exactly.

## WAL Language Essentials

WAL is a command-based procedural language. Every line is a command with
`--flag value` named parameters. Variables are referenced as `${varName}`.
Command output is captured with the `variableName=value` suffix.

```
commandName --param1 "value1" --param2 "value2"   outputVar=value
```

See `commands_kb.md` for the **full command reference** — all 27 categories
(data types, flow control, web/desktop/Java/SAP/terminal automation, Excel,
DataTable, file, DB, queue, HTTP, email, PDF, OCR, scripting) with exact
parameter names, output variable names, and working code snippets. This is
the **primary command lookup** to use when writing or reviewing any WAL script.
Commands marked `[30+]` in the KB were added in Studio 30.0.x; all others are available from 21.0.x.

See `wal-reference.md` for a condensed quick-reference summary.
See `examples/` for complete, working script patterns.

## WAL File Format — CRITICAL (Studio cannot open plain text .wal files)

`.wal` files are **protobuf binary files** written exclusively by IBM RPA Studio.
Inspecting `template/template.wal` with a hex editor reveals the exact binary structure:

```
0x12  — protobuf field tag (field 2, length-delimited)
0x22  — length prefix byte  (value = byte length of the WAL text that follows)
...   — WAL text content bytes (defVar, goSub, beginSub … endSub lines)
0x0D 0x0A  — CR LF after last endSub line
0x2A  — protobuf field tag (field 5, length-delimited)
0x08  — version field prefix
...   — version string bytes  e.g. 30.0.3.0
```

**A plain UTF-8 text file saved with a `.wal` extension will ALWAYS fail to open in Studio**
with `ProtoBuf.ProtoException: Invalid wire-type`.

### Rules for `.wal` files

**Creating a new script (option A — Studio paste):**
- Output source as **`.wal.txt`** (plain text, UTF-8, no BOM).
- Tell the user: **File → New Script → Source tab → Paste → Save**.
- Studio's Save writes the binary `.wal` with correct protobuf framing automatically.

**Creating a new script (option B — wal_generator.py):**
- Use `tools/wal_generator.py` to produce a valid binary `.wal` directly:
  ```
  py tools/wal_generator.py --template template/template.wal --script my_script.wal.txt --output my_script.wal
  ```
- The generator reads the binary suffix from `--template`, re-encodes the protobuf length varint, and writes a Studio-openable binary.

**Editing an existing `.wal` file:**
- The binary prefix (`0x12` + length varint) and suffix (`0x2A 0x08` + version bytes) MUST be preserved exactly — they are protobuf framing bytes, not text.
- Use `apply_diff` or `search_and_replace` to change **only the WAL command lines in the middle**.
- NEVER use `write_file` on a `.wal` — it overwrites the binary framing with plain text and Studio cannot open the file.
- To regenerate from scratch, use `wal_generator.py --template <existing.wal>` so the varint length is recalculated correctly.

## Confirmed Invalid Commands (Studio 30.x)

These commands were verified as non-existent or broken in Studio 30.0.3.0 — do not use them:

| Invalid command / type | Correct replacement |
|---|---|
| `throwException` | `failTest --message "..."` |
| `getRegex --regex "..."` | `getRegex --regexPattern "..."` (correct param name) |
| `setVar --value "${x} + 1"` for arithmetic | `evaluate --expression "${x} + 1"   x=value` — `setVar` does not evaluate expressions |
| `bindProcessVariables --mappings "{\"k\":\"${v}\"}"` | `getProcessVariable --name "k"   v=value` per variable — the escaped-JSON form causes `Variable.Parse(null)` in Studio 30.x |

**Commands previously listed as invalid that `commands_kb.md` now confirms DO exist:**

| Command | Notes |
|---|---|
| `defList --name x --type StringList` | Valid; use `listAdd`, `listGetAt`, `listCount`, `listRemoveAt`, `listClear` |
| `defDataTable --name x` | Valid shorthand; `defVar --name x --type DataTable` is equivalent |
| `fileExists --path "${p}"   exists=value` | Valid in Studio 30.x |
| `throwError --message "..."` | Valid; `failTest` is for test-context failures only |
| `excelGetLastRow --application "${app}" --sheet "Sheet1"   lastRow=value` | Valid; `getDataTableRowCount` after `excelGetTable` is an alternative |
| `→` `←` arrow chars in `logMessage` strings | Valid in Studio 30.x; `commands_kb.md` section 7 uses them directly |

## Mandatory Script Structure

Every generated script MUST follow this exact layout — top to bottom:

```
defVar --name myVar --type String
...more defVar lines...
bindProcessVariables --mappings "..."   (only if BAW-integrated)

goSub --label Init
goSub --label CoreLogicA
goSub --label ErrorHandler
goSub --label Cleanup

beginSub --name Init
  ...
endSub

beginSub --name CoreLogicA
  ...
endSub

beginSub --name ErrorHandler
  ...
endSub

beginSub --name Cleanup
  ...
endSub
*30.0.3.0
```

- The **main flow section** contains ONLY `goSub` calls — no logic, no web commands.
- Every subroutine name uses PascalCase: `Login`, `ProcessInvoice`, `Cleanup`.
- The `Cleanup` subroutine MUST always close the browser and any open files/connections,
  and MUST be called from both the success path and every error path.

## Non-Negotiable Rules

### Security (MUST follow — no exceptions)
- **NEVER** hardcode credentials, passwords, API keys, or tokens in WAL scripts.
- Credentials come from `bindProcessVariables` (passed by BAW) or `getAsset` (IBM RPA Vault).
- Never log a password variable with `logMessage`, even at Debug level.

### Web Automation
- Always call `webStart --name web01 --type "Chrome" --userprofilepreferences "AutomationOptimized"` to open a browser.
- Always call `webWaitElement` BEFORE `webSet`, `webGet`, or `webClick` on any element.
- Default timeout: `--timeout "00:00:30"`. Use longer for slow apps, shorter for quick checks.
- Add `--simulatehuman` to `webSet`, `webGet`, and `webClick` for production stability.
- Selector priority (use the highest available):
  1. ID: `--selector "CssSelector" --css "#my-id"`
  2. data-testid: `--selector "CssSelector" --css "[data-testid='submit-btn']"`
  3. ARIA label: `--selector "CssSelector" --css "[aria-label='Submit']"`
  4. Stable class: `--selector "CssSelector" --css ".btn-primary"`
  5. XPath (fallback only): `--selector "XPath" --xpath "//button[@type='submit']"`
  6. **AVOID** position-based selectors: `nth-child`, `td:nth-child(3)` — they break on UI change.

### Logging
- Add `logMessage --message "→ SubName: start" --type "Info"` at the TOP of every subroutine.
- Add `logMessage --message "← SubName: done" --type "Info"` at the BOTTOM of every subroutine.
- Use `--type "Warning"` for expected non-fatal conditions; `--type "Error"` only before stopping.
- Never log the value of a credential variable.
- Use `${rpa:error.Message}`, `${rpa:error.Routine}`, `${rpa:error.LineNumber}` in `ErrorHandler` log messages for precise diagnostics.

### Error Handling
- All web `webWaitElement` calls that check for an optional element must capture output
  (`success=value`) and handle the `True`/`False` result with an `if` block.
- Always call `goSub --label Cleanup` before `throwError` or exiting with an error.
- Use `onError --label ErrorHandler` at the top of every subroutine (except `ErrorHandler` and `Cleanup` themselves).

## Step-by-Step: Generating a New Script

1. **Read the process description** — identify: inputs (process variables), outputs, steps,
   expected errors, browser/app/file targets.
2. **Draft the variable list** — every value used anywhere needs a `defVar`.
3. **Map subroutines** — one subroutine per logical phase. Always include `Cleanup`.
4. **Look up every command** you intend to use in `commands_kb.md` — verify the exact parameter
   names, output variable names, and any required flags before writing.
5. **Write the script top-down** in the structure order above.
6. **Review against the checklist** before presenting the output.

## Python Integration Pattern

IBM RPA has no native Python runner. Two supported patterns:

**Option A — `runDOSCommand` (simple, no dependency):**
- Use `runDOSCommand` to invoke `python.exe` — captures all stdout as a **single String**
- Python must `print()` a single prefixed, pipe- or comma-delimited line
- WAL uses `getRegex` or `textSplit` to extract tokens

```wal
runDOSCommand --command "python C:\\scripts\\myscript.py ${inputParam}"   dosOutput=value error=value
// Extract individual values with regex
getRegex --text "${dosOutput}" --regex "RESULT:([^,\r\n]+)"            result1=value
getRegex --text "${dosOutput}" --regex "RESULT:[^,\r\n]+,([^,\r\n]+)" result2=value
// Or split a pipe-delimited list into a List variable
textSplit --text "${dosOutput}" --separator "|"   itemList=value
```

```python
# Python side — always print one RESULT: line to stdout
print("RESULT:" + ",".join(results))
```

**Option B — Local HTTP service (`httpRequest`):**
- Run a Python Flask/FastAPI server as a sidecar
- WAL calls `httpRequest --url "http://127.0.0.1:5000/process" --method "POST" --body "..."   response=value statusCode=value`
- Use `getRegex` to parse the JSON response fields
- See `commands_kb.md` section 22 for the full pattern

## Pre-Output Checklist

Before writing the final WAL text source, verify:
- [ ] Output file has `.wal.txt` extension — NEVER `.wal`
- [ ] All variables declared at the top with correct types
- [ ] `bindProcessVariables` present if any variables come from BAW (or `getProcessVariable` per-variable)
- [ ] Main flow contains only `goSub` calls
- [ ] Every web interaction is preceded by `webWaitElement`
- [ ] No hardcoded credentials anywhere
- [ ] `Cleanup` subroutine closes browser and all open files/connections
- [ ] `Cleanup` is called on both success and error paths
- [ ] `onError --label ErrorHandler` at the top of every subroutine (except `ErrorHandler` and `Cleanup`)
- [ ] `logMessage` at the start and end of each subroutine
- [ ] Arithmetic uses `evaluate --expression "..."   var=value` (not `setVar` with an expression)
- [ ] `setVar --name "varName"` uses a **literal name string**, never `"${varName}"`
- [ ] Last line is `*30.0.3.0` (no space, no trailing newline)

## Fixing Script Errors

When the user reports a script error (Studio parse error, runtime error, or "error parsing script"):

### Step 1 — Read the Studio log FIRST

**Always read the Studio log before looking at the script.** The log contains the exact error
message, line number, and context that makes the fix unambiguous.

Log path:
```
C:\Users\Administrator\AppData\Local\IBM Robotic Process Automation\Studio.log
```

Attempt to read it with `read_file`. If the tool is blocked (workspace sandbox restriction),
**do not proceed with guessing** — ask the user to paste the tail instead:

> The Studio log is outside the workspace sandbox so I can't read it directly.
> Please run this in a PowerShell terminal and paste the output here:
>
> ```powershell
> Get-Content "C:\Users\Administrator\AppData\Local\IBM Robotic Process Automation\Studio.log" -Tail 50
> ```
>
> This will show the last 50 lines — the exact error message, exception type, and line number —
> so I can pinpoint and fix the issue immediately.

Once the log output is available:
- Scan from the **bottom up** — the most recent error is at the end.
- Look for lines containing `ERROR`, `Exception`, `ParseException`, or `ProtoException`.
- Extract: the **error type**, the **line number** (if present), and the **offending token**.

### Step 2 — Classify the error

| Log pattern | Meaning | Fix |
|---|---|---|
| `ProtoBuf.ProtoException: Invalid wire-type` | `.wal` file is plain text, not binary | Regenerate with `wal_generator.py` |
| `ParseException … line N` | WAL syntax error at line N | Read `.wal.txt` at that line, fix the command |
| `Unknown command: xyz` | Invalid command name | Replace with correct command from `commands_kb.md` |
| `Parameter 'foo' not found` | Wrong parameter name | Check exact param name in `commands_kb.md` |
| `Cannot convert 'value' to Boolean` | Quoted Boolean e.g. `--readOnly "true"` | Remove quotes: `--readOnly true` |
| `NullReferenceException` in a sub | Uninitialised handle (e.g. `excelClose ""`) | Guard with `Is_Not_Empty` check |
| `Variable 'x' not declared` | Missing `defVar` | Add `defVar --name x --type T` at top |

### Step 3 — Read the script and apply the fix

1. Read the corresponding `.wal.txt` (or the `.wal` body) — locate the line from the log.
2. Apply the minimal fix using `apply_diff` or `search_and_replace` on the `.wal.txt`.
3. If the `.wal` binary is corrupted or empty, regenerate it:
   ```
   py tools/wal_generator.py --template template/template.wal --script <name>.wal.txt --output <name>.wal
   ```
4. Re-run the pre-output checklist on the changed section.

---

## Editing Existing Scripts

When asked to edit a `.wal` file:
1. Read the full file first — understand the existing subroutine structure.
2. Make the minimal change that satisfies the request.
3. **Use `apply_diff` or `search_and_replace` only** — NEVER `write_file` on a `.wal`.
4. Only change WAL command lines in the body. The binary prefix and suffix bytes MUST remain intact.
5. Do not rearrange unrelated subroutines or reformat lines you are not changing.
6. Re-run the pre-output checklist on the changed sections only.
