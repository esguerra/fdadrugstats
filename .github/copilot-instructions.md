# Python Best Practices Copilot Instructions

## Project Structure

- Use clear project structure: separate directories for source code, tests, docs, latex, articles and config.
- Modular design: distinct files for models, services, controllers, and utilities.
- Manage configuration with environment variables.

## Coding Standards

- Add typing annotations to all functions and classes, including return types.
- Add descriptive docstrings to all functions and classes (PEP 257 convention). Update existing docstrings if needed.
- Keep all existing comments in files.
- Use Ruff for code style consistency.
- Follow https://github.com/DavidAnson/markdownlint/blob/v0.40.0/doc/md022.md for markdown linting.

## Error Handling & Logging

- Implement robust error handling and logging, including context capture.

## Testing

- Use pytest (not unittest) and pytest plugins for all tests.
- Place all tests in ./tests. Create __init__.py files as needed.
- All tests must have typing annotations and docstrings.
- For type checking in tests, import:
  ```python
  from _pytest.capture import CaptureFixture
  from _pytest.fixtures import FixtureRequest
  from _pytest.logging import LogCaptureFixture
  from _pytest.monkeypatch import MonkeyPatch
  from pytest_mock.plugin import MockerFixture
  ```

## Documentation & Dependency Management

- Use docstrings and README files for documentation.
- Use https://github.com/astral-sh/uv and virtual environments for dependency management.

## CI/CD

- Use GitHub Actions or GitLab CI for CI/CD.

## AI-Friendly Coding

- Provide code snippets and explanations optimized for clarity and AI-assisted development.

## Project Aims

- Use information from the United States Food and Drug Administration (FDA) to build an application for statisitcs on drug approvals and recalls.

## Virtual Environments

- Use `uv` for creating and managing virtual environments.
- Load the virtual environment before running scripts or installing packages.
- Install dependencies using `uv pip install -r requirements.txt`. 