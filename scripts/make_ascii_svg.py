"""Transforma foto/prepped.png em ascii-portrait.svg: retrato em letras que se "digita" linha a linha.

Escuro = caractere denso, branco (fundo) = espaco (como no artigo). Animacao SMIL, toca uma vez e congela.
STATIC=1 gera o quadro final parado.
"""
import os
from html import escape
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "foto" / "prepped.png"
SAIDA = RAIZ / "ascii-portrait.svg"

LARGURA, ALTURA = 370, 470
TOPO, MARGEM = 38, 12
COLUNAS = 104
GAMA = float(os.environ.get("GAMA", "0.8"))
RAMPA = " .:-=+*#%@"
FUNDO, BORDA, TEXTO, APAGADO = "#0d1117", "#30363d", "#c9d1d9", "#8b949e"


def main() -> None:
    parado = os.environ.get("STATIC") == "1"
    img = Image.open(ENTRADA).convert("L")
    area_w, area_h = LARGURA - 2 * MARGEM, ALTURA - TOPO - MARGEM
    passo_x = area_w / COLUNAS
    # linhas que cabem mantendo a proporcao da foto
    linhas_n = int(COLUNAS * img.height / img.width * passo_x / (passo_x * 1.82))
    passo_y = min(area_h / linhas_n, passo_x * 1.82)
    img = img.filter(ImageFilter.UnsharpMask(radius=4, percent=160, threshold=2))
    img = ImageEnhance.Contrast(img).enhance(1.35)
    img = img.point(lambda v: round(255 * (v / 255) ** GAMA))  # clareia a pele, mantem tracos escuros
    img = img.resize((COLUNAS, linhas_n), Image.LANCZOS)
    px = img.load()

    fonte = passo_y * 0.98
    y0 = TOPO + (area_h - linhas_n * passo_y) / 2 + fonte * 0.8
    defs, corpo = [], []
    ultimo = len(RAMPA) - 1
    for r in range(linhas_n):
        linha = "".join(RAMPA[round((255 - px[c, r]) / 255 * ultimo)] for c in range(COLUNAS))
        if not linha.strip():
            continue
        y = y0 + r * passo_y
        texto = (
            f'<text x="{MARGEM}" y="{y:.2f}" textLength="{area_w:.1f}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve">{escape(linha)}</text>'
        )
        if parado:
            corpo.append(texto)
            continue
        ini, dur = 0.3 + r * 0.045, 0.32
        topo_lin = y - fonte
        defs.append(
            f'<clipPath id="r{r}"><rect x="{MARGEM}" y="{topo_lin:.2f}" width="0" height="{passo_y + 1:.2f}">'
            f'<animate attributeName="width" from="0" to="{area_w}" begin="{ini:.2f}s" dur="{dur}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        corpo.append(f'<g clip-path="url(#r{r})">{texto}</g>')
        corpo.append(
            f'<rect x="{MARGEM}" y="{topo_lin:.2f}" width="{passo_x * 1.2:.2f}" height="{passo_y:.2f}" fill="#39d353" opacity="0">'
            f'<set attributeName="opacity" to="0.9" begin="{ini:.2f}s"/>'
            f'<animate attributeName="x" from="{MARGEM}" to="{MARGEM + area_w}" begin="{ini:.2f}s" dur="{dur}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{ini + dur:.2f}s"/></rect>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{ALTURA}" viewBox="0 0 {LARGURA} {ALTURA}" role="img" aria-label="Retrato em ASCII de João Pedro">
<style>text{{font-family:'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace;font-size:{fonte:.2f}px;fill:{TEXTO}}}</style>
<defs>{''.join(defs)}</defs>
<rect x="0.5" y="0.5" width="{LARGURA - 1}" height="{ALTURA - 1}" rx="10" fill="{FUNDO}" stroke="{BORDA}"/>
<circle cx="20" cy="18" r="5" fill="#ff5f56"/><circle cx="38" cy="18" r="5" fill="#ffbd2e"/><circle cx="56" cy="18" r="5" fill="#27c93f"/>
<text x="{LARGURA / 2}" y="22" text-anchor="middle" style="font-size:11px;fill:{APAGADO}">retrato.txt</text>
{''.join(corpo)}
</svg>
"""
    SAIDA.write_text(svg, encoding="utf-8")
    print(f"gravado {SAIDA.name} ({COLUNAS}x{linhas_n})")


if __name__ == "__main__":
    main()
