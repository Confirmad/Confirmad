#!/usr/bin/env python3
"""
Static i18n build for the ConfirMad site.

Reads i18n/content/<lang>.json (one file per language) and
i18n/templates/<page>.html.tmpl (one template per translated page),
and writes the finished static HTML files into the repo root (English)
and /es/, /it/, /fr/ subfolders.

Run this from the repo root after editing any template or content
JSON, before committing:

    python3 i18n/build.py

This script has no dependencies beyond the Python standard library.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "i18n" / "content"
TEMPLATES_DIR = ROOT / "i18n" / "templates"

LANGS = ["en", "es", "it", "fr"]
LANG_NAMES = {"en": "EN", "es": "ES", "it": "IT", "fr": "FR"}

PAGES = ["index", "check"]

PAGE_URLS = {
    "index": {
        "en": "https://confirmad.es/",
        "es": "https://confirmad.es/es/",
        "it": "https://confirmad.es/it/",
        "fr": "https://confirmad.es/fr/",
    },
    "check": {
        "en": "https://confirmad.es/check.html",
        "es": "https://confirmad.es/es/check.html",
        "it": "https://confirmad.es/it/check.html",
        "fr": "https://confirmad.es/fr/check.html",
    },
}

OUTPUT_PATHS = {
    ("index", "en"): "index.html",
    ("index", "es"): "es/index.html",
    ("index", "it"): "it/index.html",
    ("index", "fr"): "fr/index.html",
    ("check", "en"): "check.html",
    ("check", "es"): "es/check.html",
    ("check", "it"): "it/check.html",
    ("check", "fr"): "fr/check.html",
}

PLACEHOLDER_RE = re.compile(r"\[\[([\w.\-]+)\]\]")


def get_path(data, dotted_path):
    node = data
    for part in dotted_path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def hreflang_block(page):
    lines = []
    for lang in LANGS:
        lines.append(
            '<link rel="alternate" hreflang="{0}" href="{1}">'.format(
                lang, PAGE_URLS[page][lang]
            )
        )
    lines.append(
        '<link rel="alternate" hreflang="x-default" href="{0}">'.format(
            PAGE_URLS[page]["en"]
        )
    )
    return "\n".join(lines)


def lang_selector(page, current_lang):
    parts = []
    for lang in LANGS:
        cls = ' class="lang-current"' if lang == current_lang else ""
        parts.append(
            '<a href="{0}"{1}>{2}</a>'.format(
                PAGE_URLS[page][lang], cls, LANG_NAMES[lang]
            )
        )
    return '<div class="lang-switch">' + " · ".join(parts) + "</div>"


def render(page, lang, template_text, lang_data):
    special = {
        "HTML_LANG": lang,
        "CANONICAL_URL": PAGE_URLS[page][lang],
        "OG_URL": PAGE_URLS[page][lang],
        "HREFLANG_LINKS": hreflang_block(page),
        "LANG_SELECTOR": lang_selector(page, lang),
        "JSON_I18N_FORM": json.dumps(
            {
                "sending": get_path(lang_data, "request.sending"),
                "submit": get_path(lang_data, "request.submit"),
            },
            ensure_ascii=False,
        ),
        "JSON_I18N_CHECKJS": json.dumps(
            get_path(lang_data, "check_js"), ensure_ascii=False
        ),
        "WA_FLOAT_TEXT": quote(get_path(lang_data, "whatsapp.float_message") or ""),
        "WA_EARLY_TEXT": quote(get_path(lang_data, "whatsapp.early_message") or ""),
    }

    missing = []

    def replace(m):
        key = m.group(1)
        if key in special:
            return special[key]
        value = get_path(lang_data, key)
        if value is None:
            missing.append(key)
            return m.group(0)
        return value

    out = PLACEHOLDER_RE.sub(replace, template_text)
    if missing:
        raise SystemExit(
            "Missing content keys for page={0} lang={1}: {2}".format(
                page, lang, ", ".join(sorted(set(missing)))
            )
        )
    return out


def main():
    content = {}
    for lang in LANGS:
        path = CONTENT_DIR / "{0}.json".format(lang)
        if not path.exists():
            print("Skipping {0}: no content file at {1}".format(lang, path))
            continue
        content[lang] = json.loads(path.read_text(encoding="utf-8"))

    for page in PAGES:
        tmpl_path = TEMPLATES_DIR / "{0}.html.tmpl".format(page)
        template_text = tmpl_path.read_text(encoding="utf-8")
        for lang in LANGS:
            if lang not in content:
                continue
            out_text = render(page, lang, template_text, content[lang])
            out_path = ROOT / OUTPUT_PATHS[(page, lang)]
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(out_text, encoding="utf-8")
            print("Wrote {0}".format(out_path.relative_to(ROOT)))


if __name__ == "__main__":
    main()
