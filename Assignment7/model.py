import pulp

def build_and_solve(data):
    days = data["days"]
    shifts = data["shifts"]
    employees = data["employees"]
    fixed_assignments = data["fixed_assignments"]
    cover = data["cover"]
    contracts = data["contracts"]
    emp_contracts = data["emp_contracts"]
    shift_off = data.get("shift_off", {})
    shift_on = data.get("shift_on", {})

    prob = pulp.LpProblem("Nurse_Rostering", pulp.LpMinimize)

    # =====================
    # Decision variables
    # =====================
    x = pulp.LpVariable.dicts("shift",
                              ((e,d,s) for e in employees for d in range(days) for s in shifts.keys()),
                              cat="Binary")

    # =====================
    # Hard constraints
    # =====================

    # 1. Fixed assignments
    for (e,d), s in fixed_assignments.items():
        if s != "-":
            prob += x[(e,d,s)] == 1
        else:
            for sh in shifts.keys():
                prob += x[(e,d,sh)] == 0

    # 2. Only one shift per employee per day
    for e in employees:
        for d in range(days):
            prob += pulp.lpSum(x[(e,d,s)] for s in shifts.keys()) <= 1

    # 3. Cover requirements
    for (d,s), req in cover.items():
        if req["min"] == req["max"]:
            prob += pulp.lpSum(x[(e,d,s)] for e in employees) == req["min"]
        else:
            prob += pulp.lpSum(x[(e,d,s)] for e in employees) >= req["min"]
            prob += pulp.lpSum(x[(e,d,s)] for e in employees) <= req["max"]

    # 4. Consecutive shifts / days off & max weekends
    y_weekend = {}
    for e in employees:
        e_contract_ids = emp_contracts[e]

        max_seq_vals = [contracts[cid].get("max_seq") for cid in e_contract_ids if contracts[cid].get("max_seq") is not None]
        min_off_vals = [contracts[cid].get("min_off") for cid in e_contract_ids if contracts[cid].get("min_off") is not None]
        max_weekends_vals = [contracts[cid].get("max_weekends") for cid in e_contract_ids if contracts[cid].get("max_weekends") is not None]

        max_seq = max(max_seq_vals) if max_seq_vals else days
        min_off = max(min_off_vals) if min_off_vals else 0
        max_weekends = min(max_weekends_vals) if max_weekends_vals else 2

        # Max consecutive shifts
        for d in range(days - max_seq):
            prob += pulp.lpSum(x[(e, dd, s)] for dd in range(d, d + max_seq + 1) for s in shifts.keys()) <= max_seq

        # Min consecutive days off
        for d in range(days - min_off + 1):
            prob += pulp.lpSum(1 - x[(e, dd, s)] for dd in range(d, d + min_off) for s in shifts.keys()) >= min_off

        # Max weekends
        for w, start in enumerate(range(0, days, 7)):
            weekend_days = [d for d in range(start, min(start+7, days)) if (d % 7) in [5,6]]
            if weekend_days:
                y_weekend[(e,w)] = pulp.LpVariable(f"weekend_{e}_{w}", cat="Binary")
                prob += pulp.lpSum(x[(e,d,s)] for d in weekend_days for s in shifts.keys()) <= 1000 * y_weekend[(e,w)]

        # Sum of weekend variables <= max_weekends
        e_weekend_vars = [var for (emp_id, w_idx), var in y_weekend.items() if emp_id == e]
        if e_weekend_vars:
            prob += pulp.lpSum(e_weekend_vars) <= max_weekends

    # =====================
    # Objective: minimize soft penalties
    # =====================
    obj_terms = []

    # Shift-Off requests: penalty if assigned
    for (e,d,s), w in shift_off.items():
        obj_terms.append(w * x[(e,d,s)])

    # Shift-On requests: penalty if NOT assigned
    for (e,d,s), w in shift_on.items():
        obj_terms.append(w * (1 - x[(e,d,s)]))

    prob += pulp.lpSum(obj_terms)

    # =====================
    # Solve
    # =====================
    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)

    # =====================
    # Build schedule table
    # =====================
    schedule = {e: {} for e in employees}
    for e in employees:
        for d in range(days):
            assigned = [s for s in shifts.keys() if pulp.value(x[(e,d,s)]) == 1]
            schedule[e][d] = assigned[0] if assigned else "-"

    model_info = {
        "status": pulp.LpStatus[prob.status],
        "objective_value": pulp.value(prob.objective),
        "total_assigned_shifts": sum(pulp.value(x[(e,d,s)]) for e in employees for d in range(days) for s in shifts.keys())
    }

    return schedule, model_info