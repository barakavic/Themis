from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DATABASE_PATH = Path("data/themis.db")
MATERIAL_UNITS = {
    "cement": "bags",
    "steel": "kg",
    "bricks": "units",
    "timber": "m^3",
}


def initialize_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS estimates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bedrooms INTEGER NOT NULL,
                floors INTEGER NOT NULL,
                finish TEXT NOT NULL,
                location TEXT NOT NULL,
                roof_type TEXT NOT NULL,
                budget REAL,
                total_area REAL NOT NULL,
                base_cost REAL NOT NULL,
                final_cost REAL NOT NULL,
                feasibility TEXT NOT NULL,
                reasons TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS estimate_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estimate_id INTEGER NOT NULL,
                material_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                FOREIGN KEY (estimate_id) REFERENCES estimates (id)
            )
            """
        )
        connection.commit()


def save_estimate(inputs: dict[str, Any], parsed_result: dict[str, Any]) -> int | None:
    if "area" not in parsed_result:
        return None

    budget_value = None if inputs["budget"] == "none" else float(inputs["budget"])

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO estimates (
                bedrooms,
                floors,
                finish,
                location,
                roof_type,
                budget,
                total_area,
                base_cost,
                final_cost,
                feasibility,
                reasons
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                inputs["bedrooms"],
                inputs["floors"],
                inputs["finish"],
                inputs["location"],
                inputs["roof_type"],
                budget_value,
                parsed_result["area"],
                parsed_result["base_cost"],
                parsed_result["final_cost"],
                parsed_result["feasibility"],
                "\n".join(parsed_result["reasons"]),
            ),
        )
        estimate_id = cursor.lastrowid

        material_rows = [
            (
                estimate_id,
                material_name,
                quantity,
                MATERIAL_UNITS[material_name],
            )
            for material_name, quantity in parsed_result["materials"].items()
        ]
        connection.executemany(
            """
            INSERT INTO estimate_materials (
                estimate_id,
                material_name,
                quantity,
                unit
            ) VALUES (?, ?, ?, ?)
            """,
            material_rows,
        )
        connection.commit()

    return estimate_id
