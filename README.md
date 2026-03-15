# Themis

Themis is a residential construction cost estimation decision support system built with Python, Prolog, and SQLite. It allows a user to enter high-level building requirements, applies rule-based reasoning through SWI-Prolog, and returns an estimate with material breakdown, feasibility status, and explanation.

## Features

- Generates residential construction estimates from user inputs
- Uses Prolog as the primary knowledge base and inference layer
- Explains why an estimate was classified as feasible, conditional, or not feasible
- Supports both a command-line interface and a simple Tkinter GUI
- Stores completed estimates and material breakdowns in SQLite

## Architecture

The system is split into three main parts:

- Prolog handles the construction reasoning in `src/knowledge_base.pl`
- Python handles interaction, parsing, and application flow
- SQLite stores estimates for history and traceability

In practice, the workflow is:

1. The user enters building details.
2. Python sends those inputs to Prolog.
3. Prolog evaluates the rules and returns an estimate.
4. Python displays the result and saves it to SQLite.

## Project Structure

```text
src/
  app.py              CLI entry point
  gui.py              Tkinter GUI entry point
  prolog_service.py   Prolog query, parsing, and formatting helpers
  database.py         SQLite initialization and persistence
  knowledge_base.pl   Prolog rules and inference logic

data/
  themis.db           SQLite database file (generated at runtime)
```

## Requirements

- Python 3.12 or later
- SWI-Prolog installed system-wide
- A Python virtual environment with project dependencies installed

## Installation

1. Create and activate a virtual environment.
2. Install Python dependencies.
3. Ensure SWI-Prolog is installed and available on your system path.

Example setup:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt install swi-prolog
```

## Running the Application

Run the CLI version:

```bash
./venv/bin/python src/app.py
```

Run the Tkinter GUI:

```bash
./venv/bin/python src/gui.py
```

## Example Workflow

Example input:

- Bedrooms: `3`
- Floors: `2`
- Finish: `standard`
- Location: `urban`
- Roof type: `hip`
- Budget: `8000000`

Example result:

- Total area is calculated from bedrooms and floors
- Material quantities are adjusted by structural rules
- Cost multipliers are applied based on finish, location, and roof type
- A feasibility decision is returned with explanation reasons

## Data Storage

The application creates a local SQLite database at `data/themis.db`.

It currently stores:

- `estimates`: user inputs, total area, costs, feasibility, reasons, timestamp
- `estimate_materials`: per-estimate material quantities and units

## Limitations

- Estimates are indicative and should not replace professional engineering or quantity surveying advice
- Material prices and reasoning rules are currently defined in the Prolog knowledge base
- The system works from simplified residential inputs rather than full architectural plans

## Future Work

- Add estimate history viewing from the application
- Improve explanation formatting from Prolog outputs
- Expand the knowledge base with more construction rules and constraints
- Add richer reporting and export options

## License

No license has been specified yet.
