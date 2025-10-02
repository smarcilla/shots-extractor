# src/cli.py
from pathlib import Path
import json, typer
from rich import print
from src.scraper.sofascore_fc import SofaClient

def main(
    url: str = typer.Argument(..., help="URL de partido en SofaScore"),
    out: Path = typer.Option("data/raw_event.json", "--out", "-o", help="Ruta del JSON bruto"),
):
    c = SofaClient()
    event = c.event_from_url(url)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]OK[/green] - Evento guardado en {out}")

if __name__ == "__main__":
    typer.run(main)
