# Sabores Observability (Gabartista)

Microserviço em Python/FastAPI para ingestão do dataset `sabores.xlsx` em PostgreSQL e exposição de métricas para o Grafana. Estrutura organizada em camadas (application/infrastructure) seguindo os padrões Gabartista (DDD/Clean, snake_case no banco, UUIDs, timestamps).

## Stack
- Python 3.12 + FastAPI + SQLAlchemy
- PostgreSQL 15 (Docker)
- Pandas para ingestão do Excel
- Docker/Docker Compose

## Como rodar
1. Ajuste variáveis se quiser em `.env` (veja `.env.example`). Defaults: user/pass `analytics`, DB `sabores`, API `:8000`.
2. Suba tudo:
   ```bash
   docker-compose up --build
   ```
   O entrypoint aguarda o DB, cria extensões/tabelas, carrega `data/sabores.xlsx` e sobe o FastAPI.
3. API disponível em `http://localhost:8000` (docs interativas em `/docs`).

## Endpoints principais
- `GET /health` – status
- `GET /metrics/summary` – faturamento total, margem total/% média, ticket médio, total de pedidos
- `GET /metrics/units` – ranking por unidade
- `GET /metrics/categories` – ranking por categoria
- `GET /metrics/monthly` – evolução mensal
- `GET /metrics/waiters` – ranking de garçons
- `GET /metrics/geography` – concentração por cidade/estado

## Estrutura de pastas
- `src/app/config` – settings e carregamento de ambiente
- `src/app/application/services` – regras de ingestão e métricas
- `src/app/infrastructure/db` – models, sessão, migração
- `src/app/infrastructure/cli` – comandos (load_data)
- `src/app/main.py` – FastAPI com rotas
- `data/` – dataset fonte (montado como volume no container)
- `entrypoint.sh` – orquestra migração + carga + API

## Scripts úteis
- Recarregar dados (idempotente, limpa tabelas antes):  
  ```bash
  docker-compose run --rm api python -m app.infrastructure.cli.load_data --file /data/sabores.xlsx
  ```
- Apenas criar esquema:  
  ```bash
  docker-compose run --rm api python -m app.infrastructure.db.migrate
  ```
- Testes (rodam em SQLite in-memory, usando o dataset real):  
  ```bash
  pytest
  ```

## Observabilidade/Grafana
- Grafana pode consumir os endpoints JSON (plugin Infinity) ou conectar direto no Postgres.
- Tabelas: `product`, `unit`, `waiter`, `sale` (fato). Campos derivados: `margin_value`, `margin_pct`, `month_year`.
- Métricas calculadas no banco via agregações SQL, evitando lógica no frontend.

## Notas de modelagem
- IDs em UUID, chaves de negócio preservadas (`product_code`, `unit_code`, `order_code`).
- Campos auditáveis: `created_at`, `updated_at`, `deleted_at`.
- Extensões habilitadas: `uuid-ossp`, `citext` (compatível com padrões Gabartista).
