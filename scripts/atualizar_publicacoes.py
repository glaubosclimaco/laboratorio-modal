#!/usr/bin/env python3
"""Atualiza publicacoes.json a partir da OpenAlex (ORCID do coordenador)."""

import json
import urllib.request
from datetime import date
from pathlib import Path

AUTHOR_ID = "A5004734066"
ORCID = "0000-0002-1357-1318"
SCHOLAR = "https://scholar.google.com.br/citations?user=w1d8zboAAAAJ"
MAILTO = "francisco.glaubos@ufma.br"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publicacoes.json"


def get(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "laboratorio-modal/1.0 (mailto:%s)" % MAILTO},
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.load(resp)


def venue(work):
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    return src.get("display_name") or ""


def main():
    author = get(
        "https://api.openalex.org/authors/%s?mailto=%s" % (AUTHOR_ID, MAILTO)
    )
    data = get(
        "https://api.openalex.org/works"
        "?filter=author.id:%s&sort=cited_by_count:desc&per-page=10"
        "&select=id,doi,display_name,publication_year,cited_by_count,"
        "primary_location,authorships&mailto=%s" % (AUTHOR_ID, MAILTO)
    )
    works = []
    for work in data.get("results") or []:
        works.append(
            {
                "title": work.get("display_name") or "",
                "year": work.get("publication_year"),
                "cites": work.get("cited_by_count") or 0,
                "venue": venue(work),
                "url": work.get("doi") or "",
                "authors": [
                    a["author"]["display_name"]
                    for a in (work.get("authorships") or [])
                    if a.get("author")
                ],
            }
        )
    payload = {
        "updated": date.today().isoformat(),
        "source": "OpenAlex",
        "author_id": AUTHOR_ID,
        "orcid": ORCID,
        "scholar": SCHOLAR,
        "works_count": author.get("works_count"),
        "cited_by_count": author.get("cited_by_count"),
        "h_index": (author.get("summary_stats") or {}).get("h_index"),
        "works": works,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("atualizado", OUT, "trabalhos", len(works))


if __name__ == "__main__":
    main()
