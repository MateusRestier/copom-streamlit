# Changelog

All notable changes to **copom-streamlit** will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

## [0.3.0] — 2026-03-26

### Added
- Homepage (`Inicio`) with hero section, live document count metrics pulled from the API,
  three-step how-it-works explanation, full technical stack breakdown, ASCII architecture
  diagram, and links to the three GitHub repositories.

### Fixed
- `api_post` now parses the `detail` field from API error responses and displays it
  directly to the user. 503 responses (rate limit, DB errors) are shown as `st.warning`
  instead of `st.error`.
- Ingestion tab in Admin page detects whether `copom-pipeline` is installed via
  `shutil.which` and shows local-run instructions when running in production
  (Streamlit Cloud), preventing a confusing "command not found" failure.
- Added `requirements.txt` to prevent Streamlit Cloud from attempting to use Poetry
  with `pyproject.toml`, which caused deployment failures.

## [0.2.0] — 2026-03-26

### Added
- References section renders as a numbered list `[1]`, `[2]` matching inline citations
  in the answer, with excerpt preview and direct PDF link.
- Admin page ingestion tab streams pipeline output in real time using `subprocess.Popen`.
- `DEPLOYMENT.md`: guide covering Streamlit Cloud setup, secrets management, and
  troubleshooting.

## [0.1.0] — 2026-03-25

### Added
- Initial implementation with two pages: Perguntas (Q&A) and Administracao (Admin).
- Sidebar filters: document type, date range.
- Calls `POST /ask` and renders answer with sources.
- Admin page: document list, ingestion form, database stats tab.
- Dark theme with `primaryColor = "#00b7ff"`.
