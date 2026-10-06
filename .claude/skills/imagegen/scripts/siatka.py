#!/usr/bin/env python3
"""Kontrola kompozycji: nakłada siatkę trójpodziału na wygenerowane obrazy i składa je obok siebie.

Po co: ocena „na oko” myli; z siatką od razu widać, czy obiekt stoi na przecięciu linii, gdzie leży
horyzont i czy pusta przestrzeń ma zadany rozmiar. Wynik obejrzyj narzędziem Read.

  siatka.py a.png b.png c.png -o porownanie.jpg [--etykiety "A sam opis" "B nazwy technik" "C geometria"]
"""
import argparse

from PIL import Image, ImageDraw

SZER = 620


def kafel(sciezka, etykieta):
    im = Image.open(sciezka).convert('RGB')
    w, h = im.size
    im = im.resize((SZER, int(h * SZER / w)))
    d = ImageDraw.Draw(im)
    W, H = im.size
    for k in (1, 2):
        d.line([(W * k / 3, 0), (W * k / 3, H)], fill=(0, 255, 255), width=1)
        d.line([(0, H * k / 3), (W, H * k / 3)], fill=(0, 255, 255), width=1)
    if etykieta:
        d.rectangle([0, 0, W, 24], fill=(0, 0, 0))
        d.text((8, 5), etykieta, fill=(255, 255, 255))
    return im


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('obrazy', nargs='+')
    p.add_argument('--etykiety', nargs='*', default=[])
    p.add_argument('-o', '--wyjscie', default='porownanie_siatka.jpg')
    a = p.parse_args()
    kafle = [kafel(s, a.etykiety[i] if i < len(a.etykiety) else s.rsplit('/', 1)[-1]) for i, s in enumerate(a.obrazy)]
    H = max(k.size[1] for k in kafle)
    arkusz = Image.new('RGB', (SZER * len(kafle) + 10 * (len(kafle) - 1), H), (30, 30, 30))
    for i, k in enumerate(kafle):
        arkusz.paste(k, (i * (SZER + 10), 0))
    arkusz.save(a.wyjscie, quality=88)
    print(a.wyjscie)


if __name__ == '__main__':
    main()
