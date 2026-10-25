#!/usr/bin/env python3
"""Genera el arte estático del perfil (assets/*.svg) con estética fsociety.

    python3 scripts/build_art.py

Todo es SVG puro con animaciones SMIL/CSS, sin dependencias externas,
para que GitHub lo sirva tal cual dentro de <img>.
"""
import random
from html import escape
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

RED = "#e3131b"
RED_DIM = "#4a0b0e"
RED_DARK = "#2a0608"
WHITE = "#f2f2f2"
GREY = "#8a8a8a"
GREY_DIM = "#3a3a3a"
BG = "#000000"
MONO = "'JetBrains Mono','Fira Code','SF Mono',Consolas,'DejaVu Sans Mono','Courier New',monospace"
SANS = "Lato,'Helvetica Neue','Segoe UI',Arial,sans-serif"


# ---------------------------------------------------------------- tipografía
# Letras dibujadas como trazos sobre una caja de 100 de alto. Cada trazo se
# pinta dos veces: grueso en rojo y fino en negro encima; así sale la línea
# interior del logo de la serie. Los extremos abiertos del trazo negro se
# alargan para que corte la letra de lado a lado.
STROKE = 24
INLINE = 4.5
P = STROKE / 2  # margen interior para que el trazo no se salga de la caja
EXT = P         # la línea interior llega justo al borde del trazo


def glyphs():
    t = P
    b = 100 - P

    def H(w):
        return [[(t, t), (t, b)], [(w - t, t), (w - t, b)], [(t, 50), (w - t, 50)]], []

    def E(w):
        return [[(w - t, t), (t, t), (t, b), (w - t, b)], [(t, 50), (w - t - 6, 50)]], []

    def L(w):
        return [[(t, t), (t, b), (w - t, b)]], []

    def F(w):
        return [[(w - t, t), (t, t), (t, b)], [(t, 50), (w - t - 8, 50)]], []

    def I(w):
        return [[(w / 2, t), (w / 2, b)]], []

    def N(w):
        return [[(t, b), (t, t), (w - t, b), (w - t, t)]], []

    def O(w):
        r = 22
        x0, x1, y0, y1 = t, w - t, t, b
        d = (f"M{x0 + r} {y0}H{x1 - r}Q{x1} {y0} {x1} {y0 + r}V{y1 - r}Q{x1} {y1} {x1 - r} {y1}"
             f"H{x0 + r}Q{x0} {y1} {x0} {y1 - r}V{y0 + r}Q{x0} {y0} {x0 + r} {y0}Z")
        return [], [d]

    def D(w):
        r = 26
        x0, x1, y0, y1 = t, w - t, t, b
        d = (f"M{x0} {y0}H{x1 - r}Q{x1} {y0} {x1} {y0 + r}V{y1 - r}Q{x1} {y1} {x1 - r} {y1}H{x0}Z")
        return [], [d]

    def R(w):
        r = 18
        x0, x1, y0 = t, w - t, t
        mid = 52
        bowl = (f"M{x0} {mid}H{x1 - r}Q{x1} {mid} {x1} {mid - r}V{y0 + r}Q{x1} {y0} {x1 - r} {y0}H{x0}")
        return [[(x0, b), (x0, y0 - 0.01)], [(x1 - 22, mid), (x1, b)]], [bowl]

    return {
        "H": (H, 74), "E": (E, 66), "L": (L, 62), "O": (O, 80), "F": (F, 64),
        "R": (R, 74), "I": (I, 26), "N": (N, 78), "D": (D, 78), " ": (None, 34),
    }


def _extend(pts, e):
    """Alarga los extremos de una polilínea e unidades."""
    def push(a, b):
        dx, dy = a[0] - b[0], a[1] - b[1]
        n = (dx * dx + dy * dy) ** 0.5 or 1
        return (a[0] + dx / n * e, a[1] + dy / n * e)
    return [push(pts[0], pts[1])] + pts[1:-1] + [push(pts[-1], pts[-2])]


def _poly(pts):
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def word_paths(text, gap=14):
    """Devuelve (paths_rojos, paths_inline, ancho) en unidades de caja 100."""
    g = glyphs()
    red, inner, x = [], [], 0.0
    for ch in text:
        fn, w = g[ch]
        if fn:
            polys, curves = fn(w)
            for pl in polys:
                red.append((x, _poly(pl)))
                inner.append((x, _poly(_extend(pl, EXT))))
            for c in curves:
                red.append((x, c))
                inner.append((x, c))
        x += w + gap
    return red, inner, x - gap


_ids = iter(range(10_000))


def logo(text, x, y, scale, fill=RED, ink=BG, extra=""):
    red, inner, width = word_paths(text)
    cid = f"box{next(_ids)}"
    # el recorte a la caja deja planos los remates en diagonal (R, N)
    s = [f'<g transform="translate({x:.1f} {y:.1f}) scale({scale})" {extra}>',
         f'<clipPath id="{cid}"><rect x="-50" y="0" width="{width + 100:.0f}" height="100"/></clipPath>',
         f'<g clip-path="url(#{cid})">']
    s.append(f'<g fill="none" stroke="{fill}" stroke-width="{STROKE}" stroke-linejoin="round" stroke-linecap="square">')
    s += [f'<path transform="translate({dx:.1f} 0)" d="{d}"/>' for dx, d in red]
    s.append("</g>")
    s.append(f'<g fill="none" stroke="{ink}" stroke-width="{INLINE}" stroke-linejoin="round" stroke-linecap="butt">')
    s += [f'<path transform="translate({dx:.1f} 0)" d="{d}"/>' for dx, d in inner]
    s.append("</g></g></g>")
    return "\n".join(s), width * scale


# ---------------------------------------------------------------- piezas
def hero():
    W, H = 900, 330
    text = "HELLO FRIEND"
    _, _, w = word_paths(text)
    scale = 780 / w
    big_x = (W - w * scale) / 2
    big_y = 92
    small_scale = scale * 0.42
    small_x = (W - w * small_scale) / 2
    small_y = big_y + 100 * scale + 34

    big, _ = logo(text, big_x, big_y, scale)
    small, _ = logo(text, small_x, small_y, small_scale, fill=RED_DIM)

    # glitch: copias desplazadas recortadas en franjas que aparecen un instante
    bands = [(big_y + 8, 18, -14), (big_y + 46, 10, 18), (big_y + 70, 14, -8)]
    glitch = []
    for i, (by, bh, dx) in enumerate(bands):
        glitch.append(f'<clipPath id="g{i}"><rect x="0" y="{by:.1f}" width="{W}" height="{bh}"/></clipPath>')
    glitch_layers = []
    for i, (by, bh, dx) in enumerate(bands):
        copy, _ = logo(text, big_x + dx, big_y, scale, fill=WHITE if i == 1 else RED)
        glitch_layers.append(
            f'<g clip-path="url(#g{i})" opacity="0">{copy}'
            f'<animate attributeName="opacity" values="0;0;1;0;1;0;0" keyTimes="0;0.86;0.87;0.88;0.9;0.91;1" dur="7s" begin="{2.4 + i * 0.03:.2f}s" repeatCount="indefinite"/></g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>hello, friend.</title>
<defs>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" fill-opacity="0.035"/></pattern>
<radialGradient id="glow" cx="50%" cy="45%" r="55%"><stop offset="0" stop-color="{RED}" stop-opacity="0.16"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
<clipPath id="frame"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10"/></clipPath>
{"".join(glitch)}
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{BG}"/>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#glow)">
  <animate attributeName="opacity" values="0;0;1;0.2;1;0.6;1" keyTimes="0;0.1;0.18;0.24;0.3;0.36;1" dur="2.2s" fill="freeze"/>
</rect>
<text x="24" y="34" font-family="{MONO}" font-size="12" fill="{GREY}">eterm##$: <tspan fill="{WHITE}">./fsociety00.dat</tspan></text>
<text x="{W - 24}" y="34" text-anchor="end" font-family="{MONO}" font-size="12" fill="{GREY_DIM}">PID 1337 · ROOT</text>
<g opacity="0">
  <animate attributeName="opacity" values="0;0;1;0.1;1;0.3;1" keyTimes="0;0.1;0.18;0.24;0.3;0.36;1" dur="2.2s" fill="freeze"/>
  {big}
</g>
{"".join(glitch_layers)}
<g opacity="0">
  <set attributeName="opacity" to="1" begin="1.9s" fill="freeze"/>
  {small}
</g>
<text x="{W / 2}" y="{H - 30}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{GREY}" opacity="0">boris@fsociety:~$ <tspan fill="{WHITE}">wake_up --now</tspan>
  <set attributeName="opacity" to="1" begin="2.4s" fill="freeze"/>
</text>
<rect width="{W}" height="{H}" fill="url(#scan)"/>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="none" stroke="{RED}" stroke-opacity="0.35"/>
</svg>
'''


# ---------------------------------------------------------------- máscara
# Máscara de fsociety en un lienzo de 200x200, rellena de código que corre.
def _mirror(d):
    """Refleja un path absoluto (solo comandos M L Q C Z con pares x y) en x=100."""
    out, nums, buf = [], [], ""
    tokens = []
    for ch in d.replace(",", " "):
        if ch.isalpha():
            if buf.strip():
                tokens.append(buf.strip())
            tokens.append(ch)
            buf = " "
        else:
            buf += ch
    if buf.strip():
        tokens.append(buf.strip())
    for t in tokens:
        if t.isalpha():
            out.append(t)
        else:
            vals = [float(v) for v in t.split()]
            for i in range(0, len(vals), 2):
                vals[i] = 200 - vals[i]
            out.append(" ".join(f"{v:g}" for v in vals))
    return "".join(out)


MASK_HALF = [
    # ceja
    "M22 58 C30 34 60 22 90 38 C92 44 88 48 82 46 C62 36 40 42 30 62 Z",
    # ojo
    "M36 80 C48 64 74 62 88 76 C84 92 70 98 58 96 C46 94 38 88 36 80 Z",
    # bigote
    "M100 134 C86 118 66 116 48 126 C36 132 20 130 15 116 C10 102 20 90 32 94 C24 100 26 108 34 108 C46 106 62 90 84 94 C94 96 99 104 100 108 Z",
]
MASK_CENTER = [
    # nariz
    "M95 44 C95 74 90 98 82 116 C88 124 96 122 100 118 C104 122 112 124 118 116 C110 98 105 74 105 44 Z",
    # boca
    "M66 144 C86 160 114 160 134 144 C122 172 78 172 66 144 Z",
]
MASK_LINES = [
    # contorno de mejillas y barbilla
    "M14 120 C18 160 52 194 100 196 C148 194 182 160 186 120",
]
PUPILS = [(64, 80, 5), (136, 80, 5)]


def mask(x, y, size, rows_seed=7, color=WHITE, accent=RED, opacity=1.0, uid="m"):
    rnd = random.Random(rows_seed)
    k = size / 200
    shapes = MASK_HALF + [_mirror(d) for d in MASK_HALF] + MASK_CENTER
    clip = "".join(f'<path d="{d}"/>' for d in shapes)
    rows = []
    alphabet = "0123456789abcdef"
    for i, yy in enumerate(range(20, 200, 6)):
        line = "".join(rnd.choice(alphabet) for _ in range(90))
        dur = 18 + rnd.random() * 14
        rows.append(
            f'<text x="0" y="{yy}" fill="{accent if i % 7 == 3 else color}" fill-opacity="{0.55 + rnd.random() * 0.45:.2f}">{line}{line}'
            f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{90 * 3.6:.0f} 0" dur="{dur:.1f}s" repeatCount="indefinite"/></text>'
        )
    outline = "".join(f'<path d="{d}"/>' for d in shapes + MASK_LINES)
    pupils = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>' for cx, cy, r in PUPILS)
    return f"""<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})" opacity="{opacity}">
<clipPath id="{uid}c">{clip}</clipPath>
<g clip-path="url(#{uid}c)" font-family="{MONO}" font-size="6">{"".join(rows)}</g>
<g fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round">{outline}</g>
<g fill="{color}">{pupils}</g>
</g>"""


def mask_test():
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
<rect width="400" height="400" fill="{BG}"/>
{mask(0, 0, 400)}
</svg>
"""


def readme():
    W, H = 900, 520
    lines = [
        # (y, tipo, contenido)
        ("cmd", "whoami"),
        ("out", f'<tspan fill="{WHITE}">boris</tspan> — cloud &amp; devops engineer · barcelona'),
        ("gap", ""),
        ("cmd", "more readme.txt"),
        ("rule", "------readme.txt------"),
        ("gap", ""),
        ("out", f'Hola, soy <tspan fill="{RED}" font-weight="bold">Boris</tspan>.'),
        ("out", "Me dedico a que lo repetitivo se haga solo:"),
        ("out", "pipelines, contenedores, IaC y nube."),
        ("dim", "Si hay que tocarlo a mano dos veces,"),
        ("dim", "lo automatizo la tercera."),
        ("gap", ""),
        ("kv", ("trabajando", "DevOps @ OCA GLOBAL")),
        ("kv", ("", f'<tspan fill="{GREY}">Ansible · Jenkins · Zabbix · Azure</tspan>')),
        ("kv", ("estudiando", "Ing. Informática @ UOC")),
        ("kv", ("preparando", "AWS Solutions Architect")),
        ("kv", ("rompiendo", "Terraform, K8s y mi homelab")),
        ("gap", ""),
        ("rule", "------readme.txt------"),
    ]
    out, y, t = [], 78, 0.6
    clips = []
    for kind, content in lines:
        if kind == "gap":
            y += 10
            continue
        if kind == "cmd":
            w = 8.43 * (len("eterm##$: ") + len(content))
            cid = f"c{len(clips)}"
            dur = 0.05 * len(content) + 0.2
            clips.append(f'<clipPath id="{cid}"><rect x="28" y="{y - 15}" width="0" height="20"><animate attributeName="width" from="0" to="{w + 4:.1f}" dur="{dur:.2f}s" begin="{t:.2f}s" fill="freeze"/></rect></clipPath>')
            out.append(f'<g clip-path="url(#{cid})"><text x="28" y="{y}"><tspan fill="{RED}">eterm##$: </tspan><tspan fill="{WHITE}">{content}</tspan></text></g>')
            t += dur + 0.3
        else:
            if kind == "out":
                body = f'<text x="28" y="{y}" fill="#c9c9c9">{content}</text>'
            elif kind == "dim":
                body = f'<text x="28" y="{y}" fill="{GREY}">{content}</text>'
            elif kind == "rule":
                body = f'<text x="28" y="{y}" fill="{GREY}">{content}</text>'
            else:
                k, v = content
                body = f'<text x="28" y="{y}"><tspan fill="{RED}">{k}</tspan><tspan x="148" fill="{WHITE}">{v}</tspan></text>'
            out.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>{body}</g>')
            t += 0.07
        y += 23
    cursor_y = y + 4
    out.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
               f'<text x="28" y="{cursor_y}" fill="{RED}">eterm##$:</text>'
               f'<rect x="{28 + 8.43 * 10:.1f}" y="{cursor_y - 14}" width="9" height="17" fill="{WHITE}">'
               f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></rect></g>')

    mx, my, ms = 610, 110, 250
    face = mask(mx, my, ms, uid="rm")
    caption_y = my + ms + 30
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}" font-size="14">
<title>more readme.txt</title>
<defs>{"".join(clips)}
<radialGradient id="rglow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{RED}" stop-opacity="0.10"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{BG}" stroke="{GREY_DIM}"/>
<path d="M1 11a10 10 0 0 1 10-10h878a10 10 0 0 1 10 10v26H1z" fill="#0d0d0d"/>
<line x1="1" y1="37" x2="899" y2="37" stroke="{GREY_DIM}"/>
<circle cx="24" cy="19" r="6" fill="#262626"/><circle cx="46" cy="19" r="6" fill="#262626"/><circle cx="68" cy="19" r="6" fill="{RED}"/>
<text x="450" y="24" text-anchor="middle" font-size="12" fill="{GREY}">eterm — boris@fsociety: ~</text>
{"".join(out)}
<circle cx="{mx + ms / 2}" cy="{my + ms / 2}" r="{ms * 0.75:.0f}" fill="url(#rglow)"/>
<g opacity="0"><animate attributeName="opacity" values="0;1" dur="1.5s" begin="0.3s" fill="freeze"/>{face}</g>
<text x="{mx + ms / 2}" y="{caption_y}" text-anchor="middle" font-size="10" fill="{WHITE}" letter-spacing="1">AUTOMATION INITIATED.</text>
<text x="{mx + ms / 2}" y="{caption_y + 15}" text-anchor="middle" font-size="10" fill="{GREY}">Goodbye, trabajo manual...</text>
</svg>
"""


def manifesto():
    W, H = 900, 500
    cx, cy, r = 450, 232, 205
    row_h, cw = 17, 7.8
    # los bits son "hello friend. " en ASCII, en bloques de 8
    msg = "hello friend. "
    stream = " ".join(f"{ord(c):08b}" for c in msg) + " "
    pos = 0
    # fila -> (palabra izquierda, palabra derecha); * = en rojo
    words = {
        1: ("SEGUIMOS", ""), 2: ("", "DESPLEGANDO."),
        4: ("AUNQUE", "*PROD"), 5: ("", "SE CAIGA."),
        8: ("COMO EL", ""), 9: ("MUNDO QUE", "*AUTOMATIZAMOS,"),
        12: ("VOLVEREMOS", ""), 13: ("A ENCONTRAR", "NUESTRO"),
        15: ("", "*VERDADERO"), 16: ("", "*UPTIME."),
    }
    rnd = random.Random(42)
    rows, blinks = [], []
    n_rows = int(2 * r / row_h)
    for i in range(n_rows):
        y = cy - r + row_h * (i + 0.5)
        dy = y - cy
        half = (r * r - dy * dy) ** 0.5
        n = max(int(2 * half / cw), 0)
        if n < 4:
            continue
        x0 = cx - n * cw / 2
        chars = []
        for _ in range(n):
            chars.append(stream[pos % len(stream)])
            pos += 1
        # media luna roja: dentro de un círculo desplazado y fuera de otro
        segs, cur, cur_red, start = [], "", None, 0
        for j, ch in enumerate(chars):
            x = x0 + j * cw
            inside = (x - (cx - 60)) ** 2 + (y - cy) ** 2 < 190 ** 2
            outside = (x - (cx + 10)) ** 2 + (y - (cy - 20)) ** 2 > 165 ** 2
            red = inside and outside and ch != " "
            if red != cur_red and cur:
                segs.append((start, cur, cur_red))
                cur, start = "", j
            cur_red = red
            cur += ch
        segs.append((start, cur, cur_red))
        delay = 0.2 + i * 0.07
        spans = "".join(
            f'<tspan x="{x0 + st * cw:.1f}" fill="{RED if red else "#d8d8d8"}" fill-opacity="{0.95 if red else 0.75}">{txt.replace(" ", "&#160;")}</tspan>'
            for st, txt, red in segs
        )
        rows.append(f'<text y="{y + 4.5:.1f}" opacity="0">{spans}<set attributeName="opacity" to="1" begin="{delay:.2f}s" fill="freeze"/></text>')
        # un par de bits que parpadean en rojo
        for _ in range(2):
            j = rnd.randrange(n)
            if chars[j] == " ":
                continue
            flip = "1" if chars[j] == "0" else "0"
            b = 2 + rnd.random() * 5
            blinks.append(
                f'<g opacity="0"><rect x="{x0 + j * cw - 0.5:.1f}" y="{y - 7:.1f}" width="{cw + 1}" height="15" fill="{BG}"/>'
                f'<text x="{x0 + j * cw:.1f}" y="{y + 4.5:.1f}" fill="{RED}">{flip}</text>'
                f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.6;0.62;0.8;0.82" dur="{b:.1f}s" begin="{delay + 1:.2f}s" repeatCount="indefinite"/></g>'
            )
        if i in words:
            left, right = words[i]
            for word, anchor, wx in ((left, "end", x0 - 10), (right, "start", x0 + n * cw + 8)):
                if not word:
                    continue
                red = word.startswith("*")
                word = word.lstrip("*")
                rows.append(
                    f'<text x="{wx:.1f}" y="{y + 5:.1f}" text-anchor="{anchor}" font-family="{SANS}" font-weight="900" font-size="15" letter-spacing="2" fill="{RED if red else WHITE}" opacity="0">{word}'
                    f'<set attributeName="opacity" to="1" begin="{delay + 0.6:.2f}s" fill="freeze"/></text>'
                )
    last_y = cy + r + 34
    rows.append(f'<text x="{cx}" y="{last_y}" text-anchor="middle" font-family="{SANS}" font-weight="900" font-size="15" letter-spacing="2" fill="{WHITE}" opacity="0">OTRA VEZ.'
                f'<set attributeName="opacity" to="1" begin="{0.2 + n_rows * 0.07 + 0.8:.2f}s" fill="freeze"/></text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}" font-size="13">
<title>seguimos desplegando.</title>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{BG}"/>
{"".join(rows)}
{"".join(blinks)}
</svg>
"""


def banner():
    W, H = 900, 400
    # máscara gris de fondo, enmarcada como en el cartel de la serie
    fx, fy, fw, fh = 330, 40, 240, 320
    face = mask(fx + 10, fy + 70, 220, rows_seed=3, color="#363636", accent="#4a1416", uid="bn")
    term = [
        (f'<tspan fill="{RED}">eterm##$:</tspan> <tspan fill="#5d6d86">BKUW300PS345672:</tspan> <tspan fill="#cfcfcf">ls</tspan>', 0.3),
        ('<tspan fill="#cfcfcf">fsociety00.dat   readme.txt</tspan>', 0.8),
        (f'<tspan fill="{RED}">eterm##$:</tspan> <tspan fill="#5d6d86">BKUW300PS345672:</tspan> <tspan fill="#cfcfcf">more readme.txt</tspan>', 1.3),
        ('<tspan fill="#9a9a9a">------readme.txt------</tspan>', 1.8),
        ("", 0),
        ('<tspan fill="#cfcfcf">    LEAVE ME HERE</tspan>', 2.1),
        ("", 0),
        ('<tspan fill="#9a9a9a">------readme.txt------</tspan>', 2.3),
    ]
    tl = []
    for i, (txt, t) in enumerate(term):
        if txt:
            tl.append(f'<text x="22" y="{36 + i * 18}" xml:space="preserve" opacity="0">{txt}<set attributeName="opacity" to="1" begin="{t}s" fill="freeze"/></text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}" font-size="12">
<title>nuestra infra ha sido automatizada</title>
<defs>
<linearGradient id="vig" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.55"/></linearGradient>
<clipPath id="bframe"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10"/></clipPath>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="#141414"/>
<g clip-path="url(#bframe)">
<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="6" fill="#1b1b1b" stroke="#232323" stroke-width="3"/>
<rect x="{fx + 14}" y="{fy + 14}" width="{fw - 28}" height="{fh - 28}" rx="4" fill="none" stroke="#202020" stroke-width="2"/>
{face}
{"".join(tl)}
<g opacity="0" font-family="{SANS}" font-size="46" fill="{WHITE}" text-anchor="middle" letter-spacing="1">
  <animate attributeName="opacity" values="0;1;0.3;1;0.6;1" keyTimes="0;0.2;0.3;0.5;0.6;1" dur="1.2s" begin="2.8s" fill="freeze"/>
  <text x="{W / 2}" y="196"><tspan font-weight="300">NUESTRA </tspan><tspan font-weight="900">INFRA</tspan></text>
  <text x="{W / 2}" y="250"><tspan font-weight="300">HA SIDO </tspan><tspan font-weight="900" fill="{RED}">AUTOMATIZADA</tspan></text>
</g>
<rect x="0" y="{H / 2}" width="{W}" height="{H / 2}" fill="url(#vig)"/>
<text x="{W / 2}" y="{H - 22}" text-anchor="middle" font-size="13" fill="{WHITE}" opacity="0">hello friend.<set attributeName="opacity" to="1" begin="4.2s" fill="freeze"/></text>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="none" stroke="#2a2a2a"/>
</svg>
"""


def write(name, svg):
    (ASSETS / name).write_text(svg, encoding="utf-8")
    print("escrito", name)


if __name__ == "__main__":
    random.seed(1337)
    write("hero.svg", hero())
    write("readme.svg", readme())
    write("manifesto.svg", manifesto())
    write("banner.svg", banner())
