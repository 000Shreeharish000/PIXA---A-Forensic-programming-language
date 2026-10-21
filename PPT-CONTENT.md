# PIXA — Presentation Content (editable)

Full text for the 7-slide deck (`deck/PIXA-Presentation.pptx`), with a speaker script for each slide, a live-demo walkthrough, and likely Q&A. Edit anything. Facts marked **[verify]** should be rechecked before presenting.

**Total talk time:** about 10–12 minutes (about 1.5 minutes per slide, plus the demo).

---

## Slide 1 — Title

**On the slide**
- **PIXA**
- A new programming language for digital forensics
- You write the investigation as a short script. PIXA runs it over your evidence, and every finding points back to the records behind it.
- Footer: Python standard library only · 50 passing tests · 4 sample investigations

**Team / course line (add your own):** Team name · Names · Course · Date

**Speaker script**
> "Good morning everyone. We built a new programming language called PIXA. It's designed for one job: investigating a hacked computer. Instead of clicking through tools or writing throwaway scripts, the analyst writes the investigation as a short program. PIXA runs it and produces findings that always show the evidence behind them."

---

## Slide 2 — Problem statement and existing system

**On the slide**

*Problem statement*
> Analysts lose evidence because of the tools they use, and cannot prove how they reached a conclusion.

- Unsigned collectors get quarantined by antivirus the moment they run
- Findings come from one-off scripts nobody can re-run or defend
- Hosts, network and threat intel sit in separate tools

*Existing approaches*
| Approach | Weakness |
|---|---|
| Evasive collectors | Hide from antivirus. Cannot be safely deployed, and the output is hard to defend in a report. |
| Ad hoc scripts | Python or PowerShell written per case. Fast, but undocumented and not repeatable. |
| Detection rules (e.g. Sigma) | Portable logic, but a rule detects. It does not cite the records it matched. |

**Speaker script**
> "When a computer is hacked, investigators need to collect evidence fast. The first problem is that the tools they use often look like malware, so antivirus quarantines them and the evidence is lost. The second problem is that the analysis is usually a pile of one-off scripts. If a lawyer or manager asks 'how did you reach this conclusion?', nobody can re-run it or show the steps. Existing options each solve only part of this. Evasive tools fight the antivirus. Custom scripts aren't repeatable. Detection rules say 'something matched' but don't show the exact records."

**Plain-English glossary (add as a notes slide if useful)**
- **DFIR:** Digital Forensics and Incident Response. Investigating a cyber attack.
- **Evidence:** logs, process lists and network records from the computer.
- **Antivirus / EDR:** the security software on the computer that watches for threats.
- **Sigma:** a popular format for sharing detection rules between security tools.

---

## Slide 3 — Proposed system and objectives

**On the slide**

*Proposed system*
PIXA is a small language where the steps of an investigation are the code. Run the same script on the same evidence and you get the same findings.

Flow: **Script → Evidence → Cited findings**

It works with the security stack, not against it: documented OS sources, read-only access, no evasion.

*Objectives*
1. **A readable language.** Analysts describe an investigation in plain pipelines, not glue code.
2. **Findings with proof.** Every finding names the result set and records it came from.
3. **Safe to deploy.** Read-only, loopback-only, no tricks to dodge antivirus.
4. **Same result everywhere.** Windows and Ubuntu, one interpreter, SHA-256 of every file read.

**Speaker script**
> "Our idea is to make the investigation itself a program. You write what you are looking for, PIXA reads the evidence, and gives back findings. Because it's a program, running it again gives the same answer, so the work is repeatable and defensible. We had four objectives: a language analysts can read, findings that carry proof, a tool that is safe to run on real machines, and the same behaviour on Windows and Linux."

---

## Slide 4 — The language (syntax)

**On the slide** (code block)

```
# find encoded PowerShell
case "PIXA-CASE-014"

source events = ingest "evidence/events.json"

let encoded = events
  |> where (command_line contains "-enc")
  |> where (entropy(command_line) > 4.0)
  |> select (timestamp, host, image)

finding "Encoded PowerShell"
  severity high from encoded
```

Side notes:
- **source / let:** Name your evidence, then derive result sets from it.
- **|> pipeline:** Stages: where, select, sort, group, distinct, limit, count.
- **entropy():** Built-in that scores how random a string looks. Flags base64 blobs.
- **finding … from:** Must cite a result set. A finding with no source does not parse.

**Speaker script**
> "This is what PIXA code looks like. `source` loads evidence. `let` creates a result from it. The `|>` symbol is a pipe, like in a shell: data flows from one step to the next, each step filtering or reshaping it. Here we keep command lines that contain `-enc`, then keep only the ones that look random, because hidden PowerShell commands are usually encoded. Finally `finding` raises an alert, and it must say which result it came from. If you try to write a finding without a source, the language refuses to run it."

**Reference tables (for the notes or an appendix slide)**

| Statement | Meaning |
|---|---|
| `case "ID"` | Name the investigation |
| `source N = ingest "path"` | Load evidence (.json, .csv, or one record per line) |
| `let N = expr` | Derive a result set |
| `match src.field against "intel.txt" as N` | Compare a field against a known-bad list |
| `timeline src on field as "label"` | Build the case timeline |
| `finding "text" severity S from N` | Raise a finding (low, medium, high, critical) |
| `emit N as "Label"` | Include a result in the report |

| Pipeline stage | Meaning |
|---|---|
| `where (cond)` | Filter records |
| `select (a, b)` | Keep only some fields |
| `sort by (f asc/desc)` | Order records |
| `group by (a, b)` | Bucket and count |
| `distinct (f)` | Unique values with counts |
| `limit (n)`, `count` | Truncate, count |

Operators: `==  !=  <  <=  >  >=`, `contains  startswith  endswith`, `~` / `matches` (regex), `in [...]`, `and  or  not`.
Built-ins: `sha256`, `md5`, `entropy`, `is_public_ip`, `is_private_ip`, `lower`, `upper`, `len`, `int`, `abs`, `round`, `now`, `epoch`, `age_minutes`.

---

## Slide 5 — Architecture

**On the slide**
Diagram (left to right):
- **Inputs:** Script (`.pxa` file) and Evidence (JSON, CSV, line files, threat-intel lists, read-only)
- **Language core (`pixa/`):** Lexer (source text → tokens) → Parser (tokens → AST) → Runtime (runs the AST, tracks sources) with Builtins (entropy, hashing, IP checks)
- **Interfaces:** CLI (run · compile · lint · env · serve), Console API (127.0.0.1 only, JSON over HTTP), Browser console (editor, findings, timeline, evidence hashes, token/AST view)

Caption: The CLI and the console both call the same compile and run functions, so a script behaves identically in either.

**Speaker script**
> "Here is how it works inside. A script and the evidence go in on the left. The lexer cuts the script into tokens, like splitting a sentence into words. The parser arranges the tokens into a tree called an AST, which captures the structure of the program. The runtime walks that tree and executes it against the evidence, using built-in helpers such as entropy and hashing. On the right, you can use PIXA from the command line or from a browser console. Both use exactly the same engine, so results are the same either way."

**Terms**
- **Lexer:** turns source text into tokens (words, symbols, strings).
- **Parser:** turns tokens into a tree that shows the program's structure.
- **AST:** Abstract Syntax Tree. The tree the parser produces.
- **Runtime / interpreter:** the part that actually executes the tree.

**File map**
| File | Role |
|---|---|
| `pixa/lexer.py` | Tokenizer: positions, escapes, comments, regex literals |
| `pixa/parser.py` | Recursive-descent parser producing a nested-dict AST |
| `pixa/runtime.py` | Interpreter, pipeline stages, source tracking, reports |
| `pixa/builtins.py` | Builtin functions (hashing, entropy, IP classification, time) |
| `pixa/cli.py` | run / compile / lint / env / serve commands |
| `pixa/serve.py` | Local web server for the console (loopback only) |
| `console/index.html` | The browser console, one file |

---

## Slide 6 — How it was built (phases, tools, techniques)

**On the slide**

*Phases*
1. **Design.** Grammar, forensic constraints, what the tool must never do
2. **Front end.** Hand-written lexer and recursive-descent parser
3. **Runtime.** Pipelines, intel matching, findings that cite sources
4. **Interfaces.** CLI, loopback API, single-file browser console
5. **Prove it.** Sample incident, 4 scripts, 50 unit tests

*Tools*
- Python 3.8+, standard library only, nothing to install
- `http.server` for the console API, plain HTML and JS for the UI
- `unittest` for the 50 tests; PowerShell and bash launchers

*Techniques*
- Recursive-descent parsing into a plain-dict AST
- Shannon entropy to spot encoded command lines
- SHA-256 of every evidence file for chain of custody
- Type-aware comparison: CSV strings still compare as numbers

**Speaker script**
> "We built it in five phases. First we decided what the language should do and what it must never do, such as touching the kernel or hiding from antivirus. Then we wrote the front end, the lexer and parser, by hand. Then the runtime that executes the pipelines. Then the command line and the browser console. Finally we proved it works with a sample attack on one workstation, four example scripts and fifty automated tests. We used only the Python standard library, so there is nothing to install."

**Why Python? (likely question)**
- Fast to build: about 2,200 lines of Python **[verify]** cover the whole language and server.
- Runs on Windows and Linux unchanged.
- The standard library already has hashing, regex, JSON, CSV and an HTTP server.
- Most new languages start on top of an existing one. A faster rewrite (Rust or Go) is a natural next step.

**Honest limits (say these before someone asks)**
- Fleet view uses a sample inventory. Real endpoint collectors are future work.
- Report export (signed PDF/JSON) is not written yet.
- Evidence is loaded per run. A big case would need an indexed store.
- Timeline works on a single host today.

---

## Slide 7 — How to run and test

**On the slide**
Needs Python 3.8 or newer. Run from the project folder.

**Windows**
```
.\run.ps1          # console
.\run.ps1 -Demo    # all scripts
.\run.ps1 -Test    # test suite
```
**Ubuntu / macOS**
```
chmod +x run.sh
./run.sh            # console
./run.sh --demo | --test
```
**Directly**
```
python -m pixa run scripts/beacon_hunt.pxa
python -m pixa compile scripts/triage.pxa --tokens
python -m pixa lint scripts/insider_usb.pxa
python -m pixa serve --port 8787
```
**Test it**
```
python -m unittest discover -s tests -t .
```
Expect: 50 tests, OK. Expect: `beacon_hunt` gives 6 findings.

**Speaker script**
> "Running it takes one command. On Windows, run `run.ps1` and open the browser at 127.0.0.1 port 8787. You can also run any script directly with `python -m pixa run`. To check everything works, run the tests. You should see fifty tests pass."

**Troubleshooting**
- PowerShell must be inside the folder first: `cd D:\projects\jocky-forensic-dsl-main`.
- If scripts are blocked: `Set-ExecutionPolicy -Scope Process Bypass`.
- If port 8787 is busy: `.\run.ps1 -Port 8788`.

---

## Live demo walkthrough (about 3–4 minutes)

Start the console (`.\run.ps1`) and open http://127.0.0.1:8787 before the talk. Hard-refresh with Ctrl+F5.

### Part A — Triage script (`triage.pxa`)

**Setup:** pick `triage.pxa` in the Script dropdown, then press **Run investigation** (or Ctrl+Enter).

**What the story is:** "This is the first script you run on a new case. It answers three questions: who was active, what was running, and what did not belong."

**Walk through the code**
| Code | What it does | Result you will see |
|---|---|---|
| `source procs = ingest "evidence/processes.json"` | Loads the list of processes | 19 records |
| `source events = ingest "evidence/events.json"` | Loads the log events | 45 records |
| `let hosts = procs \|> distinct (host)` | Which computers are in the data? | 1 host: FIN-WS-014 |
| `let accounts = procs \|> distinct (user)` | Which user accounts were active? | 4 accounts (CORP\a.mehta ran 12 processes) |
| `let unsigned = procs \|> where (signed == false)` | Programs with no digital signature | 2 records: `svchost_update.exe` in the Temp folder |
| `let admin_tools = events \|> where (image matches "...")` | Commands attackers use to look around and cover tracks | 5 records |
| `let integrity_mix = procs \|> group by (integrity)` | How much power the processes had | medium 13, system 5, high 1 |
| `let per_user = procs \|> group by (user)` | Processes per account | a.mehta 12, SYSTEM 5, others 1 each |
| `timeline events on timestamp` | Puts events in time order | 45 events |
| `finding "..." severity high from unsigned` | Raises an alert, citing its source | HIGH: 2 records via `unsigned` |
| `finding "..." severity high from admin_tools` | Second alert | HIGH: 5 records via `admin_tools` |
| `emit ...` | Puts the tables in the report | Tables on the right |

**What to point out in the results**
- **Findings box:** "2 findings raised, 64 records analysed."
- **The suspicious program:** `svchost_update.exe` has a name that imitates a real Windows file (`svchost.exe`), sits in a user's Temp folder, and has no signature. That is a classic sign of malware.
- **Discovery and tampering table:** the same program launched `schtasks` (to keep itself running), `whoami /all` and `net group "Domain Admins"` (to see who is powerful), and `wevtutil cl Security` and `cl System` (to **clear the logs**). Say: "That last one is the attacker covering their tracks."
- **Every finding shows its proof:** "5 records via admin_tools." Click or scroll to that table to show the exact records.

### Part B — Beacon hunt (`beacon_hunt.pxa`)

**Setup:** pick `beacon_hunt.pxa` and run it.

**What the story is:** "A Word document with a macro started PowerShell, dropped a file, called out to an attacker's server and cleared the logs."

**Point out:** 6 findings (3 critical, 3 high). The critical ones are: logs cleared, host contacted a known-bad IP, a known-malicious file hash was found. Each one cites its source.

### Part C — Show it is a real language (30 seconds each)

- **Compiler tab:** the actual tokens and AST. "Our own lexer and parser produced this. For triage it was 152 tokens and 48 nodes."
- **Timeline tab:** the 45 events in order, suspicious ones highlighted. "The incident as a story."
- **Evidence tab:** SHA-256 and size per file. "These are computed, not typed in. That is chain of custody."
- **Compatibility tab:** "What PIXA does and does not do. It never hides from antivirus and never changes the source system."

### Part D — Live edit (the strongest moment)

1. Go to the Investigate tab with `beacon_hunt.pxa`.
2. Change `bytes < 2000` to `bytes < 500`.
3. Press Ctrl+Enter.
4. Show that the results change. "It is running for real, not a recording."

### Part E — Show that errors are helpful

Delete the closing bracket of any `where (...)` and run. The console reports the line and column of the error. "A real compiler tells you exactly where you went wrong."

---

## Likely questions and answers

**Is this really a new programming language?**
Yes. It has its own syntax, lexer, parser and interpreter. It is a domain-specific language, built for one field, not a general-purpose language like Python.

**Why not just write Python scripts?**
Python can do anything, so every analyst writes it differently. PIXA limits you to forensic operations and forces every finding to name its source. That makes investigations readable, repeatable and checkable.

**How is it different from Sigma rules or SIEM queries?**
A rule says "this matched." A PIXA script is the whole investigation: load several sources, filter, match against threat intel, build a timeline, and raise findings that cite the exact records.

**Is it fast?**
It is an interpreter running on Python, so it is slower than hand-written Python. The overhead is measured in `deck/bench_baseline.json` **[verify the numbers before quoting them]**. For investigation-sized data it is fine. A faster runtime is future work.

**Is the data real?**
No. The sample attack on workstation FIN-WS-014 is synthetic, built so the whole analysis can be reproduced with no live malware. The threat-intel lists contain indicators that match the sample events.

**Does it change or damage the evidence?**
No. Evidence is opened read-only, and PIXA never writes to a source system. The console only listens on 127.0.0.1 (your own machine).

**What would you build next?**
Real endpoint collectors, signed report export (PDF/JSON), multi-host timelines, and an indexed store for large cases.

**What does `.pxa` mean?**
It is the file extension for PIXA scripts, like `.py` for Python.

---

## Notes for editors

- Keep one message per slide. If a slide gets crowded, move the extra detail into the speaker script.
- The deck file is generated by a script, so edits made directly in PowerPoint are safe, but regenerating will overwrite them.
- The screenshots in `deck/assets/` still show the old JOCKY name and the old case ID. Retake them from the running console before putting them in a slide.
- Case ID used everywhere: `PIXA-CASE-014`. Host in the sample data: `FIN-WS-014`.
