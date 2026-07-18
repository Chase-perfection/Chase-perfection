#!/usr/bin/env python3
"""
Genere contrib-heatmap.svg : ton vrai calendrier de contributions (53 semaines),
en cases arrondies qui glissent en diagonale.

Donnees reelles via l'API GraphQL GitHub.
  - En local (test)     : sans token -> jeu de donnees factice.
  - Dans GitHub Actions : le token est fourni automatiquement (voir le workflow).

Variables d'environnement utilisees :
  GH_TOKEN  : jeton GitHub (fourni par l'Action)
  GH_LOGIN  : ton pseudo GitHub
"""

import os
import json
import random
import datetime
import urllib.request

LOGIN = os.environ.get("GH_LOGIN", "Chase-perfection")
TOKEN = os.environ.get("GH_TOKEN")

# --- Couleurs (echelle verte facon GitHub, du vide au tres actif) ---
BG      = "#0d1117"
BORDER  = "#30363d"
EMPTY   = "#161b22"
LEVELS  = ["#0e4429", "#006d32", "#26a641", "#39d353"]  # 4 niveaux non-vides
LABEL   = "#8b949e"

CELL = 12          # taille d'une case
GAP  = 3           # espace entre cases
RX   = 3           # arrondi des coins
PADX = 20
PADY = 34          # espace en haut pour les mois


def fetch_calendar(login, token):
    """Recupere le calendrier reel via GraphQL. Retourne la liste des semaines."""
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays { date contributionCount weekday }
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
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def mock_calendar():
    """Jeu de donnees factice pour tester en local sans token."""
    today = datetime.date.today()
    start = today - datetime.timedelta(weeks=52, days=today.weekday() + 1)
    weeks = []
    d = start
    for _ in range(53):
        days = []
        for wd in range(7):
            days.append({
                "date": d.isoformat(),
                "contributionCount": max(0, int(random.gauss(3, 4))),
                "weekday": wd,
            })
            d += datetime.timedelta(days=1)
        weeks.append({"contributionDays": days})
    return weeks


def level(count):
    if count == 0:
        return None
    if count < 3:
        return LEVELS[0]
    if count < 6:
        return LEVELS[1]
    if count < 10:
        return LEVELS[2]
    return LEVELS[3]


def build_svg(weeks):
    n_weeks = len(weeks)
    width  = PADX * 2 + n_weeks * (CELL + GAP)
    height = PADY + 7 * (CELL + GAP) + 14   # +14 pour la legende

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'font-family="ui-monospace, Consolas, monospace" font-size="10">'
    ]

    # Fenetre / fond
    parts.append(f'<rect width="{width}" height="{height}" rx="10" '
                 f'fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>')

    # Animation : chaque case demarre decalee + transparente, puis glisse en place.
    parts.append('''<style>
      .cell { opacity:0; animation: slide .4s ease forwards; }
      @keyframes slide {
        from { opacity:0; transform: translate(-6px,-6px); }
        to   { opacity:1; transform: translate(0,0);      }
      }
    </style>''')

    # Etiquettes de mois (en haut)
    months = ["Jan","Fev","Mar","Avr","Mai","Jun","Jul","Aou","Sep","Oct","Nov","Dec"]
    last_month = None
    for wi, week in enumerate(weeks):
        first = week["contributionDays"][0]
        m = int(first["date"][5:7])
        if m != last_month:
            x = PADX + wi * (CELL + GAP)
            parts.append(f'<text x="{x}" y="{PADY-16}" fill="{LABEL}">{months[m-1]}</text>')
            last_month = m

    # Les cases
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            di = day["weekday"]
            x = PADX + wi * (CELL + GAP)
            y = PADY + di * (CELL + GAP)
            color = level(day["contributionCount"]) or EMPTY
            delay = (wi + di) * 0.012          # decalage diagonal
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="{RX}" fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{day["date"]}: {day["contributionCount"]}</title></rect>'
            )

    # Legende "Moins ... Plus"
    ly = height - 8
    lx = width - PADX - (len(LEVELS) + 1) * (CELL + 2) - 60
    parts.append(f'<text x="{lx-6}" y="{ly}" fill="{LABEL}" text-anchor="end">Moins</text>')
    for i, c in enumerate([EMPTY] + LEVELS):
        parts.append(f'<rect x="{lx + i*(CELL+2)}" y="{ly-10}" width="{CELL}" height="{CELL}" '
                     f'rx="{RX}" fill="{c}"/>')
    parts.append(f'<text x="{lx + (len(LEVELS)+1)*(CELL+2) + 4}" y="{ly}" fill="{LABEL}">Plus</text>')

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    if TOKEN:
        try:
            weeks = fetch_calendar(LOGIN, TOKEN)
            print(f"Donnees reelles recuperees pour {LOGIN} ({len(weeks)} semaines).")
        except Exception as e:
            print(f"Echec API ({e}) -> donnees factices.")
            weeks = mock_calendar()
    else:
        print("Pas de GH_TOKEN -> donnees factices (mode test local).")
        weeks = mock_calendar()

    svg = build_svg(weeks)
    with open("contrib-heatmap.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("contrib-heatmap.svg genere.")


if __name__ == "__main__":
    main()
