import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai
import requests
from PIL import Image

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="OddBra Tv", layout="wide")

ODDS_API_KEY = "45984338b7cc6ae21c8fc1907d8b5bac"
GENAI_API_KEY = "AIzaSyDJ9k6k9u0moVjV5ZqQPZUW-ciOvENbLJ0"

# --- TESTE DE CONEXÃO IA ---
try:
    genai.configure(api_key=GENAI_API_KEY)
    # Tentando o nome mais curto e direto
    model = genai.GenerativeModel('gemini-1.5-flash')
    # Teste rápido de sanidade
    teste = model.generate_content("Oi")
    ia_ativa = True
except Exception as e:
    st.error(f"⚠️ A IA ainda está com erro de conexão: {e}")
    ia_ativa = False

# --- BANCO DE DADOS ---
ARQUIVO = "banca_oddbra.json"
def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return {"historico": [], "lucro_acumulado": 2595.74, "total_apostado": 4056.00}
    with open(ARQUIVO, 'r') as f:
        return json.load(f)

dados = carregar_dados()

# --- INTERFACE ---
st.title("🏆 OddBra Tv: Gestão de Elite")

col1, col2, col3 = st.columns(3)
col1.metric("Lucro Líquido", f"R$ {dados['lucro_acumulado']:.2f}")
col2.metric("Total Apostado", f"R$ {dados['total_apostado']:.2f}")
roi = (dados['lucro_acumulado'] / dados['total_apostado'] * 100) if dados['total_apostado'] > 0 else 0
col3.metric("ROI Geral", f"{roi:.2f}%")

st.divider()

# --- RADAR GLOBAL ---
st.subheader("🎯 Radar OddBra: Scanner Global")
if st.button("🔍 Iniciar Varredura"):
    if not ia_ativa:
        st.error("IA não configurada. Verifique o erro no topo da página.")
    else:
        with st.spinner('Buscando odds...'):
            try:
                # Busca simplificada para testar
                url = f"https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato_brasileiro_serie_a/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=h2h"
                res = requests.get(url).json()
                
                if res:
                    prompt = f"Analise estas odds e sugira 2 entradas: {res[:3]}"
                    analise = model.generate_content(prompt)
                    st.info(analise.text)
                else:
                    st.warning("Sem jogos agora.")
            except Exception as e:
                st.error(f"Erro no radar: {e}")

st.divider()
# Histórico simples
if dados["historico"]:
    st.write("📋 Histórico Recente")
    st.dataframe(pd.DataFrame(dados["historico"]))


