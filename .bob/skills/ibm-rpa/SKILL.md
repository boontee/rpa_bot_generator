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
`--flag value` named parameters. Variables are referenced as `${varName}` (without surrounding quotes when passed as a command parameter handle/reference, e.g. `--file ${excelApp}`). Use `"${varName}"` only inside string values, e.g. `--message "Processing ${itemId}"`.
Command output is captured with the `variableName=value` suffix.

```
commandName --param1 "value1" --param2 "value2"   outputVar=value
```

See `commands_kb.md` for the **full command reference** — all 27 categories
(data types, flow control, web/desktop/Java/SAP/terminal automation, Excel,
DataTable, file, DB, queue, HTTP, email, PDF, OCR, scripting) with exact
parameter names, output variable names, and working code snippets. This is
the **authoritative and primary command lookup** to use when writing, reviewing, or fixing any WAL script.
Commands marked `[30+]` in the KB were added in Studio 30.0.x; all others are available from 21.0.x.

**CRITICAL COMMAND VALIDATION RULE:**
- **Every command action used in a WAL script MUST exist in `commands_kb.md`.**
- If a command action is NOT present in `commands_kb.md`, it is considered **INVALID / NON-EXISTENT** and will cause Studio syntax errors (e.g., `Command 'xyz' not found`).
- Whenever an invalid, unlisted, or hallucinated command action is encountered or used, it **MUST be replaced immediately** with the valid equivalent command and parameter syntax documented in `commands_kb.md`.

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

## Confirmed Invalid Commands & Common Syntax Traps (Studio 30.x)

These commands and patterns were verified as non-existent, invalid, or broken in Studio 30.0.3.0 — do not use them:

| Invalid command / pattern | Correct replacement & rule |
|---|---|
| `throwException` | `throwError --message "..."` (general errors) or `failTest --message "..."` (test failures) |
| `getRegex --regex "..."` | `getRegex --text "${source}" --regexPattern "..." extracted=value` (flag name is `--regexPattern`) |
| `setVar --name "${x}" --value "${x} + 1"` | `evaluate --expression "${x} + 1" x=value` — `setVar` does NOT evaluate arithmetic expressions |
| `setVar --name "varName"` (quoted literal) | ❌ Wrong form — assigns to a variable literally named `varName` (the string), not the declared WAL variable. Use `setVar --name ${varName}` instead. |
| `incrementVar --number "${n}"` | `incrementVar --number ${n}` (and `decrementVar`) — use `${n}` without surrounding quotes |
| `bindProcessVariables --mappings "{\"k\":\"${v}\"}"` | Causes `Variable.Parse(null)` crash in Studio 30.x — remove entirely; pass file paths via a parent script or `setVar` defaults instead |
| `getProcessVariable --name "k" v=value` | Not a recognised command in Studio 30.x — do not use |
| `${rpa:error.Message}` / `${rpa:error.Routine}` / `${rpa:error.LineNumber}` in `logMessage` | Causes `Variable.Parse(null)` WARN in Studio 30.x — use a plain string message in `ErrorHandler` instead |
| `if --left ${var} --operator "Equal_To" --right ""` | ❌ Not valid — `Equal_To ""` is not a supported null/empty check. Use `if --left ${var} --operator "Is_Null"` to check for null/uninitialised handles |
| Quoted booleans e.g. `--readOnly "true"` | Unquoted boolean literals: `--readOnly true` or `--readOnly false` |
| Direct Excel row deletion commands | In-memory DataTable filtering workaround: `excelGetTable` → `deleteRows` → `excelCreateFromDataTable` → `excelSave` |

> **Background noise — Studio 30.x known bug:** A `WARNParserServiceStudio Value cannot be null. Parameter name: source` entry in `Studio.log` appears on **every** script parse regardless of script content. It is a Studio 30.x internal parser defect in `Variable.Parse(String source)` and does **not** indicate a problem with the WAL script. Ignore this WARN when no `ERROR` lines are present.

**Commands confirmed VALID in Studio 30.x:**

| Command / Pattern | Notes & Usage |
|---|---|
| `defList --name x --type StringList` | Valid; use `listAdd`, `listGetAt`, `listCount`, `listRemoveAt`, `listClear` |
| `defDataTable --name x` | Valid shorthand; `defVar --name x --type DataTable` is equivalent |
| `fileExists --path "${p}" exists=value` | Valid in Studio 30.x; alternative `ifFile --file "${p}" exists=value` |
| `throwError --message "..."` | ❌ NOT valid in Studio 30.0.3 — `Command 'throwError' not found`; use `stopExecution` instead |
| `excelGetLastRow` | ❌ NOT valid in Studio 30.0.3 — `Command 'excelGetLastRow' not found`; row count is returned directly by `excelGetTable ... rows=value` |
| `setVar --name ${varName} --value "..."` | ✅ Confirmed correct — `--name` takes the variable reference `${varName}` (no surrounding quotes), e.g. `setVar --name ${sourceFile} --value "path"` |
| `→` `←` arrow chars in `logMessage` strings | Valid in Studio 30.x log messages |
| `dbQuery --parameters "{\"id\":\"${val}\"}"` | Valid for parameterized SQL queries preventing SQL injection |
| `runCSharpCode --code "..."` | Valid [30+] for inline C# execution |
| `executeScript --script "Name" --tenant "${id}"` | Valid [30.0.1+] for invoking modular WAL scripts |

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
```

> **Note:** Do NOT include `*30.0.3.0` in `.wal.txt` source files. The version marker is part of the protobuf binary suffix appended automatically by `wal_generator.py` from the template. Including it as text causes Studio to report `Command '*30.0.3.0' not found`.

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
4. **Validate every command against `commands_kb.md`** — look up every intended command action in `commands_kb.md` first. If a command action is not in `commands_kb.md`, do not use it; find the valid supported alternative. Verify exact parameter names, output variable names (`var=value`), and required flags.
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
getRegex --text ${dosOutput} --regex "RESULT:([^,\r\n]+)"            result1=value
getRegex --text ${dosOutput} --regex "RESULT:[^,\r\n]+,([^,\r\n]+)" result2=value
// Or split a pipe-delimited list into a List variable
textSplit --text ${dosOutput} --separator "|"   itemList=value
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

## Domain-Specific Quick Rules

### Desktop / Java / SAP Automation
- **Windows Desktop:** Use `launchWindow` or `launchOrAttach` followed by `attachWindow`. Always use `waitWindow --title "..." --timeout "..."` for stabilization.
- **Java Swing:** Requires JAB enabled (`jabswitch -enable`). Selectors use Accessibility role XPath names (`push_button`, `text`, `check_box`, `combo_box`, `table`, `tree`, `panel`). Always capture Java XPaths using IBM RPA Studio Recorder with the Java driver rather than guessing.
- **SAP GUI:** Requires Vision driver in Recorder or SAP GUI Scripting enabled. Use `sapOpen`, `sapSet --field "..." --value "..."`, `sapClick --button "..."`, `sapClose`.
- **Terminal (Mainframe/3270/5250):** Use `terminalConnect --emulationtype "IBM3270"`, wait for screen with `terminalWait`, read with `terminalGetText`, write with `terminalSetText`, and send keys with `terminalSendKey`.

### Excel & DataTable Automation
- Open workbooks with `excelOpen --file "${filePath}"   excelApp=value` — confirmed IBM docs 30.0.x syntax (`--file` not `--path`, no `--readOnly`).
- Read ranges into DataTable with `excelGetTable --file ${excelApp} --getfirstsheet --entiretable --hasheaders   tableData=value rows=rowCount`.
- Row count returned directly by `excelGetTable rows=rowCount` — no separate row-count command needed.
- To delete rows from Excel, use the in-memory pattern (`excelGetTable` → `deleteRows` → `excelCreateFromDataTable` → `excelSave`).
- Always close Excel handles in `Cleanup` guarded with `Is_Null` check: `if --left ${excelApp} --operator "Is_Null" --negate` then `excelClose --file ${excelApp}`. `Is_Not_Empty` and `Equal_To ""` are NOT valid operators in Studio 30.0.3.

### Databases & Queues
- **Databases:** Use `dbConnect` with provider (`SqlServer`, `Oracle`, `PostgreSQL`, `MySQL`, `DB2`, `ODBC`) or embedded `sqliteConnect`. Always use parameterized queries via `--parameters "{\"key\":\"${val}\"}"` in `dbQuery` to prevent SQL injection.
- **Queues:** Use `mqConnect`, non-blocking fetch with `mqGet --timeout "00:00:05" message=value success=value`. Acknowledge with `mqComplete` or fail with `mqFail`.

## Pre-Output Checklist

Before writing the final WAL text source, verify:
- [ ] Output file has `.wal.txt` extension — NEVER `.wal`
- [ ] All command actions used exist in `commands_kb.md` (no hallucinated or unlisted command actions)
- [ ] All variables declared at the top with correct types (`defVar`, `defList`, `defDataTable`)
- [ ] Process variable integration uses valid syntax supported by the target Studio version
- [ ] Main flow contains only `goSub` calls — no logic or direct actions
- [ ] Every web interaction is preceded by `webWaitElement` with timeout
- [ ] Web elements use highest available selector priority (`#id` → `[data-testid]` → `[aria-label]` → `.class`) — avoid `nth-child`
- [ ] Web input/click commands include `--simulatehuman` for stability
- [ ] No hardcoded credentials anywhere — loaded via `getAsset` or process variables
- [ ] `Cleanup` subroutine closes browser, Excel, DB, queues, and all open connections
- [ ] `Cleanup` is called on both success and error paths
- [ ] `onError --label ErrorHandler` at the top of every subroutine (except `ErrorHandler` and `Cleanup`)
- [ ] `logMessage` at the start (`→ SubName: start`) and end (`← SubName: done`) of each subroutine
- [ ] Arithmetic uses `evaluate --expression "..." var=value` (not `setVar` with an expression)
- [ ] `incrementVar` / `decrementVar` uses `--number ${n}` without quotes
- [ ] `setVar --name ${varName}` — use `${}` without surrounding quotes; `setVar --name "varName"` (quoted literal string) is the wrong form and assigns to a phantom variable named `varName`
- [ ] Booleans in parameters are unquoted literals (`--readOnly false`, `--ssl true`, `--ascending true`)
- [ ] Do NOT include `*30.0.3.0` in the `.wal.txt` — the version suffix is appended by `wal_generator.py` from the template binary

## Fixing Script Errors

When the user reports a script error (Studio parse error, runtime error, or "error parsing script"):

### Step 1 — Read the Studio log FIRST

**Always read the Studio log before looking at the script.** The log contains the exact error
message, line number, and context that makes the fix unambiguous.

Log path (default, can be overridden via `RPA_STUDIO_LOG`, `STUDIO_LOG_PATH`, or `STUDIO_LOG` environment variable):
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
| `NullReferenceException` in a sub | Uninitialised handle (e.g. `excelClose ""`) | Guard with `Is_Null --negate`: `if --left ${handle} --operator "Is_Null" --negate` |
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
