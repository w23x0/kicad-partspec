---
name: partspec
description: Turn a component datasheet PDF into a verified KiCad symbol and footprint. Use when the user wants a KiCad library part (symbol, footprint, pinout) made from a datasheet, or wants an existing KiCad part checked against its datasheet.
---

# PartSpec: datasheet to verified KiCad part

You read the datasheet and fill a **PartSpec** (a JSON file). Deterministic code turns it into KiCad files and verifies them.
Your job is only to extract facts accurately. Every value carries the datasheet page and a **verbatim quote**, so a human can
audit each one. Never fill a value from memory or from other parts of the same family: if the datasheet in front of you does
not state it, leave it out and say so.

Tools: the `partspec_validate`, `partspec_build` and `partspec_verify` MCP tools, or the CLI (`partspec validate|build|verify`).
The field layout, dimension names and pin-type rules are in [reference.md](reference.md); an invented example is in
[example.json](example.json).

## Workflow

1. **Find the pages.** Page numbers are PDF page indexes, starting at 1 (not the numbers printed on the page).
   `pdftotext -layout FILE.pdf - | grep -n` to search; `pdftotext -layout -f N -l N FILE.pdf -` to read one page.
   You need: the pin table or pinout, the package outline drawing (with its dimension table), and the example land pattern
   ("board layout" / "recommended footprint"). The drawings are usually near the end, far from the pin table: search for the
   package's drawing code (for example a name like `D0008A` or `RGT0016C`) or for "PACKAGE OUTLINE". If the PDF covers several
   packages, use only the one you were asked for.
2. **Look at the drawings.** Text extraction keeps numbers but loses which dimension they belong to, and pinout figures put
   pin numbers and names in different places. Render the page (`pdftoppm -f N -l N -r 110 -png FILE.pdf /tmp/page`) and view the
   image before you trust a number or a pin-to-number pairing.
3. **Get the hash.** `sha256sum FILE.pdf` goes in `datasheet.sha256`.
4. **Write the PartSpec** as JSON, following [reference.md](reference.md).
5. **Validate against the PDF** until it passes: `partspec_validate` with `datasheet_path` (CLI: `partspec validate SPEC.json --datasheet FILE.pdf`).
   Every entry in `failed` says what to change. A `prov.quote_not_found` means your quote is not on that page as printed.
6. **Build**: `partspec_build` (CLI: `partspec build SPEC.json --out DIR`; add `--concise` to see failures in full and warnings
   only counted by kind, which keeps the one important warning from being buried). Fix any failure and rebuild. A `footprint.skipped`
   warning means the datasheet's land pattern is missing or incomplete; report it, do not invent the numbers.
7. **Hand over for review.** Tell the user which pins and dimensions are `inferred`, anything you left out and why, and any place
   where two parts of the datasheet disagree. Do not mark anything `confirmed`; only a human does that.

## Quotes

- Build every quote from `pdftotext -layout` output. Plain `pdftotext` orders the text differently and its quotes will not match.
- Copy text exactly as printed on the cited page. Whitespace and line breaks do not matter; characters do (keep en dashes such as `IN1–`).
- Quote enough to contain the value and its label, no more: a table row (`5 FB I`), or the tokens beside a dimension.
- The quote must be on the page you cite. A pinout page can repeat the same labels for two packages (say a TQFP view and a
  QFN view); use the labels of the package you were asked for.
- Numbers in a figure are interleaved with other labels in the text layer. Two numbers that belong together may be printed as
  `1.0 C 0.8`, not `1.0 0.8`, and a value and its bracketed millimetres are often on different lines. Two ways out: quote one
  token (`.189-.197`, even if the value you record is the millimetre one), or use the hint `partspec validate --datasheet`
  gives on a failed quote, which is the page's own token order.
- In a pinout figure the number and the name may sit apart (rotated labels), so a quote can only carry the name. Check the
  pairing on the rendered image; that is the reason step 2 exists.

## Rules that prevent the usual mistakes

- One pin entry per **physical pin**. A row such as `1,2,3  SW` is three pins with the same name.
- A **no-connect** pin still gets an entry (type `no_connect`).
- An exposed/thermal pad gets `exposed_pad: true` and one pin entry numbered `pin_count + 1`, marked `inferred` if the datasheet gives it no number.
- Dimensions are millimetres. If the drawing prints inches with millimetres in brackets, use the bracketed millimetres.
- Leave a dimension out when the drawing does not make clear what it is. A wrong number is worse than a missing one.
- `land_*` dimensions come only from the datasheet's example land pattern, never from the package outline.
- `inferred` is honest, not a failure: use it whenever you derived a value instead of reading it.
