# MicroPython Development Guidelines

This project uses modern Python tooling and specific coding standards to ensure code quality, maintainability, and compatibility with standard development environments (VS Code, etc.).

## 1. Tooling

We use `uv` for dependency management and `ruff` / `mypy` for code quality.

- **Install Dependencies**: `uv pip install -r pyproject.toml`
- **Linting**: `ruff check .`
- **Type Checking**: `mypy .`

## 2. Dependencies

- **`micropython-esp32-stubs`**: Included in `pyproject.toml` to provide IntelliSense and type checking for MicroPython-specific modules (`machine`, `network`, etc.).

## 3. Import Conventions

### 3.1. Standard Libraries

- **Use `json` instead of `ujson`**.
  - *Why?* In modern MicroPython, `import json` aliases to the optimized `ujson` implementation, so you get the performance of `ujson` with the tooling compatibility of standard Python.
  - *Example*: `import json`

### 3.2. Types

- **Use Type Hints**.
  - *Why?* Improves code quality, enables `mypy` static analysis, and provides better IDE autocomplete. MicroPython ignores them at runtime, so there is no performance penalty.
  - *Example*:

```python
def connect(self, timeout: int = 10) -> bool:
    ...
```

### 3.3. MicroPython Modules

- **Use `import machine` style**.
  - *Why?* Prevents namespace pollution and makes it clear where `Pin`, `I2C`, etc., come from.
  - *Example*:

```python
import machine
led = machine.Pin(2, machine.Pin.OUT)
```

- *Avoid*: `from machine import Pin`

### 3.4. Project Modules

- **Use `from package import module` style**.
  - *Why?* Keeps the namespace clean and makes dependencies explicit.
  - *Example*:

```python
from drivers import hd38
sensor = hd38.HD38(34)
```

- *Avoid*: `from drivers.hd38 import HD38`

## 4. File Structure

- All imports should be at the **top of the file**.
- Drivers should be in `drivers/`.
- Core logic should be in `core/`.
