import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import api_get

import streamlit as st

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.title("COPOM RAG")
st.subheader("Sistema de busca e resposta sobre as decisoes do Banco Central do Brasil")

st.markdown(
    """
Faça perguntas em linguagem natural sobre as **Atas** e **Comunicados** do Comitê de
Política Monetária (Copom) e receba respostas fundamentadas, com citações diretas aos
documentos originais.
"""
)

st.page_link("pages/1_Perguntas.py", label="Fazer uma pergunta", icon=":material/chat:")

st.divider()

# ---------------------------------------------------------------------------
# Métricas ao vivo
# ---------------------------------------------------------------------------
st.subheader("Base de conhecimento")

data = api_get("/documents")
documents = data if isinstance(data, list) else data.get("documents", [])

total = len(documents)
atas = sum(1 for d in documents if d.get("doc_type") == "ata")
comunicados = sum(1 for d in documents if d.get("doc_type") == "comunicado")
dates = sorted(d.get("meeting_date", "") for d in documents if d.get("meeting_date"))
date_min = dates[0] if dates else "—"
date_max = dates[-1] if dates else "—"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Documentos indexados", total)
col2.metric("Atas do Copom", atas)
col3.metric("Comunicados", comunicados)
col4.metric("Periodo coberto", f"{date_min[:4]} – {date_max[:4]}" if dates else "—")

st.divider()

# ---------------------------------------------------------------------------
# Como funciona
# ---------------------------------------------------------------------------
st.subheader("Como funciona")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("**1. Ingestao**")
    st.markdown(
        "PDFs e textos das Atas e Comunicados do Copom são baixados da API do Banco Central, "
        "fragmentados em trechos e convertidos em vetores de embedding pelo modelo "
        "**Gemini Embedding 001**."
    )

with col_b:
    st.markdown("**2. Busca vetorial**")
    st.markdown(
        "Ao receber uma pergunta, o sistema gera seu embedding e busca os trechos mais "
        "relevantes no banco vetorial usando **similaridade de cosseno** via índice HNSW "
        "do **pgvector**."
    )

with col_c:
    st.markdown("**3. Geracao de resposta**")
    st.markdown(
        "Os trechos recuperados são reordenados pelo modelo **Gemini 2.5 Flash** e usados "
        "como contexto para gerar uma resposta em português, com citações inline "
        "identificando cada fonte."
    )

st.divider()

# ---------------------------------------------------------------------------
# Stack técnica
# ---------------------------------------------------------------------------
st.subheader("Stack tecnica")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Pipeline de ingestao** (`copom-vector-pipeline`)")
    st.markdown(
        """
- Python + **pdfplumber** para extração de texto
- **LangChain TextSplitter** + tiktoken para chunking (500 tokens, overlap 20)
- **Google Gemini Embedding 001** — 1536 dimensões
- **psycopg2** para escrita em lote no PostgreSQL
- Idempotência por SHA-256 do PDF original
- Retry automático com backoff em erros de rate limit (429)
        """
    )

    st.markdown("**Banco de dados**")
    st.markdown(
        """
- **PostgreSQL 17** + extensão **pgvector**
- Índice **HNSW** (m=16, ef_construction=64) para busca aproximada
- Hospedado no **Neon** (serverless, free tier)
        """
    )

with col2:
    st.markdown("**API RAG** (`copom-rag-api`)")
    st.markdown(
        """
- **FastAPI** com lifespan para gerenciamento de conexões
- Pipeline linear: embed → retrieve → rerank → generate
- Reranking por LLM antes da geração (configurável)
- Orçamento de tokens para contexto (`MAX_CONTEXT_TOKENS`)
- Providers de LLM e embedding intercambiáveis via variável de ambiente
- Hospedada no **Render** (free tier, Docker)
        """
    )

    st.markdown("**Interface** (`copom-streamlit`)")
    st.markdown(
        """
- **Streamlit** com multi-page navigation
- Filtros por tipo de documento e período
- Respostas com citações inline `[1][2]` e seção de referências com link para o PDF
- Hospedada no **Streamlit Community Cloud** (free tier)
        """
    )

st.divider()

# ---------------------------------------------------------------------------
# Arquitetura
# ---------------------------------------------------------------------------
st.subheader("Arquitetura")

st.code(
    """\
                    ┌─────────────────────────────┐
                    │     Banco Central do Brasil  │
                    │      API Open Data (BCB)     │
                    └────────────┬────────────────┘
                                 │ PDFs + HTML
                                 ▼
                    ┌─────────────────────────────┐
                    │   copom-vector-pipeline      │
                    │  (roda localmente sob demanda)│
                    │                              │
                    │  download → parse → chunk    │
                    │  → embed (Gemini) → upsert   │
                    └────────────┬────────────────┘
                                 │ embeddings (1536d)
                                 ▼
                    ┌─────────────────────────────┐
                    │   Neon (PostgreSQL + pgvector)│
                    │   tabelas: documents, chunks  │
                    └────────────┬────────────────┘
                                 │ cosine search
                                 ▼
                    ┌─────────────────────────────┐
                    │      copom-rag-api           │
                    │      (Render — Docker)       │
                    │                              │
                    │  embed query → retrieve →   │
                    │  rerank → generate (Gemini)  │
                    └────────────┬────────────────┘
                                 │ JSON (answer + sources)
                                 ▼
                    ┌─────────────────────────────┐
                    │     copom-streamlit          │
                    │  (Streamlit Community Cloud) │
                    └─────────────────────────────┘
""",
    language="text",
)

st.divider()

# ---------------------------------------------------------------------------
# Disponibilidade
# ---------------------------------------------------------------------------
st.subheader("Disponibilidade")

st.markdown(
    """
Todos os serviços rodam em **free tier**. Duas estratégias evitam interrupções por inatividade:
"""
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Render — copom-rag-api**")
    st.markdown(
        """
O Render encerra containers após **15 min sem requisição**. Um monitor do **UptimeRobot**
faz ping no endpoint `/health` a cada 14 minutos, mantendo a API sempre ativa.
        """
    )

with col2:
    st.markdown("**Streamlit Community Cloud**")
    st.markdown(
        """
O Streamlit coloca o app para dormir após **7 dias sem visitante**. Um workflow do
**GitHub Actions** (`keep-alive.yml`) envia uma requisição HTTP ao app três vezes ao dia
— 06:00, 12:00 e 16:00 BRT — impedindo o sleep automático.
        """
    )

st.divider()

# ---------------------------------------------------------------------------
# Repositórios
# ---------------------------------------------------------------------------
st.subheader("Repositorios")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**copom-vector-pipeline**")
    st.markdown("Pipeline de ingestão de dados")
    st.markdown("[github.com/MateusRestier/copom-vector-pipeline](https://github.com/MateusRestier/copom-vector-pipeline)")

with col2:
    st.markdown("**copom-rag-api**")
    st.markdown("API REST de perguntas e respostas")
    st.markdown("[github.com/MateusRestier/copom-rag-api](https://github.com/MateusRestier/copom-rag-api)")

with col3:
    st.markdown("**copom-streamlit**")
    st.markdown("Interface web (este app)")
    st.markdown("[github.com/MateusRestier/copom-streamlit](https://github.com/MateusRestier/copom-streamlit)")
