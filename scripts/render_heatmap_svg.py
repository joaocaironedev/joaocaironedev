"""Desenha contrib-heatmap.svg (53 semanas x 7 dias) a partir de data/contributions.json.

Animacao so em CSS dentro do SVG (o GitHub aceita), revela em diagonal uma unica vez.
"""
import datetime as dt
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "contributions.json"
SAIDA = RAIZ / "contrib-heatmap.svg"

CORES = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
FUNDO, BORDA, TEXTO, APAGADO, DESTAQUE = "#0d1117", "#30363d", "#c9d1d9", "#8b949e", "#39d353"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
CEL, PASSO = 12, 15
LARGURA = 860
X0, Y0 = 40, 58


def main() -> None:
    dados = json.loads(ENTRADA.read_text(encoding="utf-8"))
    dias, s = dados["days"], dados["stats"]
    primeiro = dt.date.fromisoformat(dias[0]["date"])
    domingo = primeiro - dt.timedelta(days=(primeiro.weekday() + 1) % 7)

    celulas, rotulos, mes_anterior = [], [], None
    for d in dias:
        data = dt.date.fromisoformat(d["date"])
        semana = (data - domingo).days // 7
        dia_sem = (data.weekday() + 1) % 7
        x, y = X0 + semana * PASSO, Y0 + dia_sem * PASSO
        atraso = (semana + dia_sem) * 0.018
        titulo = f"{d['count']} em {data.strftime('%d/%m/%Y')}"
        celulas.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CEL}" height="{CEL}" rx="2.5" '
            f'fill="{CORES[d["level"]]}" style="animation-delay:{atraso:.3f}s"><title>{titulo}</title></rect>'
        )
        if dia_sem == 0 and data.month != mes_anterior and data.day <= 7:
            rotulos.append(f'<text x="{x}" y="{Y0 - 8}" class="m">{MESES[data.month - 1]}</text>')
            mes_anterior = data.month

    sem_lbl = "".join(
        f'<text x="{X0 - 10}" y="{Y0 + i * PASSO + 10}" class="m" text-anchor="end">{n}</text>'
        for i, n in ((1, "seg"), (3, "qua"), (5, "sex"))
    )
    y_leg = Y0 + 7 * PASSO + 14
    legenda = "".join(
        f'<rect x="{LARGURA - 150 + i * 16}" y="{y_leg}" width="{CEL}" height="{CEL}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(CORES)
    )
    melhor = s.get("best_day") or {"count": 0, "date": dias[-1]["date"]}
    melhor_txt = dt.date.fromisoformat(melhor["date"]).strftime("%d/%m")
    y_rod = y_leg + 44
    rodape = [
        ("total no ano", s["total"]),
        ("dias ativos", s["active_days"]),
        ("sequência atual", f'{s["current_streak"]} d'),
        ("maior sequência", f'{s["longest_streak"]} d'),
        ("melhor dia", f'{melhor["count"]} ({melhor_txt})'),
    ]
    bloco = (LARGURA - 2 * X0 + 30) / len(rodape)
    stats = "".join(
        f'<g class="f" style="animation-delay:{1.6 + i * 0.12:.2f}s">'
        f'<text x="{X0 - 16 + i * bloco}" y="{y_rod}" class="v">{v}</text>'
        f'<text x="{X0 - 16 + i * bloco}" y="{y_rod + 18}" class="m">{k}</text></g>'
        for i, (k, v) in enumerate(rodape)
    )
    altura = y_rod + 42
    hoje = dt.date.today().strftime("%d/%m/%Y")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{altura}" viewBox="0 0 {LARGURA} {altura}" role="img" aria-label="Contribuições de {dados['user']} no último ano">
<style>
text{{font-family:'JetBrains Mono','Fira Code',Consolas,monospace}}
.m{{font-size:11px;fill:{APAGADO}}}
.v{{font-size:17px;font-weight:700;fill:{DESTAQUE}}}
.t{{font-size:13px;fill:{TEXTO}}}
.c{{opacity:0;animation:cai .35s ease-out forwards}}
.f{{opacity:0;animation:aparece .5s ease-out forwards}}
@keyframes cai{{from{{opacity:0;transform:translateY(-6px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes aparece{{to{{opacity:1}}}}
</style>
<rect x="0.5" y="0.5" width="{LARGURA - 1}" height="{altura - 1}" rx="10" fill="{FUNDO}" stroke="{BORDA}"/>
<circle cx="20" cy="18" r="5" fill="#ff5f56"/><circle cx="38" cy="18" r="5" fill="#ffbd2e"/><circle cx="56" cy="18" r="5" fill="#27c93f"/>
<text x="{LARGURA / 2}" y="22" class="m" text-anchor="middle">contribuicoes.sh — atualizado em {hoje}</text>
{''.join(rotulos)}{sem_lbl}
{''.join(celulas)}
<text x="{LARGURA - 158}" y="{y_leg + 10}" class="m" text-anchor="end">menos</text>{legenda}
<text x="{LARGURA - 150 + 5 * 16 + 4}" y="{y_leg + 10}" class="m">mais</text>
<line x1="{X0 - 16}" y1="{y_rod - 26}" x2="{LARGURA - 20}" y2="{y_rod - 26}" stroke="{BORDA}"/>
{stats}
</svg>
"""
    SAIDA.write_text(svg, encoding="utf-8")
    print(f"gravado {SAIDA.name} ({len(dias)} dias)")


if __name__ == "__main__":
    main()
