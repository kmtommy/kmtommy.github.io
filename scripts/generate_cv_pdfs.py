"""Generate both CV PDFs from the site's Korean HTML and English translations.

Requires reportlab and a TrueType font containing Korean glyphs. Set
CV_PDF_FONT to a font path when none of the default locations is available.
"""

import json
import os
import re
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "cv"
COPY = json.loads(re.search(
    r"const english = (\{.*?\n\});", (ROOT / "script.js").read_text(), re.S
).group(1))


class Node:
    def __init__(self, tag="root", attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []

    def all(self, tag=None, cls=None, id=None):
        found = []
        for child in self.children:
            if isinstance(child, Node):
                if ((tag is None or child.tag == tag)
                    and (cls is None or cls in child.attrs.get("class", "").split())
                    and (id is None or child.attrs.get("id") == id)):
                    found.append(child)
                found.extend(child.all(tag, cls, id))
        return found

    def first(self, tag=None, cls=None, id=None):
        return self.all(tag, cls, id)[0]

    def text(self, lang):
        key = self.attrs.get("data-i18n")
        if lang == "en" and key in COPY:
            return COPY[key]
        return "".join(c.text(lang) if isinstance(c, Node) else c for c in self.children).strip()

    def inline(self, lang):
        if self.attrs.get("aria-hidden") == "true":
            return ""
        if self.attrs.get("data-i18n"):
            value = escape(self.text(lang))
        else:
            value = "".join(c.inline(lang) if isinstance(c, Node) else escape(c) for c in self.children)
        if self.tag == "strong":
            return f"<b>{value}</b>"
        if self.tag == "a":
            url = self.attrs.get("href", "")
            if url.startswith(("https://", "mailto:")):
                return f'<link href="{escape(url, quote=True)}" color="#333333">{value}</link>'
        return value.strip()


class Parser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.root = Node()
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def register_font():
    candidates = [
        os.environ.get("CV_PDF_FONT", ""),
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic-Regular.ttf",
    ]
    font = next((Path(p) for p in candidates if p and Path(p).is_file()), None)
    if font is None:
        raise SystemExit("Set CV_PDF_FONT to a TrueType font with Korean glyphs.")
    pdfmetrics.registerFont(TTFont("CV", str(font)))
    pdfmetrics.registerFontFamily("CV", normal="CV", bold="CV", italic="CV", boldItalic="CV")


def build(lang, root):
    def text(key):
        return next(n.text(lang) for n in root.all() if n.attrs.get("data-i18n") == key)

    base = dict(fontName="CV", alignment=TA_LEFT, wordWrap="CJK", textColor=colors.HexColor("#222222"))
    styles = {
        "body": ParagraphStyle("body", fontSize=9.2, leading=13.5, spaceAfter=4, **base),
        "small": ParagraphStyle("small", fontSize=8, leading=11.5, spaceAfter=3, **base),
        "title": ParagraphStyle("title", fontSize=23, leading=29, spaceAfter=4, **base),
        "section": ParagraphStyle("section", fontSize=12.4, leading=17, spaceBefore=13, spaceAfter=7, keepWithNext=True, **base),
        "entry": ParagraphStyle("entry", fontSize=10, leading=14, spaceAfter=4, keepWithNext=True, **base),
        "bullet": ParagraphStyle("bullet", fontSize=9, leading=13, leftIndent=9, firstLineIndent=-7, spaceAfter=3, **base),
        "award": ParagraphStyle("award", fontSize=8, leading=10.5, spaceAfter=1.5, **base),
    }

    def p(value, style="body", raw=False):
        value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2011", "-")
        return Paragraph(value if raw else escape(value), styles[style])

    def section(key):
        return [p(text(key), "section"), HRFlowable(width="100%", thickness=.45, color=colors.HexColor("#cccccc")), Spacer(1, 6)]

    def header(title, date=""):
        if not date:
            return [p(title, "entry")]
        row = Table([[p(title, "entry"), p(date, "small")]], colWidths=[365, 134])
        row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        return [row]

    def project(node):
        dates = node.all(cls="date")
        out = header(node.first("h3").text(lang), dates[0].text(lang) if dates else "")
        subtitles = node.all(cls="entry-subtitle")
        labels = node.all(cls="small-label")
        if subtitles:
            out.append(p(subtitles[0].text(lang), "small"))
        elif labels:
            out.append(p(labels[0].text(lang), "small"))
        for item in node.all("li"):
            out.append(p("- " + item.text(lang), "bullet"))
        for link in node.all("a", "inline-link"):
            out.append(p(link.inline(lang), "small", raw=True))
        out.append(Spacer(1, 6))
        return out

    name = text("name")
    story = [p(name, "title"), p(text("name.secondary"), "small")]
    story.append(p('<link href="mailto:tommy816@g.hongik.ac.kr">tommy816@g.hongik.ac.kr</link>  |  <link href="https://kmtommy.github.io/">kmtommy.github.io</link>  |  <link href="https://github.com/kmtommy">GitHub</link>', "small", raw=True))
    story.extend([Spacer(1, 6), p(text("hero.description")), p(text("focus.title") + ": " + " / ".join(text(k) for k in ["focus.legged", "focus.learning", "focus.control"]), "small"), p(text("focus.note"), "small")])

    education = root.first(id="education")
    story.extend(section("nav.education"))
    story.extend(header(education.first("h3").text(lang), text("education.date")))
    story.extend([p(text("education.degree")), p(text("education.year"), "small")])

    story.extend(section("nav.research"))
    story.extend(header("HSIR Lab.", text("research.date")))
    story.extend([p(text("research.role"), "small"), p(text("research.advisor"), "small"), p(text("research.haptic") + " - " + text("status.ongoing"), "entry"), p(text("research.haptic.body"))])

    publication = root.first(id="publications")
    story.extend(section("nav.publications"))
    story.extend(header(publication.first("h3").text(lang), "2026.08"))
    story.append(p(publication.first("p", "entry-subtitle").inline(lang), raw=True))
    story.extend([p(text("publication.venue"), "small"), p(text("publication.pages") + " | " + text("publication.role"), "small"), p(text("publication.award"), "small"), p(publication.first("a", "inline-link").inline(lang), "small", raw=True)])

    projects = root.first(id="projects").all("article", "project-entry")
    story.extend(section("nav.projects"))
    story.extend(project(projects[0]))
    story.append(PageBreak())
    story.extend(section("nav.projects"))
    for entry in projects[1:]:
        story.extend(project(entry))

    story.extend(section("nav.awards"))
    for entry in root.first(id="awards").all(cls="award-entry"):
        title = entry.first("h3").text(lang)
        for badge in entry.all(cls="badge"):
            title += " · " + badge.text(lang)
        content = [p(title, "body")]
        for paragraph in entry.all("p"):
            content.append(p(paragraph.inline(lang), "award", raw=True))
        link = entry.first("a")
        href = link.attrs["href"]
        if href.startswith("./"):
            href = "https://kmtommy.github.io/" + href[2:]
        link_text = text("award.certificate") if "certificate" in href or "attachments" in href or "Jeju" in href else ("Source" if lang == "en" else "수상 기록")
        cells = [p(entry.first("time").text(lang), "small"), content, p(f'<link href="{escape(href, quote=True)}">{escape(link_text)}</link>', "small", raw=True)]
        row = Table([cells], colWidths=[68, 365, 66])
        row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        story.append(KeepTogether([row]))

    story.extend(section("nav.activities"))
    activities = root.first(id="activities")
    story.extend(header(text("leadership.title"), "2023.03-2025.12"))
    story.extend([p(text("leadership.university"), "small"), p(text("leadership.role") + " | 2025.01-2025.12", "small")])
    story.extend(p("- " + item.text(lang), "bullet") for item in activities.all("li"))

    skill_flow = section("nav.skills")
    skills = root.first(id="skills")
    for label, value in zip(skills.all("dt"), skills.all("dd")):
        skill_flow.append(p(label.text(lang) + ": " + value.text(lang), "small"))
    story.append(KeepTogether(skill_flow))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#dddddd"))
        canvas.line(42, 32, A4[0] - 42, 32)
        canvas.setFont("CV", 7.5)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(42, 20, "Gyeongmin Jung | https://kmtommy.github.io/")
        canvas.drawRightString(A4[0] - 42, 20, str(doc.page))
        canvas.restoreState()

    output = OUTPUT / f"Gyeongmin_Jung_CV_{lang.upper()}.pdf"
    document = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=42, rightMargin=42, topMargin=36, bottomMargin=43, title=f"Gyeongmin Jung - CV ({lang.upper()})", author="Gyeongmin Jung", pageCompression=1)
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == "__main__":
    register_font()
    parser = Parser()
    parser.feed((ROOT / "index.html").read_text())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for language in ("ko", "en"):
        build(language, parser.root)
