# src/match_cli.py
from pathlib import Path
import json
import typer
from rich import print
from src.scraper.sofascore_fc import SofaClient

def main(
    match: str = typer.Argument(..., help="Id del partido o URL canónica con '#id:<num>'"),
    out: Path = typer.Option("data/raw_event.json", "--out", "-o", help="Ruta del JSON bruto"),
):
    """
    D01 — Obtener evento bruto desde Sofascore (ScraperFC.get_match_dict) y guardarlo.
    Ejemplos:
      py -m src.match_cli 14566650 --out "data\\raw\\event_14566650.json"
      python -m src.match_cli "https://.../UHsrgb#id:14566650" -o "data\\raw\\event_14566650.json"
    """
    c = SofaClient()

    # Wrapper FASE 0: acepta id numérico o URL con '#id:'
    get_event = getattr(c, "event_from_match", None) or getattr(c, "event_from_url", None)
    if not callable(get_event):
        raise RuntimeError("SofaClient necesita event_from_match o event_from_url.")

    event = get_event(match)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")

    # Nota DX: si vienes con URL sin '#id:', ScraperFC 3.3.4 no extrae el id.
    print(f"[green]OK[/green] - Evento guardado en {out}")

if __name__ == "__main__":
    # Modo comando único (evita el problema de subcomandos)
    typer.run(main)
