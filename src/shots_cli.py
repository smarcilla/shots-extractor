# src/shots_cli.py
from pathlib import Path
import json
import typer
from rich import print
from src.scraper.sofascore_fc import SofaClient

def main(
    match: str = typer.Argument(..., help="Id del partido o URL canónica con '#id:<num>'"),
    out: Path = typer.Option("data/raw_shots.json", "--out", "-o", help="Ruta del JSON de disparos"),
):
    """
    D03 — Obtener disparos con ScraperFC.sofascore.scrape_match_shots(...) y guardarlos (lista de dicts).
    """
    c = SofaClient()
    df = c.shots_df(match)  # pandas.DataFrame (cuando implementes D03)
    records = df.to_dict(orient="records")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]OK[/green] - Disparos guardados en {out} ({len(records)})")

if __name__ == "__main__":
    typer.run(main)
