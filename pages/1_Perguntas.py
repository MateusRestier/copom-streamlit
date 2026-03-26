import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import api_post

import streamlit as st

st.title("Perguntas ao COPOM")
st.caption(
    "Faça perguntas em linguagem natural sobre as Atas e Comunicados do COPOM. "
    "O sistema busca os trechos mais relevantes e gera uma resposta fundamentada."
)

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filtros")

    doc_type_label = st.selectbox(
        "Tipo de documento",
        options=["Todos", "Ata", "Comunicado"],
    )

    date_from = st.date_input(
        "Data inicial",
        value=None,
        help="Filtrar documentos a partir desta data (opcional).",
    )

    date_to = st.date_input(
        "Data final",
        value=None,
        help="Filtrar documentos ate esta data (opcional).",
    )

# --- Main area ---
question = st.text_input(
    "Pergunta",
    placeholder="Ex: Qual foi a decisao do COPOM sobre a taxa Selic em agosto de 2023?",
    label_visibility="collapsed",
)

ask_button = st.button("Perguntar", type="primary")

if ask_button:
    if not question.strip():
        st.warning("Digite uma pergunta antes de continuar.")
    else:
        # Build request body
        body: dict = {"question": question}

        if doc_type_label != "Todos":
            body["doc_type"] = doc_type_label.lower()

        if date_from:
            body["date_from"] = date_from.isoformat()

        if date_to:
            body["date_to"] = date_to.isoformat()

        with st.spinner("Consultando documentos..."):
            result = api_post("/ask", body)

        # --- Answer ---
        st.subheader("Resposta")
        with st.container(border=True):
            st.markdown(result.get("answer", "Sem resposta."))

        # --- Sources ---
        sources = result.get("sources", [])
        if sources:
            st.subheader("Fontes consultadas")
            for i, source in enumerate(sources, start=1):
                title = source.get("title") or f"Documento {i}"
                meeting_date = source.get("meeting_date", "")
                doc_type = source.get("doc_type", "")
                pdf_url = source.get("url", "")
                excerpt = source.get("excerpt") or source.get("text", "")

                label = f"{i}. {title}"
                if meeting_date:
                    label += f"  —  {meeting_date}"
                if doc_type:
                    label += f"  [{doc_type}]"

                with st.expander(label):
                    cols = st.columns([2, 1])
                    with cols[0]:
                        if meeting_date:
                            st.write(f"**Reuniao:** {meeting_date}")
                        if doc_type:
                            st.write(f"**Tipo:** {doc_type}")
                    with cols[1]:
                        if pdf_url:
                            st.markdown(f"[Abrir PDF]({pdf_url})")

                    if excerpt:
                        st.divider()
                        st.markdown(f"*{excerpt}*")

        # --- Metadata ---
        processing_time = result.get("processing_time_seconds")
        chunks_used = result.get("chunks_used")
        meta_parts = []
        if processing_time is not None:
            meta_parts.append(f"Tempo de processamento: {processing_time:.1f}s")
        if chunks_used is not None:
            meta_parts.append(f"Trechos utilizados: {chunks_used}")
        if meta_parts:
            st.caption("  |  ".join(meta_parts))
