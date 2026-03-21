from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DATABASE_PATH = Path("data/themis.db")
DEFAULT_MATERIAL_DATA = {
    "cement": {"unit_price": 750.0, "unit": "bags"},
    "steel": {"unit_price": 120.0, "unit": "kg"},
    "bricks": {"unit_price": 15.0, "unit": "units"},
    "timber": {"unit_price": 45000.0, "unit": "m^3"},
}
DEFAULT_FINISH_MULTIPLIERS = {
    "basic": 1.00,
    "standard": 1.15,
    "luxury": 1.35,
}
DEFAULT_LOCATION_MULTIPLIERS = {
    "rural": 1.00,
    "urban": 1.20,
}
DEFAULT_ROOF_MULTIPLIERS = {
    "gable": 1.00,
    "hip": 1.08,
    "flat": 1.12,
}
DEFAULT_ESTIMATION_FACTORS = {
    "bedroom_area": 12.0,
    "functional_area_multiplier": 2.5,
    "circulation_factor": 0.20,
    "cement_per_m2": 5.0,
    "steel_per_m2": 35.0,
    "bricks_per_m2": 60.0,
    "timber_per_m2": 0.03,
    "multi_storey_steel_multiplier": 1.5,
    "hip_timber_multiplier": 1.10,
    "flat_steel_multiplier": 1.12,
    "feasible_budget_ratio": 0.90,
}


def initialize_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS material_prices (
                material_name TEXT PRIMARY KEY,
                unit_price REAL NOT NULL,
                unit TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS finish_multipliers (
                finish_level TEXT PRIMARY KEY,
                multiplier REAL NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS location_multipliers (
                location_type TEXT PRIMARY KEY,
                multiplier REAL NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS roof_cost_multipliers (
                roof_type TEXT PRIMARY KEY,
                multiplier REAL NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS estimation_factors (
                factor_name TEXT PRIMARY KEY,
                value REAL NOT NULL
            )
            """
        )
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
        connection.executemany(
            """
            INSERT OR IGNORE INTO material_prices (
                material_name,
                unit_price,
                unit
            ) VALUES (?, ?, ?)
            """,
            [
                (name, values["unit_price"], values["unit"])
                for name, values in DEFAULT_MATERIAL_DATA.items()
            ],
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO finish_multipliers (
                finish_level,
                multiplier
            ) VALUES (?, ?)
            """,
            list(DEFAULT_FINISH_MULTIPLIERS.items()),
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO location_multipliers (
                location_type,
                multiplier
            ) VALUES (?, ?)
            """,
            list(DEFAULT_LOCATION_MULTIPLIERS.items()),
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO roof_cost_multipliers (
                roof_type,
                multiplier
            ) VALUES (?, ?)
            """,
            list(DEFAULT_ROOF_MULTIPLIERS.items()),
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO estimation_factors (
                factor_name,
                value
            ) VALUES (?, ?)
            """,
            list(DEFAULT_ESTIMATION_FACTORS.items()),
        )
        connection.commit()


def load_reference_data() -> dict[str, dict[str, Any]]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        material_rows = connection.execute(
            """
            SELECT material_name, unit_price, unit
            FROM material_prices
            """
        ).fetchall()
        finish_rows = connection.execute(
            """
            SELECT finish_level, multiplier
            FROM finish_multipliers
            """
        ).fetchall()
        location_rows = connection.execute(
            """
            SELECT location_type, multiplier
            FROM location_multipliers
            """
        ).fetchall()
        roof_rows = connection.execute(
            """
            SELECT roof_type, multiplier
            FROM roof_cost_multipliers
            """
        ).fetchall()
        factor_rows = connection.execute(
            """
            SELECT factor_name, value
            FROM estimation_factors
            """
        ).fetchall()

    return {
        "material_prices": {
            material_name: unit_price for material_name, unit_price, _unit in material_rows
        },
        "material_units": {
            material_name: unit for material_name, _unit_price, unit in material_rows
        },
        "finish_multipliers": {
            finish_level: multiplier for finish_level, multiplier in finish_rows
        },
        "location_multipliers": {
            location_type: multiplier for location_type, multiplier in location_rows
        },
        "roof_cost_multipliers": {
            roof_type: multiplier for roof_type, multiplier in roof_rows
        },
        "estimation_factors": {
            factor_name: value for factor_name, value in factor_rows
        },
    }


def save_estimate(inputs: dict[str, Any], parsed_result: dict[str, Any]) -> int | None:
    if "area" not in parsed_result:
        return None

    budget_value = None if inputs["budget"] == "none" else float(inputs["budget"])
    material_units = load_reference_data()["material_units"]

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
                material_units[material_name],
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
