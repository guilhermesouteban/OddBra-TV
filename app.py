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
