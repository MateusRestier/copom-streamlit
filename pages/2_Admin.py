import sys
import os
import shutil
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import api_get, get_api_url

import streamlit as st
import pandas as pd

st.title("Administracao")
st.caption("Gerencie documentos, inicie ingestas e inspecione o banco de dados.")

tab_docs, tab_ingest, tab_db = st.tabs(["Documentos", "Ingerir", "Banco"])

# ---------------------------------------------------------------------------
# Tab 1 — Documentos
# ---------------------------------------------------------------------------
with tab_docs:
    st.subheader("Documentos indexados")

    docs_data = api_get("/documents")

    # Normalize: the API may return a list directly or {"documents": [...]}
    if isinstance(docs_data, list):
        documents = docs_data
    else:
        documents = docs_data.get("documents", [])

    st.metric("Total de documentos", len(documents))

    if documents:
        rows = []
        for doc in documents:
            row = {
                "ID": doc.get("id", ""),
                "Titulo": doc.get("title", ""),
                "Tipo": doc.get("doc_type", ""),
                "Data da reuniao": doc.get("meeting_date", ""),
                "URL": doc.get("url", ""),
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Make URL column clickable via column_config
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "URL": st.column_config.LinkColumn("URL", display_text="Abrir PDF"),
            },
            hide_index=True,
        )
    else:
        st.info("Nenhum documento encontrado. Use a aba 'Ingerir' para adicionar documentos.")

# ---------------------------------------------------------------------------
# Tab 2 — Ingerir
# ---------------------------------------------------------------------------
with tab_ingest:
    st.subheader("Iniciar ingesta de documentos")

    _pipeline_available = shutil.which("copom-pipeline") is not None

    if not _pipeline_available:
        st.info(
            "A ingesta nao pode ser executada a partir desta interface em producao. "
            "O comando `copom-pipeline` precisa estar instalado localmente."
        )
        st.write("**Para atualizar o banco de dados, execute localmente:**")
        st.code(
            "cd copom-vector-pipeline\n"
            "copom-pipeline --doc-type all --from-date 2026-01-01",
            language="bash",
        )
        st.write("Consulte o `DEPLOYMENT.md` do repositorio `copom-vector-pipeline` para instrucoes completas.")
    else:
        st.write(
            "Execute o pipeline de coleta e indexacao de Atas e Comunicados do COPOM. "
            "Requer que o `copom-pipeline` esteja instalado e acessivel no PATH."
        )

    if _pipeline_available:
        with st.form("ingest_form"):
            doc_type_option = st.selectbox(
                "Tipo de documento",
                options=["Atas e Comunicados", "Atas", "Comunicados"],
            )

            date_from_ingest = st.date_input(
                "Data inicial",
                help="Data de inicio do periodo de coleta.",
            )

            date_to_ingest = st.date_input(
                "Data final (opcional)",
                value=None,
                help="Data de fim do periodo de coleta. Deixe em branco para coletar ate hoje.",
            )

            submit_ingest = st.form_submit_button("Iniciar Ingesta", type="primary")

        if submit_ingest:
            doc_type_map = {
                "Atas e Comunicados": "all",
                "Atas": "ata",
                "Comunicados": "comunicado",
            }
            doc_type_arg = doc_type_map[doc_type_option]

            pipeline_dir_env = os.environ.get("COPOM_PIPELINE_DIR", "../copom-vector-pipeline")
            _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pipeline_dir = os.path.normpath(os.path.join(_repo_root, pipeline_dir_env))

            cmd = [
                "copom-pipeline",
                "--doc-type", doc_type_arg,
                "--from-date", date_from_ingest.isoformat(),
            ]
            if date_to_ingest:
                cmd += ["--to-date", date_to_ingest.isoformat()]

            st.info(f"Executando: `{' '.join(cmd)}`")
            st.info(f"Diretorio: `{pipeline_dir}`")

            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=pipeline_dir,
                    bufsize=1,
                )
            except FileNotFoundError:
                st.error(
                    "Comando `copom-pipeline` nao encontrado. "
                    "Verifique se o pacote esta instalado e se o PATH esta correto."
                )
                proc = None

            if proc is not None:
                st.subheader("Log em tempo real")
                log_area = st.empty()
                lines: list[str] = []

                for line in proc.stdout:
                    lines.append(line.rstrip())
                    visible = lines[-100:]
                    log_area.code("\n".join(visible), language="text")

                proc.wait()

                if proc.returncode == 0:
                    st.success(f"Pipeline concluido com sucesso (codigo de saida: {proc.returncode}).")
                else:
                    st.error(f"Pipeline encerrou com erro (codigo de saida: {proc.returncode}).")

# ---------------------------------------------------------------------------
# Tab 3 — Banco
# ---------------------------------------------------------------------------
with tab_db:
    st.subheader("Estatisticas do banco de dados")

    db_docs_data = api_get("/documents")

    if isinstance(db_docs_data, list):
        db_documents = db_docs_data
    else:
        db_documents = db_docs_data.get("documents", [])

    total_docs = len(db_documents)

    # Derive date range from documents
    dates = [
        d.get("meeting_date")
        for d in db_documents
        if d.get("meeting_date")
    ]
    dates_sorted = sorted(dates) if dates else []
    date_min = dates_sorted[0] if dates_sorted else "—"
    date_max = dates_sorted[-1] if dates_sorted else "—"

    # Count by type
    type_counts: dict[str, int] = {}
    for d in db_documents:
        t = d.get("doc_type") or "desconhecido"
        type_counts[t] = type_counts.get(t, 0) + 1

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de documentos", total_docs)
    col2.metric("Data mais antiga", date_min)
    col3.metric("Data mais recente", date_max)

    if type_counts:
        st.write("**Distribuicao por tipo:**")
        for tipo, count in sorted(type_counts.items()):
            st.write(f"- {tipo}: {count}")

    st.divider()
    st.write("**Inspecao detalhada do banco**")
    st.write(
        "Para inspecionar chunks, embeddings e metadados diretamente, execute o utilitario de banco:"
    )

    _repo_root_db = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pipeline_dir_env_db = os.environ.get("COPOM_PIPELINE_DIR", "../copom-vector-pipeline")
    pipeline_dir_db = os.path.normpath(os.path.join(_repo_root_db, pipeline_dir_env_db))

    st.code(f"cd {pipeline_dir_db} && python scripts/db_crud.py stats", language="bash")

    st.caption(f"API conectada em: {get_api_url()}")
