# ToMarkdown.com.ar 🚀

Una utilidad web ultra-rápida (SPA) para convertir archivos PDF, Word (.docx), PowerPoint (.pptx) y texto (.txt) a código Markdown puro, optimizando el consumo de tokens en LLMs.

## 🧠 Stack Tecnológico
* **Frontend:** Next.js 16 (App Router), Tailwind CSS v4, TypeScript.
* **Backend:** FastAPI, Python 3.12+ (pypdf, python-docx, python-pptx), gestionado con `uv`.
* **Seguridad:** Procesamiento 100% en memoria (cero escrituras en disco), límite estricto de payload de 10MB, rate limiting por IP.

## 📄 Formatos Soportados
| Extensión | Tipo | Motor |
|---|---|---|
| `.pdf` | Documento PDF | `pypdf` |
| `.docx` | Documento Word | `python-docx` |
| `.pptx` | Presentación PowerPoint | `python-pptx` |
| `.txt` | Texto plano | nativo (UTF-8 / Latin-1) |

## ⚙️ Desarrollo Local
1. Backend: `cd backend && uv run uvicorn main:app --reload`
2. Frontend: `cd frontend && pnpm dev`