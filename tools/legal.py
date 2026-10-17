#!/usr/bin/env python3
"""Gera as páginas /termos e /privacidade a partir dos textos do sistema.

A fonte é `belia_mishpat/docs/legal/`, e não uma cópia aqui: o texto jurídico
tem um lugar só, versionado junto com o código que grava o aceite. Copiar à mão
para o HTML é o caminho para a página dizer uma coisa e o contrato aceito
dizer outra.

    python3 tools/legal.py                       # lê ../belia_mishpat/docs/legal
    python3 tools/legal.py /caminho/docs/legal   # outra origem

O conversor entende só o Markdown que esses textos usam — títulos, parágrafos,
listas, tabelas, negrito, itálico e código. Coisa nova no texto que não saia
certa aqui pede uma linha a mais neste arquivo, não uma biblioteca.
"""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "mishpat"
DEFAULT_SOURCE = ROOT.parent / "belia_mishpat" / "docs" / "legal"


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w/\"])([\w.+-]+@beliasoftware\.com)", r'<a href="mailto:\1">\1</a>', text)
    return text.replace("&amp;nbsp;", "&nbsp;")


def convert(markdown: str, shift: int = 0) -> str:
    """Markdown → HTML. `shift` rebaixa os títulos (o anexo entra numa página
    que já tem o seu h1)."""
    out, para, items = [], [], []
    lines = markdown.splitlines()
    i = 0

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            items.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            flush()
        elif stripped == "---":
            flush()
            out.append("<hr>")
        elif m := re.match(r"^(#{1,6})\s+(.*)", stripped):
            flush()
            level = min(len(m.group(1)) + shift, 6)
            title = m.group(2)
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower().encode("ascii", "ignore").decode()).strip("-")
            out.append(f'<h{level} id="{slug}">{inline(title)}</h{level}>')
        elif stripped.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            head, body = rows[0], rows[1:]
            out.append(
                '<div class="table"><table><thead><tr>'
                + "".join(f"<th>{inline(c)}</th>" for c in head)
                + "</tr></thead><tbody>"
                + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
                + "</tbody></table></div>"
            )
            continue
        elif stripped.startswith("- "):
            if para:
                flush()
            items.append(stripped[2:])
        elif items and line.startswith("  "):
            items[-1] += " " + stripped
        else:
            if items:
                flush()
            para.append(stripped)
        i += 1

    flush()
    return "\n".join(out)


PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Belia Mishpat</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://beliasoftware.com/{path}/">
<meta name="theme-color" content="#12161f">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%232c3a52'/%3E%3Ctext x='16' y='23' font-family='Georgia,serif' font-size='19' font-weight='700' fill='%23fff' text-anchor='middle'%3EB%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">
<!-- Gerado por tools/legal.py a partir de belia_mishpat/docs/legal. Não editar à mão. -->
<style>
:root {{
  --navy-800: oklch(0.292 0.060 260);
  --navy-950: oklch(0.172 0.038 262);
  --neutral-0: oklch(1 0 0);
  --neutral-50: oklch(0.977 0.004 252);
  --neutral-100: oklch(0.956 0.005 252);
  --neutral-200: oklch(0.912 0.007 252);
  --text-strong: oklch(0.212 0.013 261);
  --text-body: oklch(0.285 0.013 260);
  --text-muted: oklch(0.478 0.013 256);
  --accent: oklch(0.520 0.100 200);
  --font-sans: 'IBM Plex Sans', system-ui, -apple-system, Segoe UI, sans-serif;
  --font-serif: 'Source Serif 4', Georgia, 'Times New Roman', serif;
  --font-mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}}
* {{ box-sizing: border-box; margin: 0; }}
html {{ -webkit-text-size-adjust: 100%; }}
body {{ background: var(--neutral-0); color: var(--text-body); font: 16px/1.7 var(--font-sans); }}
a {{ color: var(--navy-800); text-underline-offset: 2px; }}
.top {{ border-bottom: 1px solid var(--neutral-200); background: var(--neutral-0); position: sticky; top: 0; z-index: 2; }}
.top-in {{ max-width: 960px; margin: 0 auto; padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; gap: 16px; }}
.brand {{ display: inline-flex; align-items: center; gap: 10px; text-decoration: none; color: var(--text-strong); font: 700 19px/1 var(--font-serif); }}
.brand small {{ display: block; font: 600 10px/1 var(--font-sans); letter-spacing: .12em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 3px; }}
.top nav {{ display: flex; gap: 18px; font-size: 14px; }}
.top nav a {{ color: var(--text-muted); text-decoration: none; }}
.top nav a[aria-current] {{ color: var(--text-strong); font-weight: 600; }}
main {{ max-width: 760px; margin: 0 auto; padding: 48px 16px 72px; }}
h1, h2 {{ font-family: var(--font-serif); color: var(--text-strong); line-height: 1.2; letter-spacing: -0.01em; }}
h1 {{ font-size: clamp(30px, 5vw, 40px); margin-bottom: 8px; }}
h2 {{ font-size: 24px; margin: 44px 0 12px; scroll-margin-top: 80px; }}
h3 {{ font-size: 17px; color: var(--text-strong); margin: 32px 0 8px; scroll-margin-top: 80px; }}
h1 + p {{ color: var(--text-muted); font-size: 14px; }}
p, ul, .table {{ margin: 0 0 14px; }}
ul {{ padding-left: 22px; }}
li {{ margin-bottom: 6px; }}
hr {{ border: 0; border-top: 1px solid var(--neutral-200); margin: 32px 0; }}
code {{ font: 14px var(--font-mono); background: var(--neutral-100); padding: 1px 5px; border-radius: 4px; }}
.table {{ overflow-x: auto; border: 1px solid var(--neutral-200); border-radius: 10px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 14px; line-height: 1.5; }}
th, td {{ text-align: left; vertical-align: top; padding: 10px 12px; border-bottom: 1px solid var(--neutral-200); }}
th {{ background: var(--neutral-50); color: var(--text-strong); font-weight: 600; }}
tr:last-child td {{ border-bottom: 0; }}
.annex {{ margin-top: 64px; padding-top: 8px; border-top: 3px solid var(--navy-800); }}
footer {{ border-top: 1px solid var(--neutral-200); background: var(--neutral-50); font-size: 13px; color: var(--text-muted); }}
footer div {{ max-width: 960px; margin: 0 auto; padding: 24px 16px 32px; display: flex; flex-wrap: wrap; gap: 8px 24px; justify-content: space-between; }}
@media print {{ .top, footer {{ display: none; }} main {{ padding: 0; }} }}
</style>
</head>
<body>
<!-- O Cloudflare troca e-mail por "[email protected]" e desfaz a troca com um
     script da página. O cadastro carrega este texto numa janela, onde o script
     não passa — e o contrato sairia sem o endereço de contato. -->
<!--email_off-->
<header class="top"><div class="top-in">
  <a class="brand" href="/"><span><small>Belia</small>Mishpat</span></a>
  <nav aria-label="Documentos">
    <a href="/termos/"{terms_current}>Termos de Uso</a>
    <a href="/privacidade/"{privacy_current}>Privacidade</a>
  </nav>
</div></header>
<main>
{body}
</main>
<footer><div>
  <span>&copy; 2026 BELIA SOFTWARE LTDA · CNPJ 66.360.810/0001-67</span>
  <span>Encarregado de dados: <a href="mailto:privacidade@beliasoftware.com">privacidade@beliasoftware.com</a></span>
</div></footer>
<!--/email_off-->
</body>
</html>
"""


def write(path: str, title: str, description: str, body: str):
    target = SITE / path / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(PAGE.format(
        title=title, description=description, path=path, body=body,
        terms_current=' aria-current="page"' if path == "termos" else "",
        privacy_current=' aria-current="page"' if path == "privacidade" else "",
    ))
    print(f"→ {target.relative_to(ROOT)}")


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    terms = (source / "termos-de-uso.md").read_text()
    annex = (source / "contrato-tratamento-dados.md").read_text()
    privacy = (source / "politica-de-privacidade.md").read_text()

    # O anexo vai na mesma página dos Termos: é aceito junto, e quem lê a
    # cláusula que o cita chega nele rolando, sem trocar de página. Os links
    # do fim dos Termos viram âncoras para onde o texto de fato está.
    terms = terms.replace(
        "**Anexo I** — Contrato de Tratamento de Dados Pessoais",
        "**Anexo I** — Contrato de Tratamento de Dados Pessoais (abaixo)")
    body = convert(terms) + '\n<section class="annex" id="anexo-i">\n' + convert(annex) + "\n</section>"
    body = body.replace("<strong>Documento relacionado</strong> — Política de Privacidade",
                        '<strong>Documento relacionado</strong> — <a href="/privacidade/">Política de Privacidade</a>')
    write("termos", "Termos de Uso",
          "Termos de Uso do Belia Mishpat e o Contrato de Tratamento de Dados Pessoais anexo a eles.", body)

    write("privacidade", "Política de Privacidade",
          "Como a Belia Software trata os dados pessoais de quem visita o site e de quem usa o Belia Mishpat.",
          convert(privacy))


if __name__ == "__main__":
    main()
