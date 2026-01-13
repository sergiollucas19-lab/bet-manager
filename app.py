import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# Configuração da página
st.set_page_config(page_title="BetManager Vision", page_icon="👁️", layout="wide")

st.title("👁️ BetManager Vision")
st.write("Envie o PRINT da aposta e deixe a IA analisar.")
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
    st.header("📸 Upload")
    
    # Abas para escolher: Texto ou Imagem
    tab1, tab2 = st.tabs(["📁 Enviar Print", "✍️ Digitar"])
    
    upload_arquivo = None
    texto_input = ""
    
    with tab1:
        upload_arquivo = st.file_uploader("Solte o print aqui", type=["jpg", "png", "jpeg"])
        if upload_arquivo:
            st.image(upload_arquivo, caption="Imagem carregada", use_container_width=True)
            
    with tab2:
        texto_input = st.text_area("Ou cole o texto:", height=150)

    analisar_btn = st.button("🚀 Analisar Risco", type="primary")

with col2:
    if analisar_btn:
        if not upload_arquivo and not texto_input:
            st.warning("⚠️ Você precisa enviar um print ou digitar algo!")
        else:
            try:
                # --- CORREÇÃO: DETETOR AUTOMÁTICO DE MODELO ---
                modelo_escolhido = "gemini-1.5-flash" # Tenta esse por padrão
                try:
                    # Procura um modelo disponível na sua conta
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            # Prioriza modelos que aceitam imagem (Flash ou 1.5)
                            if 'flash' in m.name or 'gemini-1.5' in m.name:
                                modelo_escolhido = m.name
                                break
                except:
                    pass
                
                # Configura a IA com o modelo que achou
                model = genai.GenerativeModel(modelo_escolhido)
                
                prompt_base = """
                Atue como um gestor de risco de apostas esportivas experiente.
                Analise esta entrada (imagem ou texto) e identifique os erros cometidos.
                
                Retorne APENAS um JSON válido (sem markdown) com este formato exato:
                {
                    "nota": (0 a 10),
                    "risco": ("Baixo", "Médio" ou "Alto"),
                    "prejuizo_estimado": "Valor estimado (R$)",
                    "fontes_de_erro": {
                        "Emocional": (0-100),
                        "Técnico": (0-100),
                        "Gestão": (0-100)
                    },
                    "analise_texto": "Sua análise direta e curta sobre o erro..."
                }
                """
                
                with st.spinner(f'🤖 Analisando com {modelo_escolhido}...'):
                    response = None
                    
                    if upload_arquivo:
                        # Se for imagem, abre e manda pra IA
                        imagem = Image.open(upload_arquivo)
                        response = model.generate_content([prompt_base, imagem])
                    else:
                        # Se for só texto
                        response = model.generate_content([prompt_base, f"Histórico: {texto_input}"])
                    
                    # Tratamento do JSON
                    texto_limpo = response.text.replace("```json", "").replace("```", "")
                    dados = json.loads(texto_limpo)
                    
                    # Exibição do Dashboard
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Nota", f"{dados['nota']}/10")
                    c2.metric("Risco", dados['risco'])
                    c3.metric("Prejuízo", dados['prejuizo_estimado'])
                    
                    st.subheader("📊 Diagnóstico")
                    st.bar_chart(dados['fontes_de_erro'])
                    
                    st.info("🧠 Parecer da IA")
                    st.write(dados['analise_texto'])
                    
            except Exception as e:
                st.error(f"Erro detalhado: {e}")