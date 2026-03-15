% ---------- Constants ----------
material_price(cement, 750).
material_price(steel, 120).
material_price(bricks, 15).
material_price(timber, 45000).

finish_multiplier(basic, 1.00).
finish_multiplier(standard, 1.15).
finish_multiplier(luxury, 1.35).

location_multiplier(rural, 1.00).
location_multiplier(urban, 1.20).

roof_cost_multiplier(gable, 1.00).
roof_cost_multiplier(hip, 1.08).
roof_cost_multiplier(flat, 1.12).

% ---------- Area ----------
calculate_area(BedroomCount, FloorCount, TotalArea) :-
    BedroomArea is BedroomCount * 12,
    FunctionalArea is BedroomArea * 2.5,
    AreaWithCirculation is FunctionalArea * 1.20,
    TotalArea is AreaWithCirculation * FloorCount.

% ---------- Materials ----------
calculate_materials(TotalArea, FloorCount, RoofType,
                    materials(CementQuantity, SteelQuantity, BrickQuantity, TimberQuantity),
                    MaterialReasons) :-
    CementQuantity is TotalArea * 5,
    BaseSteelQuantity is TotalArea * 35,
    BaseTimberQuantity is TotalArea * 0.03,
    ( FloorCount > 1 ->
        MultiStoreySteelQuantity is BaseSteelQuantity * 1.5,
        FloorReasons = ["multi_storey: steel increased by 50%"]
    ;   MultiStoreySteelQuantity = BaseSteelQuantity,
        FloorReasons = []
    ),
    roof_structure_adjustment(
        RoofType,
        MultiStoreySteelQuantity,
        BaseTimberQuantity,
        SteelQuantity,
        TimberQuantity,
        RoofReasons
    ),
    BrickQuantity is TotalArea * 60,
    append(FloorReasons, RoofReasons, MaterialReasons).

% ---------- Cost ----------
calculate_base_cost(
    materials(CementQuantity, SteelQuantity, BrickQuantity, TimberQuantity),
    BaseCost
) :-
    material_price(cement, CementUnitPrice),
    material_price(steel, SteelUnitPrice),
    material_price(bricks, BrickUnitPrice),
    material_price(timber, TimberUnitPrice),
    BaseCost is
        CementQuantity * CementUnitPrice +
        SteelQuantity * SteelUnitPrice +
        BrickQuantity * BrickUnitPrice +
        TimberQuantity * TimberUnitPrice.

apply_multipliers(BaseCost, FinishLevel, LocationType, RoofType, FinalCost, MultiplierReasons) :-
    finish_multiplier(FinishLevel, FinishMultiplier),
    location_multiplier(LocationType, LocationMultiplier),
    roof_cost_multiplier(RoofType, RoofMultiplier),
    FinalCost is BaseCost * FinishMultiplier * LocationMultiplier * RoofMultiplier,
    finish_reason(FinishLevel, FinishReasons),
    location_reason(LocationType, LocationReasons),
    roof_reason(RoofType, RoofReasons),
    append(FinishReasons, LocationReasons, InitialReasons),
    append(InitialReasons, RoofReasons, MultiplierReasons).

finish_reason(basic, []).
finish_reason(FinishLevel, [FinishReason]) :-
    FinishLevel \= basic,
    finish_multiplier(FinishLevel, FinishMultiplier),
    format(
        atom(FinishReason),
        'finish: ~w multiplier ~2f',
        [FinishLevel, FinishMultiplier]
    ).

location_reason(rural, []).
location_reason(urban, ["location: urban logistics multiplier applied"]).

roof_reason(gable, []).
roof_reason(RoofType, [RoofReason]) :-
    RoofType \= gable,
    roof_cost_multiplier(RoofType, RoofMultiplier),
    format(atom(RoofReason), 'roof: ~w multiplier ~2f', [RoofType, RoofMultiplier]).

roof_structure_adjustment(
    gable,
    InputSteelQuantity,
    InputTimberQuantity,
    InputSteelQuantity,
    InputTimberQuantity,
    []
).
roof_structure_adjustment(hip, InputSteelQuantity, InputTimberQuantity, SteelQuantity, TimberQuantity,
                          ["roof: hip roof needs additional timber support"]) :-
    SteelQuantity is InputSteelQuantity,
    TimberQuantity is InputTimberQuantity * 1.10.
roof_structure_adjustment(flat, InputSteelQuantity, InputTimberQuantity, SteelQuantity, TimberQuantity,
                          ["roof: flat roof needs reinforced slab support"]) :-
    SteelQuantity is InputSteelQuantity * 1.12,
    TimberQuantity is InputTimberQuantity.

% ---------- Feasibility ----------
feasibility(_FinalCost, none, feasible, ["budget: none provided"]).
feasibility(FinalCost, BudgetAmount, not_feasible,
            ["budget: projected cost exceeds budget"]) :-
    BudgetAmount \= none,
    FinalCost > BudgetAmount.
feasibility(FinalCost, BudgetAmount, conditional,
            ["budget: projected cost is close to limit"]) :-
    BudgetAmount \= none,
    FinalCost =< BudgetAmount,
    FinalCost > BudgetAmount * 0.9.
feasibility(FinalCost, BudgetAmount, feasible,
            ["budget: projected cost within limit"]) :-
    BudgetAmount \= none,
    FinalCost =< BudgetAmount * 0.9.

% ---------- Main ----------
estimate(BedroomCount, FloorCount, FinishLevel, LocationType, RoofType, BudgetAmount,
         result(TotalArea, Materials, BaseCost, FinalCost, Feasibility, Reasons)) :-
    calculate_area(BedroomCount, FloorCount, TotalArea),
    calculate_materials(TotalArea, FloorCount, RoofType, Materials, MaterialReasons),
    calculate_base_cost(Materials, BaseCost),
    apply_multipliers(
        BaseCost,
        FinishLevel,
        LocationType,
        RoofType,
        FinalCost,
        MultiplierReasons
    ),
    feasibility(FinalCost, BudgetAmount, Feasibility, FeasibilityReasons),
    append(MaterialReasons, MultiplierReasons, CombinedReasons),
    append(CombinedReasons, FeasibilityReasons, Reasons).
