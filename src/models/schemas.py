# src/models/schemas.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel

class Marcador(BaseModel):
    local: int
    visitante: int

class Partido(BaseModel):
    idPartido: str
    fechaISO: str
    local: str
    visitante: str
    marcadorFinal: Marcador

class Disparo(BaseModel):
    minuto: int
    equipo: str                # nombre del equipo, no "local"/"visitante"
    jugador: str
    xG: float
    xGOT: Optional[float] = None
    situacion: Optional[str] = None
    resultado: str
    tipo_disparo: Optional[str] = None

class ShotsResponse(BaseModel):
    partido: Partido
    disparos: List[Disparo]
