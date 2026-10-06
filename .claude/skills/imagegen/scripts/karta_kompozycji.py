#!/usr/bin/env python3
"""Karta kompozycji: szkic układu kadru do podania generatorowi jako obraz referencyjny.

Odpowiednik przezroczystej karty ze złotą proporcją, którą fotograf przykłada do sceny: model dostaje
gotową geometrię (horyzont, linie prowadzące, miejsce obiektu, pustą przestrzeń) i się jej trzyma.
Sprawdzone 2026-10-06: szkic jako referencja dał najdokładniejsze trafienie kompozycji (lepsze niż
sam opis geometrii w tekście, a nazwy technik w prompcie nie dawały nic).

Prompt do generatora MUSI zawierać zdanie w rodzaju:
  "Use the attached layout sketch ONLY as a composition guide (...). Do not draw any lines, grid,
   marks or text from the sketch."

Przykłady:
  karta_kompozycji.py trojpodzial --punkt prawy-dol --pusta lewa -o karta.png
  karta_kompozycji.py punkt-zbiegu --punkt prawy --horyzont dol -o karta.png
  karta_kompozycji.py symetria | rama | spirala | centrum --aspect 9:16 -o karta.png
"""
import argparse
import math

from PIL import Image, ImageDraw

BIALY, SZARY, OBIEKT, PUSTE = (255, 255, 255), (70, 70, 70), (255, 140, 0), (40, 40, 40)
ASPEKTY = {'16:9': (1672, 941), '9:16': (941, 1672), '1:1': (1254, 1254), '4:3': (1448, 1086), '3:4': (1086, 1448), '21:9': (1920, 823)}


def siatka(d, w, h):
    for k in (1, 2):
        d.line([(w * k / 3, 0), (w * k / 3, h)], fill=SZARY, width=2)
        d.line([(0, h * k / 3), (w, h * k / 3)], fill=SZARY, width=2)


def obiekt(d, x, y, r):
    """Pomarańczowy znacznik = główny obiekt (osoba, produkt, punkt skupienia)."""
    d.ellipse([x - r, y - r, x + r, y + r], fill=OBIEKT)


def y_horyzontu(h, gdzie):
    return {'dol': h * 2 / 3, 'gora': h / 3, 'srodek': h / 2}.get(gdzie)


def trojpodzial(d, w, h, a):
    kol = 2 / 3 if 'prawy' in a.punkt else 1 / 3
    wie = 2 / 3 if 'dol' in a.punkt else 1 / 3
    if a.pusta in ('lewa', 'prawa', 'gora'):  # zacieniony obszar = pusta przestrzeń (np. na tytuł)
        box = {'lewa': [0, 0, w * 0.55, h], 'prawa': [w * 0.45, 0, w, h], 'gora': [0, 0, w, h * 0.55]}[a.pusta]
        d.rectangle(box, fill=PUSTE)
        d.text((box[0] + 30, box[1] + 30), 'EMPTY / NEGATIVE SPACE', fill=(130, 130, 130))
    hy = y_horyzontu(h, a.horyzont)
    if hy:
        d.line([(0, hy), (w, hy)], fill=BIALY, width=6)
    obiekt(d, w * kol, h * wie, min(w, h) * 0.045)


def punkt_zbiegu(d, w, h, a):
    hy = y_horyzontu(h, a.horyzont or 'dol') or h * 2 / 3
    vx = w * {'lewy': 1 / 3, 'prawy': 2 / 3}.get(a.punkt.split('-')[0], 1 / 2)
    d.line([(0, hy), (w, hy)], fill=BIALY, width=6)
    for x0 in (0, w):  # dwie linie prowadzące z dolnych rogów do punktu zbiegu
        d.line([(x0, h), (vx, hy)], fill=BIALY, width=6)
    obiekt(d, vx, hy + min(w, h) * 0.05, min(w, h) * 0.02)


def symetria(d, w, h, a):
    d.line([(w / 2, 0), (w / 2, h)], fill=BIALY, width=6)
    for x0 in (0, w):
        d.line([(x0, h), (w / 2, h * 0.45)], fill=BIALY, width=4)
    obiekt(d, w / 2, h * 0.55, min(w, h) * 0.03)


def rama(d, w, h, a):
    m = min(w, h) * 0.14
    d.rectangle([0, 0, w, h], fill=PUSTE)
    d.rounded_rectangle([m, m, w - m, h - m], radius=int(m * 1.2), fill=(0, 0, 0), outline=BIALY, width=8)
    d.text((40, 40), 'FOREGROUND FRAME (dark: window, arch, doorway, foliage)', fill=(150, 150, 150))
    obiekt(d, w * 0.6, h * 0.6, min(w, h) * 0.04)


def centrum(d, w, h, a):
    d.line([(w * 0.4, 0), (w * 0.4, h)], fill=BIALY, width=4)
    d.line([(w * 0.6, 0), (w * 0.6, h)], fill=BIALY, width=4)
    obiekt(d, w / 2, h / 2, min(w, h) * 0.06)


def spirala(d, w, h, a):
    """Złota spirala z kwadratów Fibonacciego, liczona w prawdziwym złotym prostokącie (1 × 1/φ)
    i dopiero potem rozciągnięta na kadr; w kadrze pionowym obrócona. Oko spirali = miejsce obiektu."""
    phi = (1 + 5 ** 0.5) / 2
    pion = h > w
    # złoty prostokąt poziomy (0..1, 0..1/φ) → piksele kadru (w pionie: zamiana osi)
    m = (lambda x, y: (y * phi * w, x * h)) if pion else (lambda x, y: (x * w, y * phi * h))
    x0, y0, bw, bh = 0.0, 0.0, 1.0, 1 / phi
    for i in range(10):
        k = i % 4
        if k == 0:   # kwadrat po lewej, łuk od lewego dołu do prawej góry
            s = bh; kw = (x0, y0, x0 + s, y0 + s); c = (x0 + s, y0 + s); kat = (180, 270); x0 += s; bw -= s
        elif k == 1:  # kwadrat u góry
            s = bw; kw = (x0, y0, x0 + s, y0 + s); c = (x0, y0 + s); kat = (270, 360); y0 += s; bh -= s
        elif k == 2:  # kwadrat po prawej
            s = bh; kw = (x0 + bw - s, y0, x0 + bw, y0 + s); c = (x0 + bw - s, y0); kat = (0, 90); bw -= s
        else:         # kwadrat na dole
            s = bw; kw = (x0, y0 + bh - s, x0 + s, y0 + bh); c = (x0 + s, y0 + bh - s); kat = (90, 180); bh -= s
        rogi = [m(kw[0], kw[1]), m(kw[2], kw[1]), m(kw[2], kw[3]), m(kw[0], kw[3])]
        d.polygon(rogi, outline=SZARY)
        luk = [m(c[0] + s * math.cos(math.radians(t)), c[1] + s * math.sin(math.radians(t)))
               for t in [kat[0] + (kat[1] - kat[0]) * j / 32 for j in range(33)]]
        d.line(luk, fill=BIALY, width=6)
    ox, oy = m(x0 + bw / 2, y0 + bh / 2)
    obiekt(d, ox, oy, min(w, h) * 0.035)


UKLADY = {'trojpodzial': trojpodzial, 'punkt-zbiegu': punkt_zbiegu, 'symetria': symetria, 'rama': rama, 'centrum': centrum, 'spirala': spirala}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('uklad', choices=UKLADY)
    p.add_argument('--aspect', default='16:9', choices=ASPEKTY)
    p.add_argument('--punkt', default='prawy-dol', help='lewy-gora | lewy-dol | prawy-gora | prawy-dol (trojpodzial); lewy | srodek | prawy (punkt-zbiegu)')
    p.add_argument('--horyzont', default=None, choices=['dol', 'gora', 'srodek'])
    p.add_argument('--pusta', default=None, choices=['lewa', 'prawa', 'gora'], help='obszar pustej przestrzeni (np. na tytuł)')
    p.add_argument('-o', '--wyjscie', default='karta_kompozycji.png')
    a = p.parse_args()
    w, h = ASPEKTY[a.aspect]
    im = Image.new('RGB', (w, h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    siatka(d, w, h)
    UKLADY[a.uklad](d, w, h, a)
    im.save(a.wyjscie)
    print(a.wyjscie)


if __name__ == '__main__':
    main()
