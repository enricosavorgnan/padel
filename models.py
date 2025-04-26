from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List

class Player(BaseModel):
    id: int | None = None
    nome: str = Field(max_length=100)
    cognome: str = Field(max_length=100)
    sesso: str = Field(regex='^(M|F)$')
    livello: int = Field(ge=0, le=4000)
    preferred_slot: str | None
    email: EmailStr
    telefono: str | None

class Match(BaseModel):
    id: int | None = None
    player_ids: List[int]
    orario: datetime
    created_at: datetime | None = None