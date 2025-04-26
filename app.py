import streamlit as st
import pandas as pd
from datetime import datetime
from db import init_db, get_connection
from dal import insert_player, fetch_similar_players, insert_match
from logic import score_players, parse_csv_and_clean

# --- Caricamento dati ---
st.set_page_config(page_title='Gestionale Padel', layout='wide', initial_sidebar_state='expanded')
conn = get_connection()
@st.cache_data(show_spinner=False)


def get_players_df():
    conn = get_connection()
    df = pd.read_sql('SELECT * FROM players', conn)
    return df

def refresh_players_df():
    get_players_df.clear()
    return get_players_df()

def show_players(df):
    st.dataframe(df.drop(columns=['id', 'created_at']))
    st.markdown('---')
    st.write(f"Totale Giocatori: {len(df)}")
    st.write(f"Giocatori Maschi: {len(df[df['sesso'] == 'MALE'])}")
    st.write(f"Giocatori Femmine: {len(df[df['sesso'] == 'FEMALE'])}")
    st.write(f"Livello medio: {df['livello'].mean():.2f}")


# --- Header ---
st.title('🏓 Gestionale Campi Padel')
st.markdown('---')

# --- Sidebar Operazioni ---
with st.sidebar:

    st.header('📥 Importa file')
    st.markdown('Carica un file in formato .CSV con i nuovi giocatori. Il CSV deve includere le intestazioni: `name`, `gender`, `PADEL`, `email`, `phone_number`')
    with st.expander("📂 Carica CSV giocatori"):
        uploaded_file = st.file_uploader("Carica un file CSV con i dati dei giocatori", type=["csv"])

        if uploaded_file:
            try:
                # df_clean = load_and_clean_players_csv(uploaded_file)
                df_clean = parse_csv_and_clean(uploaded_file)
                st.success(f"✅ {len(df_clean)} giocatori pronti per l'inserimento.")

                if st.button("📤 Inserisci nel database"):
                    inserted = 0
                    for _, row in df_clean.iterrows():
                        if insert_player(
                            row['name'], row['gender'],
                            row['level'], row['email'], row['phone_number']
                        ):
                            inserted += 1
                    if inserted==0:
                        st.warning(f"⚠️ Nessun giocatore da inserire. Tutti già esistenti nel database.")
                    elif inserted != len(df_clean):
                        st.warning(f"⚠️ {len(df_clean) - inserted} giocatori già esistenti nel database. \nHo inserito {inserted} nuovi giocatori nel database.")
                    else:
                        st.success(f"🎉 Giocatori inseriti correttamente.")
                    df_players = refresh_players_df()
            except Exception as e:
                st.error(str(e))


    # spazio
    st.markdown('\n\n---\n\n')


    st.header('🖊️ Nuovo Giocatore')
    st.markdown('Aggiungi un nuovo giocatore manualmente. Compila i campi richiesti e premi "Aggiungi Giocatore".')
    # use an icon plus
    with st.expander("➕ Aggiungi Giocatore"):
        with st.form('manual_insert', clear_on_submit=True):
            nome = st.text_input('Nome')
            sesso = st.selectbox('Sesso', ['MALE','FEMALE'])
            livello = st.number_input('Livello (0-4)', min_value=0, max_value=4, step=1)
            email = st.text_input('Email')
            telefono = st.text_input('Telefono')
            submitted = st.form_submit_button('Aggiungi Giocatore')
            if submitted:
                if not nome or not email:
                    st.warning('Compila almeno Nome e Email')
                else:
                    if insert_player(nome, sesso, livello, email, telefono):
                        st.success('Giocatore aggiunto!')
                        df_players = refresh_players_df()
                    else:
                        st.warning('Giocatore già esistente!')


    if st.button('🔄 Aggiorna Giocatori', key='update_players'):
        try:
            df_players = get_players_df()
            st.success('Giocatori aggiornati!')
        except Exception as e:
            st.error(f'Errore aggiornamento giocatori: {e}')


    st.markdown('\n\n---\n\n')


    st.header('🔧 Azioni rapide')
    st.markdown('TBD! Not working yet')
    if st.button('Inizializza Database', key='init_db'):
        try:
            init_db(); st.success('DB inizializzato')
        except Exception as e:
            st.error(f'Errore init_db: {e}')

# --- Caricamento iniziale o aggiornato ---
try:
    df_players = get_players_df()
except Exception:
    df_players = pd.DataFrame()

# --- Selezione Modalità ---
st.markdown('---')
col1, col2, col3 = st.columns(3)
with col1:
    if st.button('📋 Nuova prenotazione', key='btn_pren'): st.session_state.mode='pren'
with col2:
    if st.button('🎾 Inserisci nuova partita', key='btn_part'): st.session_state.mode='part'
with col3:
    if st.button('👥 Visualizza giocatori', key='btn_view'): st.session_state.mode='view'

mode = st.session_state.get('mode', None)


# --- Modulo Prenotazione ---
if mode == 'pren':
    st.header('📝 Prenotazione Automatica')
    cols = st.columns(2)
    with cols[0]:
        req = st.selectbox('Richiedente', df_players[['id','nome']]
                            .apply(lambda x: f"{x['nome']} (ID:{x['id']})", axis=1))
    with cols[1]:
        date = st.date_input('Data')
        time = st.time_input('Ora')
    dt = datetime.combine(date, time)
    if st.button('🔍 Trova possibili candidati', key='find20'):
        cands = fetch_similar_players(int(req.split('ID:')[1].strip(')')))
        scored = score_players(cands, int(req.split('ID:')[1].strip(')')), dt)
        top20 = sorted(scored, key=lambda x:x['score'], reverse=True)[:20]
        st.dataframe(pd.DataFrame(top20)[['nome','livello','preferred_slot','score']])

# --- Modulo Partita ---
elif mode == 'part':
    st.header('🎾 Registra Partita')
    cols = st.columns(4)
    with cols[0]:
        selection_1 = st.multiselect('Giocatore 1', df_players.apply(lambda x: f"{x['nome']} (ID:{x['id']})", axis=1),
                               max_selections=1, placeholder='Scegli Giocatore 1...')
    with cols[1]:
        selection_2 = st.multiselect('Giocatore 2', df_players.apply(lambda x: f"{x['nome']} (ID:{x['id']})", axis=1),
                               max_selections=1, placeholder='Scegli Giocatore 2...')
    with cols[2]:
        selection_3 = st.multiselect('Giocatore 3', df_players.apply(lambda x: f"{x['nome']} (ID:{x['id']})", axis=1),
                               max_selections=1, placeholder='Scegli Giocatore 3...')
    with cols[3]:
        selection_4 = st.multiselect('Giocatore 4', df_players.apply(lambda x: f"{x['nome']} (ID:{x['id']})", axis=1),
                               max_selections=1, placeholder='Scegli Giocatore 4...')

    # check for duplicates
    if len(selection_1) > 0 and selection_1[0] in selection_2 + selection_3 + selection_4:
        st.warning('Giocatore 1 già selezionato')
    elif len(selection_2) > 0 and selection_2[0] in selection_1 + selection_3 + selection_4:
        st.warning('Giocatore 2 già selezionato')
    elif len(selection_3) > 0 and selection_3[0] in selection_1 + selection_2 + selection_4:
        st.warning('Giocatore 3 già selezionato')
    elif len(selection_4) > 0 and selection_4[0] in selection_1 + selection_2 + selection_3:
        st.warning('Giocatore 4 già selezionato')

    selected = selection_1 + selection_2 + selection_3 + selection_4
    date = st.date_input('Data Partita', key='part_date')
    time = st.time_input('Ora Partita', key='part_time')
    dt = datetime.combine(date, time)
    if st.button('✅ Registra', key='reg_part'):
        if len(selected)!=4:
            st.warning('Seleziona esattamente 4 giocatori', )
        else:
            ids = [int(s.split('ID:')[1].strip(')')) for s in selected]
            mid = insert_match(dt, ids)
            st.success(f'Partita #{mid} registrata')
            df_players = refresh_players_df()

# --- Visualizzazione Giocatori ---
elif mode == 'view':
    st.header('👥 Lista Giocatori')
    st.markdown('Visualizza i giocatori registrati nel database.')

    cols = st.columns(2)
    with cols[0]:
        if st.button('🔄 Aggiorna Giocatori', key='update_players_view'):
            try:
                df_players = get_players_df()
                st.success('Giocatori aggiornati!')
            except Exception as e:
                st.error(f'Errore aggiornamento giocatori: {e}')
    with cols[1]:
        if st.button('🔍 Trova Giocatore', key='find_player'):
            search = st.text_input('Cerca Giocatore', placeholder='Cerca per Nome, Cognome o Email')
            if search:
                df = df_players.copy()
                df = df[
                    df['nome'].str.contains(search, case=False) |
                    df['cognome'].str.contains(search, case=False) |
                    df['email'].str.contains(search, case=False)
                ]
                show_players(df)
                # st.dataframe(df)
                st.write(f'Totale: {len(df)} giocatori')

    st.markdown('---')
    df_players = get_players_df()
    show_players(df_players)

else:
    st.info('Seleziona un\'azione tramite i pulsanti sopra, oppure apri la tendina laterale per aggiungere nuovi giocatori.')