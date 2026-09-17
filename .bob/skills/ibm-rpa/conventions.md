# IBM RPA WAL Coding Conventions

Standards and patterns for all WAL scripts generated or maintained in this project.

---

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Script files | `snake_case.wal` | `invoice_export.wal`, `order_processor.wal` |
| Variable names | `camelCase` | `invoiceNumber`, `rowCount`, `isSuccess` |
| Subroutine names | `PascalCase` | `Login`, `ProcessInvoice`, `Cleanup` |
| Boolean variables | `is` or `has` prefix | `isLoggedIn`, `hasErrors`, `isFileOpen` |
| Collection variables | plural noun | `invoiceRows`, `pendingOrders` |
| Connection handles | describe the resource | `dbConn`, `queueConn`, `excelApp`, `web01` |

---

## File Structure Template

Every new `.wal` file follows this exact layout:

```
# ── VARIABLE DECLARATIONS ──────────────────────────────────────────────────
defVar --name [var1] --type [Type]
...

# ── PROCESS VARIABLE BINDINGS (if BAW-integrated) ──────────────────────────
bindProcessVariables --mappings "..."

# ── MAIN FLOW ───────────────────────────────────────────────────────────────
goSub --label Init
goSub --label [CoreStep1]
goSub --label [CoreStep2]
goSub --label Cleanup

# ── SUBROUTINES ─────────────────────────────────────────────────────────────
beginSub --name Init
  ...
endSub

beginSub --name [CoreStep1]
  ...
endSub

beginSub --name Cleanup
  ...
endSub

# ── VERSION STAMP ────────────────────────────────────────────────────────────
* 30.0.2
```

---

## Subroutine Guidelines

### Required subroutines (every script)
| Subroutine | Purpose |
|---|---|
| `Init` | Open browser/file/connection; log start; set initial state |
| `Cleanup` | Close browser/file/connection; always called on success AND error |

### Standard subroutines (include when applicable)
| Subroutine | Purpose |
|---|---|
| `Login` | Authenticate to target application |
| `Logout` | Sign out cleanly before Cleanup |
| `ProcessItem` | Per-record business logic in a loop |
| `ErrorHandler` | Log + notify + call Cleanup on unrecoverable errors |
| `RetryWrapper` | Retry logic around a flaky operation |

### Logging template for each subroutine
```wal
beginSub --name ProcessInvoice
  logMessage --message "→ ProcessInvoice: start — invoice ${invoiceId}" --type "Info"
  
  # ... core logic ...

  logMessage --message "← ProcessInvoice: done" --type "Info"
endSub
```

---

## Security Rules

1. **No hardcoded credentials.** Passwords, API keys, and tokens MUST come from:
   - `bindProcessVariables` (passed by BAW at runtime), or
   - `getAsset --name "ASSET_NAME"   password=value` (IBM RPA Vault).

2. **No credential logging.** Do not include password variables in any `logMessage` call.
   Log a masked version if you must confirm identity: `logMessage --message "Logging in as ${username}"`.

3. **Minimal permissions.** The bot's IBM RPA service account should have access only
   to the queues, scripts, and vault assets it needs — nothing more.

---

## Web Automation Rules

### Mandatory wait-before-interact pattern
```wal
# CORRECT — always wait first
webWaitElement --selector "CssSelector" --css "#submit" --timeout "00:00:30"
webClick --selector "CssSelector" --css "#submit" --simulatehuman

# WRONG — do not interact without waiting
webClick --selector "CssSelector" --css "#submit" --simulatehuman
```

### Optional element check (check-then-act)
```wal
defVar --name elementFound --type Boolean

webWaitElement --selector "CssSelector" --css "#error-banner" --timeout "00:00:05"   elementFound=value
if --left "${elementFound}" --operator "Equal_To" --right "True"
  webGet --selector "CssSelector" --css "#error-banner"   errorText=value
  logMessage --message "Error banner detected: ${errorText}" --type "Warning"
endIf
```

### Retry pattern for transient failures
```wal
defVar --name retryCount --type Numeric
defVar --name maxRetries --type Numeric
defVar --name loginSuccess --type Boolean

setVar --name "${maxRetries}" --value "3"
setVar --name "${retryCount}" --value "0"
setVar --name "${loginSuccess}" --value "False"

while --left "${loginSuccess}" --operator "Equal_To" --right "False"
  if --left "${retryCount}" --operator "Greater_Than_Or_Equal" --right "${maxRetries}"
    logMessage --message "Max retries reached. Aborting." --type "Error"
    goSub --label Cleanup
    throwError --message "Login failed after ${maxRetries} attempts"
  endIf
  
  goSub --label AttemptLogin
  
  # AttemptLogin sets loginSuccess=True on success
  setVar --name "${retryCount}" --value "${retryCount} + 1"
endWhile
```

---

## Error Handling Patterns

### Standard error exit
```wal
# Always: log → cleanup → throw
logMessage --message "Fatal error in ProcessInvoice: ${errorMessage}" --type "Error"
goSub --label Cleanup
throwError --message "${errorMessage}"
```

### Soft failure (log and continue)
```wal
logMessage --message "Skipping invoice ${invoiceId}: amount is zero" --type "Warning"
# No throwError — loop continues to next item
```

---

## Queue / Dispatcher-Performer Pattern

For high-volume processing, split into two scripts:

**Dispatcher (`xxx_dispatcher.wal`):**
- Reads source data (database, Excel, API)
- Enqueues each work item as a queue message
- Each message contains all data needed to process one item

**Performer (`xxx_performer.wal`):**
- Loops: get queue item → process → mark complete/fail
- Exits cleanly when queue is empty (`mqGet` returns `success=False`)
- Marks item failed (not throws error) so other items continue processing

```wal
# Performer loop skeleton
while --left "True" --operator "Equal_To" --right "True"
  mqGet --connection "${queueConn}" --timeout "00:00:05"   queueItem=value hasItem=value
  if --left "${hasItem}" --operator "Equal_To" --right "False"
    logMessage --message "Queue empty — exiting" --type "Info"
    break
  endIf
  goSub --label ProcessItem
next
```

---

## BAW Integration Guidelines

When a WAL script is invoked from an IBM BAW workflow:

1. Use `bindProcessVariables` at the top of the script to receive input data.
2. Use `setProcessVariable` to write output data back to the BAW process.
3. Variable names in the mapping must exactly match the BAW process variable names.
4. Test with the IBM RPA Launcher before deploying to BAW.

```wal
# Receive inputs from BAW
bindProcessVariables --mappings "{\"customerId\":\"${customerId}\",\"orderAmount\":\"${orderAmount}\"}"

# ... processing ...

# Return outputs to BAW
setProcessVariable --name "processingStatus" --value "${status}"
setProcessVariable --name "confirmedOrderId" --value "${confirmedId}"
```

---

## Version Stamp

Every `.wal` file must end with a version comment on the final line:

```
* 30.0.2
```

Update this to reflect the IBM RPA server version when publishing.
