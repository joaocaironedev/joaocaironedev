"""Baixa o grafico publico de contribuicoes do GitHub (sem token) e grava data/contributions.json.

So usa a biblioteca padrao do Python, para a Action diaria nao precisar instalar nada.
"""
import datetime as dt
import json
import os
import re
import urllib.request
from pathlib import Path

USUARIO = os.environ.get("GH_USER", "joaocaironedev")
URL = f"https://github.com/users/{USUARIO}/contributions"
RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "data" / "contributions.json"


def baixar() -> str:
    req = urllib.request.Request(URL, headers={"User-Agent": "profile-readme-heatmap"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def ler_dias(html: str) -> list[dict]:
    celulas = {}
    for td in re.finditer(r"<td\b[^>]*ContributionCalendar-day[^>]*>", html):
        tag = td.group(0)
        data = re.search(r'data-date="([\d-]+)"', tag)
        nivel = re.search(r'data-level="(\d)"', tag)
        ident = re.search(r'id="([^"]+)"', tag)
        if data and nivel and ident:
            celulas[ident.group(1)] = {"date": data.group(1), "level": int(nivel.group(1)), "count": 0}
    for tip in re.finditer(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        cel = celulas.get(tip.group(1))
        num = re.match(r"\s*([\d,]+) contributions?", tip.group(2))
        if cel and num:
            cel["count"] = int(num.group(1).replace(",", ""))
    return sorted(celulas.values(), key=lambda d: d["date"])


def estatisticas(dias: list[dict]) -> dict:
    total = sum(d["count"] for d in dias)
    maior = atual = corrida = 0
    for d in dias:
        corrida = corrida + 1 if d["count"] > 0 else 0
        maior = max(maior, corrida)
    # sequencia atual: conta de tras para frente; hoje zerado nao quebra (o dia ainda nao acabou)
    hoje = dt.date.today().isoformat()
    for i, d in enumerate(reversed(dias)):
        if d["count"] > 0:
            atual += 1
        elif i == 0 and d["date"] >= hoje:
            continue
        else:
            break
    melhor = max(dias, key=lambda d: d["count"]) if dias else None
    meses: dict[str, int] = {}
    for d in dias:
        meses[d["date"][:7]] = meses.get(d["date"][:7], 0) + d["count"]
    return {
        "total": total,
        "current_streak": atual,
        "longest_streak": maior,
        "best_day": melhor,
        "active_days": sum(1 for d in dias if d["count"] > 0),
        "monthly": meses,
    }


def main() -> None:
    dias = ler_dias(baixar())
    if not dias:
        raise SystemExit("Nenhum dia encontrado: o GitHub mudou o formato da pagina?")
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    dados = {"user": USUARIO, "days": dias, "stats": estatisticas(dias)}
    SAIDA.write_text(json.dumps(dados, indent=1, ensure_ascii=False), encoding="utf-8")
    s = dados["stats"]
    print(f"{len(dias)} dias, {s['total']} contribuicoes, sequencia atual {s['current_streak']}, maior {s['longest_streak']}")


if __name__ == "__main__":
    main()
