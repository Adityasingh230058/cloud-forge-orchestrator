# Contributing to Cloud Forge Orchestrator

Thank you for your interest in contributing to **Cloud Forge Orchestrator**! We welcome bug reports, feature suggestions, and pull requests.

## 🛠️ Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/cloud-forge-orchestrator.git
   cd cloud-forge-orchestrator
   ```

2. **Create a virtual environment and install in editable mode:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Run the test suite:**
   ```bash
   pytest --cov=cloud_forge --cov-report=term-missing tests/
   ```

## 📋 Pull Request Guidelines

- Ensure all new features have corresponding unit tests under `tests/`.
- Keep code formatted according to PEP 8 / `black`.
- Use descriptive commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) specification (`feat:`, `fix:`, `docs:`, `test:`).
- Verify that GitHub Actions CI builds pass cleanly before requesting review.
