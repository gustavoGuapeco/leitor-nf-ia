#!/usr/bin/env bash
# Lê AWS Secrets Manager e grava .env.secrets.local (Linux/macOS/WSL).
# Uso: ./scripts/fetch-secrets.sh SECRET_ID [REGION]
#   ou: AWS_SECRET_ID=... AWS_DEFAULT_REGION=... ./scripts/fetch-secrets.sh

set -euo pipefail

SECRET_ID="${1:-${AWS_SECRET_ID:-}}"
REGION="${2:-${AWS_DEFAULT_REGION:-${AWS_REGION:-}}}"

if [[ -z "$SECRET_ID" ]]; then
  echo "Uso: $0 <secret-id> [region]" >&2
  echo "  ou defina AWS_SECRET_ID" >&2
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "AWS CLI não encontrado no PATH." >&2
  exit 1
fi

OUT_FILE=".env.secrets.local"
AWS_ARGS=(secretsmanager get-secret-value --secret-id "$SECRET_ID" --query SecretString --output text)
if [[ -n "$REGION" ]]; then
  AWS_ARGS+=(--region "$REGION")
fi

RAW="$(aws "${AWS_ARGS[@]}")"
RAW_TRIM="${RAW#"${RAW%%[![:space:]]*}"}"
RAW_TRIM="${RAW_TRIM%"${RAW_TRIM##*[![:space:]]}"}"

{
  echo "# Gerado por scripts/fetch-secrets.sh — não commitar"
  echo "# SecretId: $SECRET_ID"
  if [[ "$RAW_TRIM" == \{* ]]; then
    if ! command -v jq >/dev/null 2>&1; then
      echo "Segredo JSON requer 'jq' instalado, ou use segredo em texto puro (só a chave)." >&2
      exit 1
    fi
    while IFS= read -r line; do
      [[ -n "$line" ]] && echo "$line"
    done < <(echo "$RAW_TRIM" | jq -r 'to_entries[] | select(.key | test("^[A-Z][A-Z0-9_]*$")) | "\(.key)=\(.value)"')
    if ! echo "$RAW_TRIM" | jq -e '.OPENAI_API_KEY' >/dev/null 2>&1; then
      echo "JSON precisa incluir OPENAI_API_KEY (maiúsculas)." >&2
      exit 1
    fi
  else
    echo "OPENAI_API_KEY=$RAW_TRIM"
  fi
} >"$OUT_FILE"

echo "Escrito $OUT_FILE"
