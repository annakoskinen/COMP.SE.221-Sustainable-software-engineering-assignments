from parser import parse_ros
from model import build_and_solve

def print_schedule(schedule, employees, days, model_info):
    # Header: Days
    header = ["Nurse"] + [str(d) for d in range(days)]
    print("\t".join(header))
    for e in employees:
        row = [e] + [schedule[e][d] for d in range(days)]
        print("\t".join(row))

    # Model info
    print("\n=== Model Info ===")
    print(f"Status: {model_info['status']}")
    print(f"Objective value: {model_info['objective_value']}")
    print(f"Total assigned shifts: {int(model_info['total_assigned_shifts'])}")

if __name__ == "__main__":
    filename = "Instance1.ros"
    data = parse_ros(filename)
    schedule, model_info = build_and_solve(data)
    print("\n=== Nurse Rostering Schedule ===")
    print_schedule(schedule, data["employees"], data["days"], model_info)