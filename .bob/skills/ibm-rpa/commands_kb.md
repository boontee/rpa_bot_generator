# IBM RPA WAL Commands — Knowledge Base

> **Sources:** IBM Docs (21.0.x / 23.0.x / 30.0.x), IBM Community, GitHub samples  
> **Syntax:** `commandName --param "value"   outputVar=value`  
> **Variables:** `${varName}` — declared with `defVar --name varName --type TYPE`  
> **Version coverage:** Commands marked `[30+]` were added in 30.0.x; unmarked commands available from 21.0.x onward.

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
# Split a string into a List
splitString --text "${csvLine}" --delimiteroption "Comma"   parts=value
splitString --text "${data}"    --delimiteroption "CustomDelimiter" \
            --customdelimiter "|"   parts=value
# delimiteroption values: Comma | Semicolon | Tab | Space | CustomDelimiter

# Alternative (from web context)
textSplit --text "${rawOutput}" --separator "|"   itemList=value

# Replace text
replaceText --texttoparse "${myStr}" --textpattern "old" \
            --replacementtext "new"   result=value

# Extract with regex
getRegex --text "${output}" --regex "ID: (\d+)"   extracted=value

# Get text length
textLength --text "${myStr}"   len=value

# Get substring
getSubstring --text "${myStr}" --startindex 0 --length 5   sub=value

# Convert case
toUpperCase --text "${myStr}"   upper=value
toLowerCase --text "${myStr}"   lower=value

# Trim whitespace
trimText --text "${myStr}"   trimmed=value

# Check if text contains
textContains --text "${myStr}" --value "search"   found=value

# Concatenate
concatenate --values "${part1},${part2}"   result=value

# Convert to/from number
textToNumber --text "${numStr}"   num=value
numberToText --number "${num}"   txt=value
```

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
# Get current date/time
getCurrentDateAndTime --localorutc "LocalTime"   now=value
getCurrentDateAndTime --localorutc "UTC"         nowUtc=value

# Format a DateTime to string
formatDateTime --datetime "${now}" --format "yyyy-MM-dd"           str=value
formatDateTime --datetime "${now}" --format "dd/MM/yyyy HH:mm:ss"  str=value

# Parse text to DateTime
dateTimeToText  --date "${now}" --usecustomformat --customformat "yyyy,MM,dd"   str=value
textToDateTime  --text "2025-01-15" --format "yyyy-MM-dd"   dt=value

# Add/subtract time
addTimeSpan --datetime "${now}" --days 1 --hours 0 --minutes 0   future=value

# Compare dates
if --left "${now}" --operator "Greater_Than" --right "${deadline}"
  logMessage --message "Overdue" --type "Warning"
endIf
```

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
# Launch an application and attach to its window
launchWindow  --executablepath "C:\Apps\MyApp.exe" \
              --parameters "${args}"   vWindow=value vPID=value vSuccess=value

# Launch OR attach (if already running, attach; otherwise launch)
launchOrAttach --executablepath "C:\Apps\MyApp.exe"   vWindow=value vPID=value

# Wait for a window to appear (by title)
waitWindow --title "My Application" --timeout "00:00:30"   vWindow=value vSuccess=value

# Attach to an already-open window
attachWindow --window "${vWindow}"

# Close a window
closeWindow --window "${vWindow}"
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
# Find anchor image on screen (returns x,y coordinates)
findImageBySimilarity --image "${anchorImagePath}" \
                      --similarity 90   x=value y=value found=value

# Wait for image to appear (blocks until timeout)
waitForImage --image "${anchorImagePath}" --similarity 90 \
             --timeout "00:00:30"   x=value y=value found=value

# Click at image location
clickImage --image "${anchorImagePath}" --similarity 90

# Scope search to a specific window (avoid false positives)
waitForWindow --title "My App"   window=value
findImageBySimilarity --image "${anchorImagePath}" \
                      --window "${window}" --similarity 90   found=value

# Click by OCR (click where text appears on screen)
clickByOCR --text "Submit" --similarity 85

# Get control text by OCR (read value near an anchor image)
getControlTextByOCR --anchorimage "${anchorImagePath}" \
                    --offsetx 100 --offsety 0 \
                    --width 200 --height 30   ocrText=value

# Recognize all text in an image file or PDF page
recognizeImageTextOrPdf --imagepath "${imagePath}"   extractedText=value

# Bring window to front before image operations
setFocus --window "${window}"
bringWindowToFront --window "${window}"
```

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
excelOpen  --path "${filePath}" --readOnly false   excelApp=value
excelSave  --application "${excelApp}"
excelClose --application "${excelApp}"

# Create new workbook
createOfficeFile --type "Excel" --path "${newPath}"   excelApp=value
```

### Reading

```wal
excelReadCell  --application "${excelApp}" --sheet "Sheet1" \
               --row 2 --column 1   cellValue=value

excelGetLastRow --application "${excelApp}" --sheet "Sheet1"   lastRow=value
excelGetLastColumn --application "${excelApp}" --sheet "Sheet1"   lastCol=value

excelReadRange --application "${excelApp}" --sheet "Sheet1" \
               --startRow 1 --startColumn 1   tableData=value

excelGetTable  --application "${excelApp}" --sheet "Sheet1" \
               --fromRow 1 --fromColumn 1   tableData=value
```

### Writing

```wal
excelWriteCell --application "${excelApp}" --sheet "Sheet1" \
               --row 2 --column 1 --value "${data}"

# Write entire DataTable to sheet
excelCreateFromDataTable --application "${excelApp}" --sheet "Sheet1" \
                         --datatable "${tableData}" \
                         --startRow 1 --startColumn 1
```

### Formatting & Sheet Operations

```wal
excelMergeCells   --application "${excelApp}" --sheet "Sheet1" \
                  --startRow 1 --startColumn 1 --endRow 1 --endColumn 3

excelCalculateFormula --application "${excelApp}"   # recalculate all formulas

runMacroOffice --application "${excelApp}" --macro "MacroName"  # run VBA macro
```

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

# Get value at row/column
getDataTableValue --datatable "${myTable}" --row 2 --column 1   cellVal=value

# Set value at row/column
setDataTableValue --datatable "${myTable}" --row 2 --column 1 --value "${newVal}"

# Row count
getDataTableRowCount --datatable "${myTable}"   count=value

# Add row
addDataTableRow --datatable "${myTable}" --values "${v1},${v2},${v3}"

# Sort
sortDataTable --datatable "${myTable}" --columnname "Date" --ascending true
```

---

## 19. File & Folder Operations

```wal
# Text file read/write
fileRead  --path "${filePath}"   content=value
fileWrite --path "${outPath}" --content "${text}" --overwrite true

# File existence, copy, move, delete
fileExists  --path "${filePath}"   exists=value
fileCopy    --sourcePath "${src}" --destinationPath "${dest}"
fileMove    --sourcePath "${src}" --destinationPath "${dest}"
fileDelete  --path "${filePath}"

# Alternate existence check (returns Boolean)
ifFile --file "${filePath}"   exists=value

# Folder operations
createDir   --path "${folderPath}"        # alias: folderCreate
folderExists --path "${folderPath}"   exists=value
ifFolder    --path "${folderPath}"    success=value

# Special system folders
getSpecialFolder --folder "Desktop"   path=value
# Values: Desktop | Documents | Downloads | Temp | AppData

# List files in a folder
getFiles --path "${folderPath}" --filter "*.xlsx"   fileList=value

# Zip / unzip
zipFiles   --sourcePath "${folder}" --destinationPath "${zipFile}"
unzipFiles --sourcePath "${zipFile}" --destinationPath "${outFolder}"
```

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

```wal
# GET request
httpRequest --url "https://api.example.com/data" \
            --method "GET"   response=value statusCode=value

# POST with JSON body
httpRequest --url "https://api.example.com/submit" \
            --method "POST" \
            --body "{\"key\":\"${value}\"}" \
            --contenttype "application/json"   response=value statusCode=value

# With auth header
httpRequest --url "https://api.example.com/secure" \
            --method "GET" \
            --headers "{\"Authorization\":\"Bearer ${token}\"}"   response=value

# Extract JSON values from response
getRegex --text "${response}" --regex "\"id\":(\d+)"   id=value

# Local Python/Flask service (decoupled Python integration)
httpRequest --url "http://127.0.0.1:5000/process" \
            --method "POST" \
            --body "{\"input\":\"${data}\"}"   response=value statusCode=value
```

---

## 23. Email

```wal
# Connect IMAP
emailConnect --server "${mailServer}" --port 993 --ssl true \
             --username "${mailUser}" --password "${mailPass}"   emailConn=value

# Get unread emails
emailGet --connection "${emailConn}" --folder "INBOX" \
         --unreadOnly true   emails=value

# Send SMTP
emailSend --to "${recipient}" --subject "RPA Report" \
          --body "${body}" --smtpServer "${smtpServer}"

# Send with attachment
emailSend --to "${recipient}" --subject "Report" --body "${body}" \
          --smtpServer "${smtpServer}" --attachment "${filePath}"

# Reply to email
emailReply --connection "${emailConn}" --email "${emailObj}" \
           --body "${replyBody}"

# Mark as read
emailMarkAsRead --connection "${emailConn}" --email "${emailObj}"

# Disconnect
emailClose --connection "${emailConn}"
```

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
# DOS / shell command (primary Python invocation method)
runDOSCommand --command "python script.py ${arg1}"   output=value error=value
runDOSCommand --command "taskkill /F /IM chrome.exe"

# PowerShell
powerShell --script "Get-Date -Format 'yyyy-MM-dd'"   psOutput=value
powerShell --script "Get-ChildItem 'C:\RPA' | Measure-Object"   psOutput=value

# Inline C# code [30+]
runCSharpCode --code "return DateTime.Now.ToString(\"yyyy-MM-dd\");"   output=value

# Execute another WAL script [30.0.1+]
executeScript --script "CommonUtils" --tenant "${tenantId}"

# Environment variables
getEnvironmentVariable --name "COMPUTERNAME"   host=value
getEnvironmentVariable --name "USERNAME"       user=value

# Sleep
sleep --milliseconds 2000

# Input dialog (attended bots)
inputBox --title "Input Required" --prompt "Enter order ID:"   result=value

# Message dialog
messageBox --title "Complete" --message "Processing done."

# Open URL in default browser
openUrl --url "https://example.com"
```

---

## 26. UI Interaction Helpers

```wal
# Clipboard
setClipboard --text "${value}"
getClipboard   result=value

# Screen capture
printScreen   screenshot=value
saveImage --image ${screenshot} --directory "${logDir}" \
          --createrandomfile --format "Png"   savedPath=value

# Mouse
mouseClick  --x 500 --y 300
mouseMove   --x 500 --y 300
mouseScroll --direction "Down" --amount 3

# Keyboard
keyPress    --key "ENTER"
sendKeys    --keys "{CTRL+A}{COPY}"

# Window management
bringWindowToFront --window "${vWindow}"
setFocus           --window "${vWindow}"
minimizeWindow     --window "${vWindow}"
maximizeWindow     --window "${vWindow}"
resizeWindow       --window "${vWindow}" --width 1280 --height 720
```

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
textSplit --text "${output}" --separator "|"   itemList=value
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
