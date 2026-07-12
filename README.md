# material-register

Material Register is a desktop application for tracking materials, inventory, and transactions.
It is built with PySide6 and SQLite and is designed as a lightweight local system for managing stock movements
without requiring any external server or backend.

The application supports creating and managing commodities, categorizing materials, and recording transactions of type IN and OUT.
Each transaction automatically updates the inventory, ensuring consistent stock values across all operations.
The project also includes a test suite for core business logic and a simple, structured UI for managing data efficiently.

The project is intended as a practical desktop tool and a learning project focused on Qt-based UI development,
database handling, and service-layer architecture in Python.

## Installation

(Tested on macOS, IDE: PyCharm)

- Clone the repository:
```bash
  git clone https://github.com/Jin-Mach/material-register.git
```

- Navigate to the project directory:
```bash
  cd material-register
```

- Create a virtual environment:
  - On Windows:
```bash
  python -m venv .venv
```
  - On macOS/Linux:
```bash
  python3 -m venv .venv
```

- Activate the virtual environment:
  - On Windows (Command Prompt):
```bash
  .venv\Scripts\activate
```
  - On Windows (PowerShell):
```bash
  .venv\Scripts\activate.ps1
```
  - On macOS/Linux:
```bash
  source .venv/bin/activate
```

- Install the required packages:
  - On Windows:
```bash
  python -m pip install .
```
  - On macOS/Linux:
```bash
  python3 -m pip install .
```
- (Optional) for development and testing:

  - On Windows:
    ```bash
    python -m pip install -e .[dev]
    ```

  - On macOS/Linux:
    ```bash
    python3 -m pip install -e ".[dev]"
    ```

## Usage

After installing the dependencies, you can start the application with the following command:

- Run the application:
  - On Windows:
```bash
  python -m material_register.main
```
  - On macOS/Linux:
```bash
    python3 -m material_register.main
```

## License

- This project is licensed under the MIT License.

## Credits

- Developed by [Jin-Mach](https://github.com/Jin-Mach).

## Contact

- Questions or feedback? Reach out via GitHub: [Jin-Mach](https://github.com/Jin-Mach).