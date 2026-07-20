#!/usr/bin/env python3
"""
Genere langs.svg : un histogramme facon neofetch de tes langages les plus
utilises, dont les barres se remplissent a l'affichage.

Donnees reelles via l'API GraphQL GitHub (taille des langages sur tes depots).
  - En local (test)     : sans token -> jeu de donnees factice.
  - Dans GitHub Actions : le token est fourni automatiquement (voir le workflow).

Variables d'environnement :
  GH_TOKEN : jeton GitHub
  GH_LOGIN : ton pseudo GitHub
"""

import os
import json
import urllib.request

LOGIN = os.environ.get("GH_LOGIN", "Chase-perfection")
TOKEN = os.environ.get("GH_TOKEN")

# --- Couleurs (theme GitHub dark) ---
BG      = "#0d1117"
BORDER  = "#30363d"
TRACK   = "#161b22"
FG      = "#c9d1d9"
DIM     = "#8b949e"
ACCENT  = "#39d353"
RED     = "#ff5f56"
YELLOW  = "#ffbd2e"
GREEN   = "#27c93f"

FONT    = "ui-monospace, 'SF Mono', 'DejaVu Sans Mono', Consolas, monospace"
width   = 720
PADX    = 22
TOP     = 56          # sous la barre de titre
ROW_H   = 34
LABEL_W = 130         # largeur reservee au nom du langage
PCT_W   = 54          # largeur reservee au pourcentage
BAR_H   = 12
TOP_N   = 6           # nombre de langages affiches

# Couleur de secours si l'API ne fournit pas de couleur pour un langage.
FALLBACK = "#8b949e"


def fetch_languages(login, token):
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          nodes {
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges { size node { name color } }
            }
          }
        }
      }
    }"""
    payload = json.dumps({"query": query, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": login,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise RuntimeError(data["errors"])

    totals, colors = {}, {}
    for repo in data["data"]["user"]["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            totals[name] = totals.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"] or FALLBACK
    return totals, colors


def mock_languages():
    totals = {"Python": 52000, "JavaScript": 28000, "Shell": 15000,
              "HTML": 9000, "Dockerfile": 5000, "CSS": 3000}
    colors = {"Python": "#3572A5", "JavaScript": "#f1e05a", "Shell": "#89e051",
              "HTML": "#e34c26", "Dockerfile": "#384d54", "CSS": "#563d7c"}
    return totals, colors


def build_svg(totals, colors):
    items = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:TOP_N]
    grand = sum(v for _, v in items) or 1

    n = len(items)
    height = TOP + n * ROW_H + PADX
    bar_x = PADX + LABEL_W
    bar_full = width - bar_x - PCT_W - PADX

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="14">'
    ]
    parts.append('''<style>
      .fill { transform: scaleX(0); transform-box: fill-box; transform-origin: left;
              animation: grow 1s cubic-bezier(.2,.8,.2,1) forwards; }
      @keyframes grow { to { transform: scaleX(1); } }
      .row { opacity:0; animation: fade .4s ease forwards; }
      @keyframes fade { to { opacity:1; } }
    </style>''')

    # Fenetre + barre de titre
    parts.append(f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="10" '
                 f'fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>')
    parts.append(f'<rect x="1" y="1" width="{width-2}" height="34" rx="10" fill="{TRACK}"/>')
    parts.append(f'<rect x="1" y="20" width="{width-2}" height="15" fill="{TRACK}"/>')
    for i, c in enumerate((RED, YELLOW, GREEN)):
        parts.append(f'<circle cx="{22+i*20}" cy="18" r="6" fill="{c}"/>')
    parts.append(f'<text x="{width/2}" y="23" text-anchor="middle" fill="{DIM}" '
                 f'font-size="13">{LOGIN} — top langages</text>')

    for i, (name, size) in enumerate(items):
        pct = size / grand * 100
        y = TOP + i * ROW_H
        color = colors.get(name, FALLBACK)
        delay = 0.15 + i * 0.12
        w = max(2, bar_full * pct / 100)
        text_y = y + BAR_H
        parts.append(f'<g class="row" style="animation-delay:{delay:.2f}s">')
        # Nom du langage
        parts.append(f'<text x="{PADX}" y="{text_y}" fill="{FG}">{name}</text>')
        # Piste de la barre
        parts.append(f'<rect x="{bar_x}" y="{y}" width="{bar_full:.1f}" height="{BAR_H}" '
                     f'rx="{BAR_H/2:.0f}" fill="{TRACK}" stroke="{BORDER}" stroke-width="0.5"/>')
        # Remplissage anime
        parts.append(f'<rect class="fill" x="{bar_x}" y="{y}" width="{w:.1f}" height="{BAR_H}" '
                     f'rx="{BAR_H/2:.0f}" fill="{color}" '
                     f'style="animation-delay:{delay:.2f}s"/>')
        # Pourcentage
        parts.append(f'<text x="{width-PADX}" y="{text_y}" text-anchor="end" fill="{DIM}">'
                     f'{pct:.1f}%</text>')
        parts.append('</g>')

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    if TOKEN:
        try:
            totals, colors = fetch_languages(LOGIN, TOKEN)
            if not totals:
                raise RuntimeError("aucun langage renvoye")
            print(f"Langages reels recuperes pour {LOGIN} ({len(totals)} langages).")
        except Exception as e:
            print(f"Echec API ({e}) -> langages factices.")
            totals, colors = mock_languages()
    else:
        print("Pas de GH_TOKEN -> langages factices (mode test local).")
        totals, colors = mock_languages()

    with open("langs.svg", "w", encoding="utf-8") as f:
        f.write(build_svg(totals, colors))
    print("langs.svg genere.")


if __name__ == "__main__":
    main()
