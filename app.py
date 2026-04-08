import streamlit as st
import pandas as pd
import json
import os

# Configuração da Página
st.set_page_config(page_title="OddBra Tv - Dashboard", layout="wide")

# Inicialização de dados
ARQUIVO = "banca_oddbra.json"
if not os.path.exists(ARQUIVO):
    dados_iniciais = {"historico": [], "lucro_acumulado": 2595.74, "total_apostado": 4056.00}
    with open(ARQUIVO, 'w') as f:
        json.dump(dados_iniciais, f)

def carregar_dados():
    with open(ARQUIVO, 'r') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO, 'w') as f:
        json.dump(dados, f, indent=4)

dados = carregar_dados()

# --- INTERFACE ---
st.title("🚀 OddBra Tv: Gestão de Banca")

# Sidebar para novas apostas
st.sidebar.header("Registrar Novo Bilhete")
nome = st.sidebar.text_input("Nome do Evento")
stake = st.sidebar.number_input("Valor da Aposta (R$)", min_value=1.0)
odd = st.sidebar.number_input("Odd", min_value=1.01)
resultado = st.sidebar.selectbox("Resultado", ["Selecionar", "Green", "Red", "Void"])
motivo = st.sidebar.text_input("Motivo (se Red)")

if st.sidebar.button("Salvar Aposta"):
    if resultado != "Selecionar":
        lucro_op = (stake * odd - stake) if resultado == "Green" else (-stake if resultado == "Red" else 0)
        nova_aposta = {
            "nome": nome, "stake": stake, "odd": odd, 
            "res": resultado, "lucro": lucro_op, "motivo": motivo
        }
        dados["historico"].append(nova_aposta)
        dados["lucro_acumulado"] += lucro_op
        dados["total_apostado"] += stake
        salvar_dados(dados)
        st.sidebar.success("Registrado!")
        st.rerun()

# --- DASHBOARD PRINCIPAL ---
col1, col2, col3 = st.columns(3)
col1.metric("Lucro Líquido", f"R$ {dados['lucro_acumulado']:.2f}")
col2.metric("Total Apostado", f"R$ {dados['total_apostado']:.2f}")
roi = (dados['lucro_acumulado'] / dados['total_apostado'] * 100) if dados['total_apostado'] > 0 else 0
col3.metric("ROI Geral", f"{roi:.2f}%")

st.divider()

if dados["historico"]:
    st.subheader("Histórico de Apostas")
    df = pd.DataFrame(dados["historico"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhuma aposta registrada no site ainda.")

import requests

# Configurações das APIs
ODDS_API_KEY = "45984338b7cc6ae21c8fc1907d8b5bac"
GENAI_API_KEY = "AIzaSyDJ9k6k9u0moVjV5ZqQPZUW-ciOvENbLJ0"

st.divider()
st.subheader("🎯 Palpites de Elite da OddBra IA")

if st.button("Buscar Melhores Oportunidades de Hoje"):
    # 1. Busca jogos de Futebol (ou NBA/MLB mudando o esporte)
    # Exemplo: soccer_brazil_campeonato_brasileiro_serie_a ou basketball_nba
    url = f"https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato_brasileiro_serie_a/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=h2h"
    
    response = requests.get(url)
    if response.status_code == 200:
        jogos = response.json()
        
        # 2. Passa os dados brutos para a IA analisar
        prompt_especialista = f"""
        Como um analista senior da OddBra Tv, analise estes dados de odds: {jogos[:10]}
        
        Sua tarefa:
        1. Identifique os 3 jogos mais promissores.
        2. Justifique com base em probabilidade implícita (transforme odd em %).
        3. Dê um palpite de 'Aposta Sugerida' (ex: ML, Handicap ou Over/Under).
        4. Seja direto e use gírias de apostador profissional.
        5. Analise todas as probabilidades e adversidades do jogo pesquisando em jornais locais , especialistas , condições climaticas.
        """
        
        analise_ia = model.generate_content(prompt_especialista)
        st.success("💰 Picks Selecionadas pela IA:")
        st.write(analise_ia.text)
    else:
        st.error("Erro ao buscar odds. Verifique sua chave da API.")
