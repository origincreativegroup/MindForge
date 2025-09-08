# MindForge - AI-Powered Creative Workflow Intelligence

MindForge is a monorepo for AI-powered creative workflow intelligence with a FastAPI backend, React frontend, and AI orchestration packages.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap Environment
Install required tools first:
- `npm install -g pnpm` - Install pnpm package manager
- `pip3 install poetry` - Install Poetry for Python dependency management

### Core Setup Commands
Bootstrap, build, and test the repository:
- `pnpm install` - Install JS dependencies (~15 seconds). NEVER CANCEL. Set timeout to 60+ seconds.
- `pnpm approve-builds` - Approve esbuild scripts (interactive, select esbuild and approve)
- Fix pyproject.toml if needed:
  - Ensure `python = ">=3.11,<4.0"`
  - Ensure `package-mode = false`
  - Use `[tool.poetry.group.dev.dependencies]` instead of `[tool.poetry.dev-dependencies]`
- `poetry install` - Install Python dependencies (~20 seconds). NEVER CANCEL. Set timeout to 60+ seconds.

### Build and Test Commands
- `make build` - Build frontend (~3 seconds). NEVER CANCEL. Set timeout to 60+ seconds.
- `make test` - Run all tests (~2 seconds, 31 tests). NEVER CANCEL. Set timeout to 60+ seconds.
- `poetry run ruff check apps packages` - Python linting (finds ~70 style issues)
- `poetry run mypy apps/backend` - Type checking

### Development Servers
ALWAYS run the bootstrapping steps first before starting servers.

Frontend development:
- `make dev` or `pnpm -C apps/frontend dev` - Start Vite dev server on http://localhost:5173/

Backend development:
- `cd apps/backend && poetry run uvicorn app:app --reload --port 8000` - Start FastAPI server on http://127.0.0.1:8000/
- Backend serves both API endpoints and HTML interface
- API documentation available at `/docs`
- Backend runs in simple mode without database by default

### Alternative Commands
- `./run.sh` - Alternative way to run backend (from repo root, but has import path issues)

## Validation

### Manual Testing Scenarios
Always manually validate changes by testing these complete workflows:

**Backend API Testing:**
1. Start backend: `cd apps/backend && poetry run uvicorn app:app --port 8001`
2. Test home page: `curl http://127.0.0.1:8001/` (should return HTML)
3. Test API docs: visit http://127.0.0.1:8001/docs (should show Swagger UI)
4. Backend serves without errors and shows configuration messages

**Frontend Development Testing:**
1. Start frontend: `make dev`
2. Should start Vite server on port 5173 in ~173ms
3. Verify server starts without errors

**Build Pipeline Testing:**
1. Run full build: `make build` (should complete in ~3 seconds)
2. Run tests: `make test` (should pass 31 tests in ~2 seconds)
3. Check linting: `poetry run ruff check apps packages` (shows code style issues)

### Critical Timeouts and Warnings
- **NEVER CANCEL** any build or install commands
- `pnpm install`: NEVER CANCEL - takes ~15 seconds, set timeout to 60+ minutes
- `poetry install`: NEVER CANCEL - takes ~20 seconds, set timeout to 60+ minutes
- `make build`: NEVER CANCEL - takes ~3 seconds, set timeout to 60+ minutes
- `make test`: NEVER CANCEL - takes ~2 seconds, set timeout to 60+ minutes

### Code Quality Requirements
Always run these before committing:
- `make test` - All tests must pass
- `poetry run ruff check apps packages` - Python linting (many existing issues, don't break new functionality fixing them)

## Project Structure

### Key Directories
- `apps/backend/` - FastAPI application with AI services
- `apps/frontend/` - React + Vite + Tailwind frontend
- `packages/ai_core/` - LLM orchestration and prompts
- `packages/integrations/` - External service connectors
- `packages/ui/` - Shared React components
- `tests/` - Test suite (31 tests including async tests)

### Important Files
- `pyproject.toml` - Python dependencies and configuration
- `package.json` - Root workspace configuration
- `pnpm-workspace.yaml` - PNPM workspace setup
- `Makefile` - Build and development commands
- `apps/frontend/package.json` - Frontend dependencies
- `apps/backend/app.py` - Main FastAPI application

### Configuration Notes
- Backend runs in simple mode by default (no database required)
- Tests require pytest-asyncio for async test support
- Frontend uses Vite for fast development and building
- Python 3.11+ required due to langchain dependency
- Monorepo uses pnpm workspaces for JS packages

## Common Tasks

### Adding Dependencies
JavaScript/Node.js:
- `pnpm add <package>` (from frontend directory)

Python:
- `poetry add <package>` (from repo root)
- `poetry add --group dev <package>` (for dev dependencies)

### Database Mode
- Set `USE_DATABASE=true` environment variable to enable database features
- Default mode is simple/in-memory processing

### AI Features
- Set `OPENAI_API_KEY` environment variable to enable LLM features
- Backend warns when API key is not set

### Known Issues
- Backend import path issues when running `./run.sh` from repo root (use `cd apps/backend && poetry run uvicorn app:app` instead)
- ~70 Python linting issues exist (don't feel obligated to fix all)
- Some mypy type checking errors present
- No Docker configuration currently available
- Frontend has no lint script configured

### Repository Stats
- 31 tests (all passing with async support)
- ~200 JS dependencies installed via pnpm
- ~60 Python packages installed via poetry
- Build time: ~3 seconds
- Test time: ~2 seconds
- Install time: ~35 seconds total (JS + Python)