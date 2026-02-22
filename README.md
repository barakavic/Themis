# Themis
# Residential Construction Cost Estimation Decision Support System (DSS)

## 1. Introduction
The Residential Construction Cost Estimation DSS is an engineering decision support system designed to help non-technical users estimate the cost, feasibility, and material requirements of constructing a residential building. The system combines rule-based reasoning, database storage, and a graphical interface to simulate expert-level construction planning guidance. Its goal is to support informed decision-making before construction begins, reducing the likelihood of unrealistic budgets, unsafe designs, or poor planning.

---

## 2. Problem Statement
Many individuals who want to build houses lack technical knowledge about construction requirements, material quantities, and realistic cost estimates. Without professional guidance, they may underestimate expenses or design structures that are structurally impractical. This system addresses that gap by providing automated decision support that evaluates user specifications and generates intelligent recommendations.

---

## 3. Objectives

### 3.1 Main Objective
To develop a decision support system that evaluates residential construction specifications and generates feasibility assessments, cost estimates, and material breakdowns.

### 3.2 Specific Objectives
- Estimate total construction cost
- Determine required material quantities
- Evaluate structural feasibility
- Explain reasoning behind decisions
- Recommend improvements if constraints are violated
- Store previous estimates for reference

---

## 4. System Architecture
The system follows a modular decision support architecture consisting of the following components:

User → GUI → Controller → Inference Engine ↔ Knowledge Base → Database

### Component Descriptions
- **GUI:** Collects user inputs and displays results
- **Controller:** Coordinates communication between system modules
- **Inference Engine:** Applies decision rules to inputs
- **Knowledge Base:** Contains engineering rules and logic
- **Database:** Stores materials, templates, and generated estimates

---

## 5. Inputs
The user provides simplified construction requirements:

- Number of bedrooms
- Number of floors
- Finish level (basic, standard, luxury)
- Location type (urban or rural)
- Roof type
- Budget (optional)

These inputs represent high-level design intentions rather than technical engineering parameters.

---

## 6. Database Design

### Materials Table
Stores construction material properties and prices.

Fields:
- material_name
- unit_price
- strength
- max_temperature

---

### Design Templates Table
Stores predefined construction quantity estimates.

Fields:
- bedrooms
- floors
- cement_quantity
- steel_quantity
- brick_quantity

---

### Estimates Table
Stores generated results for record keeping.

Fields:
- estimate_id
- specifications
- total_cost
- decision
- timestamp

---

## 7. Knowledge Base
The knowledge base contains logical rules representing engineering reasoning. Examples include:

- Multi-storey buildings require reinforced structures
- Reinforced structures increase steel usage
- Luxury finishes increase overall cost
- Designs exceeding budget constraints are infeasible
- Certain roof types require additional structural support

These rules allow the system to mimic expert construction planning logic.

---

## 8. Inference Engine
The inference engine evaluates user input against stored rules to determine:

- structural requirements
- cost multipliers
- constraint violations
- feasibility status

Instead of relying only on formulas, the engine performs logical reasoning, making the system intelligent rather than computational only.

---

## 9. Outputs
After processing, the system produces:

### Estimated Cost
Total projected construction expense based on selected specifications.

### Material Breakdown
List of required materials and their quantities.

### Feasibility Decision
One of:
- Feasible
- Conditionally Feasible
- Not Feasible

### Explanation
A clear statement describing why the system reached its conclusion.

Example:
> The design requires reinforced structural support because it has more than one floor.

---

## 10. Decision Support Characteristics
The system satisfies key DSS properties:

- interactive user interface
- rule-based reasoning
- database integration
- explanation capability
- decision traceability
- structured logic evaluation

---

## 11. Technologies Used

- GUI: Python Tkinter
- Logic Engine: Prolog
- Database: SQLite
- Query Language: SQL

---

## 12. Benefits
This system helps users:

- understand realistic construction costs
- plan budgets more effectively
- explore different design options
- identify structural constraints early
- make informed construction decisions

---

## 13. Limitations
The system provides estimated results rather than exact costs. Real-world costs may vary due to:

- market price fluctuations
- labor charges
- contractor fees
- legal permits
- site-specific conditions

---

## 14. Conclusion
The Residential Construction Cost Estimation DSS demonstrates how decision support systems can assist real-world engineering planning through the integration of databases, logical reasoning, and interactive interfaces. By translating expert construction knowledge into programmable rules, the system enables non-technical users to make informed and realistic building decisions.

This project illustrates the practical value of decision support technology in civil engineering planning while showcasing the integration of multiple computing concepts including databases, logic programming, and system design.
