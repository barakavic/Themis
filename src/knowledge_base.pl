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
calculate_materials(TotalArea, Floors, materials(Cement, Steel, Bricks, Timber)) :-
    Cement is TotalArea * 5,
    Steel0 is TotalArea * 35,
    ( Floors > 1 -> Steel is Steel0 * 1.5 ; Steel is Steel0 ),
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

apply_multipliers(BaseCost, Finish, Location, FinalCost) :-
    finish_multiplier(Finish, FM),
    location_multiplier(Location, LM),
    FinalCost is BaseCost * FM * LM.

% ---------- Feasibility ----------
feasibility(_FinalCost, none, feasible).
feasibility(FinalCost, Budget, not_feasible) :-
    Budget \= none,
    FinalCost > Budget.
feasibility(FinalCost, Budget, conditional) :-
    Budget \= none,
    FinalCost =< Budget,
    FinalCost > Budget * 0.9.
feasibility(FinalCost, Budget, feasible) :-
    Budget \= none,
    FinalCost =< Budget * 0.9.

% ---------- Main ----------
estimate(Bedrooms, Floors, Finish, Location, Budget,
         result(TotalArea, Materials, BaseCost, FinalCost, Feasibility)) :-
    calculate_area(Bedrooms, Floors, TotalArea),
    calculate_materials(TotalArea, Floors, Materials),
    calculate_base_cost(Materials, BaseCost),
    apply_multipliers(BaseCost, Finish, Location, FinalCost),
    feasibility(FinalCost, Budget, Feasibility).
