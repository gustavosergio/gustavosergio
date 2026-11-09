"""Gera um cartão SVG com dados públicos, sem dependências externas."""

import json
import os
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen


def fetch(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-profile-statistics",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GH_TOKEN']}"
    with urlopen(Request(f"https://api.github.com/{path}", headers=headers), timeout=30) as response:
        return json.load(response)


owner = os.environ.get("PROFILE_OWNER", "gustavosergio")
profile = fetch(f"users/{owner}")
repos = []
page = 1
while True:
    batch = fetch(f"users/{owner}/repos?type=owner&per_page=100&page={page}")
    repos.extend(repo for repo in batch if not repo["private"] and not repo["fork"])
    if len(batch) < 100:
        break
    page += 1

languages = Counter(repo["language"] for repo in repos if repo["language"])
stars = sum(repo["stargazers_count"] for repo in repos)
cards = [("PROJETOS ORIGINAIS", len(repos)), ("ESTRELAS RECEBIDAS", stars), ("SEGUIDORES", profile["followers"])]
updated = datetime.now(timezone.utc).strftime("%d/%m/%Y · %H:%M UTC")
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="270" viewBox="0 0 900 270" role="img" aria-labelledby="title desc">',
    '<title id="title">GitHub em números</title>',
    f'<desc id="desc">{len(repos)} repositórios públicos originais, {stars} estrelas e {profile["followers"]} seguidores. Atualizado em {updated}.</desc>',
    '<rect x="1" y="1" width="898" height="268" rx="18" fill="#111827" stroke="#334155"/>',
    '<g font-family="Segoe UI,Arial,sans-serif">',
    '<text x="32" y="40" fill="#a78bfa" font-size="15" font-weight="600">ATIVIDADE PÚBLICA</text>',
]
for index, (label, value) in enumerate(cards):
    x = 32 + index * 290
    parts.append(f'<text x="{x}" y="98" fill="#f8fafc" font-size="42" font-weight="700">{value}</text>')
    parts.append(f'<text x="{x}" y="126" fill="#94a3b8" font-size="12" letter-spacing="1">{label}</text>')
parts.append('<path d="M32 151H868" stroke="#334155"/>')
language_text = " · ".join(f"{name} ({count})" for name, count in languages.most_common(5)) or "Em construção"
parts.extend([
    '<text x="32" y="179" fill="#22d3ee" font-size="12" letter-spacing="1">LINGUAGENS PRINCIPAIS POR REPOSITÓRIO</text>',
    f'<text x="32" y="207" fill="#e2e8f0" font-size="16">{escape(language_text)}</text>',
    f'<text x="32" y="245" fill="#94a3b8" font-size="11">Sem forks · Dados da API do GitHub · {updated}</text>',
    '</g></svg>',
])
Path("dist").mkdir(exist_ok=True)
Path("dist/stats.svg").write_text("\n".join(parts), encoding="utf-8")
print(f"Estatísticas geradas: {len(repos)} projetos, {stars} estrelas, {len(languages)} linguagens.")
