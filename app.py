import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# Configuração da página
st.set_page_config(page_title="BetManager Pro", page_icon="💎", layout="wide")

# --- ESTILO BLACK PREMIUM (CSS) ---
st.markdown("""
<style>
    /* Fundo Preto Fosco */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Botões em Vinho Premium */
    div.stButton > button {
        background-color: #800020;
        color: white;
        border: 1px solid #4a0012;
        border-radius: 8px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #a30029; /* Vinho mais claro ao passar o mouse */
        border-color: #ff0040;
    }
    
    /* Inputs Escuros */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #262730;
        color: white;
        border-radius: 8px;
    }
    
    /* Títulos e Métricas */
    h1, h2, h3 {
        color: #EEEEEE !important;
    }
    [data-testid="stMetricValue"] {
        color: #ff4b4b; /* Vermelho destaque nos números */
    }
</style>
""", unsafe_allow_html=True)

# Título
st.title("💎 BetManager Premium")
st.write("Inteligência Artificial & Visão Computacional para Gestão de Banca.")
st.markdown("---")

# Configuração da Chave
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Configure a chave API nos Secrets!")
    st.stop()

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📸 Dados da Aposta")
    
    # Abas estilizadas
    tab1, tab2 = st.tabs(["📁 Enviar Print", "✍️ Digitar"])
    
    upload_arquivo = None
    texto_input = ""
    
    with tab1:
        upload_arquivo = st.file_uploader("Solte o print aqui", type=["jpg", "png", "jpeg"])
        if upload_arquivo:
            st.image(upload_arquivo, caption="Imagem carregada", use_container_width=True)
            
    with tab2:
        texto_input = st.text_area("Descreva a aposta:", height=150, placeholder="Ex: All in no Lakers...")

    analisar_btn = st.button("🚀 ANALISAR RISCO", type="primary")

with col2:
    if analisar_btn:
        if not upload_arquivo and not texto_input:
            st.warning("⚠️ Você precisa enviar um print ou digitar algo!")
        else:
            try:
                # Detecção Automática de Modelo
                modelo_escolhido = "gemini-1.5-flash"
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            if 'flash' in m.name or 'gemini-1.5' in m.name:
                                modelo_escolhido = m.name
                                break
                except:
                    pass
                
                model = genai.GenerativeModel(modelo_escolhido)
                
                prompt_base = """
                Atue como um gestor de risco de elite.
                Analise esta entrada (imagem ou texto).
                
                Retorne APENAS um JSON válido (sem markdown) com este formato exato:
                {
                    "nota": (0 a 10),
                    "risco": ("Baixo", "Médio" ou "Alto"),
                    "prejuizo_estimado": "R$ Valor",
                    "fontes_de_erro": {
                        "Emocional": (0-100),
                        "Técnico": (0-100),
                        "Gestão": (0-100)
                    },
                    "analise_texto": "Sua análise direta..."
                }
                """
                
                with st.spinner(f'💎 Processando com IA...'):
                    response = None
                    if upload_arquivo:
                        imagem = Image.open(upload_arquivo)
                        response = model.generate_content([prompt_base, imagem])
                    else:
                        response = model.generate_content([prompt_base, f"Histórico: {texto_input}"])
                    
                    texto_limpo = response.text.replace("```json", "").replace("```", "")
                    dados = json.loads(texto_limpo)
                    
                    # Dashboard
                    st.success("Análise Concluída")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Nota de Disciplina", f"{dados['nota']}/10")
                    c2.metric("Nível de Risco", dados['risco'])
                    c3.metric("Prejuízo Estimado", dados['prejuizo_estimado'])
                    
                    st.subheader("📊 Raio-X do Erro")
                    st.bar_chart(dados['fontes_de_erro'])
                    
                    st.info("🧠 Consultoria IA")
                    st.write(dados['analise_texto'])
                    
            except Exception as e:
                st.error(f"Erro: {e}")