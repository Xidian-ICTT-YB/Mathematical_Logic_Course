#!/usr/bin/env python3
"""Render the project Markdown docs to Chinese PDFs with ReportLab.

This is deliberately a small, local renderer: headings, paragraphs, lists,
fenced code, pipe tables, blockquotes and local images.  It avoids a system
LaTeX/Pandoc dependency while keeping the source Markdown editable.
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Preformatted, Spacer, Table, TableStyle,
)
from reportlab.platypus.flowables import HRFlowable

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_PATH = pathlib.Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
ICON_PATH = pathlib.Path("/System/Library/Fonts/Arial Unicode.ttf")
MONO_PATH = pathlib.Path(__import__("matplotlib").__file__).parent / "mpl-data/fonts/ttf/DejaVuSansMono.ttf"
pdfmetrics.registerFont(TTFont("ArialUnicode", str(FONT_PATH)))
pdfmetrics.registerFont(TTFont("DejaVuSansMono", str(MONO_PATH)))

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm


def inline(text: str) -> str:
    text = html.escape(text)

    def inline_code(m):
        code = m.group(1)
        # Chinese paths and formula symbols do not exist in DejaVu Sans Mono.
        font = "ArialUnicode" if any(ord(ch) > 127 for ch in code) else "DejaVuSansMono"
        return f'<font name="{font}" size="8.5">{code}</font>'

    text = re.sub(r"`([^`]+)`", inline_code, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2">\1</link>', text)
    return text


def table_cell(text: str) -> str:
    # A table cell such as `stage1.log`、`warnings.json` is one unbroken
    # ReportLab "word"; the renderer then splits it at an arbitrary character.
    # Give the list separators a break opportunity so identifiers stay whole.
    return inline(text).replace("、", "、 ").replace("；", "； ")


def code_lines(lines: list[str], width: int = 105) -> list[str]:
    out = []
    for line in lines:
        line = line.expandtabs(4)
        if len(line) <= width:
            out.append(line)
        else:
            # Preserve indentation on continuation lines.
            indent = len(line) - len(line.lstrip(" "))
            chunks = textwrap.wrap(line, width=width, subsequent_indent=" " * min(indent, 16),
                                   break_long_words=True, break_on_hyphens=False)
            out.extend(chunks or [""])
    return out


class MarkdownDoc(BaseDocTemplate):
    def __init__(self, filename: str, title: str):
        self.title_for_page = title
        super().__init__(
            filename, pagesize=A4,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=2.0 * cm, bottomMargin=1.8 * cm,
            title=title, author="UBITect reproduction project",
        )
        frame = Frame(MARGIN, 1.6 * cm, PAGE_W - 2 * MARGIN,
                      PAGE_H - 3.6 * cm, id="body")
        self.addPageTemplates([
            PageTemplate(id="main", frames=[frame], onPage=self.decorate),
        ])

    def decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("ArialUnicode", 7.5)
        canvas.setFillColor(colors.HexColor("#52514e"))
        canvas.drawString(MARGIN, PAGE_H - 1.15 * cm, self.title_for_page)
        canvas.drawRightString(PAGE_W - MARGIN, 1.0 * cm, f"{doc.page}")
        canvas.setStrokeColor(colors.HexColor("#e1e0d9"))
        canvas.line(MARGIN, 1.35 * cm, PAGE_W - MARGIN, 1.35 * cm)
        canvas.restoreState()


def build_styles():
    base = getSampleStyleSheet()["Normal"]
    return {
        "normal": ParagraphStyle("NormalCN", parent=base, fontName="ArialUnicode",
                                 fontSize=10.5, leading=16, textColor=colors.HexColor("#0b0b0b"),
                                 spaceAfter=6),
        "h1": ParagraphStyle("H1CN", parent=base, fontName="ArialUnicode",
                             fontSize=21, leading=27, textColor=colors.HexColor("#0b0b0b"),
                             spaceBefore=8, spaceAfter=12),
        "h2": ParagraphStyle("H2CN", parent=base, fontName="ArialUnicode",
                             fontSize=15, leading=20, textColor=colors.HexColor("#0b0b0b"),
                             spaceBefore=14, spaceAfter=8),
        "h3": ParagraphStyle("H3CN", parent=base, fontName="ArialUnicode",
                             fontSize=12, leading=17, textColor=colors.HexColor("#0b0b0b"),
                             spaceBefore=10, spaceAfter=6),
        "bullet": ParagraphStyle("BulletCN", parent=base, fontName="ArialUnicode",
                                 bulletFontName="ArialUnicode",
                                 fontSize=10.2, leading=15.5, leftIndent=16,
                                 bulletIndent=4, spaceAfter=3),
        "num": ParagraphStyle("NumCN", parent=base, fontName="ArialUnicode",
                              fontSize=10.2, leading=15.5, leftIndent=18,
                              firstLineIndent=-14, spaceAfter=3),
        "quote": ParagraphStyle("QuoteCN", parent=base, fontName="ArialUnicode",
                                fontSize=9.8, leading=15, leftIndent=14,
                                rightIndent=10, textColor=colors.HexColor("#52514e"),
                                backColor=colors.HexColor("#f0efec"),
                                borderPadding=5, spaceBefore=5, spaceAfter=8),
        "code": ParagraphStyle("CodeCN", fontName="DejaVuSansMono", fontSize=7.3,
                               leading=9.7, textColor=colors.HexColor("#1a1a19"),
                               backColor=colors.HexColor("#f5f5f0"),
                               leftIndent=8, rightIndent=6, borderPadding=5,
                               spaceBefore=4, spaceAfter=9),
        "code_cjk": ParagraphStyle("CodeCJK", fontName="ArialUnicode", fontSize=8.0,
                                    leading=10.5, textColor=colors.HexColor("#1a1a19"),
                                    backColor=colors.HexColor("#f5f5f0"),
                                    leftIndent=8, rightIndent=6, borderPadding=5,
                                    spaceBefore=4, spaceAfter=9),
        "cell": ParagraphStyle("CellCN", parent=base, fontName="ArialUnicode",
                               fontSize=8.0, leading=10.5),
        "cellhead": ParagraphStyle("CellHeadCN", parent=base, fontName="ArialUnicode",
                                   fontSize=8.0, leading=10.5,
                                   textColor=colors.HexColor("#0b0b0b")),
        "imgcap": ParagraphStyle("ImgCapCN", parent=base, fontName="ArialUnicode",
                                 fontSize=8.5, leading=12, alignment=TA_LEFT,
                                 textColor=colors.HexColor("#52514e"), spaceAfter=10),
    }


def parse_table(lines: list[str], styles) -> Table:
    rows = []
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        rows.append(cells)
    ncols = max(len(r) for r in rows)
    data = []
    for i, row in enumerate(rows):
        row += [""] * (ncols - len(row))
        style = styles["cellhead"] if i == 0 else styles["cell"]
        data.append([Paragraph(table_cell(c), style) for c in row])
    colw = (PAGE_W - 2 * MARGIN) / ncols
    avail = PAGE_W - 2 * MARGIN
    weights = []
    needs = []
    for j in range(ncols):
        cells = [re.sub(r"[`*]", "", r[j]) for r in rows]
        longest = max(len(c) for c in cells)
        # Keep ASCII identifiers/paths on one line where possible.  Measure
        # the rendered width, not just the character count, and reserve that
        # width for the column below.
        tokens = [t for c in cells for t in re.findall(r"[A-Za-z0-9_.+%/-]{8,}", c)]
        token_pt = max((pdfmetrics.stringWidth(t, "DejaVuSansMono", 8.5)
                        for t in tokens), default=0)
        needs.append(min(token_pt + 8, avail * 0.40) if tokens else 0.0)
        weights.append(min(max(longest, token_pt / 3.2, 10), 90))
    total = sum(weights)
    colw = [max(2.5 * cm, avail * w / total) for w in weights]
    scale = avail / sum(colw)
    if scale < 1:
        colw = [w * scale for w in colw]
    # Move width from columns with slack to columns whose longest identifier
    # would otherwise be split mid-token by ReportLab.
    for _ in range(4):
        for j in range(ncols):
            want = needs[j] - colw[j]
            if want <= 1:
                continue
            donors = sorted(
                (k for k in range(ncols)
                 if k != j and colw[k] - max(needs[k], 2.0 * cm) > 1),
                key=lambda k: colw[k] - max(needs[k], 2.0 * cm),
                reverse=True,
            )
            for k in donors:
                room = colw[k] - max(needs[k], 2.0 * cm)
                take = min(want, room)
                colw[k] -= take
                colw[j] += take
                want -= take
                if want <= 1:
                    break
    table = Table(data, colWidths=colw, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f0fb")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c3c2b7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def render(md_path: pathlib.Path, pdf_path: pathlib.Path, title: str) -> None:
    styles = build_styles()
    lines = md_path.read_text(encoding="utf-8").splitlines()
    story = [Spacer(1, 0.35 * cm),
             Paragraph("UBITect / backlog.c 与 ahci_xgene 历史案例 · 教学与录屏材料",
                       styles["normal"]),
             Spacer(1, 0.15 * cm)]
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            code_text = "\n".join(code_lines(code))
            code_style = styles["code_cjk"] if any(ord(ch) > 127 for ch in code_text) else styles["code"]
            story.append(Preformatted(code_text, code_style))
            continue
        if line.strip() in ("---", "***", "___"):
            story.append(HRFlowable(width="100%", thickness=0.6,
                                    color=colors.HexColor("#c9c7bf"),
                                    spaceBefore=3, spaceAfter=9))
            i += 1
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            style = styles["h1"] if level == 1 else styles["h2"] if level == 2 else styles["h3"]
            story.append(Paragraph(inline(text), style))
            i += 1
            continue
        if line.strip().startswith("|") and i + 1 < len(lines) and "|" in lines[i + 1]:
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            story.append(parse_table(block, styles))
            story.append(Spacer(1, 7))
            continue
        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if m:
            alt, rel = m.group(1), m.group(2)
            image_path = (md_path.parent / rel).resolve()
            if not image_path.is_file():
                image_path = (ROOT / rel).resolve()
            if image_path.is_file():
                img = Image(str(image_path))
                maxw = PAGE_W - 2 * MARGIN
                scale = min(1.0, maxw / img.imageWidth)
                img.drawWidth = img.imageWidth * scale
                img.drawHeight = img.imageHeight * scale
                if alt:
                    story.append(KeepTogether([img, Paragraph(inline(alt), styles["imgcap"])]))
                else:
                    story.append(img)
            i += 1
            continue
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            text = line.strip()[2:]
            i += 1
            while i < len(lines) and lines[i].strip():
                nxt = lines[i]
                stripped = nxt.strip()
                if (stripped.startswith("- ") or stripped.startswith("* ")
                        or re.match(r"^\d+\.\s+", stripped)
                        or stripped.startswith(("#", "|", "```", ">"))
                        or stripped in ("---", "***", "___")):
                    break
                if nxt.startswith(("  ", "\t")):
                    text += " " + stripped
                    i += 1
                    continue
                break
            if text.startswith("[ ] "):
                story.append(Paragraph(inline(text[4:]), styles["bullet"], bulletText="☐"))
            elif text.lower().startswith("[x] "):
                story.append(Paragraph(inline(text[4:]), styles["bullet"], bulletText="☑"))
            else:
                story.append(Paragraph(inline(text), styles["bullet"], bulletText="•"))
            continue
        if re.match(r"^\d+\.\s+", line.strip()):
            m = re.match(r"^(\d+)\.\s+(.*)$", line.strip())
            text = m.group(2)
            i += 1
            while i < len(lines) and lines[i].strip():
                nxt = lines[i]
                stripped = nxt.strip()
                if (stripped.startswith("- ") or stripped.startswith("* ")
                        or re.match(r"^\d+\.\s+", stripped)
                        or stripped.startswith(("#", "|", "```", ">"))
                        or stripped in ("---", "***", "___")):
                    break
                if nxt.startswith(("  ", "\t")):
                    text += " " + stripped
                    i += 1
                    continue
                break
            story.append(Paragraph(inline(f"{m.group(1)}. {text}"), styles["num"]))
            continue
        if line.strip().startswith(">"):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            story.append(Paragraph(inline(" ".join(quote)), styles["quote"]))
            continue
        if not line.strip():
            i += 1
            continue
        para = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and lines[i].strip() not in ("---", "***", "___") and not (
            lines[i].startswith("#") or lines[i].startswith("```")
            or lines[i].strip().startswith("|") or lines[i].strip().startswith("- ")
            or lines[i].strip().startswith("* ") or re.match(r"^\d+\.\s+", lines[i].strip())
            or lines[i].strip().startswith(">")
        ):
            para.append(lines[i].strip())
            i += 1
        story.append(Paragraph(inline(" ".join(para)), styles["normal"]))
    doc = MarkdownDoc(str(pdf_path), title)
    doc.build(story)
    print(f"wrote {pdf_path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("pdf")
    ap.add_argument("--title", required=True)
    args = ap.parse_args()
    render(pathlib.Path(args.markdown), pathlib.Path(args.pdf), args.title)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
