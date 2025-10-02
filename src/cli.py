# src/cli.py
import json
from pathlib import Path
import typer
from rich import print
from src.scraper.sofascore_fc import SofaClient
from src.mapping.sofa_mapper_fc import map_event_to_contract
from src.models.schemas import ShotsResponse

app = typer.Typer(help="Shots Extractor CLI")

@app.command("scrape-url")
def scrape_url(url: str, out: str = "data/raw_event.json"):
    """Obtiene el evento bruto desde una URL de SofaScore (ScraperFC)."""
    c = SofaClient()
    event = c.event_from_url(url)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]OK[/green] - Evento guardado en {out}")

if __name__ == "__main__":
    app()
