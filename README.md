# ToMarkdown.com.ar 🚀

Una utilidad web ultra-rápida (SPA) para convertir archivos PDF y Word (.docx) a código Markdown puro, optimizando el consumo de tokens en LLMs.

## 🧠 Stack Tecnológico
* **Frontend:** Next.js 15+ (App Router), Tailwind CSS v4, TypeScript.
* **Backend:** FastAPI, Python 3.12+ (pypdf, python-docx), gestionado con `uv`.
* **Seguridad:** Procesamiento 100% en memoria (cero escrituras en disco), límite estricto de payload de 10MB.

## ⚙️ Desarrollo Local
1. Backend: `cd backend && uv run uvicorn main:app --reload`
2. Frontend: `cd frontend && pnpm dev`