# copom-streamlit

Interface web em [Streamlit](https://streamlit.io) para o sistema **COPOM RAG** — permite fazer perguntas em linguagem natural sobre Atas e Comunicados do Comitê de Política Monetária do Banco Central do Brasil, com respostas geradas por LLM e citações diretas aos documentos originais.

Demo: [copom-rag.streamlit.app](https://copom-rag.streamlit.app)

---

## Funcionalidades

- **Perguntas em linguagem natural** sobre atas e comunicados do COPOM
- **Filtros por tipo de documento** (Ata / Comunicado) e **período**
- **Respostas com citações inline** `[1][2]` vinculadas aos trechos originais
- **Referências detalhadas**: título, data, tipo, excerpt e link para o PDF
- **Página Admin** com lista de documentos, formulário de ingestion e estatísticas do banco
- **Página Inicio** com métricas ao vivo e descrição da arquitetura do sistema

---

## Arquitetura

Este projeto é a camada de interface do ecossistema COPOM RAG:

```
Banco Central (PDFs)
        │
        ▼
copom-vector-pipeline   ← ingestão, chunking, embeddings
        │
        ▼
PostgreSQL + pgvector   ← armazenamento vetorial (Neon)
        │
        ▼
copom-rag-api           ← busca semântica + geração via Gemini (Render)
        │
        ▼
copom-streamlit         ← interface web (Streamlit Cloud)  ← você está aqui
```

---

## Páginas

### Inicio
- Métricas ao vivo: total de documentos, atas, comunicados e período coberto
- Descrição do pipeline RAG em 3 etapas
- Detalhes da stack técnica e diagrama de arquitetura

### Perguntas
- Input de pergunta com filtros na sidebar (tipo de documento, data inicial/final)
- Resposta em markdown com citações numeradas
- Lista de referências com links para os PDFs originais
- Metadados: tempo de processamento e número de trechos utilizados

### Administração
- **Documentos**: tabela de todos os documentos indexados com link para o PDF
- **Ingerir**: formulário para iniciar ingestion (local) com streaming de logs em tempo real
- **Banco**: estatísticas do banco (total, período, distribuição por tipo)

---

## Stack

| Componente | Tecnologia |
|-----------|-----------|
| Interface | Streamlit >= 1.35 |
| HTTP client | httpx >= 0.27 |
| Configuração | python-dotenv |
| Dados | pandas |
| Python | >= 3.11 |

---

## Como rodar localmente

### Pré-requisitos

- Python 3.11+
- [`copom-rag-api`](https://github.com/mateusfg7/copom-rag-api) rodando (local ou remoto)

### Setup

```bash
git clone https://github.com/mateusfg7/copom-streamlit.git
cd copom-streamlit

pip install -r requirements.txt

cp .env.example .env
# edite .env com a URL da API
```

### Configuração (`.env`)

```env
COPOM_API_URL=http://localhost:8001   # URL da copom-rag-api
COPOM_API_KEY=                        # API Key (deixe vazio se não usar)
COPOM_PIPELINE_DIR=../copom-vector-pipeline  # caminho do pipeline (ingestion local)
```

### Executar

```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`.

---

## Deployment (Streamlit Cloud)

A aplicação faz deploy automático no [Streamlit Community Cloud](https://streamlit.io/cloud) a cada push para `main`.

Configure os secrets no dashboard do Streamlit Cloud:

```toml
COPOM_API_URL = "https://copom-rag-api.onrender.com"
COPOM_API_KEY = ""
```

> O Streamlit Cloud lê os secrets no formato TOML, não `.env`.

Veja [DEPLOYMENT.md](DEPLOYMENT.md) para o guia completo.

---

## Projetos relacionados

- [copom-rag-api](https://github.com/mateusfg7/copom-rag-api) — API RAG com FastAPI + Gemini + pgvector
- [copom-vector-pipeline](https://github.com/mateusfg7/copom-vector-pipeline) — pipeline de ingestão de PDFs do COPOM (parte deste ecossistema)

> A página **Admin** do app permite disparar o `copom-vector-pipeline` localmente via subprocess, com streaming de logs em tempo real. Em produção, o pipeline precisa ser executado manualmente no ambiente local com acesso ao banco Neon.
