# Knowledge Base: Using IBM Bob to Generate IBM RPA Bots

> **Last updated:** 2025  
> **Scope:** How IBM Bob (AI coding agent) can be used to author, scaffold, and maintain IBM RPA `.wal` bot scripts.

---

## 1. Understanding IBM RPA Bot Scripts

### 1.1 IBM RPA Architecture

IBM RPA bots are **WAL scripts** (`.wal` files) — a proprietary procedural scripting language authored inside **IBM RPA Studio**. A script is the core unit of automation: it contains variables, subroutines, commands, and control flow that define what the bot does.

```
IBM RPA Ecosystem
├── IBM RPA Studio     — Low-code + script IDE for authoring .wal files
├── IBM RPA Server     — Orchestrates, schedules, and monitors bot execution
├── IBM RPA Agent      — Runtime that executes bots on the target machine
└── IBM RPA Vault      — Credential and asset store for bots
```

### 1.2 WAL Script Language Fundamentals

WAL is a **command-based procedural language** where each line is a command with named parameters using `--flag value` syntax. Variables are referenced with `${varName}`.

**Core constructs:**

| Construct | WAL Syntax |
|---|---|
| Declare variable | `defVar --name myVar --type String` |
| Set variable | `setVar --name "${myVar}" --value "hello"` |
| Call subroutine | `goSub --label MySubName` |
| Begin subroutine | `beginSub --name MySubName` |
| End subroutine | `endSub` |
| If/else | `if --left "${x}" --operator "Equal_To" --right "5"` / `else` / `endIf` |
| For loop | `for --variable ${i} --from 1 --to 10 --step 1` / `next` |
| Log message | `logMessage --message "Processing ${item}" --type "Info"` |
| Capture output | `someCommand ... variableName=value` |

**Data types:** `String`, `Numeric`, `Boolean`, `DateTime`, `QueueConnection`, `MessageQueue`, `List`, `DataTable`

**Real script example** (from IBM cp4ba-labs):
```wal
defVar --name companyName --type String
defVar --name counter --type Numeric
defVar --name success --type Boolean

bindProcessVariables --mappings "{\"companyName\":\"${companyName}\"}"
webStart --name web01 --type "Chrome" --userprofilepreferences "AutomationOptimized"
goSub --label Login
goSub --label ProcessData

beginSub --name Login
  webNavigate --url "https://app.example.com/login"
  webWaitElement --selector "CssSelector" --css "#username" --timeout "00:00:30"
  webSet --value "${username}" --selector "CssSelector" --css "#username"
  webSet --value "${password}" --selector "CssSelector" --css "#password"
  webClick --selector "CssSelector" --css "#login-btn"
endSub

beginSub --name ProcessData
  webWaitElement --selector "CssSelector" --css "#data-table" --timeout "00:00:20"
  webGet --selector "CssSelector" --css "#result-field" success=value
endSub
```

### 1.3 WAL Command Categories

IBM RPA Studio provides commands organized into these categories:

| Category | Key Commands |
|---|---|
| **Web Automation** | `webStart`, `webNavigate`, `webSet`, `webGet`, `webClick`, `webWaitElement`, `webClose`, `webSetComboBox` |
| **Smart Web (Browser Extension)** | `openBrowser`, `selectItem`, `typeText`, `clickElement` |
| **Desktop / Windows UI** | `windowOpen`, `windowSet`, `windowGet`, `windowClick`, `mouseClick`, `keyPress` |
| **Excel / Office** | `excelOpen`, `excelReadCell`, `excelWriteCell`, `excelClose`, `excelGetRows` |
| **File & Folder** | `fileRead`, `fileWrite`, `fileDelete`, `folderCreate`, `fileCopy` |
| **Data & Variables** | `defVar`, `setVar`, `defList`, `listAdd`, `defDataTable` |
| **Control Flow** | `if`/`else`/`endIf`, `for`/`next`, `while`/`endWhile`, `goSub`, `break` |
| **SAP** | `sapOpen`, `sapSet`, `sapGet`, `sapClick`, `sapClose` |
| **Database** | `dbConnect`, `dbQuery`, `dbExecute`, `dbClose` |
| **Queue / MQ** | `mqConnect`, `mqGet`, `mqPut`, `mqClose` |
| **PDF / OCR** | `ocrReadText`, `pdfExtractText`, `pdfOpen` |
| **Email** | `emailConnect`, `emailSend`, `emailGet` |
| **System / OS** | `powerShell`, `runDOSCommand`, `getSpecialFolder`, `getCurrentDateAndTime` |
| **Process Variables** | `bindProcessVariables`, `setProcessVariable` |
| **Logging** | `logMessage`, `logError` |

---

## 2. How IBM Bob Can Help Generate IBM RPA Bots

Bob is not natively aware of WAL syntax by default, but can be configured to generate high-quality `.wal` scripts through several complementary approaches. These are ordered from lowest to highest effort/complexity.

---

### 2.1 Approach 1 — Chat-Based Script Generation (Zero Setup)

**Use when:** You need a quick `.wal` script and want to describe the process in natural language.

**How it works:**  
Bob's Agent mode can generate WAL scripts directly when given sufficient language context. Provide the WAL syntax rules and a process description in your prompt.

**Prompt template:**
```
You are an IBM RPA developer. Generate an IBM RPA WAL script (.wal file) for the following process:

PROCESS: {describe the process step by step}

WAL LANGUAGE RULES:
- Each line is a command with --flag value parameters
- Variables declared with: defVar --name myVar --type String|Numeric|Boolean|DateTime
- Variables referenced as: ${myVar}
- Subroutines: beginSub --name SubName ... endSub, called with goSub --label SubName
- Capture output: commandName ... variableName=value
- If: if --left "${x}" --operator "Equal_To|Not_Equal|Greater_Than|Less_Than" --right "value"
- For loop: for --variable ${i} --from 1 --to 10 --step 1 ... next
- Web: webStart --name web01 --type "Chrome", webNavigate --url "...", webSet --value "..." --selector "CssSelector" --css "...", webGet --selector "CssSelector" --css "..." varName=value, webClick --selector "CssSelector" --css "...", webWaitElement --selector "CssSelector" --css "..." --timeout "00:00:30", webClose --name web01
- Logging: logMessage --message "text" --type "Info|Warning|Error"
- Bind BAW process variables: bindProcessVariables --mappings "{\"var\":\"${var}\"}"

REQUIREMENTS:
- Declare all variables at the top of the script
- Organize logic into subroutines
- Include error handling where appropriate
- Use CssSelector for web element selectors
- Read credentials from process variables, not hardcoded
```

---

### 2.2 Approach 2 — IBM RPA Skill for Bob (Recommended)

**Use when:** You or your team will be generating IBM RPA scripts repeatedly and want consistent, high-quality output with minimal prompting.

**How it works:**  
Create a [Bob Skill](https://bob.ibm.com/docs/ide/features/skills) — a `SKILL.md` file in `.bob/skills/ibm-rpa/` — that teaches Bob the WAL language, IBM RPA conventions, and your organisation's patterns. Bob auto-activates this skill whenever you ask it to work on `.wal` files or IBM RPA tasks.

**File structure:**
```
your-project/
└── .bob/
    └── skills/
        └── ibm-rpa/
            ├── SKILL.md           ← Skill entry point
            ├── wal-reference.md   ← WAL command reference
            ├── examples/
            │   ├── web-login.wal
            │   ├── excel-reader.wal
            │   └── queue-processor.wal
            └── conventions.md     ← Team coding standards
```

**`SKILL.md` template:**
```markdown
---
name: ibm-rpa
description: Generate, edit, and review IBM RPA WAL scripts. Activated when
  working with .wal files or when the user mentions IBM RPA, WAL scripts, RPA
  bots, or IBM RPA Studio.
---

You are an IBM RPA specialist. When generating or editing WAL scripts:

## WAL Script Structure
1. All `defVar` declarations at the top
2. Bind process variables with `bindProcessVariables` if BAW-integrated
3. Main logic: `goSub --label SubName` calls
4. Subroutines defined with `beginSub`/`endSub` at the bottom
5. File ends with `* VERSION_NUMBER` comment

## Key Rules
- Never hardcode credentials — use process variables or IBM RPA Vault assets
- Always `webWaitElement` before interacting with a web element
- Always `webClose --name web01` in a cleanup subroutine
- Use `logMessage --message "..." --type "Info"` at key steps
- Use `--simulatehuman` flag on web commands for better stability
- Selector preference order: `data-testid` > ID > CssSelector > XPath

## Reference Files
See wal-reference.md for the complete command reference.
See examples/ for working script patterns.
See conventions.md for team coding standards.
```

---

### 2.3 Approach 3 — Literate Coding in `.wal` Files

**Use when:** You have a partially written WAL script and want Bob to fill in sections using natural language inline.

**How it works:**  
Open a `.wal` file in Bob IDE. Use `Cmd+I` (Mac) / `Ctrl+I` (Windows/Linux) to activate literate coding mode. Write natural language descriptions where commands should go, then press `Cmd+Enter` to generate. Bob converts the natural language into WAL commands in-place.

**Example — inline instruction inside a .wal file:**
```wal
defVar --name invoiceNumber --type String
defVar --name invoiceAmount --type Numeric
defVar --name success --type Boolean

bindProcessVariables --mappings "{\"invoiceNumber\":\"${invoiceNumber}\"}"
webStart --name web01 --type "Chrome"

goSub --label Login
goSub --label ProcessInvoice

beginSub --name Login
  # Bob literate coding: navigate to https://erp.example.com/login, 
  # wait for username field (id="user"), fill username from ${username}, 
  # fill password from ${password}, click submit button (id="submit")
endSub

beginSub --name ProcessInvoice
  # Bob literate coding: navigate to invoice entry page, wait for 
  # invoice number field, enter ${invoiceNumber}, enter ${invoiceAmount},
  # click Save button, wait for confirmation message, capture its text to success
endSub
```
With the IBM RPA skill active, Bob knows WAL syntax and generates correct WAL commands from those natural language comments.

---

### 2.4 Approach 4 — Plan + Agent Mode for Full Bot Generation

**Use when:** You want Bob to generate a complete, multi-file IBM RPA bot project from a process description document.

**Workflow:**

**Step 1 — Create a Process Description Document**
```markdown
# Process: Daily Invoice Export

## Trigger
Runs daily at 08:00 via IBM RPA Scheduler

## Steps
1. Log into ERP portal (https://erp.example.com/login)
2. Navigate to Reports > Invoice Export
3. Set date filter to yesterday
4. Click Export → Download CSV to C:\RPA\output\invoices_YYYYMMDD.csv
5. Log success + record count to IBM RPA log

## Error Handling
- If login fails: retry 3 times, then log error and exit
- If no invoices found: log warning, create empty file, exit with success
- If download fails: log error, raise exception

## Process Variables (passed from BAW workflow)
- username: String
- password: String
- output_folder: String
```

**Step 2 — Prompt Bob in Plan mode:**
```
Read the process description in @process-invoice-export.md and create an 
implementation plan for an IBM RPA WAL script. The plan should include:
- Script structure (subroutines and their responsibilities)
- Variable declarations needed  
- Error handling strategy
- Web selectors strategy

Place the plan in plans/invoice-export-plan.md
```

**Step 3 — Switch to Agent/Code mode:**
```
Implement the IBM RPA bot according to @plans/invoice-export-plan.md.
Generate the file as bots/invoice_export.wal following IBM RPA WAL conventions.
Use the IBM RPA skill for language guidance.
```

Bob reads the plan, generates the complete `.wal` file, and can also generate a `README.md` explaining the bot's usage.

---

### 2.5 Approach 5 — IBM RPA MCP Server Integration (IBM RPA 30.0.2+)

**Use when:** You want AI agents (including Bob) to directly invoke running IBM RPA bots as tools, or trigger bot execution programmatically.

**How it works:**  
IBM RPA 30.0.2 introduced an official **MCP (Model Context Protocol) server** that exposes IBM RPA bots as callable tools to any MCP-compatible AI agent.

```
IBM Bob (MCP client)
    ↓  calls tool: run_rpa_bot(bot_name, parameters)
IBM RPA MCP Server (gateway)
    ↓  Streamable HTTP protocol
IBM RPA API Server
    ↓  executes bot on IBM RPA Agent
Running Bot → returns result to agent
```

**Configuration:**  
Add the IBM RPA MCP server to Bob's MCP configuration. Once connected, Bob can:
- List available RPA bots as tools
- Invoke bots with parameters
- Receive bot outputs back into the agent context
- Chain RPA bot execution with other agent reasoning steps

IBM provides a **hosted MCP server for SaaS customers** (no infrastructure to manage), and an on-premises gateway for self-hosted IBM RPA installations.

This makes IBM RPA bots composable building blocks within Bob-driven agentic workflows.

---

## 3. Practical Prompting Patterns for WAL Generation

### 3.1 Web Automation Bot

```
Generate an IBM RPA WAL script that:
1. Opens Chrome and navigates to ${portalUrl}
2. Logs in with ${username} / ${password} (CSS: #user, #pass, #btn-login)
3. Navigates to the "Reports" section (CSS: nav > a[href='/reports'])
4. Waits for the report table to load (CSS: #report-table)
5. Reads all rows from the table into a DataTable variable
6. Closes the browser
7. Returns the row count as a process variable

Use --simulatehuman on all web interactions.
Include webWaitElement before every webSet or webClick.
Handle the case where login redirects to a 2FA page (CSS: #2fa-container) 
by logging an error and stopping.
```

### 3.2 Excel Processing Bot

```
Generate an IBM RPA WAL script that:
1. Opens the Excel file at path ${inputFile}
2. Reads all rows from Sheet1 starting at row 2 (row 1 is header)
3. For each row: extract columns A (invoice_id), B (amount), C (date)
4. Writes a summary line to a new sheet called "Summary"
5. Saves and closes the file
6. Logs total rows processed

Use a for loop over the row count.
Declare all variables at the top.
```

### 3.3 Queue-Based Bot (Dispatcher/Performer Pattern)

```
Generate an IBM RPA WAL script (Performer) that:
1. Connects to an IBM RPA queue named ${queueName}
2. Gets the next available queue item
3. Parses the item payload: extract fields customerName, orderId, amount
4. Performs web automation to enter the order into the ERP system
5. On success: marks queue item as completed
6. On error: marks queue item as failed with error message
7. Loops back to get the next item until the queue is empty

Include proper beginSub/endSub organization:
- Main (goSub flow controller)
- ConnectQueue
- ProcessItem  
- MarkComplete
- MarkFailed
```

### 3.4 Refining Generated Code

```
The generated WAL script has this issue:
[paste the problematic section]

The selector "body > form > table > tbody > tr:nth-child(1) > td > input" is 
too fragile. The input field has id="invoice-number". 
Update the selector strategy to use ID selectors where available,
and add a fallback to the original CSS selector if the ID is not found.
```

---

## 4. Key Constraints and Best Practices for Bob-Generated WAL

### 4.1 Security Requirements (Mandatory)
- **Never** hardcode credentials in WAL scripts — always use `bindProcessVariables` or IBM RPA Vault assets
- Variables containing passwords must never be written to `logMessage`
- Use `getAsset` command to retrieve secrets from the IBM RPA Vault at runtime

### 4.2 Selector Strategy (Resilience)
| Priority | Selector Type | WAL Example |
|---|---|---|
| 1 (Best) | ID selector | `--selector "CssSelector" --css "#my-field"` |
| 2 | data-testid | `--selector "CssSelector" --css "[data-testid='submit']"` |
| 3 | ARIA label | `--selector "CssSelector" --css "[aria-label='Submit']"` |
| 4 | Stable class | `--selector "CssSelector" --css ".btn-primary"` |
| 5 (Avoid) | Position-based | `--selector "CssSelector" --css "table > tr:nth-child(3)"` |
| 6 (Fallback) | XPath | `--selector "XPath" --xpath "//button[@type='submit']"` |

### 4.3 Script Structure Conventions
```
[Script]
├── Variable declarations (defVar)         ← All at top
├── bindProcessVariables                   ← If BAW-integrated
├── Main flow (goSub calls only)           ← Readable top-level flow
├── beginSub --name Initialization
├── beginSub --name [CoreLogic]
├── beginSub --name ErrorHandler
└── beginSub --name Cleanup                ← Always close browser/files
```

### 4.4 Always Include
- `webWaitElement` before every `webSet`, `webGet`, or `webClick`
- `--timeout "00:00:30"` on wait commands (adjust for slow pages)
- `logMessage` at entry/exit of each subroutine for auditability
- Cleanup subroutine that runs even on error (use `goSub --label Cleanup` in error paths)
- `* VERSION` comment at the end of the file (IBM RPA version stamp)

---

## 5. Complete Working Example — Bob-Generated WAL Script

The following script was generated from the prompt in Section 3.1:

```wal
defVar --name portalUrl --type String
defVar --name username --type String
defVar --name password --type String
defVar --name rowCount --type Numeric
defVar --name tableData --type DataTable
defVar --name success --type Boolean

bindProcessVariables --mappings "{\"portalUrl\":\"${portalUrl}\",\"username\":\"${username}\",\"password\":\"${password}\"}"

goSub --label OpenBrowser
goSub --label Login
goSub --label NavigateToReports
goSub --label ExtractTable
goSub --label Cleanup

beginSub --name OpenBrowser
  logMessage --message "Opening browser" --type "Info"
  webStart --name web01 --type "Chrome" --userprofilepreferences "AutomationOptimized"
  webNavigate --url "${portalUrl}"
  webWaitElement --selector "CssSelector" --css "#user" --timeout "00:00:30"
endSub

beginSub --name Login
  logMessage --message "Logging in as ${username}" --type "Info"
  webSet --value "${username}" --selector "CssSelector" --css "#user" --simulatehuman
  webSet --value "${password}" --selector "CssSelector" --css "#pass" --simulatehuman
  webClick --selector "CssSelector" --css "#btn-login" --simulatehuman
  webWaitElement --selector "CssSelector" --css "#2fa-container" --timeout "00:00:05" success=value
  if --left "${success}" --operator "Equal_To" --right "True"
    logMessage --message "2FA page detected — manual intervention required" --type "Error"
    goSub --label Cleanup
    throwError --message "2FA challenge detected"
  endIf
  webWaitElement --selector "CssSelector" --css "nav" --timeout "00:00:20"
  logMessage --message "Login successful" --type "Info"
endSub

beginSub --name NavigateToReports
  logMessage --message "Navigating to Reports" --type "Info"
  webClick --selector "CssSelector" --css "nav > a[href='/reports']" --simulatehuman
  webWaitElement --selector "CssSelector" --css "#report-table" --timeout "00:00:30"
endSub

beginSub --name ExtractTable
  logMessage --message "Extracting report table" --type "Info"
  webGetDataTable --selector "CssSelector" --css "#report-table" tableData=value
  listCount --list "${tableData}" rowCount=value
  logMessage --message "Extracted ${rowCount} rows" --type "Info"
  setProcessVariable --name "rowCount" --value "${rowCount}"
endSub

beginSub --name Cleanup
  logMessage --message "Closing browser" --type "Info"
  webClose --name web01
endSub
* 30.0.2
```

---

## 6. IBM RPA MCP Server Quick Reference

For teams running IBM RPA 30.0.2+, Bob can be connected to the MCP server to trigger bots as tools.

**What the MCP server exposes:**
- All published IBM RPA bots as MCP tools
- Each bot's input parameters as tool arguments
- Bot execution results returned as structured output

**IBM RPA MCP Server documentation:**  
`https://www.ibm.com/docs/en/rpa/30.0.x?topic=client-rpa-mcp-server`

**SaaS hosted MCP server:**  
`https://www.ibm.com/docs/en/rpa/30.0.x?topic=server-rpa-mcp-saas`

---

## 7. References

| Resource | Link |
|---|---|
| IBM Bob Skills Documentation | https://bob.ibm.com/docs/ide/features/skills |
| IBM Bob Literate Coding | https://bob.ibm.com/docs/ide/features/literate-coding |
| IBM Bob Agentic Chat | https://bob.ibm.com/docs/ide/features/chat-interface |
| IBM RPA Script Development | https://www.ibm.com/docs/en/rpa/21.0.x?topic=automation-developing-scripts |
| IBM RPA Commands Reference (v30) | https://www.ibm.com/docs/en/rpa/30.0.x?topic=commands |
| IBM RPA Web Automation | https://www.ibm.com/docs/en/rpa/30.0.x?topic=tasks-web-automation |
| IBM RPA MCP Server | https://www.ibm.com/docs/en/rpa/30.0.x?topic=client-rpa-mcp-server |
| IBM RPA MCP Server (SaaS) | https://www.ibm.com/docs/en/rpa/30.0.x?topic=server-rpa-mcp-saas |
| IBM cp4ba-labs WAL Examples (GitHub) | https://github.com/IBM/cp4ba-labs |
| WAL Code Companion (IBM RPA Studio) | https://community.ibm.com/community/user/blogs/adam-rogers/2026/05/26/introducing-the-wal-code-companion |
| IBM Bob + BPMN to Agents Tutorial | https://developer.ibm.com/components/ibm-bob/tutorials/ |
