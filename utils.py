import os
import sys
from pathlib import Path

import httpx
import streamlit as st
from dotenv import load_dotenv

# Load .env from the repo root (one level up if running from pages/, same dir if running from root)
_REPO_ROOT = Path(__file__).parent
load_dotenv(_REPO_ROOT / ".env")


def get_api_url() -> str:
    return os.environ.get("COPOM_API_URL", "http://localhost:8001").rstrip("/")


def get_api_key() -> str:
    return os.environ.get("COPOM_API_KEY", "")


def _headers() -> dict:
    key = get_api_key()
    if key:
        return {"X-API-Key": key}
    return {}


def api_get(path: str, timeout: float = 60.0, retries: int = 1) -> dict | list:
    """Perform a GET request to the COPOM API. Retries once on timeout (handles Render cold start)."""
    url = f"{get_api_url()}{path}"
    for attempt in range(retries + 1):
        try:
            response = httpx.get(url, headers=_headers(), timeout=timeout)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            if attempt < retries:
                continue
            st.error("A requisicao excedeu o tempo limite. Tente novamente.")
            st.stop()
        except httpx.ConnectError:
            st.error(f"Nao foi possivel conectar a API em {get_api_url()}. Verifique se o servidor esta rodando.")
            st.stop()
        except httpx.HTTPStatusError as e:
            st.error(f"Erro na API: {e.response.status_code} — {e.response.text}")
            st.stop()
        except Exception as e:
            st.error(f"Erro inesperado: {e}")
            st.stop()


def api_post(path: str, body: dict) -> dict | list:
    """Perform a POST request to the COPOM API. Raises st.stop() on error."""
    url = f"{get_api_url()}{path}"
    try:
        response = httpx.post(url, json=body, headers=_headers(), timeout=120.0)
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        st.error(f"Nao foi possivel conectar a API em {get_api_url()}. Verifique se o servidor esta rodando.")
        st.stop()
    except httpx.TimeoutException:
        st.error("A requisicao excedeu o tempo limite (120s). O modelo pode estar sobrecarregado — tente novamente.")
        st.stop()
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", e.response.text)
        except Exception:
            detail = e.response.text
        if e.response.status_code == 503:
            st.warning(detail)
        else:
            st.error(f"Erro na API ({e.response.status_code}): {detail}")
        st.stop()
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        st.stop()
