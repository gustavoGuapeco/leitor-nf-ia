# leitor-nf-ia

API FastAPI que analisa notas fiscais veterinárias (PDF/imagem) com **OpenAI** (multimodal), comparando com um procedimento informado.

## Configuração

Na **raiz do repositório** (mesma pasta que `pyproject.toml`), são carregados, por ordem:
**`.env.example`** → **`.env`** → **`.env.local`** (o último sobrescreve).  
Variáveis de ambiente do sistema **vazias** não sobrescrevem os ficheiros (`env_ignore_empty`).

```bash
copy .env.example .env
```

Edite **`.env`**, defina **`OPENAI_API_KEY`** (obrigatório para `/analisar`) e reinicie o servidor.

## Executar local

```bash
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
.\.venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Documentação interativa: `http://localhost:8000/docs`.

## Variáveis de ambiente

Ver `.env.example`.

## Docker

Com Docker Desktop / daemon ativo:

```bash
docker build -t leitor-nf-ia .
docker run --rm -p 8000:8000 -e OPENAI_API_KEY=sua_chave leitor-nf-ia
```

Ou `docker compose up --build` (use `.env` com `OPENAI_API_KEY`).

## Testar com cURL

Substitua a URL base se a API não estiver em `localhost:8000`. No **PowerShell**, use `curl.exe` (o alias `curl` chama `Invoke-WebRequest` e quebra o `-F`). Em uma linha só evita problema de continuação.

### `GET /health`

```bash
curl.exe -sS http://localhost:8000/health
```

### `GET /ready`

```bash
curl.exe -sS http://localhost:8000/ready
```

### `POST /analisar` (multipart: procedimento + arquivo)

Ajuste o caminho após `@` (PDF):

```bash
curl.exe -sS -X POST "http://localhost:8000/analisar" -H "X-Request-ID: meu-teste-001" -F "procedimento=Vacina antirrábica" -F "arquivo=@C:\caminho\para\nota.pdf;type=application/pdf"
```

Git Bash / Linux / macOS (pode quebrar linhas com `\`):

```bash
curl -sS -X POST "http://localhost:8000/analisar" \
  -H "X-Request-ID: meu-teste-001" \
  -F "procedimento=Vacina antirrábica" \
  -F "arquivo=@./nota.pdf;type=application/pdf"
```

### `POST /analisar` com `debug=true`

```bash
curl.exe -sS -X POST "http://localhost:8000/analisar?debug=true" -F "procedimento=Consulta clínica" -F "arquivo=@C:\caminho\para\nota.png;type=image/png"
```

### Exemplo com JPEG

```bash
curl.exe -sS -X POST "http://localhost:8000/analisar" -F "procedimento=Exame de sangue" -F "arquivo=@C:\caminho\para\foto.jpg;type=image/jpeg"
```
