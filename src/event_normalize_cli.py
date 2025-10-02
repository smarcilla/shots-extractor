# src/event_normalize_cli.py
from pathlib import Path
import json
import typer
from rich import print
from src.mapping.sofa_mapper_fc import map_event_to_contract
from src.models.schemas import ShotsResponse

def main(
    raw_file: Path = typer.Argument(..., exists=True, dir_okay=False, help="Ruta al JSON bruto del evento"),
    out_dir: Path = typer.Option(Path("data/matches"), "--out-dir", "-o", help="Directorio de salida"),
):
    """
    D02 — Normaliza un evento bruto al contrato ShotsResponse (FASE 0: partido + disparos = []).
    Ejemplos:
      py -m src.event_normalize_cli data\\raw\\event_14566650.json -o data\\matches
      python -m src.event_normalize_cli "data/raw/event_14566650.json" --out-dir "data/matches"
    """
    # 1) Cargar evento bruto
    event = json.loads(raw_file.read_text(encoding="utf-8"))

    # 2) Mapear -> dict con {partido, disparos: []}
    normalized = map_event_to_contract(event)

    # 3) Validar con Pydantic
    model = ShotsResponse.model_validate(normalized)

    # 4) Persistir con nombre por idPartido
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{model.partido.idPartido}.json"
    out_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[green]OK[/green] - Normalizado guardado en [bold]{out_path}[/bold]")

if __name__ == "__main__":
    # Modo comando único (funciona igual que tu match_cli.py)
    typer.run(main)
