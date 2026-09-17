# Knowledge Base: Using Coding Agents to Create RPA Bots

> **Last updated:** 2025  
> **Scope:** How AI coding agents can be used to generate, scaffold, test, and deploy Robotic Process Automation (RPA) workflows and bots.

---

## 1. Conceptual Foundation

### 1.1 What is RPA?

Robotic Process Automation (RPA) automates repetitive, rule-based digital tasks by mimicking human interactions with software UIs, APIs, and data sources — without modifying existing systems. Classic RPA excels at:

- High-volume, low-variation workflows (data entry, copy-paste, form filling)
- Structured data processing (spreadsheets, databases)
- Deterministic multi-step processes with stable UIs

**Limitations of classic RPA:**
- Fragile against UI changes (brittle selectors)
- Cannot handle unstructured data or ambiguous inputs
- Requires specialist scripting / low-code expertise to author bots

---

### 1.2 What is a Coding Agent?

A coding agent is an AI system that:
1. Accepts a **goal or process description** as input
2. **Plans** the required steps autonomously
3. **Generates** executable code or workflow files
4. **Executes** the code, observes the results, and self-corrects
5. **Packages and deploys** the output to a target runtime

Coding agents differ from chatbots in that they operate in a **multi-step loop** (ReAct pattern: Thought → Action → Observation → Repeat) rather than producing a single response.

---

### 1.3 RPA vs AI Agents vs Coding Agents for RPA

| Dimension | Classic RPA | AI Agent | Coding Agent for RPA |
|---|---|---|---|
| Input | Fixed workflow definition | Natural language goal | Natural language process description |
| Logic | Rule-based scripts | Reasoning + planning | Code generation + scaffolding |
| Adaptability | Low – breaks on UI change | High – adapts to context | Medium – generates deterministic code |
| Output | Running bot | Decisions + actions | RPA code / workflow files |
| Governance | Orchestrator-managed | Requires own guardrails | Inherits RPA platform governance |
| Best for | Stable, high-volume tasks | Dynamic, knowledge-intensive | Accelerating RPA authoring |

---

## 2. Approaches to Coding-Agent-Driven RPA Bot Generation

### 2.1 Approach A — Direct Code Generation (Python / Playwright / Selenium)

The agent generates Python scripts that drive a browser or desktop UI directly.

**Stack:**
- **Language:** Python 3.11+
- **Browser Automation:** Playwright (preferred) or Selenium WebDriver
- **AI Orchestration:** LangChain / LangGraph / CrewAI
- **Packaging:** Docker or virtual environment

**Typical prompt flow:**
```
SYSTEM: You are an RPA developer. Generate a Python Playwright script that:
- Automates the following process: {process_description}
- Includes error handling for network timeouts and missing elements
- Uses auto-waiting (no hardcoded sleep())
- Returns structured output as JSON

USER: "Log into the HR portal at https://hr.example.com, navigate to
       leave requests, and download all pending requests as CSV."
```

**Why Playwright over Selenium for AI-generated bots:**
- Built-in auto-wait eliminates the #1 source of flaky AI-generated code (`sleep()` hacks)
- Cross-browser support (Chrome, Firefox, Safari) without extra drivers
- Native headless/headed toggle — easier for agents to reason about
- Better tracing and screenshot APIs for debugging agent-generated scripts

---

### 2.2 Approach B — UiPath Coded Agents (Enterprise)

UiPath's "Coded Agents" platform allows coding agents (Claude, Codex, Copilot, Gemini) to scaffold, test, and deploy UiPath workflows natively from an IDE or terminal.

**Architecture:**
```
Coding Agent (Claude / Codex / Copilot)
    ↓  uses UiPath Agent Skills (open-source, AGENTS.md format)
UiPath CLI
    ↓  uipath new / uipath pack / uipath publish
UiPath Orchestrator
    ↓  schedule / trigger / govern / audit
Running Robot
```

**Development lifecycle (CLI commands):**
```bash
uipath auth               # Link local IDE to UiPath tenant
uipath new <agent_name>   # Scaffold project structure
# ... agent writes logic in Python + uipath-python SDK ...
uipath pack               # Compile to .nupkg package
uipath publish            # Push to Orchestrator feed
```

**Key SDKs:**
| SDK | Primary Use |
|---|---|
| `uipath-python` | Core CLI, credentials (Assets), storage, job triggering |
| `uipath-langchain-python` | Multi-agent LangGraph workflows |
| `uipath-llamaindex-python` | RAG / document-heavy workflows |

**Best practice from UiPath docs:** The coding agent generates **deterministic RPA by default**. ScreenPlay (agentic UI activities) should be added only at specific brittle points — keep the agentic surface minimal.

---

### 2.3 Approach C — LLM-Driven Workflow Generation (FlowMind / PromptRPA)

Academic/research approaches where an LLM directly generates workflow specifications (e.g., BPMN, JSON-based DSLs) from natural language.

**FlowMind (ACM 2024):**
1. **Stage 1:** LLM learns API knowledge from documentation
2. **Stage 2:** LLM maps user queries → workflow code using that API knowledge
3. Result: Full workflow graph generated from a single prompt

**PromptRPA (Tsinghua University, 2024):**
- Targets smartphone GUI automation
- Accepts high-level goals ("change the ringtone") or step-by-step instructions
- Achieved **95.21% success rate** (up from 22.28% baseline) with continuous learning from user feedback
- Average of 1.66 user interventions per new task

---

## 3. Prompting Strategies for RPA Bot Generation

### 3.1 The ReAct Pattern (Foundational)

All effective coding agents for RPA use some variant of ReAct (Reasoning + Acting):

```
Thought: I need to automate invoice extraction from the portal.
Action: generate_code("login to portal, navigate to invoices, download PDF list")
Observation: Code generated — 48 lines of Playwright Python
Thought: I should add error handling for session timeouts.
Action: modify_code(add_try_catch_for_timeout)
Observation: Code updated with retry logic
Thought: Ready to package.
Action: run_tests()
```

### 3.2 Key Prompting Techniques

#### Provide Process Documentation as Context
```
You are an RPA developer. The following SOP describes the process:
<SOP>
1. Open SAP transaction FB60
2. Enter vendor number from column A of the attached spreadsheet
3. Enter invoice amount from column B
4. Set payment term to "NET30"
5. Save and note the document number back to column C
</SOP>
Generate a Python RPA script using uipath-python SDK that implements this SOP exactly.
```

#### Specify Constraints Up Front
```
Constraints:
- Do NOT use hardcoded sleep() calls — use explicit waits or auto-wait APIs
- All credentials must be read from environment variables, never hardcoded
- Include structured JSON logging for each step
- Handle ElementNotFoundError with a 3-attempt retry + exponential backoff
- Use Page Object Model pattern for selector management
```

#### Define the Output Contract
```
The script must:
1. Accept these parameters: portal_url (str), username (str from env), output_path (str)
2. Return: {"status": "success"|"error", "records_processed": int, "error_message": str|null}
3. Exit with code 0 on success, 1 on handled error, 2 on unhandled exception
```

#### Iterative Refinement Prompt
```
The generated script fails when the portal shows a CAPTCHA on login.
Modify the script to:
1. Detect the presence of a CAPTCHA element (selector: #captcha-container)
2. Pause and send a Human-in-the-Loop notification via Orchestrator Action Center
3. Resume once the human completes the CAPTCHA and approves continuation
```

### 3.3 Anti-Patterns to Avoid in Prompts

| Anti-Pattern | Problem | Fix |
|---|---|---|
| "Automate this website" (no details) | Agent hallucinates steps | Provide exact URL, step-by-step SOP, field names |
| No error handling specification | Generated code has no resilience | Explicitly list failure modes and expected handling |
| No credential guidance | Agent hardcodes secrets | State "read credentials from environment variables" |
| Monolithic prompt for complex flows | Context overload → poor quality | Break into sub-tasks: login → navigate → extract → export |
| Ignoring selector strategy | Brittle generated code | Specify preferred selector strategy (data-testid, ARIA, etc.) |

---

## 4. Technical Architecture Patterns

### 4.1 Minimal Deterministic + Targeted Agentic (Recommended)

```
┌─────────────────────────────────────────────────┐
│  RPA Workflow                                    │
│                                                  │
│  [Login]       ← Deterministic (stable selectors)│
│  [Navigate]    ← Deterministic                   │
│  [Read Invoice]← AGENTIC (unstructured PDF/image)│
│  [Fill Form]   ← Deterministic                   │
│  [Submit]      ← Deterministic                   │
└─────────────────────────────────────────────────┘
```

**Principle:** Keep the agentic surface as small as possible. Every deterministic step:
- Costs no LLM call → faster and cheaper at scale
- Behaves identically every run → safe for unattended execution
- Is easier to audit and govern

### 4.2 Human-in-the-Loop (HITL) Integration

Coding agents should generate HITL interrupt points for:
- High-risk decisions (large payments, deletions)
- CAPTCHA / MFA challenges
- Exception cases requiring judgment
- Compliance sign-off requirements

```python
# Agent-generated HITL pattern
from uipath.orchestrator import action_center

def request_human_approval(context: dict) -> bool:
    task = action_center.create_task(
        title="Invoice Approval Required",
        data=context,
        priority="High"
    )
    # Process suspends here — frees robot resources
    result = action_center.wait_for_completion(task.id)
    return result.approved
```

### 4.3 Multi-Agent RPA Architecture

For complex end-to-end workflows, use a coordinator + specialist pattern:

```
┌──────────────────┐
│ Orchestrator Agent│  ← Receives high-level goal
│ (LangGraph)      │  ← Breaks into sub-tasks
└──────┬───────────┘
       ├──→ [Web Scraper Agent]   → Playwright bot
       ├──→ [Data Processor Agent]→ pandas/tabula bot
       ├──→ [Form Filler Agent]   → SAP/ERP bot
       └──→ [Notifier Agent]      → Email/Teams bot
```

---

## 5. Tool Ecosystem

### 5.1 Browser/UI Automation Libraries

| Library | Language | Best For | Agent Compatibility |
|---|---|---|---|
| Playwright | Python/JS/Java | Modern web apps, SPA, dynamic content | Excellent — clean API, good docs for LLM context |
| Selenium | Python/Java/C# | Legacy web apps, broad browser support | Good — widely known in training data |
| PyAutoGUI | Python | Desktop GUI (non-browser) | Fair — limited error handling |
| pywinauto | Python | Windows desktop automation | Fair — Windows only |

### 5.2 AI/Agent Frameworks

| Framework | Use Case |
|---|---|
| LangChain | General agent orchestration, tool use, memory |
| LangGraph | Stateful multi-agent workflows, complex decision cycles |
| LlamaIndex | Document-heavy RAG workflows, knowledge retrieval |
| CrewAI | Role-based multi-agent teams |
| AutoGen | Collaborative AI agent conversations |

### 5.3 RPA Platforms with Coding Agent Support

| Platform | Coding Agent Support | Notes |
|---|---|---|
| UiPath | Native (AGENTS.md, CLI, Agent Skills) | Claude, Codex, Copilot, Gemini all supported |
| Microsoft Power Automate | Copilot Studio integration | Focus on low-code generation |
| Automation Anywhere | CoE Bot Insight + AI | LLM-assisted bot generation |
| Robocorp | Python-first, open RCC toolchain | Strong for code-gen agents |

---

## 6. Quality, Testing, and Governance

### 6.1 Validating Agent-Generated Bot Code

Before deploying any agent-generated RPA:

```
1. Static analysis     — lint + type-check generated Python
2. Selector validation — verify all UI selectors exist in target app
3. Dry run             — execute against a staging environment
4. Edge case testing   — test with empty inputs, network errors, session expiry
5. Compliance review   — audit for hardcoded secrets, PII logging, overly broad permissions
```

### 6.2 UiPath Workflow Analyzer (Automated)

When using UiPath Coded Agents, the coding agent can run workflow analysis automatically:

```bash
# Agent can call this as part of its loop:
uipath analyze --project ./my_bot --fix
```

The analyzer surfaces:
- Dependency version mismatches
- Missing error handlers
- Non-reusable selectors
- Convention violations

### 6.3 Security Checklist for Agent-Generated Bots

- [ ] No hardcoded credentials (must use environment variables or vault)
- [ ] TLS 1.2+ for all HTTP calls in generated code
- [ ] Input validation present for all external data ingested
- [ ] Structured logging without PII or sensitive values
- [ ] Least-privilege: bot credentials scoped to minimum required permissions
- [ ] HITL gates on destructive or financial operations
- [ ] Audit trail: all bot actions logged to Orchestrator or equivalent

---

## 7. Common RPA Use Cases Well-Suited to Coding Agents

| Use Case | Why Coding Agent Helps |
|---|---|
| Invoice/PO data extraction → ERP entry | Agent generates OCR + form-fill logic from process doc |
| Bank reconciliation | Agent scaffolds dispatcher + performer pattern from SOP |
| Customer onboarding document processing | Agent generates multi-step extraction + validation workflow |
| Compliance report generation | Agent creates scheduled data-pull + PDF generation bot |
| IT ticket routing | Agent builds classification + API-routing workflow |
| HR leave request processing | Agent generates portal login + CSV export + email notification |
| Web scraping + structured output | Agent produces Playwright scraper with retry + JSON schema output |

---

## 8. Limitations and Failure Modes

### 8.1 Where Coding Agents Struggle

| Issue | Root Cause | Mitigation |
|---|---|---|
| Brittle selectors | Agent picks obvious but unstable selectors (text content, position) | Prompt to prefer `data-testid`, ARIA roles, stable IDs |
| Missing edge case handling | Agent optimizes the happy path | Explicitly enumerate failure modes in prompt |
| Selector hallucination | Agent invents selectors not present on the page | Always validate against live app before deployment |
| Over-agentic workflows | Agent uses LLM calls where deterministic code works | Review generated code and replace agentic steps with deterministic ones |
| Security gaps | Agent omits auth / credential handling | Mandate security checklist in system prompt |
| Context window limits | Complex processes exceed token limits | Break into sub-processes; use RAG for large SOPs |

### 8.2 When NOT to Use a Coding Agent for RPA

- The process is simple enough for a human to automate in < 1 hour using a no-code tool
- The target system has an official API — use the API instead of UI automation
- The process requires real-time judgment on every record — use an AI agent, not RPA
- Compliance requires full human authorship and review of automation code

---

## 9. Getting Started — Minimal Example

### Generate a Playwright bot with Claude Code (or similar)

```bash
# 1. Create project
mkdir my_rpa_bot && cd my_rpa_bot
python -m venv .venv && source .venv/bin/activate
pip install playwright langchain-anthropic python-dotenv
playwright install chromium

# 2. Create process description file
cat > process.md << 'EOF'
Process: Export Daily Sales Report
1. Navigate to https://reports.internal/login
2. Login with credentials from env vars REPORT_USER, REPORT_PASS
3. Click "Daily Sales" in the left navigation
4. Select today's date in the date picker
5. Click "Export CSV"
6. Save the downloaded file to ./output/sales_YYYY-MM-DD.csv
EOF

# 3. Prompt the coding agent
# Agent system prompt:
# "You are an RPA developer. Read process.md and generate a Playwright Python
#  script. Use auto-waiting, read credentials from environment variables,
#  include try/except with structured JSON logging, and return 
#  {"status": ..., "file_path": ..., "error": ...}."
```

### Expected agent output structure

```python
# agent_generated_bot.py
import os, json, logging
from datetime import date
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logging.basicConfig(format='%(message)s')
logger = logging.getLogger(__name__)

def run_export() -> dict:
    user = os.environ["REPORT_USER"]
    password = os.environ["REPORT_PASS"]
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://reports.internal/login", wait_until="networkidle")
            page.fill('[data-testid="username"]', user)
            page.fill('[data-testid="password"]', password)
            page.click('[data-testid="login-btn"]')
            page.wait_for_url("**/dashboard")

            page.click('[aria-label="Daily Sales"]')
            page.fill('[data-testid="date-picker"]', date.today().isoformat())
            
            with page.expect_download() as dl_info:
                page.click('[data-testid="export-csv"]')
            download = dl_info.value
            filename = f"sales_{date.today().isoformat()}.csv"
            download.save_as(f"{output_dir}/{filename}")

            logger.info(json.dumps({"step": "complete", "file": filename}))
            return {"status": "success", "file_path": f"{output_dir}/{filename}", "error": None}
        except PlaywrightTimeout as e:
            logger.error(json.dumps({"step": "timeout", "error": str(e)}))
            return {"status": "error", "file_path": None, "error": f"Timeout: {e}"}
        finally:
            browser.close()

if __name__ == "__main__":
    result = run_export()
    print(json.dumps(result))
```

---

## 10. References

| Source | Link |
|---|---|
| UiPath Coded Agents Guide | https://rpabotsworld.com/comprehensive-guide-to-uipath-coded-agents/ |
| UiPath for Coding Agents | https://www.uipath.com/developers/coding-agents |
| UiPath ScreenPlay Best Practices | https://docs.uipath.com/agents/automation-cloud/latest/user-guide-ui-agent/best-practices |
| PromptRPA (Tsinghua, 2024) | https://arxiv.org/html/2404.02475v1 |
| FlowMind: LLM Workflow Generation (ACM 2024) | https://arxiv.org/abs/2404.13050 |
| AI Agents vs RPA Comparison | https://codiant.com/blog/ai-agents-vs-rpa/ |
| AI Agent Prompting Guide | https://sureprompts.com/blog/ai-agents-prompting-guide |
| Playwright in RPA | https://www.sphinx-solution.com/blog/how-to-use-playwright-in-rpa/ |
