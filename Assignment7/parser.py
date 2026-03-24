import xml.etree.ElementTree as ET
from datetime import datetime

def parse_ros(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    # Planning horizon
    start_date = datetime.strptime(root.find("StartDate").text, "%Y-%m-%d")
    end_date = datetime.strptime(root.find("EndDate").text, "%Y-%m-%d")
    days = (end_date - start_date).days + 1

    # Shift types
    shifts = {}
    for s in root.findall(".//ShiftTypes/Shift"):
        shift_id = s.attrib["ID"]
        start_time = int(s.find("StartTime").text.split(":")[0])
        duration = int(s.find("Duration").text)
        shifts[shift_id] = {"start_time": start_time, "duration": duration}

    # Employees
    employees = []
    emp_contracts = {}
    for e in root.findall(".//Employees/Employee"):
        emp_id = e.attrib["ID"]
        employees.append(emp_id)
        emp_contracts[emp_id] = [c.text for c in e.findall("ContractID")]

    # Fixed assignments
    fixed_assignments = {}
    for fa in root.findall(".//FixedAssignments/Employee"):
        emp_id = fa.find("EmployeeID").text
        for assign in fa.findall("Assign"):
            day = int(assign.find("Day").text)
            shift = assign.find("Shift").text
            fixed_assignments[(emp_id, day)] = shift

    # Shift off/on requests
    shift_off = {}
    for req in root.findall(".//ShiftOffRequests/ShiftOff"):
        emp = req.find("EmployeeID").text
        day = int(req.find("Day").text)
        shift = req.find("Shift").text
        weight = int(req.attrib["weight"])
        shift_off[(emp, day, shift)] = weight

    shift_on = {}
    for req in root.findall(".//ShiftOnRequests/ShiftOn"):
        emp = req.find("EmployeeID").text
        day = int(req.find("Day").text)
        shift = req.find("Shift").text
        weight = int(req.attrib["weight"])
        shift_on[(emp, day, shift)] = weight

    # Cover requirements
    cover = {}
    for c in root.findall(".//CoverRequirements/DateSpecificCover"):
        day = int(c.find("Day").text)
        for cv in c.findall("Cover"):
            shift = cv.find("Shift").text
            min_staff = int(cv.find("Min").text)
            max_staff = int(cv.find("Max").text)
            cover[(day, shift)] = {"min": min_staff, "max": max_staff}

    # Contracts (consecutive shifts/days off)
    contracts = {}
    for c in root.findall(".//Contracts/Contract"):
        cid = c.attrib["ID"]
        contracts[cid] = {}
        # Max consecutive shifts
        mc = c.find(".//MaxSeq")
        contracts[cid]["max_seq"] = int(mc.attrib["value"]) if mc is not None else None
        # Min consecutive shifts
        mn = c.find(".//MinSeq")
        contracts[cid]["min_seq"] = int(mn.attrib["value"]) if mn is not None else None
        # Min consecutive days off
        mo = c.find(".//MinSeq[@shift='-']")
        contracts[cid]["min_off"] = int(mo.attrib["value"]) if mo is not None else None

    return {
        "days": days,
        "shifts": shifts,
        "employees": employees,
        "fixed_assignments": fixed_assignments,
        "shift_off": shift_off,
        "shift_on": shift_on,
        "cover": cover,
        "contracts": contracts,
        "emp_contracts": emp_contracts
    }