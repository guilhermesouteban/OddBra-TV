import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai
import requests
from PIL import Image

# --- 1. CONFIGURAÇÕES E CHAVES ---
st.set_page_config(page_title="OddBra Tv - Dashboard", layout="wide")

# Suas chaves (The Odds API e Gemini)
ODDS_API_KEY = "45984338b7cc6ae21c8fc1907d8b5bac"
GENAI_API_KEY = "AIzaSyDJ9k6k9u0moVjV5ZqQPZUW-ciOvENbLJ0"

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. BANCO DE DADOS ---
ARQUIVO = "banca_oddbra.json"

def carregar_dados():
    if not os.path.exists(ARQUIVO):
        # Inicia com seu histórico atual
        return {"historico": [], "lucro_acumulado": 2595.74, "total_apostado": 4056.00}
    with open(ARQUIVO, 'r') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO, 'w') as f:
        json.dump(dados, f, indent=4)

dados = carregar_dados()

# --- 3. FUNÇÕES IA (AUDITORIA E LEITURA) ---

def explicar_red_ia(evento, odd, motivo):
    prompt = f"Analise como o Advogado do Diabo da OddBra Tv: O evento {evento} com odd {odd} deu RED. Motivo: {motivo}. Explique tecnicamente por que perdemos e use gírias de apostador profissional."
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "IA offline no momento."

def ler_print_bet365(imagem):
    prompt = """Analise este print da Bet365 e extraia: Nome do Evento, Stake e Odd. 
    Retorne APENAS um JSON no formato: {"evento": "nome", "stake": 0.0, "odd": 0.0}"""
    img = Image.open(imagem)
    response = model.generate_content([prompt, img])
    texto = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(texto)

# --- 4. INTERFACE (SIDEBAR) ---
st.sidebar.title("🚀 OddBra Tv")
st.sidebar.divider()

# Registro Automático
st.sidebar.subheader("📸 Registro por Print")
arquivo_print = st.sidebar.file_uploader("Suba o print da aposta", type=["png", "jpg", "jpeg"])

# Variáveis de preenchimento automático
ev_l, st_l, od_l = "", 0.0, 1.01

if arquivo_print:
    if st.sidebar.button("🤖 IA, Ler Print"):
        with st.spinner('Lendo dados do bilhete...'):
            try:
                res = ler_print_bet365(arquivo_print)
                ev_l, st_l, od_l = res['evento'], res['stake'], res['odd']
                st.sidebar.success("Dados extraídos!")
            except:
                st.sidebar.error("Erro ao ler print.")

st.sidebar.divider()
st.sidebar.subheader("📝 Confirmar Bilhete")
f_nome = st.sidebar.text_input("Evento", value=ev_l)
f_stake = st.sidebar.number_input("Stake (R$)", value=float(st_l))
f_odd = st.sidebar.number_input("Odd", value=float(od_l))
f_res = st.sidebar.selectbox("Resultado", ["Pendente", "Green", "Red", "Void"])
f_motivo = st.sidebar.text_input("Placar/Motivo (se Red)")

if st.sidebar.button("Salvar na Banca"):
    lucro = (f_stake * f_odd - f_stake) if f_res == "Green" else (-f_stake if f_res == "Red" else 0)
    audit = explicar_red_ia(f_nome, f_odd, f_motivo) if f_res == "Red" else "-"
    
    nova = {
        "Data": pd.Timestamp.now().strftime("%d/%m/%Y"), 
        "Evento": f_nome, 
        "Stake": f_stake, 
        "Odd": f_odd, 
        "Res": f_res, 
        "Lucro": lucro, 
        "Auditoria_IA": audit
    }
    
    dados["historico"].append(nova)
    dados["lucro_acumulado"] += lucro
    dados["total_apostado"] += f_stake
    salvar_dados(dados)
    st.sidebar.success("Salvo com sucesso!")
    st.rerun()

# --- 5. DASHBOARD PRINCIPAL ---
st.title("🏆 OddBra Tv: Gestão de Elite")
col1, col2, col3 = st.columns(3)
col1.metric("Lucro Líquido", f"R$ {dados['lucro_acumulado']:.2f}")
col2.metric("Total Apostado", f"R$ {dados['total_apostado']:.2f}")
roi = (dados['lucro_acumulado'] / dados['total_apostado'] * 100) if dados['total_apostado'] > 0 else 0
col3.metric("ROI Geral", f"{roi:.2f}%")

st.divider()

# --- 6. BUSCA DE ODDS (IA) ---
st.subheader("🎯 Picks Sugeridas pela IA (Série A)")
if st.button("🔍 Buscar Jogos de Hoje"):
    url = f"https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato_brasileiro_serie_a/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=h2h"
    with st.spinner('Varrendo mercado e notícias locais...'):
        resp = requests.get(url)
        if resp.status_code == 200:
            prompt = f"Analise estas odds da Série A: {resp.json()[:8]}. Sugira 3 picks de valor, considere clima e notícias. Use gírias de bettor profissional da OddBra Tv."
            analise = model.generate_content(prompt)
            st.info(analise.text)
        else:
            st.error("Erro na API de Odds.")

st.divider()

# --- 7. HISTÓRICO ---
if dados["historico"]:
    st.subheader("📋 Auditoria e Histórico")
    df = pd.DataFrame(dados["historico"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhuma aposta registrada no site ainda.")

