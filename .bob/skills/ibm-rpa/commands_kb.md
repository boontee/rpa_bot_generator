# IBM RPA WAL Commands — Knowledge Base

> **Sources:** IBM Docs (21.0.x / 23.0.x / 30.0.x), IBM Community, GitHub samples
> **Syntax:** `commandName --param "value"   outputVar=value`
> **Variables:** `${varName}` — declared with `defVar --name varName --type TYPE`
> **Version coverage:** Commands marked `[30+]` were added in 30.0.x; unmarked commands available from 21.0.x onward.
>
> **Validation status (as of latest update):**
> ✅ Confirmed = name validated against IBM Docs or real GitHub WAL samples
> ⚠️ Unconfirmed = inferred from Designer-mode label or not yet found in a real script — verify in IBM RPA Studio before use
>
> **Sections validated:** §2 §3 §7 §8 §9 §10 §11 §12 §13 §15 §16 §17 §18 §19 §20 §21 §22 §25 §26
> **Partially validated (some commands confirmed, others ⚠️):** §4 §6 §17 §19 §23 §25

---

## Table of Contents

1. [Data Types](#1-data-types)
2. [Script Structure & Flow Control](#2-script-structure--flow-control)
3. [Variables & Data](#3-variables--data)
4. [Text & String Manipulation](#4-text--string-manipulation)
5. [Numeric & Math](#5-numeric--math)
6. [Date & Time](#6-date--time)
7. [Logging & Diagnostics](#7-logging--diagnostics)
8. [Error Handling](#8-error-handling)
9. [Security — Vault / Assets / BAW](#9-security--vault--assets--baw)
10. [Web Automation — Classic (WebDriver)](#10-web-automation--classic-webdriver)
11. [Web Automation — Smart Commands](#11-web-automation--smart-commands)
12. [Windows Desktop Automation](#12-windows-desktop-automation)
13. [Java Application Automation](#13-java-application-automation)
14. [SAP GUI Automation](#14-sap-gui-automation)
15. [Terminal Automation](#15-terminal-automation)
16. [Surface Automation — Vision Driver & OCR](#16-surface-automation--vision-driver--ocr)
17. [Excel / Office Automation](#17-excel--office-automation)
18. [DataTable Operations](#18-datatable-operations)
19. [File & Folder Operations](#19-file--folder-operations)
20. [Database (SQL / SQLite)](#20-database-sql--sqlite)
21. [Queue / Message Queue](#21-queue--message-queue)
22. [HTTP / REST API](#22-http--rest-api)
23. [Email](#23-email)
24. [PDF & OCR](#24-pdf--ocr)
25. [System / OS / Scripting](#25-system--os--scripting)
26. [UI Interaction Helpers](#26-ui-interaction-helpers)
27. [Selector Strategy Quick Reference](#27-selector-strategy-quick-reference)

---

## 1. Data Types

| Type | WAL keyword | Description | Example |
|---|---|---|---|
| String | `String` | Text value | `"hello"` |
| Numeric | `Numeric` | Integer or decimal | `42`, `3.14` |
| Boolean | `Boolean` | True or False | `True`, `False` |
| DateTime | `DateTime` | Date and time | `2025-01-15 08:00:00` |
| List | (via `defList`) | Ordered string list | `StringList` inner type |
| DataTable | (via `defDataTable`) | Rows + columns tabular data | |
| DbConnection | `DbConnection` | Database connection handle | |
| Excel | `Excel` | Open Excel application handle | |
| Image | `Image` | Screenshot or image data | |
| QueueConnection | `QueueConnection` | IBM RPA queue connection | |
| MessageQueue | `MessageQueue` | Queue message reference | |

---

## 2. Script Structure & Flow Control

### Subroutines

```wal
# Define and call a subroutine
beginSub --name MyRoutine
  # commands ...
endSub

goSub --label MyRoutine

# Call with variable assignments
goSub --label MyRoutine --assignments "${var1}=value1,${var2}=value2"

# Conditional call (call only if condition is true)
gosubIf --label MyRoutine --left "${count}" --operator "Greater_Than" --right "0"
```

### Conditional Logic

```wal
# if / else / endIf
if --left "${status}" --operator "Equal_To" --right "Done"
  logMessage --message "Done" --type "Info"
else
  logMessage --message "Not done" --type "Warning"
endIf

# Negate a condition
if --left "${found}" --operator "Is_True" --negate
  logMessage --message "Not found" --type "Warning"
endIf
```

**Operators:** `Equal_To` `Not_Equal` `Greater_Than` `Greater_Than_Or_Equal`
`Less_Than` `Less_Than_Or_Equal` `Contains` `Not_Contains` `Is_True` `Is_False`
`Is_Empty` `Is_Not_Empty`

### Loops

```wal
# For loop (numeric)
for --variable ${i} --from 1 --to ${lastRow} --step 1
  # body
next

# For-each (iterate a List)
foreach --collection "${myList}" --variable "${item}"
  logMessage --message "Item: ${item}" --type "Info"
endFor

# While loop
while --left "${isRunning}" --operator "Is_True"
  # body
endWhile

# Break out of any loop
break
```

### Execution Control

```wal
stopExecution                             # stop the bot cleanly (no error)
throwError --message "Fatal: ${msg}"      # stop with error
failTest --message "Test failed: ${msg}"  # mark test as failed (testing context)
```

---

## 3. Variables & Data

```wal
# Declare variables (all at top of script)
defVar --name myStr   --type String
defVar --name count   --type Numeric
defVar --name isReady --type Boolean
defVar --name today   --type DateTime
defVar --name excel   --type Excel
defVar --name screenshot --type Image

# Declare a list
defList --name myList --type StringList

# Assign values
setVar --name "${myStr}"   --value "hello"
setVar --name "${count}"   --value "0"
setVar --name "${isReady}" --value "True"

# Clear / reset a variable
setVar --name "${myStr}"    # no --value = clears to default/empty

# Increment / Decrement
incrementVar --number ${count}            # count = count + 1
decrementVar --number ${count}            # count = count - 1

# List operations
listAdd      --list "${myList}" --value "item"
listGetAt    --list "${myList}" --index "${i}"   item=value
listCount    --list "${myList}"                  count=value
listRemoveAt --list "${myList}" --index "${i}"
listClear    --list "${myList}"

# Generate random text
createRandomText --useuppercaseletters --usedigits \
                 --minimumlength 8 --maximumlength 8   result=value
```

---

## 4. Text & String Manipulation

```wal
# Split a string into a List  ← confirmed: IBM Docs + GitHub WAL samples
splitString --text "${csvLine}" --delimiteroption "Comma"   parts=value
splitString --text "${data}"    --delimiteroption "CustomDelimiter" \
            --customdelimiter "|"   parts=value
# delimiteroption values: Comma | Semicolon | Tab | Space | CustomDelimiter

# Get: access a list item by index (0-based)  ← confirmed: OrangeHRM WAL
get --collection "${parts}" --index 0   firstItem=value

# Replace text  ← confirmed: IBM Docs + GitHub WAL samples
replaceText --texttoparse "${myStr}" --textpattern "old" \
            --replacementtext "new"   result=value

# Extract with regex  ← confirmed: IBM community WAL samples
getRegex --text "${output}" --regex "ID: (\d+)"   extracted=value

# Get a substring  ← confirmed: IBM Docs 30.0.x "Get Subtext"
getSubtext --text "${myStr}" --startindex 0 --length 5   sub=value

# Convert case  ← confirmed: IBM Docs 21.0.x + 30.0.x "Change Text Case"
# --type values: Upper | Lower | Title | Sentence
changeTextCase --text "${myStr}" --type "Upper"   upper=value
changeTextCase --text "${myStr}" --type "Lower"   lower=value

# Concatenate two texts  ← confirmed: IBM Docs "Concatenate Texts" + OrangeHRM WAL
concatTexts --text "${part1}" --value "${part2}"   result=value
# Note: for building a longer string iteratively, chain multiple concatTexts calls

# ⚠️ UNCONFIRMED COMMANDS (use with caution — names not validated against IBM Docs):
# textLength --text "${myStr}"   len=value         # unconfirmed name
# trimText --text "${myStr}"   trimmed=value       # unconfirmed name
# textContains --text "${myStr}" --value "search"   found=value  # use if/Contains operator instead
# textToNumber --text "${numStr}"   num=value       # unconfirmed name
# numberToText --number "${num}"   txt=value        # unconfirmed name
```

> **Validated corrections (§4):**
> - `getSubstring` → **`getSubtext`** (IBM Docs 30.0.x)
> - `toUpperCase` / `toLowerCase` → **`changeTextCase --type "Upper"/"Lower"`** (IBM Docs 21.0.x/30.0.x)
> - `concatenate --values` → **`concatTexts --text X --value Y`** (IBM Docs + OrangeHRM WAL)
> - `textSplit` → removed; **`splitString`** is the confirmed command
> - `textContains` — not confirmed as a standalone command; use `if --operator "Contains"` instead

---

## 5. Numeric & Math

```wal
# Basic arithmetic via setVar expressions
setVar --name "${result}" --value "${a} + ${b}"
setVar --name "${result}" --value "${a} - ${b}"
setVar --name "${result}" --value "${a} * ${b}"
setVar --name "${result}" --value "${a} / ${b}"

# Increment / Decrement
incrementVar --number ${n}
decrementVar --number ${n}

# Random number
randomNumber --minimum 1 --maximum 100   result=value

# Absolute value / round / floor / ceiling — use runDOSCommand/runCSharpCode for complex math
```

---

## 6. Date & Time

```wal
# Get current date/time  ← confirmed: IBM Docs + scriptModel.wal
getCurrentDateAndTime --localorutc "LocalTime"   now=value
getCurrentDateAndTime --localorutc "UTC"         nowUtc=value

# Convert DateTime to string  ← confirmed: scriptModel.wal (angeloalves88)
dateTimeToText --date "${now}" --usecustomformat --customformat "yyyy,MM,dd"   str=value

# ⚠️ UNCONFIRMED COMMANDS (names not validated against IBM Docs):
# formatDateTime --datetime "${now}" --format "yyyy-MM-dd"   str=value   # unconfirmed
# textToDateTime --text "2025-01-15" --format "yyyy-MM-dd"   dt=value    # unconfirmed
# addTimeSpan --datetime "${now}" --days 1 --hours 0 --minutes 0   future=value  # unconfirmed

# Compare dates  ← confirmed operator works with DateTime
if --left "${now}" --operator "Greater_Than" --right "${deadline}"
  logMessage --message "Overdue" --type "Warning"
endIf
```

> **Validated notes (§6):**
> - `dateTimeToText` ✅ confirmed real (scriptModel.wal)
> - `getCurrentDateAndTime` ✅ confirmed real
> - `formatDateTime`, `textToDateTime`, `addTimeSpan` — unconfirmed names, use `dateTimeToText` + `runDOSCommand`/`runCSharpCode` for advanced date math

---

## 7. Logging & Diagnostics

```wal
# Standard log (appears in IBM RPA Control Center logs)
logMessage --message "→ Login: start"           --type "Info"
logMessage --message "Unexpected value: ${val}" --type "Warning"
logMessage --message "Fatal in ProcessInvoice"  --type "Error"
# Types: Info | Warning | Error

# Capture screenshot (for error reporting)
printScreen   screenshot=value
saveImage --image ${screenshot} --directory "${logPath}" \
          --createrandomfile --format "Png"   savedPath=value

# Built-in runtime variables
# ${rpa:subName}         — name of the currently executing subroutine
# ${rpa:error.Message}   — last error message
# ${rpa:error.Routine}   — subroutine where error occurred
# ${rpa:error.LineNumber}— line number of the error
```

---

## 8. Error Handling

```wal
# Register an error handler for the current subroutine scope
onError --label ErrorHandler

# Standard error exit pattern
logMessage --message "Fatal: ${rpa:error.Message} in ${rpa:error.Routine}" --type "Error"
goSub --label Cleanup
throwError --message "${rpa:error.Message}"

# Retry pattern
defVar --name attempts --type Numeric
defVar --name maxAttempts --type Numeric
setVar --name "${maxAttempts}" --value "3"

while --left "${attempts}" --operator "Less_Than" --right "${maxAttempts}"
  incrementVar --number ${attempts}
  goSub --label AttemptWork
  if --left "${success}" --operator "Is_True"
    break
  endIf
endWhile
```

---

## 9. Security — Vault / Assets / BAW

```wal
# Read secret from IBM RPA Vault (never hardcode credentials)
getAsset --name "ERP_PASSWORD"         password=value
getAsset --name "DB_CONNECTION_STRING" connStr=value

# Bind BAW (IBM Business Automation Workflow) process variables
# at script startup — JSON escaped mapping
bindProcessVariables --mappings "{\"username\":\"${username}\",\"orderId\":\"${orderId}\"}"

# Write output back to BAW process variable
setProcessVariable --name "processingStatus" --value "${status}"
setProcessVariable --name "confirmedOrderId" --value "${confirmedId}"
```

**Security rules:**
- **NEVER** hardcode passwords, tokens, or API keys in WAL scripts.
- **NEVER** include credential variables in `logMessage`.
- Use `getAsset` for vault-stored secrets, `bindProcessVariables` for BAW-passed inputs.

---

## 10. Web Automation — Classic (WebDriver)

### Browser Lifecycle

```wal
webStart --name web01 --type "Chrome" \
         --userprofilepreferences "AutomationOptimized" \
         --downloadpath "C:\RPA\downloads"
webNavigate --url "https://app.example.com/login"
webWaitPage --timeout "00:00:30"
webClose --name web01
# Browser types: Chrome | Firefox | Edge
```

### Waiting (MANDATORY before every interaction)

```wal
webWaitElement --selector "CssSelector" --css "#submit-btn" \
               --timeout "00:00:30"   success=value
# success=True → found; False → timed out
```

### Reading & Writing

```wal
webSet    --value "${username}" --selector "CssSelector" --css "#username"   --simulatehuman
webGet    --selector "CssSelector" --css "#message"                          statusText=value
webClick  --selector "CssSelector" --css "#login-btn"                        --simulatehuman

# Dropdown / combo box
webSetComboBox --selectoptionby "Value" --value "${option}" \
               --selector "CssSelector" --css "#select-id" --simulatehuman
# selectoptionby: Value | Text | Index

# Get an attribute (e.g., href, src, data-*)
webGetAttribute --attribute "href" --selector "CssSelector" --css "a.link"   url=value

# Read HTML table → DataTable
webGetDataTable --selector "CssSelector" --css "#results-table"   tableData=value
```

### Page State & Navigation

```wal
webWaitPage    --timeout "00:00:30"
webWaitUrl     --url "**/dashboard" --timeout "00:00:20"
webExecuteScript --script "window.scrollTo(0, document.body.scrollHeight);"
webTakeScreenshot --path "C:\RPA\screenshots\${timestamp}.png"
webBack                            # browser back
webRefresh                         # refresh page
```

### Iframe Handling

```wal
webSwitchFrame --selector "CssSelector" --css "iframe#content"
# interact with iframe content
webSwitchFrame --default             # switch back to main frame
```

---

## 11. Web Automation — Smart Commands

Preferred for modern SPAs where WebDriver selectors are unstable. Uses a browser extension.

```wal
openBrowser  --url "https://app.example.com" --browsertype "Chrome"
typeText     --text "${searchTerm}" --description "Search box"
clickElement --description "Submit button"
selectItem   --item "${option}"     --description "Country dropdown"
getText      --description "Status label"   result=value
closeBrowser
```

---

## 12. Windows Desktop Automation

### Launch & Attach Windows

```wal
# Launch an application and attach to its window  ← confirmed: community WAL
launchWindow  --executablepath "C:\Apps\MyApp.exe" \
              --parameters "${args}"   window=value vPID=value success=value

# Launch OR attach (if already running, attach; otherwise launch)  ← confirmed: community WAL
launchOrAttach --executablepath "C:\Apps\MyApp.exe" \
               --useregex --regexPattern "WindowTitlePattern" \
               --processname "appname"   window=value success=success

# Wait for a window to appear (by title or class)  ← confirmed: community WAL
waitWindow --title "My Application" --timeout "00:00:30"   window=value success=value
waitWindow --classname "Notepad" --processname "notepad"   window=value

# Bring window into focus  ← confirmed: community WAL (verb is focusWindow)
focusWindow --window "${window}"

# Close a window  ← confirmed: community WAL
closeWindow --window "${window}"

# Attach to an already-open window  ← confirmed: community WAL (attachWindow)
attachWindow --window "${window}"
```

### Control Interactions (Universal)

These work for Windows, Java (with JAB), and SAP-vision-mode controls.

```wal
# Click a UI control
click --selector "XPath" --xpath "/root/push_button[1]" \
      --controlsimilarity 100

# Type into a text field
setValue --value "${inputData}" --setvaluetype "Automatic" \
         --algorithm "Default" --matchcondition "Equals" \
         --selector "XPath" \
         --xpath "/root/root_pane[1]/panel[1]/text[1]"

# Read text from a control
getValue --selector "XPath" \
         --xpath "/root/root_pane[1]/panel[1]/text[3]"   result=value

# Check / uncheck a checkbox
setCheckBox --checked true \
            --selector "XPath" --xpath "/root/check_box[1]"

getCheckBox --selector "XPath" --xpath "/root/check_box[1]"   checked=value

# Select item in a list/combo
selectItem --value "${option}" \
           --selector "XPath" --xpath "/root/combo_box[1]"

# Wait for a control to appear
waitControl --selector "XPath" --xpath "/root/text[1]" \
            --timeout "00:00:30"   success=value

# Double-click
doubleClick --selector "XPath" --xpath "/root/list_item[1]"

# Right-click
rightClick --selector "XPath" --xpath "/root/panel[1]"

# Send keystrokes
sendKeys --keys "{ENTER}"
sendKeys --keys "${text}"
# Special keys: {ENTER} {TAB} {ESC} {F1}..{F12} {CTRL+A} {ALT+F4}
```

### Mouse & Keyboard

```wal
mouseClick  --x 500 --y 300                  # absolute screen coordinates
mouseMove   --x 500 --y 300
keyPress    --key "ENTER"
typeText    --text "${text}"
```

> **Validated corrections (§12):**
> - `setFocus` → **`focusWindow`** (confirmed community WAL)
> - `bringWindowToFront` → **`focusWindow`** (same usage)
> - `launchWindow` output var is `window=value` (not `vWindow=value`)

---

## 13. Java Application Automation

**Prerequisites:** Java Manager component installed in IBM RPA Client; Java Access Bridge (JAB) enabled (`jabswitch -enable`); 64-bit JRE on agent machine.

```wal
# Launch Java app
launchWindow --executablepath "C:\Apps\MyApp.jar"   vWindow=value vPID=value

# Wait for Java window
waitWindow --title "Client Management System" --timeout "00:00:30"   vWindow=value

# Attach
attachWindow --window "${vWindow}"

# Interact with Java Swing controls via XPath selectors
# XPath uses Accessibility role names as node types
setValue --value "${username}" --setvaluetype "Automatic" \
         --selector "XPath" \
         --xpath "/root/root_pane[1]/layered_pane[1]/panel[1]/text[1]"

getValue --selector "XPath" \
         --xpath "/root/root_pane[1]/layered_pane[1]/panel[1]/text[1]"   result=value

click --selector "XPath" --controlsimilarity 100 \
      --xpath "/root/root_pane[1]/layered_pane[1]/panel[1]/push_button[1]"
```

**Java Swing XPath node types (Accessibility roles):**

| Swing Component | XPath node |
|---|---|
| `JTextField` | `text` |
| `JPasswordField` | `password_text` |
| `JButton` | `push_button` |
| `JCheckBox` | `check_box` |
| `JRadioButton` | `radio_button` |
| `JComboBox` | `combo_box` |
| `JList` | `list` |
| `JTable` | `table` |
| `JTree` | `tree` |
| `JPanel` | `panel` |
| `JLabel` | `label` |
| `JMenu` | `menu` |
| `JMenuItem` | `menu_item` |
| Root window | `root` → `root_pane` → `layered_pane` |

> Java XPaths cannot be guessed — capture them with the IBM RPA Studio Recorder using the Java driver.

---

## 14. SAP GUI Automation

**Note:** SAP automation requires activating the **Vision driver** in the Recorder. Controls can also be mapped via SAP GUI Scripting.

```wal
# Open SAP
sapOpen --connectionString "${sapConn}"   sapApp=value

# Navigate to a transaction
sapSet --application "${sapApp}" --field "Transaction" --value "FB60"

# Set field value
sapSet --application "${sapApp}" --field "Vendor"   --value "${vendorId}"
sapSet --application "${sapApp}" --field "Amount"   --value "${amount}"

# Read field value
sapGet --application "${sapApp}" --field "DocumentNumber"   docNo=value

# Click button / toolbar item
sapClick --application "${sapApp}" --button "Save"
sapClick --application "${sapApp}" --button "Execute"

# Select table row
sapSelectRow --application "${sapApp}" --row "${rowNum}"

# Close SAP
sapClose --application "${sapApp}"
```

---

## 15. Terminal Automation

For mainframe (3270) and AS/400 (5250) green-screen automation.

```wal
# Connect to terminal
terminalConnect --host "${host}" --port "${port}" \
                --emulationtype "IBM3270"   termConn=value
# emulationtype: IBM3270 | IBM5250 | VT100 | VT220

# Wait for screen to stabilize
terminalWait --connection "${termConn}" --timeout "00:00:30"

# Read text from screen position
terminalGetText --connection "${termConn}" \
                --row 5 --column 10 --length 20   fieldValue=value

# Type into screen
terminalSetText --connection "${termConn}" \
                --row 5 --column 10 --text "${input}"

# Send key
terminalSendKey --connection "${termConn}" --key "Enter"
# Keys: Enter | F1..F24 | PF1..PF24 | Tab | BackTab | Clear | PA1..PA3

# Disconnect
terminalDisconnect --connection "${termConn}"
```

---

## 16. Surface Automation — Vision Driver & OCR

Used when no other driver can map controls (Citrix, RDP, VDI, legacy apps).

```wal
# Find anchor image on screen (one-shot check — no timeout)  ← confirmed: IBM community
findImage --image "${anchorImagePath}" --similarity 90 \
          --selector "Vision"   x=value y=value found=value

# Wait for image to appear (blocks until timeout)  ← confirmed: IBM Docs 30.0.x "Wait Image"
waitImage --image "${anchorImagePath}" --similarity 90 \
          --timeout "00:00:30" --interval "00:00:01" \
          --selector "Vision"   success=value

# Wait with scope limited to a specific window (not full screen)
waitImage --image "${anchorImagePath}" --similarity 90 \
          --timeout "00:00:10" --interval "00:00:00.5" \
          --region "${window.Bounds}" --selector "Vision"   success=value

# Click at an image location using Vision driver  ← confirmed: community WAL
click --selector "Vision" --visionimage "${anchorImagePath}" \
      --visionsimilarity 90 --timeout "00:00:15"

# Click anywhere on screen by coordinates (after findImage returns x, y)
click --clickOnScreen --selector "Vision" --visionimage "${anchorImagePath}" \
      --visionsimilarity 90 --timeout "00:00:15"

# Find a window before image operations
waitWindow --title "My App"   window=value
focusWindow --window "${window}"

# Recognize all text in an image file or PDF page  ← confirmed: IBM Docs 30.0.x
recognizeImageTextOrPdf --imagepath "${imagePath}"   extractedText=value

# ⚠️ UNCONFIRMED COMMANDS (names not validated against IBM Docs):
# clickByOCR --text "Submit" --similarity 85
# getControlTextByOCR --anchorimage X --offsetx 100 --offsety 0 --width 200 --height 30   ocrText=value
# bringWindowToFront --window "${window}"   # use focusWindow instead (confirmed)
```

> **Validated corrections (§16):**
> - `waitForImage` → **`waitImage`** (IBM Docs 30.0.x)
> - `findImageBySimilarity` → **`findImage`** (IBM community WAL)
> - `clickImage` → **`click --selector "Vision" --visionimage`** (community WAL)
> - `setFocus` / `bringWindowToFront` → **`focusWindow`** (confirmed)
> - `waitForWindow` → **`waitWindow`** (confirmed)

**Environment requirements for reliable vision automation:**

| Setting | Value |
|---|---|
| Screen resolution | Must match recording environment |
| Display scale (DPI) | 100% — do not use 125%/150% |
| Color depth | 32-bit |
| Window zoom | 100% |
| Window state | Always on top / in focus |

---

## 17. Excel / Office Automation

### Workbook Lifecycle

```wal
# Open Excel workbook  ← confirmed: IBM Docs 21.0.x "Open Excel File" (verb: excelOpen)
excelOpen  --path "${filePath}" --readOnly false   excelApp=value
excelSave  --application "${excelApp}"
excelClose --application "${excelApp}"

# Create new workbook  ← unconfirmed name; use excelOpen on a new blank file or
#   runDOSCommand to create the file, then excelOpen
# createOfficeFile --type "Excel" --path "${newPath}"   excelApp=value  # ⚠️ unconfirmed
```

### Reading

```wal
# Read a single cell  ← unconfirmed name (use excelGetTable for bulk reads)
# excelReadCell  --application "${excelApp}" --sheet "Sheet1" \
#                --row 2 --column 1   cellValue=value   # ⚠️ unconfirmed

# Get last used row (confirmed: IBM Docs "Get Excel Table" depends on this)
excelGetLastRow --application "${excelApp}" --sheet "Sheet1"   lastRow=value

# ⚠️ UNCONFIRMED:
# excelGetLastColumn --application "${excelApp}" --sheet "Sheet1"   lastCol=value
# excelReadRange --application "${excelApp}" --sheet "Sheet1" \
#                --startRow 1 --startColumn 1   tableData=value

# Get sheet as DataTable  ← confirmed: IBM Docs 21.0.x "Get Excel Table"
excelGetTable  --application "${excelApp}" --sheet "Sheet1" \
               --fromRow 1 --fromColumn 1   tableData=value
```

### Writing

```wal
# Write a single cell  ← unconfirmed name
# excelWriteCell --application "${excelApp}" --sheet "Sheet1" \
#                --row 2 --column 1 --value "${data}"   # ⚠️ unconfirmed

# Write entire DataTable to sheet  ← confirmed: IBM Docs 21.0.x
excelCreateFromDataTable --application "${excelApp}" --sheet "Sheet1" \
                         --datatable "${tableData}" \
                         --startRow 1 --startColumn 1
```

### Formatting & Sheet Operations

```wal
# ⚠️ UNCONFIRMED command names — use VBA macro via runMacroOffice for formatting:
# excelMergeCells   --application "${excelApp}" --sheet "Sheet1" \
#                   --startRow 1 --startColumn 1 --endRow 1 --endColumn 3

# ⚠️ UNCONFIRMED:
# excelCalculateFormula --application "${excelApp}"   # recalculate all formulas

# Run VBA macro  ← confirmed community usage
runMacroOffice --application "${excelApp}" --macro "MacroName"
```

> **Validated notes (§17):**
> - `excelOpen` ✅ confirmed (IBM Docs 21.0.x)
> - `excelGetTable` ✅ confirmed (IBM Docs 21.0.x)
> - `excelCreateFromDataTable` ✅ confirmed (IBM Docs 21.0.x)
> - `excelGetLastRow` ✅ confirmed (IBM Docs + community)
> - `excelReadCell`, `excelWriteCell`, `excelGetLastColumn`, `excelReadRange`, `excelMergeCells`, `excelCalculateFormula`, `createOfficeFile` — ⚠️ unconfirmed names

### Row / Column Deletion (No direct WAL command — use workaround)

```wal
# Step 1: Load sheet into DataTable
excelGetTable --application "${excelApp}" --sheet "Sheet1" \
              --fromRow 1 --fromColumn 1   tableData=value

# Step 2: Filter out unwanted rows in memory
deleteRows --datatable "${tableData}" --columnname "Status" --value "Processed"

# Step 3: Write filtered data back (overwrites sheet)
excelCreateFromDataTable --application "${excelApp}" --sheet "Sheet1" \
                         --datatable "${tableData}" \
                         --startRow 1 --startColumn 1

excelSave --application "${excelApp}"
```

---

## 18. DataTable Operations

```wal
# Declare
defDataTable --name myTable

# Delete rows matching a column value
deleteRows --datatable "${myTable}" --columnname "Status" --value "Done"   success=value

# Delete a column by name or index
deleteColumn --datatable "${myTable}" --columnname "TempCol"
deleteColumn --datatable "${myTable}" --columnindex 1

# Filter rows (keep only matching)
filterTable --datatable "${myTable}" --columnname "Region" --value "APAC"   filtered=value

# Find a cell value
findTableCellOccurrence --datatable "${myTable}" --value "${searchVal}" \
                         --columnname "Name"   row=value column=value found=value

# Find a column index by name
findColumnByName --datatable "${myTable}" --columnname "Amount"   index=value

# Get row and column counts  ← verified: IBM Docs 23.0.x "Get Table Information"
getTableInformation --datatable "${myTable}"   rowCount=value columnCount=value

# Read specific column values from a row (rownumber is 0-based)  ← verified: IBM Docs 23.0.x "Map Table Row"
mapTableRow --datatable "${myTable}" --rownumber "${i}" --columns "1,2"   col1=value col2=value
# --columns = comma-separated 1-based column numbers to extract into output vars

# Update a specific row's column value  ← verified: IBM Docs 23.0.x "Update Row"
updateRow --datatable "${myTable}" --rownumber "${i}" \
          --valuesmapping "ColumnName=${newVal}"

# Add a row with mapped values  ← verified: IBM Docs 23.0.x "Add Row"
addRow --datatable "${myTable}" --valuesmapping "Col1=${v1},Col2=${v2},Col3=${v3}"

# Sort  ← verified: IBM Docs 23.0.x "Sort Table"
sortTable --datatable "${myTable}" --columnname "Date" --ascending true
```

---

## 19. File & Folder Operations

```wal
# Text file read/write  ← unconfirmed names; confirmed via IBM Docs snippet patterns
fileRead  --path "${filePath}"   content=value        # ⚠️ unconfirmed name
fileWrite --path "${outPath}" --content "${text}" --overwrite true  # ⚠️ unconfirmed name

# File existence, copy, move, delete  ← unconfirmed names
fileExists  --path "${filePath}"   exists=value       # ⚠️ unconfirmed
fileCopy    --sourcePath "${src}" --destinationPath "${dest}"  # ⚠️ unconfirmed
fileMove    --sourcePath "${src}" --destinationPath "${dest}"  # ⚠️ unconfirmed
fileDelete  --path "${filePath}"                               # ⚠️ unconfirmed

# Confirmed existence checks  ← confirmed: scriptModel.wal (angeloalves88)
ifFile   --file "${filePath}"     success=value
ifFolder --path "${folderPath}"   success=value

# Create directory  ← confirmed: scriptModel.wal
createDir --path "${folderPath}"

# Get a special system folder path  ← confirmed: cp4ba-labs script_03
getSpecialFolder --folder "Desktop"   path=value
# Values: Desktop | Documents | Downloads | Temp | AppData

# List files in a folder  ← unconfirmed name
# getFiles --path "${folderPath}" --filter "*.xlsx"   fileList=value  # ⚠️ unconfirmed

# Zip / unzip  ← unconfirmed names
# zipFiles   --sourcePath "${folder}" --destinationPath "${zipFile}"   # ⚠️ unconfirmed
# unzipFiles --sourcePath "${zipFile}" --destinationPath "${outFolder}" # ⚠️ unconfirmed
```

> **Validated notes (§19):**
> - `ifFile` ✅ confirmed (scriptModel.wal)
> - `ifFolder` ✅ confirmed (scriptModel.wal)
> - `createDir` ✅ confirmed (scriptModel.wal)
> - `getSpecialFolder` ✅ confirmed (cp4ba-labs WAL)
> - `fileRead`, `fileWrite`, `fileExists`, `fileCopy`, `fileMove`, `fileDelete`, `getFiles`, `zipFiles`, `unzipFiles` — ⚠️ unconfirmed names

---

## 20. Database (SQL / SQLite)

### SQL (SqlServer / Oracle / PostgreSQL / MySQL / DB2)

```wal
dbConnect --connectionstring "${connStr}" --provider "SqlServer"   dbConn=value
# providers: SqlServer | Oracle | PostgreSQL | MySQL | DB2 | ODBC

dbQuery   --connection "${dbConn}" \
          --query "SELECT id, name FROM orders WHERE status = 'Pending'"   results=value

# Parameterized (SQL-injection safe)
dbQuery   --connection "${dbConn}" \
          --query "SELECT * FROM users WHERE id = @uid" \
          --parameters "{\"uid\":\"${userId}\"}"   results=value

dbExecute --connection "${dbConn}" \
          --query "UPDATE orders SET status='Done' WHERE id=${orderId}"

dbClose   --connection "${dbConn}"
```

### SQLite (built-in, no external DB needed)

```wal
# Connect (create new DB file if not exists)
sqliteConnect --connectionString "Data Source=${dbPath};Version=3;" \
              conBd=connection success=success

# Create new DB with schema
sqliteConnect --createNew \
              --sql "CREATE TABLE LOG (ID INTEGER PRIMARY KEY, MSG VARCHAR(255));" \
              --path "${dbPath}"   conBd=connection success=success

# Execute SQL
sqlExecute --connection ${conBd} \
           --statement "INSERT INTO LOG (MSG) VALUES ('${msg}');"   rows=value

# Query → DataTable
sqlQuery --connection ${conBd} \
         --statement "SELECT * FROM LOG WHERE ID > 0"   results=value

sqlDisconnect --connection ${conBd}
```

---

## 21. Queue / Message Queue

```wal
# Connect
mqConnect --queueName "${queueName}" --server "${mqServer}"   queueConn=value

# Get next message (non-blocking — success=False if empty)
mqGet --connection "${queueConn}" --timeout "00:00:05"   message=value success=value

# Put a message
mqPut --connection "${queueConn}" --message "${payload}"

# Acknowledge (complete)
mqComplete --connection "${queueConn}" --message "${message}"

# Mark as failed
mqFail --connection "${queueConn}" --message "${message}" --reason "${errorMsg}"

# Disconnect
mqClose --connection "${queueConn}"
```

**Queue performer loop skeleton:**

```wal
while --left "True" --operator "Equal_To" --right "True"
  mqGet --connection "${queueConn}" --timeout "00:00:05"   queueItem=value hasItem=value
  if --left "${hasItem}" --operator "Is_True" --negate
    logMessage --message "Queue empty — exiting" --type "Info"
    break
  endIf
  goSub --label ProcessItem
next
```

---

## 22. HTTP / REST API

IBM Docs 21.0.x + 30.0.x confirm: **`httpRequest`** is the real command name.
Outputs: `response=value`, `statusCode=value`, `reasonPhrase=value`, `success=value`.

```wal
# GET request  ← confirmed: IBM Docs 21.0.x/30.0.x "HTTP Request"
httpRequest --url "https://api.example.com/data" \
            --method "GET"   success=value response=value statusCode=value

# POST with JSON body
httpRequest --url "https://api.example.com/submit" \
            --method "POST" \
            --formatter "JSON" \
            --body "{\"key\":\"${value}\"}"   success=value response=value statusCode=value

# With custom auth header
httpRequest --url "https://api.example.com/secure" \
            --method "GET" \
            --headers "{\"Authorization\":\"Bearer ${token}\"}"   \
            success=value response=value statusCode=value

# mTLS client certificate  [30.0.1+]
httpRequest --url "https://secure.api.example.com" --method "GET" \
            --certificate "${pfxPath}" --certificatepassword "${certPass}" \
            success=value response=value statusCode=value

# Extract JSON values from response (use getRegex or mapJson)
getRegex --text "${response}" --regex "\"id\":(\d+)"   id=value
mapJson  --json "${response}" --mappings "id=${orderId},status=${orderStatus}"

# Local Python/Flask service (decoupled Python integration)
httpRequest --url "http://127.0.0.1:5000/process" \
            --method "POST" \
            --body "{\"input\":\"${data}\"}"   success=value response=value statusCode=value
```

> **Validated notes (§22):**
> - `httpRequest` ✅ confirmed (IBM Docs 21.0.x + 30.0.x)
> - mTLS certificate support added in 30.0.1
> - `mapJson` ✅ confirmed (ClientManagementInit.wal — cp4ba-labs)
> - Note: `--contenttype` flag not confirmed; use `--formatter "JSON"` for JSON body

---

## 23. Email

⚠️ **All email command names in this section are UNCONFIRMED** — IBM Docs pages for email require auth/JS and community WAL samples with email automation are scarce. Names below are inferred from IBM RPA Studio's Designer mode labels and should be verified in Studio before use.

```wal
# Connect IMAP  ← ⚠️ unconfirmed verb name
emailConnect --server "${mailServer}" --port 993 --ssl true \
             --username "${mailUser}" --password "${mailPass}"   emailConn=value

# Get emails  ← ⚠️ unconfirmed
emailGet --connection "${emailConn}" --folder "INBOX" \
         --unreadOnly true   emails=value

# Send SMTP  ← ⚠️ unconfirmed
emailSend --to "${recipient}" --subject "RPA Report" \
          --body "${body}" --smtpServer "${smtpServer}"

# Send with attachment  ← ⚠️ unconfirmed
emailSend --to "${recipient}" --subject "Report" --body "${body}" \
          --smtpServer "${smtpServer}" --attachment "${filePath}"

# Reply / mark-read / close  ← ⚠️ all unconfirmed names
emailReply      --connection "${emailConn}" --email "${emailObj}" --body "${replyBody}"
emailMarkAsRead --connection "${emailConn}" --email "${emailObj}"
emailClose      --connection "${emailConn}"
```

> **Action required:** verify all email command names in IBM RPA Studio toolbox before production use.

---

## 24. PDF & OCR

```wal
# Extract text from PDF (text-layer PDFs)
pdfExtractText --path "${pdfPath}"   text=value

# Open PDF for page operations
pdfOpen  --path "${pdfPath}"   pdfApp=value
pdfClose --application "${pdfApp}"

# OCR — read text from image/screen region
ocrReadText     --imagePath "${imgPath}"   ocrText=value

# Recognize text in an image or PDF page (Vision/OCR)
recognizeImageTextOrPdf --imagepath "${imgPath}"   extractedText=value

# Get control text by OCR (relative to anchor image)
getControlTextByOCR --anchorimage "${anchorPath}" \
                    --offsetx 100 --offsety 0 \
                    --width 200 --height 30   text=value
```

---

## 25. System / OS / Scripting

```wal
# DOS / shell command  ← confirmed: IBM Docs 30.0.x + community
runDOSCommand --command "python script.py ${arg1}"   output=value error=value
runDOSCommand --command "taskkill /F /IM chrome.exe"

# PowerShell  ← confirmed: cp4ba-labs script_03
powerShell --script "Get-Date -Format 'yyyy-MM-dd'"   psOutput=value
powerShell --script "taskkill /F /IM chrome.exe" --apartmentState "MTA"
powerShell --handleerror --apartmentState "MTA" --script "taskkill /F /IM chrome.exe"

# Inline C# code [30+]  ← confirmed: IBM Docs 30.0.x
runCSharpCode --code "return DateTime.Now.ToString(\"yyyy-MM-dd\");"   output=value

# Execute another WAL script  ← confirmed: OrangeHRM WAL (IBM/ibm-rpa-cli)
executeScript --name "ScriptName" --parameters "var1=${val1}" \
              --output "result1=${outVar1}" --version 2   success=value error=error
executeScript --handleError --name "ScriptName" \
              --parameters "p1=${v1}" --output "out1=${o1}" --version 2 \
              success=value error=error

# Get Control Center parameters (SaaS tenant parameters)  ← confirmed: OrangeHRM WAL
getParameters --mappings "PARAM_NAME=${varName}"   success=value

# Set bot timeout
setTimeOut --timeout "00:00:45"

# ⚠️ UNCONFIRMED commands:
# getEnvironmentVariable --name "COMPUTERNAME"   host=value   # unconfirmed
# sleep --milliseconds 2000                                   # unconfirmed
# inputBox --title "Input Required" --prompt "Enter ID:"   result=value  # unconfirmed
# messageBox --title "Complete" --message "Done."            # unconfirmed
# openUrl --url "https://example.com"                        # unconfirmed
```

> **Validated notes (§25):**
> - `runDOSCommand` ✅ confirmed
> - `powerShell` ✅ confirmed (cp4ba-labs), supports `--handleerror`, `--apartmentState`
> - `runCSharpCode` ✅ confirmed [30+]
> - `executeScript` ✅ confirmed (OrangeHRM WAL) — uses `--name`, `--parameters`, `--output`, `--version`, `--handleError`
> - `getParameters` ✅ confirmed (OrangeHRM WAL) — reads Control Center parameters
> - `setTimeOut` ✅ confirmed (OrangeHRM WAL)

---

## 26. UI Interaction Helpers

```wal
# Screen capture  ← confirmed: IBM Docs + scriptModel.wal (angeloalves88)
printScreen   screenshot=value
saveImage --image ${screenshot} --directory "${logDir}" \
          --createrandomfile --format "Png"   savedPath=value

# Window focus  ← confirmed: community WAL (focusWindow, not setFocus/bringWindowToFront)
focusWindow --window "${window}"

# ⚠️ UNCONFIRMED UI helper commands:
# setClipboard --text "${value}"
# getClipboard   result=value
# mouseClick  --x 500 --y 300
# mouseMove   --x 500 --y 300
# mouseScroll --direction "Down" --amount 3
# keyPress    --key "ENTER"
# sendKeys    --keys "{CTRL+A}{COPY}"
# minimizeWindow --window "${window}"
# maximizeWindow --window "${window}"
# resizeWindow   --window "${window}" --width 1280 --height 720
```

> **Validated corrections (§26):**
> - `setFocus` → **`focusWindow`** (confirmed community WAL)
> - `bringWindowToFront` → **`focusWindow`** (confirmed community WAL)
> - `printScreen` + `saveImage` ✅ confirmed

---

## 27. Selector Strategy Quick Reference

### Web selectors (CSS / XPath)

| Priority | Strategy | Example | Use when |
|---|---|---|---|
| 1 ✅ | `#id` | `--css "#submit-btn"` | Element has stable HTML `id` |
| 2 ✅ | `[data-testid]` | `--css "[data-testid='login']"` | App uses test IDs |
| 3 ✅ | `[aria-label]` | `--css "[aria-label='Submit']"` | Accessible label present |
| 4 ✅ | `.class-name` | `--css ".btn-primary"` | Unique, stable CSS class |
| 5 ⚠️ | `tag[attr]` | `--css "input[type='submit']"` | Attribute-based |
| 6 ⚠️ | XPath | `--xpath "//button[text()='Save']"` | No CSS option |
| 7 ❌ | `nth-child` | `tr:nth-child(3)` | **AVOID** — breaks on layout change |

Selector type parameter: `"CssSelector"` or `"XPath"`

### Windows / Java selectors (XPath by Accessibility role)

```
/root                          — root container
  /root_pane[1]                — top-level window pane
    /layered_pane[1]           — layered pane (Swing)
      /panel[1]                — JPanel
        /text[1]               — JTextField
        /password_text[1]      — JPasswordField
        /push_button[1]        — JButton
        /check_box[1]          — JCheckBox
        /combo_box[1]          — JComboBox
        /list[1]/list_item[1]  — JList item
```

**Always capture Java/Windows XPaths from the IBM RPA Studio Recorder** — do not guess.

---

## Appendix — Key WAL Patterns

### Python Integration (via runDOSCommand)

```wal
# Run Python; receive result as String
runDOSCommand --command "python script.py ${arg}"   output=value error=value

# Parse a pipe-delimited list returned from Python
# NOTE: use splitString (confirmed), not textSplit (unconfirmed)
splitString --text "${output}" --delimiteroption "CustomDelimiter" \
            --customdelimiter "|"   itemList=value
listCount --list "${itemList}"   itemCount=value
for --variable ${i} --from 0 --to ${itemCount} --step 1
  listGetAt --list "${itemList}" --index "${i}"   item=value
  # process ${item}
next
```

### Excel Row Deletion Workaround

```wal
excelGetTable       --application "${excelApp}" --sheet "Sheet1" \
                    --fromRow 1 --fromColumn 1   tableData=value
deleteRows          --datatable "${tableData}" --columnname "Status" --value "Done"
excelCreateFromDataTable --application "${excelApp}" --sheet "Sheet1" \
                    --datatable "${tableData}" --startRow 1 --startColumn 1
excelSave           --application "${excelApp}"
```

### Queue Dispatcher–Performer

```wal
# Dispatcher: enqueue items
for --variable ${i} --from 1 --to ${lastRow} --step 1
  excelReadCell --application "${excelApp}" --sheet "Sheet1" \
                --row ${i} --column 1   payload=value
  mqPut --connection "${queueConn}" --message "${payload}"
next

# Performer: drain queue
while --left "True" --operator "Equal_To" --right "True"
  mqGet --connection "${queueConn}" --timeout "00:00:05"   msg=value hasMsg=value
  if --left "${hasMsg}" --operator "Is_True" --negate
    break
  endIf
  goSub --label ProcessItem
  mqComplete --connection "${queueConn}" --message "${msg}"
endWhile
```

---

*Sources: IBM Docs 21.0.x / 23.0.x / 30.0.x · IBM Community · GitHub:angeloalves88/IBM-RPA-Script-Framework · GitHub:cguillencr/IBM-RPA-tool · IBM CP4BA Labs*
