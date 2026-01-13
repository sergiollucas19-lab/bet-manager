import streamlit as st
import google.generativeai as genai
import json

# Configuração da página (Modo Wide para caber os gráficos)
st.set_page_config(page_title="BetManager Pro", page_icon="💎", layout="wide")

# Cabeçalho com estilo
st.title("💎 BetManager Pro")
st.write("Inteligência Artificial para Gestão de Banca")
st.markdown("---")

# Configuração da Chave (Secrets)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Configure a chave API nos Secrets do Streamlit!")
    st.stop()

# Layout de Colunas (Input na esquerda, Resultado na direita)
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📥 Dados")
    historico = st.text_area("Cole o histórico:", height=300, placeholder="Ex: Apostei 50 no Real e perdi...")
    analisar_btn = st.button("🚀 Analisar Agora", type="primary")

with col2:
    if analisar_btn and historico:
        try:
            # Seleção de Modelo
            modelo_final = "gemini-1.5-flash"
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        if 'gemini' in m.name:
                            modelo_final = m.name
                            break
            except:
                pass
            
            model = genai.GenerativeModel(modelo_final)
            
            # PROMPT AVANÇADO (Pede JSON para gerar gráficos)
            prompt = f"""
            Atue como um analista de risco profissional. Analise este histórico: "{historico}"
            
            Retorne APENAS um JSON válido (sem markdown) com este formato exato:
            {{
                "nota": (número de 0 a 10),
                "risco": ("Baixo", "Médio" ou "Alto"),
                "prejuizo_estimado": "Valor em R$",
                "fontes_de_erro": {{
                    "Emocional": (porcentagem de 0 a 100),
                    "Técnico": (porcentagem de 0 a 100),
                    "Gestão": (porcentagem de 0 a 100)
                }},
                "analise_texto": "Sua análise completa e dicas aqui..."
            }}
            """
            
            with st.spinner('🤖 A IA está gerando o Dashboard...'):
                response = model.generate_content(prompt)
                
                # Limpeza do texto para garantir que é JSON
                texto_limpo = response.text.replace("```json", "").replace("```", "")
                dados = json.loads(texto_limpo)
                
                # --- A MÁGICA DO DASHBOARD ---
                
                # 1. Indicadores (Metrics)
                c1, c2, c3 = st.columns(3)
                c1.metric("Nota de Disciplina", f"{dados['nota']}/10")
                c2.metric("Nível de Risco", dados['risco'], delta_color="inverse")
                c3.metric("Prejuízo Estimado", dados['prejuizo_estimado'])
                
                # 2. Gráfico de Erros
                st.subheader("📊 Onde você está errando?")
                st.bar_chart(dados['fontes_de_erro'])
                
                # 3. Análise em Texto
                st.info("🧠 Análise da IA")
                st.write(dados['analise_texto'])
                
        except Exception as e:
            st.error(f"Erro ao gerar dashboard: {e}")
            st.write("Tente novamente, a IA pode ter se confundido.")

    elif not historico:
        st.info("👈 Cole seus dados na esquerda para ver a mágica.")