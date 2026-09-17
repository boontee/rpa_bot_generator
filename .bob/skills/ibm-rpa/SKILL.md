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

See `wal-reference.md` for the full command reference, organized by category.
See `examples/` for complete, working script patterns.

## Mandatory Script Structure

Every generated script MUST follow this exact layout — top to bottom:

```
1. defVar declarations          (ALL variables, declared before any logic)
2. defList / defDataTable       (collection types, if needed)
3. bindProcessVariables         (if the bot is called from IBM BAW/workflow)
4. Main flow: goSub calls only  (readable, one-line-per-step overview)
5. beginSub --name Init ... endSub
6. beginSub --name [CoreLogicA] ... endSub
7. beginSub --name [CoreLogicB] ... endSub
8. beginSub --name ErrorHandler ... endSub
9. beginSub --name Cleanup ... endSub   (ALWAYS last — must close browser/files)
* VERSION                        (IBM RPA version stamp on the very last line)
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

### Error Handling
- All web `webWaitElement` calls that check for an optional element must capture output
  (`success=value`) and handle the `True`/`False` result with an `if` block.
- Always call `goSub --label Cleanup` before `throwError` or exiting with an error.

## Step-by-Step: Generating a New Script

1. **Read the process description** — identify: inputs (process variables), outputs, steps,
   expected errors, browser/app/file targets.
2. **Draft the variable list** — every value used anywhere needs a `defVar`.
3. **Map subroutines** — one subroutine per logical phase. Always include `Cleanup`.
4. **Write the script top-down** in the structure order above.
5. **Review against the checklist** before presenting the output.

## Pre-Output Checklist

Before writing the final `.wal` file, verify:
- [ ] All variables declared at the top with correct types
- [ ] `bindProcessVariables` present if any variables come from BAW
- [ ] Main flow contains only `goSub` calls
- [ ] Every web interaction is preceded by `webWaitElement`
- [ ] No hardcoded credentials anywhere
- [ ] `Cleanup` subroutine closes browser and all open files/connections
- [ ] `Cleanup` is called on both success and error paths
- [ ] `logMessage` at the start and end of each subroutine
- [ ] File ends with `* VERSION` stamp

## Editing Existing Scripts

When asked to edit a `.wal` file:
1. Read the full file first — understand the existing subroutine structure.
2. Make the minimal change that satisfies the request.
3. Do not rearrange unrelated subroutines or reformat lines you are not changing.
4. Re-run the pre-output checklist on the changed sections only.
