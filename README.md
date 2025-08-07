## Desktop Assistant (Local LLM via LM Studio)

Python desktop assistant powered by a local LLM using LM Studio's OpenAI-compatible server. It can interpret natural language to:
- Open local files
- Search the web in Brave
- Search YouTube

Voice input and richer actions will be added in follow-up commits.

### Prerequisites
- Python 3.10+
- Windows 10/11
- [LM Studio](https://lmstudio.ai/) installed
- In LM Studio, download a chat-capable model (e.g., Llama 3.1 Instruct or similar)
- Enable the OpenAI-compatible local server in LM Studio (default base URL: `http://localhost:1234/v1`)
  - Note the model name as it appears in the server panel; use that as `LMSTUDIO_MODEL`

### Quick Start
1) Clone and open this folder in a terminal.

2) (Optional) Create and activate a virtual environment:
   - PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

3) Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4) Configure environment. Create a `.env` file with at least:
   ```
   LMSTUDIO_BASE_URL=http://localhost:1234/v1
   LMSTUDIO_MODEL=<your_model_name_from_LM_Studio>
   # Optional: specify Brave path if auto-detect fails
   # BRAVE_PATH=C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe
   ```

5) In LM Studio, ensure the local server is running and the selected model is active in the server panel.

6) Run the assistant (text mode):
   ```powershell
   python -m assistant.main --text "open youtube and search for lo-fi beats"
   ```

Example commands you can type:
- "open brave and search for rust tutorials"
- "search youtube for python packaging"
- "open file C:\\Users\\<you>\\Documents\\notes.txt"

### Configuration
Set via environment variables:
- `LMSTUDIO_BASE_URL` (default: `http://localhost:1234/v1`)
- `LMSTUDIO_MODEL` (required unless your LM Studio server default matches `local-model`)
- `BRAVE_PATH` (optional; auto-detect tries common install locations)

### Roadmap
- Basic microphone input (offline STT via Vosk) — added minimal fixed-duration capture
- Add TTS for spoken responses
- Expand action set (open apps, control system, file search, etc.)

### Voice (Vosk) — minimal test
1) Download a small Vosk model (e.g., `vosk-model-small-en-us-0.15`) and extract it.
2) Set `VOSK_MODEL_PATH` to that folder in your environment or `.env`.
3) Test a 5-second capture:
   ```powershell
   python -c "from assistant.speech import transcribe_fixed_duration as t; print(t(5))"
   ```


