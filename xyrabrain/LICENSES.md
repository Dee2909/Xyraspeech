# Licenses & Compliance Audit

This document records license classifications for all code, runtime dependencies, and candidate models utilized in **XyraBrain**.

---

## 1. Core Application

| Component | License | Notes | Commercial Permitted |
| :--- | :--- | :--- | :--- |
| **XyraBrain Codebase** | MIT License | Copyright (c) 2026 XyraTech | Yes |

---

## 2. Python Dependencies

| Package | License | Distribution / Commercial Terms |
| :--- | :--- | :--- |
| `fastapi` | MIT | Permissive, commercial allowed |
| `uvicorn` | BSD-3-Clause | Permissive, commercial allowed |
| `pydantic` | MIT | Permissive, commercial allowed |
| `httpx` | BSD-3-Clause | Permissive, commercial allowed |
| `python-dotenv` | BSD-3-Clause | Permissive, commercial allowed |
| `pytest` | MIT | Development testing only |

---

## 3. Local Model Checkpoints & Runtimes

| Model / Runtime | Upstream Author | License / Terms | Commercial Gate Review |
| :--- | :--- | :--- | :--- |
| **Ollama Runtime** | Ollama Inc. | MIT License | Permitted locally |
| **Mistral-7B / mistral:latest** | Mistral AI | Apache 2.0 | Permitted for commercial use |
| **Llama 3.2 (3B)** | Meta AI | Llama 3.2 Community License | Permitted up to 700M monthly active users |
| **AI4Bharat Indic-TTS** | AI4Bharat / IIT Madras | MIT / CC-BY-4.0 | Requires attribution |
| **faster-whisper** | SYSTRAN / OpenAI | MIT / Apache 2.0 | Permitted for commercial use |
