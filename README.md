# 🏓 Gestionale Prenotazioni Campi Padel

## Descrizione
Questa applicazione consente di:
- Inserire nuovi giocatori manualmente o tramite file CSV.
- Visualizzare, cercare e gestire i giocatori esistenti.
- Creare **prenotazioni automatiche** trovando i 20 giocatori più compatibili.
- Registrare **partite manualmente** scegliendo 4 giocatori.
- Aggiornare dinamicamente il database senza riavvii.

Realizzato con:
- Python
- Streamlit
- MySQL

---

## Struttura del progetto

| File | Descrizione |
|:----|:------------|
| `app.py` | Interfaccia Streamlit principale: gestione dati, prenotazioni, partite, visualizzazione |
| `dal.py` | Data Access Layer: operazioni CRUD su MySQL |
| `logic.py` | Business logic: pulizia CSV, calcolo punteggi matching |
| `db.py` | Configurazione del database MySQL |
|
| `requirements.txt` | Dipendenze del progetto |

---

## Funzioni principali

### app.py

- **get_players_df()**: Carica i dati dei giocatori in un DataFrame (con caching).
- **refresh_players_df()**: Pulisce la cache e ricarica i dati aggiornati.
- **show_players(df)**: Mostra i dati dei giocatori con statistiche aggiuntive.
- **Prenotazione Automatica**: Ricerca e visualizza i 20 migliori candidati compatibili.
- **Registrazione Partita**: Permette di scegliere 4 giocatori e registrare una nuova partita.
- **Visualizzazione e Ricerca**: Tabella dei giocatori + ricerca per nome/cognome/email.

---

### dal.py

- **get_player(player_id)**: Recupera i dati di un giocatore dal DB.
- **fetch_similar_players(req_id)**: Cerca giocatori compatibili per sesso e livello.
- **count_past_matches(player_id, orario)**: Conta le partite precedenti nella stessa fascia oraria.
- **insert_match(orario, player_ids)**: Inserisce una nuova partita e aggiorna i preferred_slot.
- **update_player_preferred_slot(player_id)**: Aggiorna la fascia preferita del giocatore.
- **player_exists(player_name)**: Verifica se il giocatore esiste già.
- **insert_player(nome, sesso, livello, email, telefono)**: Inserisce un nuovo giocatore nel DB.

---

### logic.py

- **parse_csv_and_clean(file)**: Pulisce un file CSV (controllo colonne, livelli numerici, rimozione nulli).
- **gaussian(x, sigma)**: Valuta la gaussiana standard per normalizzare differenze.
- **score_players(candidates, requester_id, orario)**: Calcola lo score per ciascun candidato sulla base di:
  - Differenza di livello
  - Storico di presenza
  - Preferenza di fascia oraria

---
### TODO
- Sistemare il Trova Giocatore
- Sistemare l'euristica
