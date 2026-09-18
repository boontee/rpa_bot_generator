# WAL Command Reference — IBM RPA

> IBM RPA 30.x command reference for use with the `ibm-rpa` Bob skill.  
> Syntax: `commandName --param "value"   outputVar=value`  
> Variables: `${varName}` — declared with `defVar --name varName --type TYPE`

---

## Data Types

| Type | WAL keyword | Description | Example |
|---|---|---|---|
| `String` | `String` | Text | `"hello world"` |
| `Numeric` | `Numeric` | Integer or decimal | `42`, `3.14` |
| `Boolean` | `Boolean` | True/False | `True`, `False` |
| `DateTime` | `DateTime` | Date and time | `2025-01-15 08:00:00` |
| `List` | (via `defList`) | Ordered string list | `StringList` inner type |
| `DataTable` | (via `defDataTable`) | Rows + columns tabular data | |
| `DbConnection` | `DbConnection` | Database connection handle | |
| `Excel` | `Excel` | Open workbook handle | |
| `Image` | `Image` | Screenshot / image data | |
| `QueueConnection` | `QueueConnection` | IBM RPA queue connection | |
| `MessageQueue` | `MessageQueue` | Queue message reference | |

---

## Variables & Data

```wal
# Declare variables (all at top of script)
defVar --name myVar      --type String
defVar --name count      --type Numeric
defVar --name isReady    --type Boolean
defVar --name today      --type DateTime
defVar --name excel      --type Excel
defVar --name screenshot --type Image

# Assign a value — NOTE: --name takes a LITERAL string, not "${varName}"
setVar --name "myVar" --value "hello"
setVar --name "count" --value "0"

# Declare and populate a list
defList --name myList --type StringList
listAdd      --list "${myList}" --value "item1"
listGetAt    --list "${myList}" --index "${i}"   item=value
listCount    --list "${myList}"                  count=value
listRemoveAt --list "${myList}" --index "${i}"
listClear    --list "${myList}"

# Declare a DataTable
defDataTable --name myTable

# Increment / Decrement (preferred over setVar for counters)
incrementVar --number ${count}    # count = count + 1
decrementVar --number ${count}    # count = count - 1

# Arithmetic — use evaluate, not setVar
evaluate --expression "${a} + ${b}"   result=value

# Get current date/time
getCurrentDateAndTime --localorutc "LocalTime"   today=value

# Format a date
formatDateTime --datetime "${today}" --format "yyyy-MM-dd"   str=value
dateTimeToText --date "${today}" --usecustomformat --customformat "yyyy-MM-dd"   myVar=value
```

---

## Control Flow

```wal
# If / Else
# Operators: Equal_To  Not_Equal  Greater_Than  Greater_Than_Or_Equal
#            Less_Than  Less_Than_Or_Equal  Contains  Not_Contains
#            Is_True  Is_False  Is_Empty  Is_Not_Empty
if --left "${status}" --operator "Equal_To" --right "Success"
  logMessage --message "succeeded" --type "Info"
else
  logMessage --message "failed" --type "Error"
endIf

# Negate a condition
if --left "${found}" --operator "Is_True" --negate
  logMessage --message "Not found" --type "Warning"
endIf

# For loop
for --variable ${i} --from 1 --to 10 --step 1
  logMessage --message "Row ${i}" --type "Info"
next

# For-each (iterate a List)
foreach --collection "${myList}" --variable "${item}"
  logMessage --message "Item: ${item}" --type "Info"
endFor

# While loop
while --left "${count}" --operator "Greater_Than" --right "0"
  # ... work ...
  decrementVar --number ${count}
endWhile

# Break out of a loop
break

# Call a subroutine
goSub --label MySubroutine

# Conditional call
gosubIf --label MySubroutine --left "${count}" --operator "Greater_Than" --right "0"

# Subroutine definition
beginSub --name MySubroutine
  # ... commands ...
endSub

# Stop cleanly (no error)
stopExecution

# Throw an error (stops execution with error)
throwError --message "Unexpected state: ${status}"
```

---

## Logging

```wal
logMessage --message "→ Login: start"             --type "Info"
logMessage --message "Processing item ${itemId}"  --type "Info"
logMessage --message "Retrying after timeout"     --type "Warning"
logMessage --message "Login failed for user"      --type "Error"
# Types: Info | Warning | Error

# Built-in runtime variables for error diagnostics
# ${rpa:subName}            — currently executing subroutine
# ${rpa:error.Message}      — last error message
# ${rpa:error.Routine}      — subroutine where the error occurred
# ${rpa:error.LineNumber}   — line number of the error

# Capture screenshot for error reports
printScreen   screenshot=value
saveImage --image ${screenshot} --directory "${logPath}" \
          --createrandomfile --format "Png"   savedPath=value
```

---

## Process Variables (IBM BAW integration)

```wal
# Preferred: bind each variable individually (avoids Variable.Parse null crash)
getProcessVariable --name "username"   username=value
getProcessVariable --name "orderId"    orderId=value

# Alternative (only if JSON form works in your Studio version)
bindProcessVariables --mappings "{\"username\":\"${username}\",\"orderId\":\"${orderId}\"}"

# Write a value back to a BAW process variable
setProcessVariable --name "outputStatus" --value "${status}"
setProcessVariable --name "rowCount"     --value "${rowCount}"
```

---

## IBM RPA Vault / Assets

```wal
# Read a credential or secret from the IBM RPA Vault
getAsset --name "ERP_PASSWORD"   password=value
getAsset --name "DB_CONNECTION_STRING"   connStr=value
```

---

## Web Automation (Classic — WebDriver)

### Browser lifecycle
```wal
webStart --name web01 --type "Chrome" --userprofilepreferences "AutomationOptimized" --downloadpath "C:\RPA\downloads"
webNavigate --url "https://app.example.com/login"
webClose --name web01
# Browser types: Chrome | Firefox | Edge
```

### Waiting
```wal
# Wait for element to appear — MUST precede every interaction
webWaitElement --selector "CssSelector" --css "#submit-btn" --timeout "00:00:30"   success=value
webWaitElement --selector "XPath" --xpath "//button[@type='submit']" --timeout "00:00:20"   success=value
# success=True when found, False when timed out
```

### Reading & writing
```wal
# Type into a field
webSet --value "${username}" --selector "CssSelector" --css "#username" --simulatehuman

# Read text content of an element
webGet --selector "CssSelector" --css "#status-message"   statusText=value

# Click an element
webClick --selector "CssSelector" --css "#login-btn" --simulatehuman

# Select a combo box / dropdown
webSetComboBox --selectoptionby "Value" --value "${industry}" --selector "CssSelector" --css "#industry-select" --simulatehuman
# selectoptionby: Value | Text | Index

# Read all rows from an HTML table into a DataTable
webGetDataTable --selector "CssSelector" --css "#results-table"   tableData=value

# Get an attribute value
webGetAttribute --attribute "href" --selector "CssSelector" --css "a.download-link"   linkUrl=value
```

### Navigation & page state
```wal
webWaitPage --timeout "00:00:30"
webWaitUrl --url "**/dashboard" --timeout "00:00:20"
webExecuteScript --script "window.scrollTo(0, document.body.scrollHeight);"
webTakeScreenshot --path "C:\RPA\screenshots\error.png"
```

---

## Smart Web Commands (Browser Extension)

Prefer these for modern SPAs when the classic WebDriver commands are flaky.

```wal
openBrowser --url "https://app.example.com" --browsertype "Chrome"
typeText --text "${searchTerm}" --description "Search box"
clickElement --description "Submit button"
selectItem --item "${option}" --description "Country dropdown"
closeBrowser
```

---

## Excel / Office Automation

```wal
# Open / create workbook
excelOpen --path "${inputFile}" --readOnly false   excelApp=value
createOfficeFile --type "Excel" --path "${newPath}"   excelApp=value

# Read
excelReadCell  --application "${excelApp}" --sheet "Sheet1" --row 2 --column 1   cellValue=value
excelGetLastRow --application "${excelApp}" --sheet "Sheet1"   lastRow=value
excelGetLastColumn --application "${excelApp}" --sheet "Sheet1"   lastCol=value
excelReadRange --application "${excelApp}" --sheet "Sheet1" \
               --startRow 1 --startColumn 1   tableData=value
excelGetTable  --application "${excelApp}" --sheet "Sheet1" \
               --fromRow 1 --fromColumn 1   tableData=value

# Write
excelWriteCell --application "${excelApp}" --sheet "Sheet1" \
               --row 2 --column 1 --value "${result}"
excelCreateFromDataTable --application "${excelApp}" --sheet "Sheet1" \
                         --datatable "${tableData}" --startRow 1 --startColumn 1

# Format & macros
excelMergeCells --application "${excelApp}" --sheet "Sheet1" \
                --startRow 1 --startColumn 1 --endRow 1 --endColumn 3
runMacroOffice  --application "${excelApp}" --macro "MacroName"

# Save and close
excelSave  --application "${excelApp}"
excelClose --application "${excelApp}"
```

---

## File & Folder Operations

```wal
# Text file read/write
fileRead  --path "${filePath}"                              content=value
fileWrite --path "${outPath}" --content "${text}" --overwrite true

# File operations
fileExists  --path "${filePath}"                            exists=value
fileCopy    --sourcePath "${src}" --destinationPath "${dest}"
fileMove    --sourcePath "${src}" --destinationPath "${dest}"
fileDelete  --path "${filePath}"
ifFile      --file "${filePath}"                            success=value

# Folder operations
createDir    --path "${folderPath}"       # alias: folderCreate
folderExists --path "${folderPath}"       exists=value
ifFolder     --path "${folderPath}"       success=value

# Special system folders
getSpecialFolder --folder "Desktop"   path=value
# Values: Desktop | Documents | Downloads | Temp | AppData

# List files / zip
getFiles   --path "${folderPath}" --filter "*.xlsx"   fileList=value
zipFiles   --sourcePath "${folder}"  --destinationPath "${zipFile}"
unzipFiles --sourcePath "${zipFile}" --destinationPath "${outFolder}"
```

---

## Database (SQL)

```wal
# Connect
dbConnect --connectionstring "${connStr}" --provider "SqlServer"   dbConn=value
# Providers: SqlServer | Oracle | PostgreSQL | MySQL | DB2 | ODBC

# Query → DataTable
dbQuery --connection "${dbConn}" --query "SELECT id, name FROM orders WHERE status = 'Pending'"   results=value

# Execute (INSERT / UPDATE / DELETE)
dbExecute --connection "${dbConn}" --query "UPDATE orders SET status='Done' WHERE id=${orderId}"

# Parameterized query (prevents SQL injection)
dbQuery --connection "${dbConn}" --query "SELECT * FROM users WHERE id = @userId" --parameters "{\"userId\":\"${userId}\"}"   results=value

# Disconnect
dbClose --connection "${dbConn}"
```

---

## Queue / Message Queue

```wal
# Connect to IBM RPA queue
mqConnect --queueName "${queueName}" --server "${mqServer}"   queueConn=value

# Get next message (non-blocking: success=False if empty)
mqGet --connection "${queueConn}" --timeout "00:00:10"   message=value success=value

# Put a message
mqPut --connection "${queueConn}" --message "${payload}"

# Acknowledge / complete a message
mqComplete --connection "${queueConn}" --message "${message}"

# Mark message as failed
mqFail --connection "${queueConn}" --message "${message}" --reason "${errorMessage}"

# Disconnect
mqClose --connection "${queueConn}"
```

---

## PDF & OCR

```wal
# Extract text from a PDF
pdfExtractText --path "${pdfPath}"   extractedText=value

# OCR — read text from an image or screen region
ocrReadText --imagePath "${imagePath}"   ocrText=value

# Open PDF application
pdfOpen --path "${pdfPath}"   pdfApp=value
pdfClose --application "${pdfApp}"
```

---

## Email

```wal
# Connect (IMAP)
emailConnect --server "${mailServer}" --port 993 --ssl true --username "${mailUser}" --password "${mailPass}"   emailConn=value

# Send email (SMTP)
emailSend --to "${recipientEmail}" --subject "RPA Report" --body "${reportBody}" --smtpServer "${smtpServer}"

# Get unread emails
emailGet --connection "${emailConn}" --folder "INBOX" --unreadOnly true   emails=value

# Disconnect
emailClose --connection "${emailConn}"
```

---

## SAP GUI Automation

```wal
# Start SAP
sapOpen --connectionString "${sapConn}"   sapApp=value

# Navigate (transaction)
sapSet --application "${sapApp}" --field "Transaction" --value "FB60"

# Set a field value
sapSet --application "${sapApp}" --field "Vendor" --value "${vendorId}"

# Read a field value
sapGet --application "${sapApp}" --field "DocumentNumber"   docNumber=value

# Click a button
sapClick --application "${sapApp}" --button "Save"

# Close SAP
sapClose --application "${sapApp}"
```

---

## System / OS

```wal
# Run a PowerShell command
powerShell --script "Get-Date -Format 'yyyy-MM-dd'"   psOutput=value

# Run a DOS/shell command
runDOSCommand --command "taskkill /F /IM chrome.exe"

# Get an environment variable
getEnvironmentVariable --name "COMPUTERNAME"   hostname=value

# Sleep / wait
sleep --milliseconds 2000
```

---

## Selector Quick Reference

| Strategy | When to use | Example |
|---|---|---|
| `#id` | Element has a stable HTML `id` | `--css "#submit-btn"` |
| `[data-testid='x']` | App uses test IDs | `--css "[data-testid='login']"` |
| `[aria-label='x']` | Accessible label present | `--css "[aria-label='Submit']"` |
| `.class-name` | Unique, stable CSS class | `--css ".btn-primary"` |
| `tag[attr='val']` | Attribute selector | `--css "input[type='submit']"` |
| XPath | No CSS option available | `--xpath "//button[text()='Save']"` |
| `nth-child` | **AVOID** — fragile | ❌ `tr:nth-child(3)` |

Selector type parameter values: `"CssSelector"` or `"XPath"`
