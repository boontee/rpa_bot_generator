"""
IBM RPA Docs Crawler
====================
Crawls https://www.ibm.com/docs/en/rpa/30.0?topic=commands and every linked
command detail page. Outputs:
  - commands_crawled.md   — markdown knowledge-base (append-friendly)
  - commands_crawled.json — structured JSON for programmatic use

IMPORTANT — IBM docs network access
-------------------------------------
www.ibm.com/docs returns HTTP 403 from some networks (geo/bot restriction).
If you see "Oops - that's not right!" the machine is blocked.

Three modes of operation:
  1. Normal crawl (default)  -- fetches index page, discovers all command links.
  2. --seed-file urls.txt    -- skip index discovery; crawl a user-supplied list
                               of URLs (one per line). Use when index is blocked
                               but individual pages are accessible.
  3. --local-html dir/       -- parse pre-downloaded HTML files from a directory
                               (saved manually from a browser or wget on another
                               machine). No network access needed.

Usage:
    py tools/ibm_rpa_docs_crawler.py
    py tools/ibm_rpa_docs_crawler.py --version 30.0 --out-dir knowledge_base
    py tools/ibm_rpa_docs_crawler.py --max-pages 10 --delay 2.0 --headless false
    py tools/ibm_rpa_docs_crawler.py --seed-file knowledge_base/command_urls.txt
    py tools/ibm_rpa_docs_crawler.py --local-html knowledge_base/html_pages/

Options:
    --version     IBM RPA version string in the docs URL  (default: 30.0)
    --out-dir     Output directory                        (default: knowledge_base)
    --max-pages   Max command detail pages to crawl       (default: 0 = unlimited)
    --delay       Seconds between page loads              (default: 1.5)
    --headless    Run Chrome headless: true/false          (default: true)
    --seed-file   Path to a text file with one URL per line (skips index page)
    --local-html  Path to a directory of pre-downloaded .html files (offline mode)

Exit codes:
    0  -- success
    1  -- network blocked (403) on index page
    2  -- no commands found
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Parameter:
    name: str
    type: str
    required: bool
    description: str


@dataclass
class CommandEntry:
    name: str
    category: str
    url: str
    description: str
    syntax: str
    parameters: list = field(default_factory=list)
    output_vars: list = field(default_factory=list)
    notes: str = ""


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------

def make_driver(headless: bool) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)


def wait_for_content(driver: webdriver.Chrome, timeout: int = 30):
    """Wait until the main IBM Docs content div is present."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "article, main, .ibm-document-content, #mc-main-content")
            )
        )
    except Exception:
        pass


def get_soup(driver: webdriver.Chrome, url: str, delay: float) -> BeautifulSoup:
    driver.get(url)
    wait_for_content(driver)
    time.sleep(delay)
    return BeautifulSoup(driver.page_source, "lxml")


def is_blocked_page(soup: BeautifulSoup) -> bool:
    """Return True if IBM served a 403/error page instead of real content."""
    title = soup.title.get_text() if soup.title else ""
    h2s = [t.get_text(strip=True) for t in soup.select("h2")]
    return any([
        "cannot be displayed" in title.lower(),
        "403" in title,
        any("oops" in h.lower() for h in h2s),
        any("not right" in h.lower() for h in h2s),
    ])


# ---------------------------------------------------------------------------
# Index page -- collect command links
# ---------------------------------------------------------------------------

def collect_command_links(soup: BeautifulSoup, base_url: str) -> list:
    """
    Returns list of (display_text, absolute_url) for command links on the
    commands index page.
    """
    links = []
    seen = set()

    for a in soup.select(
        "article a[href], main a[href], "
        ".ibm-document-content a[href], #mc-main-content a[href]"
    ):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if not text or not href or "topic=" not in href:
            continue
        if href.startswith("http"):
            full = href
        elif href.startswith("/"):
            full = "https://www.ibm.com" + href
        else:
            continue
        if full not in seen:
            seen.add(full)
            links.append((text, full))

    # Fallback: all topic= links on the page
    if len(links) < 5:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if not text or "topic=" not in href:
                continue
            if href.startswith("/"):
                full = "https://www.ibm.com" + href
            elif href.startswith("http"):
                full = href
            else:
                continue
            if full not in seen:
                seen.add(full)
                links.append((text, full))

    return links


# ---------------------------------------------------------------------------
# Command detail page parser
# ---------------------------------------------------------------------------

def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_command_page(soup: BeautifulSoup, url: str, category: str) -> CommandEntry:
    # Command name -- first h1 or h2
    name = ""
    for tag in soup.select("h1, h2"):
        t = clean(tag.get_text())
        if t:
            name = t
            break

    article = soup.select_one(
        "article, main, .ibm-document-content, #mc-main-content"
    )

    # Description -- first substantive <p>
    description = ""
    if article:
        for p in article.select("p"):
            t = clean(p.get_text())
            if t and len(t) > 20:
                description = t
                break

    # Syntax -- <pre> or <code> blocks
    syntax = ""
    scope = article if article else soup
    for block in scope.select("pre code, pre, code.language-wal, code"):
        t = clean(block.get_text())
        if t and len(t) > 5:
            syntax = t
            break

    # Parameters -- <table> elements
    parameters = []
    output_vars = []
    tables = scope.select("table")
    for table in tables:
        headers = [clean(th.get_text()).lower() for th in table.select("th")]
        if not headers:
            continue
        name_col = next((i for i, h in enumerate(headers) if "name" in h or "param" in h), None)
        type_col = next((i for i, h in enumerate(headers) if "type" in h), None)
        req_col  = next((i for i, h in enumerate(headers) if "required" in h or "optional" in h), None)
        desc_col = next((i for i, h in enumerate(headers) if "description" in h or "desc" in h), None)
        out_col  = next((i for i, h in enumerate(headers) if "output" in h or "return" in h), None)

        for row in table.select("tr"):
            cells = row.select("td")
            if not cells:
                continue

            def cell(i):
                return clean(cells[i].get_text()) if i is not None and i < len(cells) else ""

            p_name    = cell(name_col) if name_col is not None else cell(0)
            p_type    = cell(type_col) if type_col is not None else ""
            p_req_raw = cell(req_col)  if req_col  is not None else ""
            p_req     = p_req_raw.lower() not in ("optional", "no", "false", "")
            p_desc    = cell(desc_col) if desc_col is not None else cell(len(cells) - 1)

            if p_name:
                if out_col is not None and cell(out_col):
                    output_vars.append(f"{p_name}=value")
                else:
                    parameters.append(Parameter(
                        name=p_name, type=p_type, required=p_req, description=p_desc
                    ))

    # Notes
    notes_parts = []
    for note in scope.select(".note, .tip, .important, aside"):
        t = clean(note.get_text())
        if t:
            notes_parts.append(t)

    return CommandEntry(
        name=name or url.split("topic=")[-1].replace("-", " ").title(),
        category=category,
        url=url,
        description=description,
        syntax=syntax,
        parameters=parameters,
        output_vars=output_vars,
        notes=" | ".join(notes_parts),
    )


# ---------------------------------------------------------------------------
# Markdown formatter
# ---------------------------------------------------------------------------

def entry_to_markdown(e: CommandEntry) -> str:
    lines = [f"## {e.name}", ""]
    if e.category:
        lines += [f"**Category:** {e.category}", ""]
    if e.description:
        lines += [e.description, ""]
    if e.syntax:
        lines += ["**Syntax:**", "```wal", e.syntax, "```", ""]
    if e.parameters:
        lines += ["**Parameters:**", "",
                  "| Name | Type | Required | Description |", "|---|---|---|---|"]
        for p in e.parameters:
            lines.append(f"| `{p.name}` | {p.type} | {'Yes' if p.required else 'No'} | {p.description} |")
        lines.append("")
    if e.output_vars:
        lines += ["**Output variables:**", ""]
        for ov in e.output_vars:
            lines.append(f"- `{ov}`")
        lines.append("")
    if e.notes:
        lines += [f"> {e.notes}", ""]
    lines += [f"**Source:** [{e.url}]({e.url})", "", "---", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Shared output writer
# ---------------------------------------------------------------------------

def write_outputs(entries, out_path: Path, version: str, source: str):
    md_file   = out_path / "commands_crawled.md"
    json_file = out_path / "commands_crawled.json"

    md_lines = [
        f"# IBM RPA {version} -- Commands Reference (auto-crawled)",
        f"> Source: {source}",
        f"> Crawled: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"> Total commands: {len(entries)}",
        "", "---", "",
    ]
    for e in entries:
        md_lines.append(entry_to_markdown(e))
    md_file.write_text("\n".join(md_lines), encoding="utf-8")

    json_data = {
        "version": version,
        "source": source,
        "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "count": len(entries),
        "commands": [asdict(e) for e in entries],
    }
    json_file.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nWritten {len(entries)} commands:")
    print(f"  Markdown : {md_file.resolve()}")
    print(f"  JSON     : {json_file.resolve()}")


# ---------------------------------------------------------------------------
# Offline mode
# ---------------------------------------------------------------------------

def crawl_local(html_dir: str, out_dir: str, version: str) -> int:
    html_path = Path(html_dir)
    out_path  = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    html_files = sorted(html_path.glob("*.html")) + sorted(html_path.glob("*.htm"))
    print(f"[LOCAL] {len(html_files)} HTML files in {html_path.resolve()}")
    entries = []
    for idx, fpath in enumerate(html_files, 1):
        print(f"[{idx:03d}/{len(html_files):03d}] {fpath.name}")
        soup  = BeautifulSoup(fpath.read_text(encoding="utf-8", errors="replace"), "lxml")
        entry = parse_command_page(soup, f"file://{fpath.resolve()}",
                                   fpath.stem.replace("-", " ").title())
        entries.append(entry)
    if entries:
        write_outputs(entries, out_path, version, source=str(html_path.resolve()))
    return len(entries)


# ---------------------------------------------------------------------------
# Main crawler
# ---------------------------------------------------------------------------

def crawl(version: str, out_dir: str, max_pages: int, delay: float,
          headless: bool, seed_file, local_html) -> int:

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Mode 3: offline local HTML
    if local_html:
        count = crawl_local(local_html, out_dir, version)
        return 0 if count > 0 else 2

    # Mode 2: seed file of URLs
    if seed_file:
        seed_path = Path(seed_file)
        if not seed_path.exists():
            print(f"[ERROR] Seed file not found: {seed_path.resolve()}", file=sys.stderr)
            return 1
        raw_links = [
            (ln.strip(), ln.strip())
            for ln in seed_path.read_text().splitlines()
            if ln.strip() and not ln.startswith("#")
        ]
        print(f"[SEED] {len(raw_links)} URLs from {seed_path}")
    else:
        raw_links = None  # discover from index page

    index_url = f"https://www.ibm.com/docs/en/rpa/{version}?topic=commands"
    print(f"IBM RPA docs crawler  --  version {version}")
    print(f"  Index : {index_url}")
    print(f"  Output: {out_path.resolve()}")
    print(f"  Delay : {delay}s  |  Headless: {headless}")
    print()

    driver  = make_driver(headless)
    entries = []

    try:
        # Mode 1: discover links from index page
        if raw_links is None:
            print(f"[INDEX] Loading {index_url} ...")
            soup = get_soup(driver, index_url, delay)

            if is_blocked_page(soup):
                debug_file = out_path / "index_debug.html"
                debug_file.write_text(driver.page_source, encoding="utf-8")
                print(
                    "\n[BLOCKED] IBM docs returned a 403 / error page.\n"
                    "  The server is geo-blocking or bot-protecting this IP.\n"
                    "  Raw HTML saved to: " + str(debug_file) + "\n\n"
                    "  Workarounds:\n"
                    "  1. Run from a different machine/network.\n"
                    "  2. Save command pages manually as HTML, then:\n"
                    "       py tools/ibm_rpa_docs_crawler.py --local-html <folder>\n"
                    "  3. Put command URLs in a text file (one per line), then:\n"
                    "       py tools/ibm_rpa_docs_crawler.py --seed-file <file.txt>\n"
                    "     Example URL:\n"
                    "       https://www.ibm.com/docs/en/rpa/30.0?topic=commands-log-message",
                    file=sys.stderr,
                )
                return 1

            raw_links = collect_command_links(soup, index_url)
            print(f"[INDEX] Found {len(raw_links)} command links")

            if not raw_links:
                print("[WARN] No links found -- page may not have rendered.")
                print("       Try --headless false to inspect the browser.")
                debug_file = out_path / "index_debug.html"
                debug_file.write_text(driver.page_source, encoding="utf-8")
                print(f"       Raw HTML: {debug_file}")
                return 2

        # Crawl each command page
        limit = max_pages if max_pages > 0 else len(raw_links)
        for idx, (link_text, link_url) in enumerate(raw_links[:limit], 1):
            label = (link_text or link_url.split("topic=")[-1])[:55]
            print(f"[{idx:03d}/{min(limit, len(raw_links)):03d}] {label:55s} ...", end="", flush=True)
            try:
                page_soup = get_soup(driver, link_url, delay)
                if is_blocked_page(page_soup):
                    print(" BLOCKED -- skipped")
                    continue
                category = link_text or link_url.split("topic=")[-1]
                entry    = parse_command_page(page_soup, link_url, category)
                entries.append(entry)
                print(f" ok  ({entry.name[:40]})")
            except Exception as exc:
                print(f" ERROR: {exc}")

        if not entries:
            print("\n[ERROR] No commands parsed.", file=sys.stderr)
            return 2

        write_outputs(entries, out_path, version, source=index_url)
        print(f"\nDone. {len(entries)} commands crawled.")
        return 0

    finally:
        driver.quit()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Crawl IBM RPA docs command reference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version",    default="30.0",
                        help="IBM RPA docs version (default: 30.0)")
    parser.add_argument("--out-dir",    default="knowledge_base",
                        help="Output directory (default: knowledge_base)")
    parser.add_argument("--max-pages",  type=int, default=0,
                        help="Max pages to crawl, 0=all (default: 0)")
    parser.add_argument("--delay",      type=float, default=1.5,
                        help="Seconds between page loads (default: 1.5)")
    parser.add_argument("--headless",   default="true",
                        help="Chrome headless: true/false (default: true)")
    parser.add_argument("--seed-file",  default=None,
                        help="Text file with one command URL per line")
    parser.add_argument("--local-html", default=None,
                        help="Directory of pre-downloaded .html files")
    args = parser.parse_args()

    headless = args.headless.lower() not in ("false", "0", "no")
    rc = crawl(
        version=args.version,
        out_dir=args.out_dir,
        max_pages=args.max_pages,
        delay=args.delay,
        headless=headless,
        seed_file=args.seed_file,
        local_html=args.local_html,
    )
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
