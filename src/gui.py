from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

try:
    from .database import initialize_database
    from .prolog_service import (
        build_prolog_service,
        format_estimate_text,
        generate_and_save_estimate,
        validate_budget,
        validate_positive_integer,
    )
except ImportError:
    from database import initialize_database
    from prolog_service import (
        build_prolog_service,
        format_estimate_text,
        generate_and_save_estimate,
        validate_budget,
        validate_positive_integer,
    )


class ThemisGui:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Themis Construction Estimator")
        self.root.geometry("860x620")
        self.root.minsize(760, 540)

        initialize_database()
        self.prolog = build_prolog_service()

        self.bedrooms_var = tk.StringVar(value="3")
        self.floors_var = tk.StringVar(value="1")
        self.finish_var = tk.StringVar(value="standard")
        self.location_var = tk.StringVar(value="urban")
        self.roof_type_var = tk.StringVar(value="gable")
        self.budget_var = tk.StringVar()
        self.status_var = tk.StringVar(
            value="Enter project details and click Generate Estimate."
        )

        self.build_layout()

    def build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        container = ttk.Frame(self.root, padding=18)
        container.grid(sticky="nsew")
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Label(
            container,
            text="Residential Construction Cost Estimator",
            font=("TkDefaultFont", 15, "bold"),
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        form_frame = ttk.LabelFrame(container, text="Project Inputs", padding=14)
        form_frame.grid(row=1, column=0, sticky="nsw", padx=(0, 16))

        result_frame = ttk.LabelFrame(container, text="Estimate Output", padding=14)
        result_frame.grid(row=1, column=1, sticky="nsew")
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        fields = [
            ("Bedrooms", self.bedrooms_var, "entry"),
            ("Floors", self.floors_var, "entry"),
            ("Finish", self.finish_var, ("basic", "standard", "luxury")),
            ("Location", self.location_var, ("rural", "urban")),
            ("Roof Type", self.roof_type_var, ("gable", "hip", "flat")),
            ("Budget", self.budget_var, "entry"),
        ]

        for row_index, (label_text, variable, field_type) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(
                row=row_index,
                column=0,
                sticky="w",
                pady=6,
            )
            if field_type == "entry":
                widget = ttk.Entry(form_frame, textvariable=variable, width=18)
            else:
                widget = ttk.Combobox(
                    form_frame,
                    textvariable=variable,
                    values=list(field_type),
                    state="readonly",
                    width=15,
                )
            widget.grid(row=row_index, column=1, sticky="ew", pady=6)

        form_frame.columnconfigure(1, weight=1)

        button_row = ttk.Frame(form_frame)
        button_row.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(14, 0))
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)

        ttk.Button(
            button_row,
            text="Generate Estimate",
            command=self.generate_estimate,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            button_row,
            text="Clear Form",
            command=self.clear_form,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.result_text = tk.Text(result_frame, wrap="word", height=20)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        self.result_text.insert(
            "1.0",
            "Results will appear here after you generate an estimate.",
        )
        self.result_text.configure(state="disabled")

        scrollbar = ttk.Scrollbar(
            result_frame,
            orient="vertical",
            command=self.result_text.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=scrollbar.set)

        status_label = ttk.Label(
            container,
            textvariable=self.status_var,
            foreground="#355070",
        )
        status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    def set_result_text(self, content: str) -> None:
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", content)
        self.result_text.configure(state="disabled")

    def clear_form(self) -> None:
        self.bedrooms_var.set("3")
        self.floors_var.set("1")
        self.finish_var.set("standard")
        self.location_var.set("urban")
        self.roof_type_var.set("gable")
        self.budget_var.set("")
        self.set_result_text("Results will appear here after you generate an estimate.")
        self.status_var.set("Form cleared.")

    def collect_inputs(self) -> dict[str, Any]:
        return {
            "bedrooms": validate_positive_integer(self.bedrooms_var.get(), "Bedrooms"),
            "floors": validate_positive_integer(self.floors_var.get(), "Floors"),
            "finish": self.finish_var.get(),
            "location": self.location_var.get(),
            "roof_type": self.roof_type_var.get(),
            "budget": validate_budget(self.budget_var.get()),
        }

    def generate_estimate(self) -> None:
        try:
            inputs = self.collect_inputs()
            parsed, estimate_id = generate_and_save_estimate(self.prolog, inputs)
        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))
            self.status_var.set("Please correct the input values and try again.")
            return
        except Exception as error:
            messagebox.showerror("Estimation Error", str(error))
            self.status_var.set("The estimate could not be generated.")
            return

        self.set_result_text(format_estimate_text(parsed, estimate_id))
        self.status_var.set("Estimate generated and saved successfully.")


def main() -> None:
    root = tk.Tk()
    app = ThemisGui(root)
    app.root.mainloop()


if __name__ == "__main__":
    main()
