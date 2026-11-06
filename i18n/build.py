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
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "i18n" / "content"
TEMPLATES_DIR = ROOT / "i18n" / "templates"

# Pages that are NOT generated from a template (hand-maintained static HTML)
# but still need the confirmad-build meta tag kept in sync on every build,
# so a stale CDN/edge cache in front of any one of them is easy to spot:
# every page on the live site should report the same value. This is the
# short hash of the commit this build ran against (i.e. HEAD's parent once
# you commit the output) - good enough to prove "these pages were built
# together", which is all the check in README/Santiago's instructions needs.
STATIC_PAGES = [
    "sample-report.html",
    "terminos.html",
    "privacidad.html",
    "aviso-legal.html",
    "cookies.html",
    "modelo-desistimiento.html",
    "gracias.html",
]

BUILD_META_RE = re.compile(
    r'<meta name="confirmad-build" content="[^"]*">'
)


def get_build_id():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def stamp_static_page(path, build_id):
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    tag = '<meta name="confirmad-build" content="{0}">'.format(build_id)
    if BUILD_META_RE.search(text):
        new_text = BUILD_META_RE.sub(tag, text, count=1)
    else:
        marker = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        if marker not in text:
            marker = '<meta name="viewport" content="width=device-width, initial-scale=1">'
        if marker not in text:
            return
        new_text = text.replace(marker, marker + "\n" + tag, 1)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print("Stamped {0}".format(path.relative_to(ROOT)))

LANGS = ["en", "es", "it", "fr"]
LANG_NAMES = {"en": "EN", "es": "ES", "it": "IT", "fr": "FR"}

PAGES = ["index", "check", "solicitar", "empresas"]

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
    "solicitar": {
        "en": "https://confirmad.es/solicitar.html",
        "es": "https://confirmad.es/es/solicitar.html",
        "it": "https://confirmad.es/it/solicitar.html",
        "fr": "https://confirmad.es/fr/solicitar.html",
    },
    "empresas": {
        "en": "https://confirmad.es/empresas.html",
        "es": "https://confirmad.es/es/empresas.html",
        "it": "https://confirmad.es/it/empresas.html",
        "fr": "https://confirmad.es/fr/empresas.html",
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
    ("solicitar", "en"): "solicitar.html",
    ("solicitar", "es"): "es/solicitar.html",
    ("solicitar", "it"): "it/solicitar.html",
    ("solicitar", "fr"): "fr/solicitar.html",
    ("empresas", "en"): "empresas.html",
    ("empresas", "es"): "es/empresas.html",
    ("empresas", "it"): "it/empresas.html",
    ("empresas", "fr"): "fr/empresas.html",
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


def render(page, lang, template_text, lang_data, build_id):
    special = {
        "HTML_LANG": lang,
        "BUILD_META": build_id,
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
        "WA_SHARE_TEXT": quote(get_path(lang_data, "whatsapp.share_message") or ""),
        "EMAIL_SHARE_SUBJECT": quote(get_path(lang_data, "whatsapp.share_email_subject") or ""),
        "WA_BUSINESS_TEXT": quote(get_path(lang_data, "whatsapp.business_message") or ""),
        "JSON_I18N_BUSINESS": json.dumps(
            {
                "sending": get_path(lang_data, "business.sending"),
                "submit": get_path(lang_data, "business.submit"),
                "success_strong": get_path(lang_data, "business.success_strong"),
                "success_rest": get_path(lang_data, "business.success_rest"),
                "error_strong": get_path(lang_data, "business.error_strong"),
                "error_rest_pre": get_path(lang_data, "business.error_rest_pre"),
                "error_rest_post": get_path(lang_data, "business.error_rest_post"),
            },
            ensure_ascii=False,
        ),
        "JSON_I18N_PLANS": json.dumps(
            get_path(lang_data, "plans"), ensure_ascii=False
        ),
        "JSON_I18N_REQUEST": json.dumps(
            {
                "submitting_button": get_path(lang_data, "request.submitting_button"),
                "submit_button": get_path(lang_data, "request.submit_button"),
                "error_prefix": get_path(lang_data, "request.error_prefix"),
                "error_fallback": get_path(lang_data, "request.error_fallback"),
                "reference_label": get_path(lang_data, "request.reference_label"),
            },
            ensure_ascii=False,
        ),
        "STRIPE_LOCALE": lang,
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
    build_id = get_build_id()
    print("Build id: {0}".format(build_id))

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
            out_text = render(page, lang, template_text, content[lang], build_id)
            out_path = ROOT / OUTPUT_PATHS[(page, lang)]
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(out_text, encoding="utf-8")
            print("Wrote {0}".format(out_path.relative_to(ROOT)))

    for rel in STATIC_PAGES:
        stamp_static_page(ROOT / rel, build_id)


if __name__ == "__main__":
    main()
