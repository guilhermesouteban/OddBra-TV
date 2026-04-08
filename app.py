import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai
import requests
from PIL import Image

# --- 1. CONFIGURAÇÕES E CHAVES ---
st.set_page_config(page_title="OddBra Tv - Radar Global", layout="wide")

ODDS_API_KEY = "45984338b7cc6ae21c8fc1907d8b5bac"
GENAI_API_KEY = "AIzaSyDJ9k6k9u0moVjV5ZqQPZUW-ciOvENbLJ0"

# AJUSTE AQUI: Configuração simplificada para evitar o erro 404
genai.configure(api_key=GENAI_API_KEY)
# Mudamos para 'gemini-1.5-flash-latest' que é o endereço mais estável
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. BANCO DE DADOS ---
ARQUIVO = "banca_oddbra.json"

def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return {"historico": [], "lucro_acumulado": 2595.74, "total_apostado": 4056.00}
    with open(ARQUIVO, 'r') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO, 'w') as f:
        json.dump(dados, f, indent=4)

dados = carregar_dados()

# --- 3. FUNÇÕES IA ---

def explicar_red_ia(evento, odd, motivo):
    prompt = f"Analise como o Advogado do Diabo da OddBra Tv: O evento {evento} com odd {odd} deu RED. Motivo: {motivo}. Explique tecnicamente e use gírias de bettor profissional."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"IA indisponível: {e}"

def ler_print_bet365(imagem):
    prompt = """Analise este print da Bet365 e extraia: Nome do Evento, Stake e Odd. 
    Retorne APENAS um JSON: {"evento": "nome", "stake": 0.0, "odd": 0.0}"""
    img = Image.open(imagem)
    response = model.generate_content([prompt, img])
    texto = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(texto)

# --- 4. INTERFACE (SIDEBAR) ---
st.sidebar.title("🚀 OddBra Tv")
st.sidebar.divider()

st.sidebar.subheader("📸 Registro por Print")
arquivo_print = st.sidebar.file_uploader("Suba o print da aposta", type=["png", "jpg", "jpeg"])

ev_l, st_l, od_l = "", 0.0, 1.01

if arquivo_print:
    if st.sidebar.button("🤖 IA, Ler Print"):
        with st.spinner('Lendo bilhete...'):
            try:
                res = ler_print_bet365(arquivo_print)
                ev_l, st_l, od_l = res['evento'], res['stake'], res['odd']
                st.sidebar.success("Dados extraídos!")
            except:
                st.sidebar.error("Erro ao ler imagem.")

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
    
    nova = {"Data": pd.Timestamp.now().strftime("%d/%m/%Y"), "Evento": f_nome, "Stake": f_stake, "Odd": f_odd, "Res": f_res, "Lucro": lucro, "Auditoria_IA": audit}
    dados["historico"].append(nova)
    dados["lucro_acumulado"] += lucro
    dados["total_apostado"] += f_stake
    salvar_dados(dados)
    st.sidebar.success("Salvo!")
    st.rerun()

# --- 5. DASHBOARD ---
st.title("🏆 OddBra Tv: Gestão de Elite")
c1, c2, c3 = st.columns(3)
c1.metric("Lucro Líquido", f"R$ {dados['lucro_acumulado']:.2f}")
c2.metric("Total Apostado", f"R$ {dados['total_apostado']:.2f}")
roi = (dados['lucro_acumulado'] / dados['total_apostado'] * 100) if dados['total_apostado'] > 0 else 0
c3.metric("ROI Geral", f"{roi:.2f}%")

st.divider()

# --- 6. RADAR OMNI-LIGAS ---
st.subheader("🎯 Radar OddBra: Scanner Global de Valor")
if st.button("🔍 Iniciar Varredura de Todos os Campeonatos"):
    
    with st.spinner('IA OddBra varrendo mercados mundiais...'):
        try:
            url_esportes = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
            res_esp = requests.get(url_esportes).json()
            
            ligas_selecionadas = []
            for esp in res_esp:
                key = esp['key']
                if "soccer" in key:
                    ligas_selecionadas.append(key)
                elif key in ["basketball_nba", "basketball_brazil_nbb", "basketball_euroleague"]:
                    ligas_selecionadas.append(key)
                elif "baseball_mlb" in key or "tennis" in key:
                    ligas_selecionadas.append(key)
            
            dados_mercado = []
            # Reduzi para as 8 primeiras ligas para a resposta ser mais rápida e não travar
            for liga in ligas_selecionadas[:8]:
                url_odds = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=h2h"
                res_odds = requests.get(url_odds)
                if res_odds.status_code == 200:
                    jogos = res_odds.json()
                    if jogos:
                        dados_mercado.append({"liga": liga, "odds": jogos[:3]})

            if dados_mercado:
                # Prompt otimizado para não dar erro de versão
                prompt = f"Analise como o Analista-Chefe da OddBra Tv: {dados_mercado}. Identifique 5 entradas de valor globais com gírias de bettor. Seja direto."
                analise = model.generate_content(prompt)
                st.info(analise.text)
            else:
                st.warning("⚠️ Nenhuma odd disponível no radar agora.")
        except Exception as e:
            st.error(f"Erro na varredura global: {e}")

st.divider()

# --- 7. HISTÓRICO ---
if dados["historico"]:
    st.subheader("📋 Histórico e Auditoria")
    st.dataframe(pd.DataFrame(dados["historico"]), use_container_width=True)
