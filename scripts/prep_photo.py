"""Prepara a foto para o retrato ASCII: tira o fundo (rembg), recorta rosto/ombros e aumenta o contraste.

Uso (uma vez por foto):  python scripts/prep_photo.py foto/original.jpg
Saida: foto/prepped.png (fundo branco, pessoa em tons de cinza). Fica fora do Git.
Parametros do recorte (fracoes da foto): CROP="esq,topo,dir,baixo"
"""
import os
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps
from rembg import remove

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "foto" / "prepped.png"
RECORTE_PADRAO = "0.29,0.15,0.79,0.52"  # cabeca e pescoco desta foto (rosto grande = tracos visiveis)


def main() -> None:
    origem = Path(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "foto" / "original.jpg")
    foto = ImageOps.exif_transpose(Image.open(origem)).convert("RGB")
    w, h = foto.size
    e, t, d, b = (float(v) for v in os.environ.get("CROP", RECORTE_PADRAO).split(","))
    foto = foto.crop((int(e * w), int(t * h), int(d * w), int(b * h)))

    recortada = remove(foto)  # RGBA com o fundo transparente
    alfa = recortada.getchannel("A").filter(ImageFilter.GaussianBlur(1))
    cinza = ImageOps.equalize(recortada.convert("L"), mask=alfa)
    cinza = ImageOps.autocontrast(cinza, cutoff=1)

    fundo = Image.new("L", cinza.size, 255)
    final = Image.composite(cinza, fundo, alfa)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    final.save(SAIDA)
    print(f"gravado {SAIDA.relative_to(RAIZ)} {final.size}")


if __name__ == "__main__":
    main()
