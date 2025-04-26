import math
from datetime import datetime
from dal import get_player, count_past_matches, get_timeslot
import pandas as pd


SIGMA_LEVEL = 800
SIGMA_HISTORY = 3

def parse_csv_and_clean(df) -> pd.DataFrame:
    """
    Pulisce e filtra un DataFrame CSV in input, estraendo solo i campi rilevanti.
    """
    df = pd.read_csv(df, sep=';', decimal='.')
    print(df.head())

    df.columns = df.iloc[0]
    df = df[1:]

    try:
        df_clean = df[["name", "gender", "PADEL", "email", "phone_number"]].copy()
        df_clean.columns = ["name", "gender", "level", "email", "phone_number"]

        df_clean.dropna(subset=["name", "gender", "level", "email", "phone_number"], inplace=True)
        df_clean["level"] = pd.to_numeric(df_clean["level"], errors="coerce")
        df_clean.dropna(subset=["level"], inplace=True)
        df_clean.reset_index(drop=True, inplace=True)

    except Exception as error:
        raise ValueError(f"Errore durante la pulizia del CSV: {error}\n\nProbabilmente il CSV non ha le intestazioni corrette o i dati non sono formattati come previsto.")

    print(df_clean.head())

    return df_clean





def gaussian(x: float, sigma: float) -> float:
    return math.exp(- (x ** 2) / (2 * sigma ** 2))



def score_players(candidates: list[dict], requester_id: int, orario: datetime) -> list[dict]:
    # TODO: IMPROVE SCORE FUNCTION
    req = get_player(requester_id)
    req_level = req['livello']
    req_slot  = req.get('preferred_slot')
    timeslot = get_timeslot(orario)
    risultato = []

    for p in candidates:
        diff_lvl = p['livello'] - req_level
        lvl_score  = gaussian(diff_lvl, SIGMA_LEVEL)
        hist = count_past_matches(p['id'], orario)
        hist_score = gaussian(hist, SIGMA_HISTORY)
        cand_slot  = p.get('preferred_slot') or get_timeslot(orario)
        slot_score = 1.0 if cand_slot == req_slot else 0.2
        slot_score += (timeslot==cand_slot) * 2.5
        raw = lvl_score * 0.2 + hist_score * 0.1 + slot_score
        risultato.append({**p, 'score': raw})

    return risultato