#!/usr/bin/env python3
"""
Genere info-card.svg : un panneau facon "neofetch" qui se devoile ligne par ligne.

=> EDITE UNIQUEMENT LE BLOC 'CONFIG' CI-DESSOUS avec tes infos.
Aucune donnee reseau : cette carte est statique (elle ne change que si tu la modifies).
"""

from html import escape

# ============================ CONFIG (a personnaliser) ============================
USER   = "Chase-perfection"          # affiche dans l'en-tete : user@profile
TITLE  = "~"                          # ce qui suit les ":" dans la barre de titre

# Logo ASCII a gauche (garde des lignes de meme largeur pour un rendu propre)
LOGO = r"""
   __
  /  \___
 /       \
 \  o  o  /
  \  __  /
   \____/
"""

# Lignes d'info a droite : (etiquette, valeur). L'ordre = l'ordre d'apparition.
INFO = [
    ("role",    "Consultant en cybersécurité et automatisation des processus"),
    ("Compétence",   "Concevoir et déployer des solutions d'automatisation pour les équipes IT et cybersécurité, en intégrant des technologies d'intelligence artificielle afin d'optimiser les processus, renforcer la sécurité du système d'information et réduire les tâches répétitives."),
    ("editor",  "VS Code / Antigravity / Manus / Claude"),
    ("os",      "Linux  ·  Windows"),
    ("focus",   "AI builder  ·  Open source"),
    ("uptime",  "coding since 2020"),
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
PAD        = 20
LINE_H     = 22
LOGO_X     = PAD
INFO_X     = 200
TOP        = 60          # espace pour la barre de titre
FONT       = "ui-monospace, 'SF Mono', 'DejaVu Sans Mono', Consolas, monospace"

logo_lines = [l for l in LOGO.splitlines() if l.strip("\n")]
n_rows = max(len(logo_lines), len(INFO) + 2)   # +2 : ligne "user@profile" + separateur
height = TOP + n_rows * LINE_H + PAD
width  = 720

parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
    f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="14">'
)

# Styles + keyframes (le fondu ligne par ligne)
parts.append(f'''<style>
  .row {{ opacity:0; animation: appear .5s ease forwards; }}
  @keyframes appear {{
    from {{ opacity:0; transform: translateX(10px); }}
    to   {{ opacity:1; transform: translateX(0);    }}
  }}
  .k {{ fill:{ACCENT}; font-weight:600; }}
  .v {{ fill:{FG}; }}
  .logo {{ fill:{CYAN}; white-space:pre; }}
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
    f'{escape(USER)}@profile: {escape(TITLE)}</text>'
)

# Logo (gauche)
for i, line in enumerate(logo_lines):
    y = TOP + (i + 1) * LINE_H
    delay = i * 0.08
    parts.append(
        f'<text class="row logo" x="{LOGO_X}" y="{y}" xml:space="preserve" '
        f'style="animation-delay:{delay:.2f}s">{escape(line)}</text>'
    )

# En-tete "user@profile" + ligne de separation (droite)
def row(y, delay, content):
    return (f'<g class="row" style="animation-delay:{delay:.2f}s">'
            f'<text x="{INFO_X}" y="{y}">{content}</text></g>')

y0 = TOP + LINE_H
parts.append(row(y0, 0.0,
    f'<tspan class="k">{escape(USER)}</tspan>'
    f'<tspan class="v">@</tspan>'
    f'<tspan fill="{CYAN}">profile</tspan>'))
parts.append(row(y0 + LINE_H, 0.12,
    f'<tspan class="v">{"—" * 22}</tspan>'))

# Lignes d'info
for i, (k, v) in enumerate(INFO):
    y = y0 + (i + 2) * LINE_H
    delay = 0.24 + i * 0.12
    parts.append(row(y, delay,
        f'<tspan class="k">{escape(k)}</tspan>'
        f'<tspan class="v">: {escape(v)}</tspan>'))

parts.append('</svg>')

with open("info-card.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(parts))

print("info-card.svg genere.")
