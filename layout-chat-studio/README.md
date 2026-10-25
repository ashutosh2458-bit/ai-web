# Layout Chat Studio

A website layout builder where **Python runs in the browser via WebAssembly (Pyodide)**.
Chat with the built-in assistant or use the tools, then copy or download the HTML, CSS and optional JavaScript.
There is no server, no build step and no API key.

## Deploy on GitHub
1. Create a repo and upload this folder's contents to the `main` branch (keep `web/` and `.github/`).
2. Settings -> Pages -> Source: **GitHub Actions**.
3. The workflow publishes `web/`. Your site appears at `https://<user>.github.io/<repo>/`.

## Run locally
```
python3 -m http.server -d web 8000
```
Open http://localhost:8000 (it needs internet once to load Pyodide from a CDN).

## Extend it
All logic is in `web/app.py`: add sections in `SEC`, `BLOCK` and `section_html()`, and teach the chatbot new phrases in `chat()`.
