# src/cli.py
from pathlib import Path
import json
import typer
from rich import print
from src.scraper.sofascore_fc import SofaClient

app = typer.Typer(help="Shots Extractor CLI (FASE 0)")

@app.command("event")
def cmd_event(
    match: str = typer.Argument(..., help="Id del partido o URL SofaScore con '#id:<num>'"),
    out: Path = typer.Option("data/raw_event.json", "--out", "-o", help="Ruta del JSON bruto"),
):
    """
    Guarda el evento bruto de SofaScore (ScraperFC.get_match_dict).
    Ejemplo:
      python -m src.cli event 14566650 --out "data\\raw\\event_14566650.json"
    """
    c = SofaClient()

    # Soporta ambos nombres de método según tu wrapper actual
    get_event = getattr(c, "event_from_match", None) or getattr(c, "event_from_url", None)
    if not callable(get_event):
        raise RuntimeError(
            "No se encontró un método válido en SofaClient: event_from_match/event_from_url."
        )

    event = get_event(match)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]OK[/green] - Evento guardado en {out}")

if __name__ == "__main__":
    app()
