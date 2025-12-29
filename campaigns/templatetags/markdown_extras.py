from __future__ import annotations

from django import template
from django.utils.safestring import mark_safe

try:
  import bleach
except Exception:  # pragma: no cover
  bleach = None

try:
  import markdown as md
except Exception:  # pragma: no cover
  md = None

register = template.Library()


_ALLOWED_TAGS = [
  "a",
  "blockquote",
  "br",
  "code",
  "em",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "hr",
  "img",
  "li",
  "ol",
  "p",
  "pre",
  "strong",
  "ul",
]

_ALLOWED_ATTRIBUTES = {
  "a": ["href", "title", "rel", "target"],
  "img": ["src", "alt", "title"],
}

_ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


@register.filter(name="markdownify")
def markdownify(value: str) -> str:
  """Render Markdown to safe HTML.

  Falls back to escaped plain text if optional deps aren't installed.
  """
  text = (value or "").strip()
  if not text:
    return ""

  if md is None or bleach is None:
    # No optional deps installed; keep it plain.
    from django.utils.html import escape

    return "<p>" + escape(text).replace("\n", "<br>") + "</p>"

  html = md.markdown(
    text,
    extensions=["fenced_code", "tables"],
    output_format="html5",
  )

  cleaned = bleach.clean(
    html,
    tags=_ALLOWED_TAGS,
    attributes=_ALLOWED_ATTRIBUTES,
    protocols=_ALLOWED_PROTOCOLS,
    strip=True,
  )

  cleaned = bleach.linkify(cleaned)
  return mark_safe(cleaned)
