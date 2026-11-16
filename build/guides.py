#!/usr/bin/env python3
"""Build the ES/CA teacher guides from Markdown (requires pandoc)."""

from html import escape
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TEXT = {
    'es': {'title': 'Guías para el profesorado', 'home': 'Volver a los juegos',
           'all': 'Todas las guías', 'print': 'Imprimir esta guía',
           'play': 'Abrir el juego en otra pestaña', 'skip': 'Ir al contenido',
           'license': 'Guías didácticas de EduTicTac · Samuel Soriano ·',
           'other': 'Valencià', 'other_lang': 'ca'},
    'ca': {'title': 'Guies per al professorat', 'home': 'Tornar als jocs',
           'all': 'Totes les guies', 'print': 'Imprimir esta guia',
           'play': 'Obrir el joc en una altra pestanya', 'skip': 'Anar al contingut',
           'license': 'Guies didàctiques d’EduTicTac · Samuel Soriano ·',
           'other': 'Castellano', 'other_lang': 'es'},
}


def main():
    for lang, text in TEXT.items():
        for source in sorted((ROOT / 'guides' / lang).glob('*.md')):
            markdown = source.read_text(encoding='utf-8')
            title = markdown.splitlines()[0].removeprefix('# ')
            body = subprocess.run(
                ['pandoc', '-f', 'markdown+autolink_bare_uris', '-t', 'html5', '--wrap=none'],
                input=markdown, text=True, capture_output=True, check=True,
            ).stdout
            game = source.stem
            play = '' if game == 'index' else (
                f'<a class="button" href="../../{game}.html?lang={lang}&amp;level=1" '
                f'target="_blank" rel="noopener">{text["play"]}</a>')
            page = f'''<!doctype html>
<html lang="{lang}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · Blockly Games · EduTicTac</title>
<link rel="stylesheet" href="../style.css"><script src="../guide.js" defer></script></head>
<body><a class="skip" href="#content">{text['skip']}</a>
<header><p class="eyebrow">EduTicTac · Blockly Games</p>
<nav aria-label="{'Navegación' if lang == 'es' else 'Navegació'}">
<a href="../../index.html?lang={lang}">{text['home']}</a>
<a href="index.html">{text['all']}</a>
<a href="../{text['other_lang']}/{game}.html" lang="{text['other_lang']}" hreflang="{text['other_lang']}">{text['other']}</a>
</nav></header>
<main id="content"><div class="actions">{play}<button type="button" id="print-guide">{text['print']}</button></div>
<article>{body}</article></main>
<footer>{text['license']} <a rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.{'es' if lang == 'es' else 'ca'}">CC BY-NC-SA 4.0</a>.
<p>Blockly Games: Google · Apache-2.0. Dance: EduTicTac.</p></footer></body></html>
'''
            target = ROOT / 'appengine' / 'guias' / lang / (game + '.html')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page, encoding='utf-8')
    print('Teacher guides built: ES and CA.')


if __name__ == '__main__':
    main()
