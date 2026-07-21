"""Generate PDFs designed to trigger LOW confidence in the pipeline."""

from fpdf import FPDF
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_pdf(filename, content_fn):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    content_fn(pdf)
    path = os.path.join(OUTPUT_DIR, filename)
    pdf.output(path)
    print(f"Created: {path}")


# ─────────────────────────────────────────────
# 9. FRAGMENT - Truncated, messy, ambiguous
# ─────────────────────────────────────────────
def fragment_content(pdf: FPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "", 9)
    # No title, no structure, just random fragments
    lines = [
        "...continued from previous section",
        "",
        "the amount shall not exceed the previously agreed upon terms as",
        "referenced in document B-4412 (see appendix). However given the",
        "circumstances described by the attending party, modifications to",
        "",
        "XXXXX REDACTED XXXXX",
        "",
        "pg 47 of 112",
        "",
        "Table 3.2 - [DATA CORRUPTED]",
        "  Row 1:  N/A    |  --   |  ????  |  0.00",
        "  Row 2:  TBD    |  --   |  ????  |  0.00",
        "  Row 3:  see note 14    |  --   |",
        "",
        "Furthermore, the implications of section 12(b) remain unclear",
        "pending review by [NAME WITHHELD] and associates. The deadline",
        "was originally set for Q3 but has been postponed indefinitely.",
        "",
        "--- PAGE BREAK - SCAN ERROR ---",
        "",
        "asdfkjh scanning artifact qwerty",
        "||||||||||||| barcode region |||||||||||||",
        "",
        "Note: This page was partially scanned. Original document",
        "may contain additional information not captured here.",
        "",
        "Ref: unknown",
        "Date: unclear (possibly 2023 or 2024)",
        "Category: unclassified",
        "",
        "...text continues on missing page...",
    ]
    for line in lines:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")

    pdf.add_page()
    pdf.set_font("Helvetica", "", 8)
    more_lines = [
        "[Page 48 - partially illegible]",
        "",
        "The f0ll0wing s3ction c0ntains OCR err0rs fr0m p00r sc4nning",
        "qu4lity. Pl3ase r3fer to th3 0riginal d0cument f0r acc4rate",
        "inf0rmation. M4ny ch4racters h4ve b3en misint3rpreted.",
        "",
        "Signatures:",
        "  [illegible] ________________",
        "  [illegible] ________________",
        "",
        "Witness: [not present]",
        "Notary: [stamp unclear]",
        "",
        "END OF FRAGMENT",
        "This document is INCOMPLETE and should NOT be used",
        "for any legal or business purpose without verification",
        "of the complete original.",
    ]
    for line in more_lines:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")


# ─────────────────────────────────────────────
# 10. MIXED - Multiple languages, no clear type
# ─────────────────────────────────────────────
def mixed_content(pdf: FPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)

    lines = [
        "INTERNAL MEMO / NOTA INTERNA",
        "",
        "From: Operations Dept",
        "Para: Todos os departamentos",
        "Re: Various pending items / Assuntos pendentes",
        "Date: sometime in February",
        "",
        "1. Budget review meeting was cancelled. Reuniao cancelada.",
        "   New date TBD. Nova data a confirmar.",
        "",
        "2. The quarterly numbers look like this (approximate):",
        "   Q1: maybe $2M? (unconfirmed)",
        "   Q2: around $1.8M (estimate only)",
        "   Q3: unknown",
        "   Q4: projected somewhere between $1.5M-$3M",
        "",
        "3. HR update: Several positions are open but we're not sure",
        "   which ones exactly. Check the intranet (link broken).",
        "",
        "4. IT note: Server migration happening soon. O sistema vai",
        "   ficar fora do ar por tempo indeterminado.",
        "",
        "5. Random notes from last meeting:",
        "   - someone mentioned something about compliance",
        "   - action items were assigned but not recorded",
        "   - follow up needed (with whom? unclear)",
        "   - parking lot issues again",
        "",
        "6. Lunch menu for next week:",
        "   Monday: pasta",
        "   Tuesday: TBD",
        "   Wednesday-Friday: see cafeteria",
        "",
        "7. URGENT (maybe): Client XYZ called about something.",
        "   Please call back. Number: [check voicemail]",
        "",
        "This memo is informal and may contain inaccuracies.",
        "Do not distribute externally.",
        "",
        "Regards / Abracos,",
        "The Ops Team / Equipe de Operacoes",
    ]
    for line in lines:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")


if __name__ == "__main__":
    samples = [
        ("09_fragment_corrupted_scan.pdf", fragment_content),
        ("10_mixed_informal_memo.pdf", mixed_content),
    ]

    print("Generating LOW confidence sample PDFs...\n")
    for filename, fn in samples:
        create_pdf(filename, fn)

    print("\nExpected results:")
    print("  09 - Fragment:  LOW confidence (incomplete, corrupted, no structure, ambiguous type)")
    print("  10 - Mixed:     LOW/MEDIUM confidence (bilingual, vague data, informal, unclear category)")
