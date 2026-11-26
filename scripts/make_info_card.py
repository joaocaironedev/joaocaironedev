"""Gera info-card.svg: cartao estilo neofetch. Rode de novo quando quiser mudar o texto.

STATIC=1 gera o quadro parado (sem animacao), util para conferir.
"""
import os
from html import escape
from pathlib import Path

SAIDA = Path(__file__).resolve().parent.parent / "info-card.svg"
LARGURA, ALTURA = 490, 470
FUNDO, BORDA, TEXTO, APAGADO = "#0d1117", "#30363d", "#c9d1d9", "#8b949e"
VERDE, AZUL, ROXO, AMARELO = "#39d353", "#58a6ff", "#bc8cff", "#e3b341"

# (chave, valor, cor da chave). Chave vazia = linha de texto solta; None = linha em branco.
LINHAS = [
    ("joao@github", "", VERDE),
    ("-" * 28, "", BORDA),
    ("Nome", "João Pedro Cairone Ribeiro", AZUL),
    ("Função", "Dev Python & Full Stack Jr.", AZUL),
    ("Agora", "Analista de E-commerce @ Mei Mei", AZUL),
    ("Foco", "Integrações com marketplaces", AZUL),
    ("Local", "Taquarituba, SP", AZUL),
    ("Formação", "ADS - UNINTER (2024-2026)", AZUL),
    None,
    ("Back", "Python · FastAPI · SQL · n8n", ROXO),
    ("Front", "TypeScript · React · Next.js", ROXO),
    ("Desktop", "PySide6 (Qt) · Excel VBA", ROXO),
    ("Infra", "Docker · Cloudflare · MySQL · Redis", ROXO),
    ("APIs", "Mercado Livre · Shopee · Magalu · Amazon", ROXO),
    None,
    ("Destaques", "", AMARELO),
    ("", "▸ App de preços p/ 4 marketplaces (~2.500 testes)", AMARELO),
    ("", "▸ Central de agentes 24/7 em Docker (600+ testes)", AMARELO),
    ("", "▸ Painel de preços que trocou ferramenta paga", AMARELO),
    ("", "▸ Sistema web de gestão no ar na Cloudflare", AMARELO),
]


def main() -> None:
    parado = os.environ.get("STATIC") == "1"
    x, y, passo = 24, 64, 19
    linhas = []
    for i, item in enumerate(LINHAS):
        if item is None:
            y += passo * 0.6
            continue
        chave, valor, cor = item
        atraso = 0.25 + i * 0.11
        estilo = "" if parado else f' style="animation-delay:{atraso:.2f}s"'
        if chave and valor:
            conteudo = (
                f'<tspan fill="{cor}" font-weight="700">{escape(chave)}</tspan>'
                f'<tspan fill="{APAGADO}">: </tspan><tspan fill="{TEXTO}">{escape(valor)}</tspan>'
            )
        elif chave:
            conteudo = f'<tspan fill="{cor}" font-weight="700">{escape(chave)}</tspan>'
        else:
            conteudo = f'<tspan fill="{TEXTO}">{escape(valor)}</tspan>'
        linhas.append(f'<text class="l" x="{x}" y="{y:.0f}"{estilo}>{conteudo}</text>')
        y += passo

    atraso_paleta = "" if parado else f' style="animation-delay:{0.25 + len(LINHAS) * 0.11:.2f}s"'
    paleta = "".join(
        f'<rect class="l" x="{x + i * 26}" y="{y + 4:.0f}" width="22" height="12" rx="2" fill="{c}"{atraso_paleta}/>'
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f", AZUL, ROXO, AMARELO, TEXTO, "#484f58"])
    )
    animacao = "" if parado else (
        ".l{opacity:0;animation:entra .45s ease-out forwards}"
        "@keyframes entra{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}"
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{ALTURA}" viewBox="0 0 {LARGURA} {ALTURA}" role="img" aria-label="João Pedro Cairone Ribeiro - Dev Python e Full Stack">
<style>text{{font-family:'JetBrains Mono','Fira Code',Consolas,monospace;font-size:13px}}{animacao}</style>
<rect x="0.5" y="0.5" width="{LARGURA - 1}" height="{ALTURA - 1}" rx="10" fill="{FUNDO}" stroke="{BORDA}"/>
<circle cx="20" cy="18" r="5" fill="#ff5f56"/><circle cx="38" cy="18" r="5" fill="#ffbd2e"/><circle cx="56" cy="18" r="5" fill="#27c93f"/>
<text x="{LARGURA / 2}" y="22" text-anchor="middle" fill="{APAGADO}" style="font-size:11px">neofetch</text>
{''.join(linhas)}
{paleta}
</svg>
"""
    SAIDA.write_text(svg, encoding="utf-8")
    print(f"gravado {SAIDA.name}")


if __name__ == "__main__":
    main()
