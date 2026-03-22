:- dynamic material_price/2.
:- dynamic finish_multiplier/2.
:- dynamic location_multiplier/2.
:- dynamic roof_cost_multiplier/2.
:- dynamic estimation_factor/2.

%  Area 
calculate_area(BedroomCount, FloorCount, TotalArea) :-
    estimation_factor(bedroom_area, BedroomAreaFactor),
    estimation_factor(functional_area_multiplier, FunctionalAreaMultiplier),
    estimation_factor(circulation_factor, CirculationFactor),
    BedroomArea is BedroomCount * BedroomAreaFactor,
    FunctionalArea is BedroomArea * FunctionalAreaMultiplier,
    AreaWithCirculation is FunctionalArea * (1 + CirculationFactor),
    TotalArea is AreaWithCirculation * FloorCount.

%  Materials 
calculate_materials(TotalArea, FloorCount, RoofType,
                    materials(CementQuantity, SteelQuantity, BrickQuantity, TimberQuantity),
                    MaterialReasons) :-
    estimation_factor(cement_per_m2, CementPerSquareMetre),
    estimation_factor(steel_per_m2, SteelPerSquareMetre),
    estimation_factor(bricks_per_m2, BricksPerSquareMetre),
    estimation_factor(timber_per_m2, TimberPerSquareMetre),
    estimation_factor(multi_storey_steel_multiplier, MultiStoreySteelMultiplier),
    CementQuantity is TotalArea * CementPerSquareMetre,
    BaseSteelQuantity is TotalArea * SteelPerSquareMetre,
    BaseTimberQuantity is TotalArea * TimberPerSquareMetre,
    ( FloorCount > 1 ->
        MultiStoreySteelQuantity is BaseSteelQuantity * MultiStoreySteelMultiplier,
        SteelIncreasePercentage is (MultiStoreySteelMultiplier - 1) * 100,
        format(
            atom(FloorReason),
            'multi_storey: steel increased by ~0f%',
            [SteelIncreasePercentage]
        ),
        FloorReasons = [FloorReason]
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
    BrickQuantity is TotalArea * BricksPerSquareMetre,
    append(FloorReasons, RoofReasons, MaterialReasons).

% Cost 
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
    estimation_factor(hip_timber_multiplier, HipTimberMultiplier),
    SteelQuantity is InputSteelQuantity,
    TimberQuantity is InputTimberQuantity * HipTimberMultiplier.
roof_structure_adjustment(flat, InputSteelQuantity, InputTimberQuantity, SteelQuantity, TimberQuantity,
                          ["roof: flat roof needs reinforced slab support"]) :-
    estimation_factor(flat_steel_multiplier, FlatSteelMultiplier),
    SteelQuantity is InputSteelQuantity * FlatSteelMultiplier,
    TimberQuantity is InputTimberQuantity.

%  Feasibility 
feasibility(_FinalCost, none, feasible, ["budget: none provided"]).
feasibility(FinalCost, BudgetAmount, not_feasible,
            ["budget: projected cost exceeds budget"]) :-
    BudgetAmount \= none,
    FinalCost > BudgetAmount.
feasibility(FinalCost, BudgetAmount, conditional,
            ["budget: projected cost is close to limit"]) :-
    estimation_factor(feasible_budget_ratio, FeasibleBudgetRatio),
    BudgetAmount \= none,
    FinalCost =< BudgetAmount,
    FinalCost > BudgetAmount * FeasibleBudgetRatio.
feasibility(FinalCost, BudgetAmount, feasible,
            ["budget: projected cost within limit"]) :-
    estimation_factor(feasible_budget_ratio, FeasibleBudgetRatio),
    BudgetAmount \= none,
    FinalCost =< BudgetAmount * FeasibleBudgetRatio.

%  Main 
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
