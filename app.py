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
    /* Inputs de Senha e Texto */
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
        border-radius: 8px;
        border: 1px solid #4a4a4a;
    }
    /* Botões */
    div.stButton > button {
        background-color: #800020;
        color: white;
        border: 1px solid #4a0012;
        border-radius: 8px;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #a30029;
        border-color: #ff0040;
    }
    h1, h2, h3 { color: #EEEEEE !important; }
</style>
""", unsafe_allow_html=True)

# --- SISTEMA DE LOGIN (A TRAVA) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def verificar_senha():
    if st.session_state.senha_input == st.secrets["ACCESS_PASSWORD"]:
        st.session_state.authenticated = True
    else:
        st.error("🚫 Senha Incorreta! Tente novamente.")

if not st.session_state.authenticated:
    # TELA DE BLOQUEIO
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 Acesso Restrito")
        st.write("Este software é exclusivo para membros do Clube.")
        st.markdown("---")
        st.text_input("Digite sua Chave de Acesso:", type="password", key="senha_input", on_change=verificar_senha)
        st.markdown("---")
        # Aqui você colocará seu link de venda no futuro
        st.markdown("👉 **[Não tem acesso? Clique aqui para adquirir](https://wa.me/5531999999999)**") 
    st.stop() # PARA TUDO AQUI SE NÃO TIVER LOGADO

# --- A PARTIR DAQUI, SÓ APARECE SE A SENHA ESTIVER CERTA ---

st.title("💎 BetManager Premium")
st.write("Inteligência Artificial & Visão Computacional para Gestão de Banca.")
st.markdown("---")

# Configuração da Chave da IA
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Erro técnico: Chave API não configurada.")
    st.stop()

# Layout Principal
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📸 Dados da Aposta")
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
            st.warning("⚠️ Envie um print ou digite algo!")
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
                
                with st.spinner(f'💎 Validando Acesso & Processando...'):
                    response = None
                    if upload_arquivo:
                        imagem = Image.open(upload_arquivo)
                        response = model.generate_content([prompt_base, imagem])
                    else:
                        response = model.generate_content([prompt_base, f"Histórico: {texto_input}"])
                    
                    texto_limpo = response.text.replace("```json", "").replace("```", "")
                    dados = json.loads(texto_limpo)
                    
                    st.success("Análise Concluída")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Nota", f"{dados['nota']}/10")
                    c2.metric("Risco", dados['risco'])
                    c3.metric("Prejuízo", dados['prejuizo_estimado'])
                    
                    st.subheader("📊 Raio-X")
                    st.bar_chart(dados['fontes_de_erro'])
                    
                    st.info("🧠 Consultoria")
                    st.write(dados['analise_texto'])
                    
            except Exception as e:
                st.error(f"Erro: {e}")