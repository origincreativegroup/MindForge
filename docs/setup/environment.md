# Environment setup

This project uses [direnv](https://direnv.net/) and `.env` files to manage configuration.

## Loading order

1. `direnv` reads the root `.envrc` and loads variables from `.env` via `use dotenv`.
2. Application-specific `.env` files (e.g. `apps/backend/.env`, `apps/frontend/.env`) can override root values when their services start.
3. Variables defined in the shell or hosting environment take precedence over file-based values.

## Managing secrets

- `.env.example` files provide non-secret templates. Copy them to `.env` and fill in real values for local development.
- Never commit populated `.env` files or secrets to version control; rely on secret stores in production.
- Use `ops/scripts/check-env.sh` to validate that all required variables are set.
