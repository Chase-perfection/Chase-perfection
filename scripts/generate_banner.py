#!/usr/bin/env python3
"""
Genere banner.svg : une fenetre terminal qui "tape" une petite sequence de
commandes, ligne par ligne, avec un curseur qui clignote a la fin.

Aucune donnee reseau : le banner est statique (il ne change que si tu edites
le bloc LINES ci-dessous).
"""

from html import escape

# ============================ CONFIG (a personnaliser) ============================
USER  = "chase-perfection"
TITLE = "~/profile"

# Sequence "tapee". Type "cmd"  -> ligne de commande ($ ...) ;  "out" -> sortie.
LINES = [
    ("cmd", "whoami"),
    ("out", "Chase-perfection — cybersécurité & automatisation"),
    ("cmd", "cat stack.txt"),
    ("out", "Python · Bash · IA · Linux · VS Code"),
    ("cmd", "echo $STATUS"),
    ("out", "online · coding since 2020 · toujours en train de builder"),
]
# ================================================================================

# --- Couleurs (theme GitHub dark) ---
BG      = "#0d1117"
BORDER  = "#30363d"
FG      = "#c9d1d9"
DIM     = "#8b949e"
ACCENT  = "#39d353"
CYAN    = "#58a6ff"
RED     = "#ff5f56"
YELLOW  = "#ffbd2e"
GREEN   = "#27c93f"

# --- Geometrie ---
FONT    = "ui-monospace, 'SF Mono', 'DejaVu Sans Mono', Consolas, monospace"
FS      = 15
CHAR_W  = 9.0          # largeur approx. d'un caractere a 15px
PADX    = 22
TOP     = 50           # sous la barre de titre
LINE_H  = 27
width   = 720

# Duree de frappe par caractere (secondes) et pause entre les lignes.
PER_CHAR = 0.045
GAP      = 0.35


def line_text(kind, text):
    """Retourne (texte_brut_pour_mesure, contenu_svg_tspans)."""
    if kind == "cmd":
        raw = "$ " + text
        svg = (f'<tspan fill="{ACCENT}" font-weight="600">$ </tspan>'
               f'<tspan fill="{FG}">{escape(text)}</tspan>')
    else:
        raw = text
        svg = f'<tspan fill="{DIM}">{escape(text)}</tspan>'
    return raw, svg


parts = []
n_rows = len(LINES)
height = TOP + n_rows * LINE_H + 22

parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
    f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="{FS}">'
)

# Styles : effet machine a ecrire (clip qui se deroule) + curseur clignotant.
parts.append(f'''<style>
  .type {{ transform: scaleX(0); transform-box: fill-box; transform-origin: left;
           animation: type var(--d) steps(var(--n)) forwards; animation-delay: var(--t); }}
  @keyframes type {{ to {{ transform: scaleX(1); }} }}
  .cursor {{ opacity: 0; animation: blink 1s steps(1) infinite; animation-delay: var(--t); }}
  @keyframes blink {{ 0%,49% {{ opacity: 1; }} 50%,100% {{ opacity: 0; }} }}
</style>''')

# Fond + bordure (fenetre terminal)
parts.append(
    f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="10" '
    f'fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
)
# Barre de titre
parts.append(f'<rect x="1" y="1" width="{width-2}" height="34" rx="10" fill="#161b22"/>')
parts.append(f'<rect x="1" y="20" width="{width-2}" height="15" fill="#161b22"/>')
for i, c in enumerate((RED, YELLOW, GREEN)):
    parts.append(f'<circle cx="{22+i*20}" cy="18" r="6" fill="{c}"/>')
parts.append(
    f'<text x="{width/2}" y="23" text-anchor="middle" fill="{DIM}" font-size="13">'
    f'{escape(USER)}: {escape(TITLE)}</text>'
)

# Lignes tapees les unes apres les autres.
t = 0.0                         # instant de depart de la ligne courante
last_end_x = PADX
last_y = TOP
for i, (kind, text) in enumerate(LINES):
    raw, svg = line_text(kind, text)
    n = max(1, len(raw))
    dur = round(n * PER_CHAR, 3)
    y = TOP + i * LINE_H
    parts.append(
        f'<g class="type" style="--n:{n}; --d:{dur}s; --t:{t:.3f}s">'
        f'<text x="{PADX}" y="{y}" xml:space="preserve">{svg}</text></g>'
    )
    t = round(t + dur + GAP, 3)
    last_end_x = PADX + n * CHAR_W
    last_y = y

# Curseur clignotant a la fin de la derniere ligne (apparait quand tout est tape).
parts.append(
    f'<rect class="cursor" x="{last_end_x+2:.0f}" y="{last_y-13}" width="9" height="17" '
    f'fill="{ACCENT}" style="--t:{t:.3f}s"/>'
)

parts.append('</svg>')

with open("banner.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(parts))

print("banner.svg genere.")
