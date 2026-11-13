
# Development Commands

## Tests

Run all tests:

```bash
pytest -v
```

## Test Coverage

Run tests with coverage report in the terminal and generate an HTML report:

```bash
pytest --cov=material_register --cov-report=term-missing --cov-report=html
```

Open the HTML report:

```bash
open htmlcov/index.html
```

## Ruff

Automatically fix linting issues:

```bash
ruff check --fix
```

Format code:

```bash
ruff format
```
