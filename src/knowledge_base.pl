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

% ---------- Area ----------
calculate_area(Bedrooms, Floors, TotalArea) :-
    BedroomArea is Bedrooms * 12,
    FunctionalArea is BedroomArea * 2.5,
    AreaWithCirculation is FunctionalArea * 1.20,
    TotalArea is AreaWithCirculation * Floors.

% ---------- Materials ----------
calculate_materials(TotalArea, Floors,
                    materials(Cement, Steel, Bricks, Timber),
                    Reasons) :-
    Cement is TotalArea * 5,
    Steel0 is TotalArea * 35,
    ( Floors > 1 ->
        Steel is Steel0 * 1.5,
        Reasons = ["multi_storey: steel increased by 50%"]
    ;   Steel is Steel0,
        Reasons = []
    ),
    Bricks is TotalArea * 60,
    Timber is TotalArea * 0.03.

% ---------- Cost ----------
calculate_base_cost(materials(Cement, Steel, Bricks, Timber), BaseCost) :-
    material_price(cement, CP),
    material_price(steel, SP),
    material_price(bricks, BP),
    material_price(timber, TP),
    BaseCost is
        Cement * CP +
        Steel * SP +
        Bricks * BP +
        Timber * TP.

apply_multipliers(BaseCost, Finish, Location, FinalCost, Reasons) :-
    finish_multiplier(Finish, FM),
    location_multiplier(Location, LM),
    FinalCost is BaseCost * FM * LM,
    finish_reason(Finish, FinishReasons),
    location_reason(Location, LocationReasons),
    append(FinishReasons, LocationReasons, Reasons).

finish_reason(basic, []).
finish_reason(Finish, [Reason]) :-
    Finish \= basic,
    finish_multiplier(Finish, FM),
    format(atom(Reason), 'finish: ~w multiplier ~2f', [Finish, FM]).

location_reason(rural, []).
location_reason(urban, ["location: urban logistics multiplier applied"]).

% ---------- Feasibility ----------
feasibility(_FinalCost, none, feasible, ["budget: none provided"]).
feasibility(FinalCost, Budget, not_feasible,
            ["budget: projected cost exceeds budget"]) :-
    Budget \= none,
    FinalCost > Budget.
feasibility(FinalCost, Budget, conditional,
            ["budget: projected cost is close to limit"]) :-
    Budget \= none,
    FinalCost =< Budget,
    FinalCost > Budget * 0.9.
feasibility(FinalCost, Budget, feasible,
            ["budget: projected cost within limit"]) :-
    Budget \= none,
    FinalCost =< Budget * 0.9.

% ---------- Main ----------
estimate(Bedrooms, Floors, Finish, Location, Budget,
         result(TotalArea, Materials, BaseCost, FinalCost, Feasibility, Reasons)) :-
    calculate_area(Bedrooms, Floors, TotalArea),
    calculate_materials(TotalArea, Floors, Materials, MaterialReasons),
    calculate_base_cost(Materials, BaseCost),
    apply_multipliers(BaseCost, Finish, Location, FinalCost, MultiplierReasons),
    feasibility(FinalCost, Budget, Feasibility, FeasibilityReasons),
    append(MaterialReasons, MultiplierReasons, R1),
    append(R1, FeasibilityReasons, Reasons).
