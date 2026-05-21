---
title: DocBuddy
emoji: 🩺
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# DocBuddy 🩺
### AI-Powered Clinical Diagnostic Assistant

DocBuddy is a full-stack medical AI assistant that routes patient queries through a **multi-specialist LangGraph agent pipeline**. Users can describe symptoms, check drug interactions, get personalized diet plans, find nearby clinics, and upload medical images — all through a clean conversational interface.

> ⚠️ **Disclaimer:** DocBuddy is an AI research/portfolio project. It does not constitute medical advice. Always consult a licensed physician for health concerns.

---

## Architecture

```
User → React Frontend
         ↓ FormData (text + optional image)
       FastAPI Backend (/api/chat)
         ↓
       LangGraph StateGraph
         ↓
       Orchestrator LLM (Llama-3.3-70B)
         ↓ tool_calls routing
    ┌────┴─────────────────────────────────┐
    │                                      │
 Symptoms Tool          Medications Tool   Diet Tool
 (OpenBioLLM-8B)       (FDA + NIH APIs)  (Llama-3.1-8B)
    │                                      │
 Doctors Tool                         Vision Tool
 (OpenStreetMap)               (Llama-3.2-11B-Vision)
```

Each user session is isolated via a `thread_id` with in-memory LangGraph checkpointing, giving the agent conversation history within a session.

---

## Features

- **Symptom Analysis** — Routes to a specialized OpenBioLLM model for differential diagnosis with urgency triage
- **Drug Interaction Checker** — Queries the NIH RxNorm API for live interaction data; falls back to the FDA label database for single-drug lookups
- **Diet Planning** — A dedicated Llama-3.1-8B nutrition model generates condition-specific meal plans
- **Doctor/Clinic Finder** — Searches globally via OpenStreetMap Nominatim with specialty-aware query mapping
- **Medical Image Analysis** — Encodes uploaded images in Base64 and sends them to Llama-3.2-11B-Vision; includes an offline fallback cache for common image types
- **Session Memory** — Conversations persist within a session via LangGraph's `MemorySaver` checkpointer

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS v4, react-markdown |
| Backend | Python, FastAPI, python-multipart |
| Agent Framework | LangGraph, LangChain Core |
| LLM Provider | HuggingFace Inference API |
| External APIs | FDA Drug Label API, NIH RxNorm API, OpenStreetMap Nominatim |

### Models Used

| Role | Model |
|---|---|
| Orchestrator / Router | `meta-llama/Llama-3.3-70B-Instruct` |
| Clinical Diagnostics | `aaditya/Llama3-OpenBioLLM-8B` |
| Nutrition Specialist | `meta-llama/Llama-3.1-8B-Instruct` |
| Medical Vision | `meta-llama/Llama-3.2-11B-Vision-Instruct` |

---

## Project Structure

```
DocBuddy/
├── Dockerfile
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app, CORS, static file serving
│   │   ├── agent/
│   │   │   ├── graph.py          # LangGraph StateGraph definition
│   │   │   ├── nodes.py          # Orchestrator LLM node + routing logic
│   │   │   ├── state.py          # PatientState TypedDict
│   │   │   └── tools/
│   │   │       ├── symptoms.py   # Differential diagnosis tool
│   │   │       ├── medications.py# FDA + NIH drug interaction tool
│   │   │       ├── diet.py       # Diet plan generation tool
│   │   │       ├── doctors.py    # OpenStreetMap clinic finder tool
│   │   │       └── vision.py     # Medical image analysis tool
│   │   └── utils/
│   │       └── hf_client.py      # HuggingFace LLM factory functions
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx               # Session state, message handling
    │   └── components/
    │       ├── ChatWindow.jsx    # Message renderer with ReactMarkdown
    │       └── ChatInput.jsx     # Text + file upload input
    └── package.json
```

---

## Deployment (HuggingFace Spaces)

This project is deployed as a Docker Space on HuggingFace. The Dockerfile builds the React frontend and serves it as static files through FastAPI on port **7860**.

### Required Secrets

Add these in your Space settings under **Settings → Repository Secrets**:

| Secret | Description |
|---|---|
| `HUGGINGFACEHUB_API_TOKEN` | Your HuggingFace API token |
| `DEVELOPER_EMAIL` | Contact email for NIH API good-citizen header |

No `.env` file is needed — secrets are injected as environment variables automatically.

---

## Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- A free [HuggingFace](https://huggingface.co/) account with an API token

### 1. Clone the repository

```bash
git clone https://github.com/PrithirajP/DocBuddy.git
cd DocBuddy
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv myvenv
source myvenv/bin/activate  # Windows: myvenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your environment file
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
HUGGINGFACEHUB_API_TOKEN=your_token_here
DEVELOPER_EMAIL=your_email@example.com
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## How It Works

1. The user sends a message (and optionally a file) from the React frontend.
2. FastAPI receives the `multipart/form-data` request, saves any uploaded file, and constructs a prompt.
3. The prompt enters the **LangGraph StateGraph** as a `HumanMessage`.
4. The **Orchestrator LLM** (Llama-3.3-70B) reads the system prompt's routing rules and decides which tool to call.
5. LangGraph's `ToolNode` executes the selected tool, which may call an external API or a specialist LLM.
6. The tool result is appended to the message state and the Orchestrator summarizes it for the user.
7. The final response is returned to the frontend and rendered as Markdown.

---

## Known Limitations / Future Work

- **Session persistence** — Memory resets on server restart (RAM-only). A future version would use a persistent checkpointer (e.g., Redis or PostgreSQL).
- **Authentication** — No user auth. Production deployment would require JWT or session-based auth.
- **File storage** — Uploaded images are saved locally to `uploads/` with no cleanup. A production system would use object storage (S3/GCS) with lifecycle policies.
- **Vision API** — The HuggingFace Inference API format for multimodal models may require updates as the API evolves.

---

## License

MIT License — see [LICENSE](LICENSE) for details.