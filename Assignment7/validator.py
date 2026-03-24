def validate_schedule(schedule, data, model_info):
    """
    Validate a nurse rostering solution.

    Args:
        schedule: dict[e][day] = shift or "-"
        data: parsed .ros data
        model_info: dict with solver info

    Returns:
        dict with feasibility check results
    """
    days = data["days"]
    employees = data["employees"]
    shifts = data["shifts"]
    cover = data["cover"]
    fixed_assignments = data["fixed_assignments"]
    contracts = data["contracts"]
    emp_contracts = data["emp_contracts"]

    feasible = True
    errors = []

    # 1. One shift per employee per day
    for e in employees:
        for d in range(days):
            if schedule[e][d] not in shifts.keys() and schedule[e][d] != "-":
                feasible = False
                errors.append(f"Invalid shift {schedule[e][d]} for {e} on day {d}")

    # 2. Fixed assignments
    for (e,d), s in fixed_assignments.items():
        if s != "-" and schedule[e][d] != s:
            feasible = False
            errors.append(f"Fixed assignment violated for {e} on day {d}: expected {s}, got {schedule[e][d]}")
        elif s == "-" and schedule[e][d] != "-":
            feasible = False
            errors.append(f"Fixed day off violated for {e} on day {d}")

    # 3. Cover requirements
    for (d,s), req in cover.items():
        assigned = sum(1 for e in employees if schedule[e][d] == s)
        if assigned < req["min"] or assigned > req["max"]:
            feasible = False
            errors.append(f"Cover violation on day {d} shift {s}: assigned {assigned}, required [{req['min']},{req['max']}]")

    # 4. Max consecutive shifts & min consecutive days off
    for e in employees:
        e_contract_ids = emp_contracts[e]
        max_seq_vals = [contracts[cid].get("max_seq") for cid in e_contract_ids if contracts[cid].get("max_seq") is not None]
        min_off_vals = [contracts[cid].get("min_off") for cid in e_contract_ids if contracts[cid].get("min_off") is not None]

        max_seq = max(max_seq_vals) if max_seq_vals else days
        min_off = max(min_off_vals) if min_off_vals else 0

        # Max consecutive shifts
        consec = 0
        for d in range(days):
            if schedule[e][d] != "-":
                consec += 1
                if consec > max_seq:
                    feasible = False
                    errors.append(f"Max consecutive shifts exceeded for {e} at day {d}")
            else:
                consec = 0

        # Min consecutive days off
        off_streak = 0
        for d in range(days):
            if schedule[e][d] == "-":
                off_streak += 1
            else:
                if 0 < off_streak < min_off:
                    feasible = False
                    errors.append(f"Min consecutive days off violated for {e} ending day {d-1}")
                off_streak = 0
        if 0 < off_streak < min_off:
            feasible = False
            errors.append(f"Min consecutive days off violated for {e} at end of schedule")

    # 5. Objective value check (soft penalties)
    penalty_calc = 0
    for (e,d,s), w in data["shift_off"].items():
        if schedule[e][d] == s:
            penalty_calc += w
    for (e,d,s), w in data["shift_on"].items():
        if schedule[e][d] != s:
            penalty_calc += w

    reasonable_obj = abs(model_info["objective_value"] - penalty_calc) < 1e-5

    return {
        "feasible": feasible,
        "errors": errors,
        "objective_matches_penalty": reasonable_obj,
        "calculated_penalty": penalty_calc,
        "reported_objective": model_info["objective_value"]
    }

if __name__ == "__main__":
    from parser import parse_ros
    from model import build_and_solve

    filename = "Instance1.ros"
    data = parse_ros(filename)
    schedule, model_info = build_and_solve(data)

    result = validate_schedule(schedule, data, model_info)

    print("\n=== Validation Results ===")
    print(f"Feasible schedule: {result['feasible']}")
    print(f"Objective matches calculated penalty: {result['objective_matches_penalty']}")
    print(f"Calculated penalty: {result['calculated_penalty']}")
    print(f"Reported objective: {result['reported_objective']}")
    if not result["feasible"]:
        print("\nErrors:")
        for e in result["errors"]:
            print(f"- {e}")