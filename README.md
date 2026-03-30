# leitor-nf-ia

API FastAPI que analisa notas fiscais veterinárias (PDF/imagem) com **OpenAI** (multimodal), comparando com um procedimento informado.

## Configuração

Na **raiz do repositório** (mesma pasta que `pyproject.toml`), são carregados, por ordem:
**`.env.example`** → **`.env`** → **`.env.local`** (o último sobrescreve).  
Variáveis de ambiente do sistema **vazias** não sobrescrevem os ficheiros (`env_ignore_empty`).

```bash
# Linux/macOS
cp .env.example .env

# Windows PowerShell
copy .env.example .env
```

Edite **`.env`**, defina **`OPENAI_API_KEY`** (obrigatório para `/analisar`) e reinicie o servidor.

## Execução (somente Docker)

Com Docker Desktop / daemon ativo, execute na raiz do projeto:

```bash
docker compose up --build
```

A API ficará disponível em `http://localhost:8000` e a documentação interativa em
`http://localhost:8000/docs`.

Para rodar em background:

```bash
docker compose up --build -d
```

Para parar e remover os containers:

```bash
docker compose down
```

## Variáveis de ambiente

Ver `.env.example`.

## Docker (comando alternativo sem Compose)

Se preferir, também é possível executar sem Compose:

```bash
docker build -t leitor-nf-ia .
docker run --rm -p 8000:8000 --env-file .env leitor-nf-ia
```

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

Use o query parameter `debug=true` para incluir o objeto **`debug`** na resposta JSON (além dos campos normais de análise).

O objeto **`debug`** pode incluir, entre outros:

- **`provedor`**, **`modelo`**: identificação do provedor e do modelo configurados
- **`provider_latency_ms`**: tempo aproximado da chamada ao provedor
- **`request_id`**: correlaciona com o header `X-Request-ID`, se enviado
- **`tokens_entrada`**, **`tokens_saida`**, **`tokens_total`**: uso de tokens quando a API do provedor (ex.: OpenAI) devolve `usage`
- **`texto_extraido_completo`**: transcrição textual completa do documento pedida ao modelo em modo debug (estilo OCR); pode vir vazio se o modelo não preencher

Resposta de análise (sem o prefixo `debug`): **`procedimentos_aprovados`** (itens que sustentam a aprovação após regras), **`todos_procedimentos`** (todos os procedimentos/serviços identificados na nota), **`aprovado`**, **`confidence`**.

```bash
curl.exe -sS -X POST "http://localhost:8000/analisar?debug=true" -F "procedimento=Consulta clínica" -F "arquivo=@C:\caminho\para\nota.png;type=image/png"
```

### Exemplo com JPEG

```bash
curl.exe -sS -X POST "http://localhost:8000/analisar" -F "procedimento=Exame de sangue" -F "arquivo=@C:\caminho\para\foto.jpg;type=image/jpeg"
```
