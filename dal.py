import json
from collections import Counter
from datetime import datetime
from db import get_connection

TIME_SLOTS = {
    'MATTINA': (6, 12),
    'POMERIGGIO': (12, 18),
    'SERA': (18, 23)
}

def get_player(player_id: int) -> dict:
    sql = "SELECT * FROM players WHERE id = %s"
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, (player_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row


def fetch_similar_players(req_id: int) -> list[dict]:
    req = get_player(req_id)
    sesso, livello = req['sesso'], req['livello']
    sql = (
        "SELECT * FROM players WHERE sesso = %s AND ABS(livello - %s) <= 1 AND id != %s"
    )
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, (sesso, livello, req_id))
    rows = cur.fetchall()
    if len(rows) < 10:
        sql = (
            "SELECT * FROM players WHERE ABS(livello - %s) <= 2 AND id != %s"
        )
        cur.execute(sql, (livello, req_id))
        rows += cur.fetchall()
    cur.close(); conn.close()
    return rows


def count_past_matches(player_id: int, orario: datetime) -> int:
    slot = get_timeslot(orario)
    start_h, end_h = TIME_SLOTS[slot]
    start = orario.replace(hour=start_h, minute=0, second=0)
    end   = orario.replace(hour=end_h, minute=0, second=0)
    sql = (
        "SELECT COUNT(*) FROM matches "
        "WHERE JSON_CONTAINS(player_ids, %s, '$') "
        "AND orario BETWEEN %s AND %s"
    )
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (json.dumps(player_id), start, end))
    cnt = cur.fetchone()[0]
    cur.close(); conn.close()
    return cnt


def get_timeslot(orario: datetime) -> str:
    h = orario.hour
    for slot, (lo, hi) in TIME_SLOTS.items():
        if lo <= h < hi:
            return slot
    return 'SERA'


def insert_match(orario: datetime, player_ids: list[int]) -> int:
    sql = "INSERT INTO matches (player_ids, orario) VALUES (%s, %s)"
    payload = json.dumps(player_ids)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (payload, orario))
    match_id = cur.lastrowid
    conn.commit()
    cur.close(); conn.close()
    # Aggiorna preferred_slot dei partecipanti
    for pid in player_ids:
        update_player_preferred_slot(pid)
    return match_id


def update_player_preferred_slot(player_id: int) -> None:
    sql = "SELECT orario FROM matches WHERE JSON_CONTAINS(player_ids, %s, '$')"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (json.dumps(player_id),))
    rows = cur.fetchall()
    cur.close(); conn.close()

    slots = [get_timeslot(r[0]) for r in rows]
    if not slots:
        return
    mode = Counter(slots).most_common(1)[0][0]

    upd = "UPDATE players SET preferred_slot = %s WHERE id = %s"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(upd, (mode, player_id))
    conn.commit()
    cur.close(); conn.close()


def player_exists(player_name: str) -> bool:
    """
    Controlla se il giocatore esiste già nel DB.
    """
    conn = get_connection()
    sql = "SELECT COUNT(*) FROM players WHERE nome = %s"

    cur = conn.cursor()
    cur.execute(sql, (player_name,))
    count = cur.fetchone()[0]
    cur.close(); conn.close()
    return count > 0


def insert_player(nome, sesso, livello, email, telefono):
    """
    Inserisce un singolo giocatore nel DB.
    """
    if player_exists(nome):
        print(f"Il giocatore {nome} esiste già nel DB.")
        return False
    try:
        sql = (
            "INSERT IGNORE INTO players "
            "(nome,sesso,livello,email,telefono) VALUES (%s,%s,%s,%s,%s)"
        )
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, (nome, sesso, livello, email, telefono))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Errore durante l'inserimento del giocatore: {e}")
        return False
