import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Ustawienia strony - to sprawi, że program będzie wyglądał jak aplikacja
st.set_page_config(page_title="Monitor Opady - Nowy Tomyśl", layout="centered")

st.title("🍄 Monitor Opady: Paproć / Nowy Tomyśl")
st.write("Dane pobierane bezpośrednio z systemów IMGW")

def pobierz_dane():
    url = "https://danepubliczne.imgw.pl/api/data/synop"
    try:
        response = requests.get(url)
        dane = response.json()
        ulubione = ['Paproć', 'Poznań', 'Gorzów']
        
        for nazwa_szukana in ulubione:
            for stacja in dane:
                if stacja['stacja'] == nazwa_szukana:
                    return {
                        'data': datetime.now().strftime('%Y-%m-%d'),
                        'opad': float(stacja['suma_opadu']) if stacja['suma_opadu'] else 0.0,
                        'stacja': stacja['stacja']
                    }
    except:
        return None

# Ładowanie i zapisywanie danych
def odswiez_baze():
    nowy = pobierz_dane()
    try:
        df = pd.read_csv('baza_grzybiarza.csv')
    except:
        df = pd.DataFrame(columns=['data', 'opad', 'stacja'])
    
    if nowy:
        df = pd.concat([df, pd.DataFrame([nowy])]).drop_duplicates('data', keep='last')
        df.to_csv('baza_grzybiarza.csv', index=False)
    return df

df = odswiez_baze()

# Wyświetlanie aktualnego stanu
if not df.empty:
    ostatni = df.iloc[-1]
    col1, col2 = st.columns(2)
    col1.metric("Ostatni opad", f"{ostatni['opad']} mm")
    col2.metric("Stacja pomiarowa", ostatni['stacja'])

    # Wykres
    fig, ax = plt.subplots(figsize=(10, 4))
    kolory = ['#2ecc71' if x >= 10 else '#3498db' for x in df['opad']]
    ax.bar(df['data'], df['opad'], color=kolory)
    ax.axhline(y=10, color='red', linestyle='--', alpha=0.5)
    ax.set_ylabel("Opad (mm)")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    st.write("---")
    st.write("ℹ️ *Czerwona linia (10mm) oznacza opad, który realnie nawilża ściółkę pod dębami.*")
else:
    st.warning("Pobieranie danych... Uruchom program ponownie za chwilę.")
