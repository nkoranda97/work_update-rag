# Work‑Update RAG Prototype

At my lab we send **bi‑weekly work‑update emails**—each member outlines the projects they’re tackling and their current status. After a few cycles, useful information gets buried in everyone’s inbox.

This repo is a mini project for **Retrieval‑Augmented Generation (RAG)** app built with **FastAPI**:

* 📨 Parses the raw `.eml` messages
* 🔍 Indexes them with Sentence‑Transformers + FAISS
* 💬 Lets you query the corpus through a tiny web GUI
* 🤖 Uses OpenAI GPT‑4o‑mini to craft answers that cite dates & snippets