# IBM RPA Bob Skill

A Bob skill that teaches IBM Bob to generate, edit, review, and refactor IBM RPA **WAL scripts** (`.wal` files) — the native scripting language of IBM RPA Studio.

## Activation

The skill activates **automatically** when you:
- Ask Bob to create an IBM RPA bot or WAL script
- Open or reference a `.wal` file
- Mention keywords: `IBM RPA`, `WAL script`, `RPA bot`, `defVar`, `beginSub`, `webStart`, `IBM RPA Studio`

You can also invoke it explicitly:

```
/ibm-rpa
```

## What This Skill Does

When active, Bob generates WAL scripts that:

- Follow the **mandatory script layout** (variables → bindings → main flow → subroutines → version stamp)
- **Never hardcode credentials** — uses `bindProcessVariables` or IBM RPA Vault `getAsset`
- Always call `webWaitElement` before every web interaction
- Include structured `logMessage` logging at the start and end of every subroutine
- Call `Cleanup` on both success and error paths
- Use stable CSS selectors (`#id`, `[data-testid]`) over fragile position-based ones
- Pass a pre-output checklist before the file is written

## Skill Files

| File | Purpose |
|---|---|
| [`.bob/skills/ibm-rpa/SKILL.md`](.bob/skills/ibm-rpa/SKILL.md) | Skill entry point — rules, script structure, pre-output checklist |
| [`.bob/skills/ibm-rpa/wal-reference.md`](.bob/skills/ibm-rpa/wal-reference.md) | Full WAL command reference by category |
| [`.bob/skills/ibm-rpa/conventions.md`](.bob/skills/ibm-rpa/conventions.md) | Naming conventions, patterns, and team standards |
| [`.bob/skills/ibm-rpa/examples/web-login.wal`](.bob/skills/ibm-rpa/examples/web-login.wal) | Web authentication pattern with 2FA detection |
| [`.bob/skills/ibm-rpa/examples/excel-reader.wal`](.bob/skills/ibm-rpa/examples/excel-reader.wal) | Excel read / loop / write pattern |
| [`.bob/skills/ibm-rpa/examples/excel-reconcile.wal`](.bob/skills/ibm-rpa/examples/excel-reconcile.wal) | Two-file data reconciliation with status report |
| [`.bob/skills/ibm-rpa/examples/queue-processor.wal`](.bob/skills/ibm-rpa/examples/queue-processor.wal) | Queue performer pattern (drain loop, complete/fail) |

## Usage Examples

### Generate a new bot

```
Create an IBM RPA WAL script that logs into https://erp.example.com,
navigates to the Invoices page, and exports the pending list to CSV.
```

### Edit an existing script

```
Edit @bots/invoice_export.wal to retry login up to 3 times before aborting.
```

### Literate coding inside a `.wal` file

Open a `.wal` file, press `Cmd+I` / `Ctrl+I`, write a natural language comment
in the body, then press `Cmd+Enter` to generate WAL commands in-place:

```wal
beginSub --name ExtractTable
  # wait for table #invoices-grid, read all rows into a DataTable, log row count
endSub
```

### Reference the command guide

```
What WAL commands are available for SAP automation? @.bob/skills/ibm-rpa/wal-reference.md
```

## Mandatory WAL Script Structure

Every generated script follows this layout:

```
defVar declarations
bindProcessVariables          ← if called from IBM BAW
goSub --label Init
goSub --label [CoreStep...]
goSub --label Cleanup

beginSub --name Init ... endSub
beginSub --name [CoreStep] ... endSub
beginSub --name Cleanup ... endSub    ← always last; always closes browser/files
* 30.0.2                              ← version stamp on final line
```

## Supported Automation Types

### Web Automation
Automates browser-based applications using WebDriver commands.

```wal
webStart --name web01 --type "Chrome" --userprofilepreferences "AutomationOptimized"
webNavigate --url "https://app.example.com"
webWaitElement --selector "CssSelector" --css "#username" --timeout "00:00:30"
webSet --value "${username}" --selector "CssSelector" --css "#username" --simulatehuman
webClick --selector "CssSelector" --css "#login-btn" --simulatehuman
webClose --name web01
```

### Java Application UI Automation
Automates Java Swing / AWT desktop applications via **Java Access Bridge (JAB)**.

**Prerequisites:**
- 64-bit Windows only
- Java Access Bridge must be enabled: run `jabswitch -enable` on the bot machine
- XPath selectors must be captured using IBM RPA Studio's recorder

**Core commands:**

```wal
launchWindow --executablepath "C:\Apps\MyApp.jar"   vWindow=value vPID=processId vSuccess=success
waitWindow --title "My Application"                  vWindow=value vPID=processId vSuccess=success
attachWindow --window ${vWindow}
setValue --value "${inputData}" --setValueType "Automatic" --algorithm "Default" --matchcondition "Equals" --selector "XPath" --xpath "/root/root_pane[1]/layered_pane[1]/panel[1]/text[1]"
getValue --selector "XPath" --xpath "/root/root_pane[1]/layered_pane[1]/panel[1]/text[3]"   result=value
click --selector "XPath" --controlsimilarity 100 --xpath "/root/root_pane[1]/layered_pane[1]/panel[1]/push_button[1]"
```

**Java Swing XPath control types:**

| Swing Component | XPath node type |
|---|---|
| `JTextField` | `text` |
| `JPasswordField` | `password_text` |
| `JButton` | `push_button` |
| `JCheckBox` | `check_box` |
| `JRadioButton` | `radio_button` |
| `JComboBox` | `combo_box` |
| `JPanel` | `panel` |

> **Important:** Java XPaths cannot be guessed — capture them from IBM RPA Studio's recorder, then provide them to Bob to generate the full script.

### Excel / Office Automation
Reads and writes Excel workbooks without opening a browser.

```wal
excelOpen --path "${filePath}" --readOnly false   excelApp=value
excelGetLastRow --application "${excelApp}" --sheet "Sheet1"   lastRow=value
excelReadCell --application "${excelApp}" --sheet "Sheet1" --row 2 --column 1   cellValue=value
excelWriteCell --application "${excelApp}" --sheet "Sheet1" --row 2 --column 2 --value "${result}"
excelSave --application "${excelApp}"
excelClose --application "${excelApp}"
```

### Queue-Based (Dispatcher / Performer)
For high-volume processing — see [`examples/queue-processor.wal`](.bob/skills/ibm-rpa/examples/queue-processor.wal).

## Security Rules

| Rule | Detail |
|---|---|
| No hardcoded credentials | Use `bindProcessVariables` or `getAsset --name "VAULT_ASSET"` |
| No password logging | Never include a password variable in `logMessage` |
| Least privilege | Bot service account scoped to minimum required resources |

## Web Selector Priority

1. `#id` — most stable
2. `[data-testid='x']`
3. `[aria-label='x']`
4. `.stable-class`
5. XPath — fallback only
6. ~~`nth-child`~~ — **never use**, breaks on UI change

## IBM RPA References

- [IBM RPA Commands Reference (v30)](https://www.ibm.com/docs/en/rpa/30.0.x?topic=commands)
- [IBM RPA Script Development](https://www.ibm.com/docs/en/rpa/21.0.x?topic=automation-developing-scripts)
- [IBM RPA Windows Automation](https://www.ibm.com/docs/en/rpa/30.0.x?topic=tasks-windows-automation)
- [IBM RPA MCP Server](https://www.ibm.com/docs/en/rpa/30.0.x?topic=client-rpa-mcp-server)
- [IBM cp4ba-labs WAL Examples](https://github.com/IBM/cp4ba-labs)
