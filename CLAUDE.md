# Smart Chessboard Agent Guidelines

Guidelines for anyone, human or AI, contributing code here. The project is a smart chessboard: 3D printed enclosure, custom PCB, and companion software.

## Guiding principle

Always build the simplest thing that solves the problem in front of you. Do not add abstraction, configuration, or extension points for needs that do not exist yet. After finishing a feature, stop and ask: is this the simplest, most elegant way to do this? If not, simplify before moving on.

## Project structure

```
docs/           scoped documentation, one topic per file
hardware/
  cad/          build123d scripts for the enclosure and internal parts
  pcb/          SKiDL scripts for the schematic and board
software/       companion app and/or firmware code
```

Do not add new top level folders without good reason.

## Code style

- Python is strongly typed. Full type hints on every function, method, and class attribute, including return types. Check with mypy or pyright.
- Small files, one responsibility each. Split a file once it starts doing more than one job.
- Comment on why, not what. Skip the comment if the code already reads clearly. Add one only where the reasoning would not otherwise be obvious.
- No em dash. Not in code, comments, docs, or commit messages. Use a period, comma, or parentheses instead.

Example:

```python
def square_index(file_letter: str, rank: int) -> int:
    # zero based so it lines up directly with the sensor array
    return (rank - 1) * 8 + (ord(file_letter) - ord("a"))
```

## Git

- Use short Conventional Commit messages, for example `fix: align JLCPCB exports`.

## Documentation

Docs live in `docs/`, split by topic, mirroring the hardware and software split. No single document tries to explain everything, each file stays scoped and concise.

`docs/functional/` is the product functional specification: what the board is and must do (gameplay, physical form and dimensions, displays, light bars, controls), independent of any sensing architecture or other implementation choice. It is the stable input hardware and software design serves, and it survives a change of implementation. Ground new hardware and software design in it, not in whatever a previous generation happened to build.

`docs/planning.md` is the milestone plan for hardware development (see Hardware below). Keep it current as boards move through the process; Claude follows it rather than inventing its own sequencing.

Example layout:

```
docs/
  functional/
    overview.md
    gameplay.md
    physical.md
    interface.md
  hardware/
    enclosure.md
    pcb.md
  software/
    architecture.md
  planning.md
  setup.md
```

Standard shape per file: short title, one paragraph on what it covers, then the specifics. Update the relevant doc when behavior changes instead of letting it drift out of sync.

## Hardware

- Minimize JLCPCB Extended-library selections because each unique Extended component currently
  adds a 2.70 EUR feeder-change labor fee. Use a safe Basic match whenever possible. Keep an
  Extended part only when no Basic part preserves the required function, package, and electrical
  limits.
- `hardware/cad`: build123d code generating the enclosure and internal parts. Parametric where it matters (fit, clearance, tolerance). Comment why a dimension is what it is, not what the line of code does.
- `hardware/pcb`: SKiDL code generating the schematic and netlist. Group parts by function (power, sensing, MCU) rather than one flat file.

### Development process

Hardware development proceeds board by board, grounded in `docs/functional/` rather than in whatever a previous generation happened to build, and tracked in `docs/planning.md` as a milestone list. Follow that plan; do not invent your own sequencing.

1. **Board definition.** Decide which physical boards exist and what each is responsible for, derived from `docs/functional/`.
2. **Schematic.** Design each board's electrical schematic in SKiDL (`hardware/pcb/`) to meet its slice of the functional spec. Keep bill-of-materials cost low: prefer fewer parts and simpler switching over a more elegant but pricier circuit.
3. **PCB layout, as code.** Lay out the board in SKiDL/KiCad-generation code, not by hand in a GUI, so the layout stays reproducible and versioned like the schematic. If a board's SPICE validation needs layout-derived values (real trace or antenna inductance, resistance, coupling, parasitics) rather than an analytical estimate, do this step before SPICE validation for that board; otherwise validate the schematic first.
4. **SPICE validation.** Validate the schematic automatically in ngspice (`hardware/sim/`, invoked from the test suite) against the numeric limits in `docs/hardware/criteria.yaml`. A board is not done while its only evidence is a formula; it needs a passing simulation.

A board is done only when its schematic, SPICE validation, and PCB layout all exist and pass. See `docs/planning.md` for the current milestone status.

## Software

Companion app and/or firmware. Same rules apply regardless of language: typed where the language supports it, small modules, minimal comments, no speculative abstraction.

## LLM Wiki

An [Obsidian](https://obsidian.md) vault in this repo runs the [llm-wiki pattern](https://gist.github.com/kennyg/6c45cace2e1c4e424a28fcd51dd6c25b) (after [Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)): incrementally build and maintain a persistent, interlinked wiki from raw sources instead of re-deriving knowledge on every query. This is where research feeding the chessboard lives (reference papers, datasheets, clipped articles, design notes). This section is the schema. It makes you a disciplined wiki maintainer, not a generic chatbot.

### Layers

1. Raw sources: immutable clippings and captures. You read them, you never modify them.
2. The wiki: LLM generated, interlinked markdown. Summaries, entity pages, concept pages, synthesis. You own it entirely.
3. The schema: this section. How the wiki is maintained.

### Layout

The active Obsidian vault is `Vault/Scacchiera/`. Everything below is relative to it.

```
Vault/Scacchiera/
  Clippings/         raw sources, immutable, drop zone for captures
  assets/            downloaded images so the vault stays self-contained
  Wiki/
    index.md         content catalog, read this first
    log.md           append-only operation log
    overview.md      high level synthesis of everything
    sources/         one summary per ingested source
    entities/        people, tools, orgs, repos
    concepts/        ideas, patterns, techniques
    synthesis/       query answers filed back into the wiki
```

### Page conventions

- Every page has `type:` in YAML frontmatter: `source-summary`, `entity`, `concept`, or `synthesis`.
- Tags use the `wiki/` prefix namespace (`wiki/source`, `wiki/entity`, `wiki/concept`, `wiki/synthesis`).
- `date_updated:` on every page.
- `source_count:` on entity and concept pages.
- `confidence:` on concept pages (high, medium, low) tracks how well supported a claim is.
- Heavy `[[wikilinks]]` everywhere so the Obsidian graph view stays useful.
- `[key::value]` inline metadata where a Dataview query would want it.

### Operations

Ingest, process a raw source into the wiki:

1. Read the raw source completely.
2. Create a source summary in `Wiki/sources/`.
3. Create or update entity pages in `Wiki/entities/`.
4. Create or update concept pages in `Wiki/concepts/`.
5. Update `Wiki/index.md` (add to the tables, remove from Unprocessed).
6. Update `Wiki/overview.md` if the big picture changed.
7. Append an entry to `Wiki/log.md`.

A single ingest typically touches 5 to 15 wiki pages. Seed with 2 or 3 rich sources first to calibrate the templates, then batch the rest.

Query, answer a question against the wiki:

1. Read `Wiki/index.md` to find relevant pages.
2. Read the relevant wiki pages, not the raw sources. The wiki should already have what you need.
3. Synthesize an answer with wikilinks.
4. If the answer is substantial, file it as a new page in `Wiki/synthesis/`.
5. Update index and log.

Filing query answers back is the point. Explorations compound in the knowledge base the same way ingested sources do.

Lint, health-check the wiki:

- Orphan pages (no inbound links).
- Broken wikilinks.
- Stale pages (`date_updated` older than the newest relevant source).
- Contradictions between pages.
- Concepts named in prose but lacking their own page.
- Missing cross-references.

### Rules

- Raw sources (`Clippings/`) are immutable. Never modify them, even when their metadata is wrong. Add clarity in the wiki layer instead.
- You own `Wiki/` entirely. Update `index.md` and `log.md` on every wiki change.
- Keep source summaries factual. Interpretation belongs in concept and synthesis pages.
- When a new source contradicts existing wiki content, note the contradiction explicitly. Do not silently overwrite.
- Do not hand-edit wiki pages as the human. The human reads the wiki, the LLM writes it.
- This schema co-evolves. Update this section as the domain teaches you what works.

### Environment setup

Image capture is already configured: `Vault/Scacchiera/.obsidian/app.json` sets the attachment folder to `assets/`, and `hotkeys.json` binds Ctrl+Shift+D to `editor:download-attachments`. After clipping an article, open it and hit Ctrl+Shift+D to localize its images. Find clippings that still point at remote images with:

```bash
grep -rl '!\[.*\](http' Vault/Scacchiera/Clippings/
```

Two optional tools are left for the human to install (this machine is Fedora Linux, not macOS, so the gist's `/Applications` and Homebrew paths do not apply):

- Obsidian CLI (Obsidian 1.12+): register it under Settings > General > Command line interface, then symlink the binary from the Obsidian install into `~/.local/bin/obsidian`. Prefer it over hand-editing markdown for task management so Obsidian stays in sync.
- [qmd](https://github.com/tobi/qmd) for hybrid BM25 and vector search once the wiki outgrows `index.md` (roughly 25+ sources): `go install github.com/tobi/qmd@latest`, then `qmd collection add`, `qmd update`, `qmd embed`. It also exposes an MCP server (`qmd mcp`) so search becomes a native agent tool.

At small scale `index.md` alone is enough. Do not reach for qmd early.
