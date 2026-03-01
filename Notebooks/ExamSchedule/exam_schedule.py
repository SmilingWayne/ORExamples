# data generate ... 

import random
import numpy as np
from visualize import plot_all_visualizations
from ortools.sat.python import cp_model

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

def generate_intervals_weights():
    weights = np.array([[1] * 7 for _ in range(10)])
    weights[0] += 3 # 8:00
    weights[5] += 3 # 8:00
    weights[4] += 1 # night exam
    weights[9] += 1 # night exam 
    weights[0:5, -2: ] += 2 # weekend 
    weights[5:10, -2: ] += 4 # weekend
    weights[9, -2: ] += 3 # "goal keeper"
    # The result is just like:
    # [[4 4 4 4 4 6 6]
    #  [1 1 1 1 1 3 3]
    #  [1 1 1 1 1 3 3]
    #  [1 1 1 1 1 3 3]
    #  [2 2 2 2 2 4 4]
    #  [4 4 4 4 4 8 8]
    #  [1 1 1 1 1 5 5]
    #  [1 1 1 1 1 5 5]
    #  [1 1 1 1 1 5 5]
    #  [2 2 2 2 2 8 8]]
    # Two weeks in total, each day has 7 time slots (based on array shape 10x7=70)
    # Apparently, students don't like 8:00~10:00, and 19:00~21:00 exams.
    # Apparently too, students don't like exams during weekends.
    weights = weights.flatten()
    return list(weights)

def generate_student_exam_relation(num_exams, num_students):
    # exams for student
    student_exams = {}
    exam_students = {}
    # all exam has student
    for exam in range(num_exams):
        if exam not in exam_students:
            exam_students[exam] = []
        student = random.randint(0, num_students - 1)
        if student in student_exams:
            student_exams[student].append(exam)
        else:
            student_exams[student] = [exam]
        exam_students[exam].append(student)
    
    # each students has 2~10 exams ... 
    for student in range(num_students):
        if student not in student_exams:
            student_exams[student] = []
        while len(student_exams[student]) < random.randint(2, 10):
            exam = random.randint(0, num_exams - 1)
            if exam not in student_exams[student] and len(student_exams[student]) < 10:
                student_exams[student].append(exam)
                exam_students[exam].append(student)
    return student_exams, exam_students

def check_feasibility(result, student_exams, exam_students, weights, num_exams, num_students, intervals):
    feasible = True
    # check if the result is okay ... 
    # 1. if all exams are assigned ... 
    if len(result.keys()) != num_exams:
        feasible = False
    # 2. if students time conflict ... 
    if not feasible:
        return feasible    
    for student in range(num_students):
        check_interv = set()
        for exam in student_exams[student]:
            if exam in result:
                slot = result[exam]
                if slot in check_interv:
                    print(f"Wrong! Student {student} has conflict with exam {exam} at interval {slot}")
                    feasible = False 
                else:
                    check_interv.add(slot)
            else:
                # exam not assigned
                feasible = False
    return feasible


def solver(student_exams, exam_students, weights, num_exams, num_students, intervals):
    # Create the CP-SAT model
    model = cp_model.CpModel()
    
    # 1. Decision Variables
    # x[exam, interv] = 1 if exam is assigned to interval, else 0
    x = {}
    for exam in range(num_exams):
        for interv in range(intervals):
            x[exam, interv] = model.NewBoolVar(f"exam_{exam}_slot_{interv}")

    # 2. Objective Function
    # Minimize total weighted cost: sum(x * weight * num_students_in_exam)
    objective_terms = []
    for exam in range(num_exams):
        num_students_in_exam = len(exam_students[exam])
        weight_factor = weights[interv] * num_students_in_exam if (interv := 0) else 0 # Placeholder logic fix below
        
        # We need to iterate intervals inside to build the sum correctly
        for interv in range(intervals):
            cost_coeff = weights[interv] * len(exam_students[exam])
            objective_terms.append(x[exam, interv] * cost_coeff)

    model.Minimize(sum(objective_terms))

    # 3. Constraints
    
    # Constraint A: Each exam must be assigned to exactly one interval
    for exam in range(num_exams):
        model.AddExactlyOne(x[exam, interv] for interv in range(intervals))

    # Constraint B: No student can have more than one exam at the same interval
    # For each student and each interval, sum of exams assigned <= 1
    for student in range(num_students):
        exams_for_student = student_exams[student]
        for interv in range(intervals):
            # Collect variables for this student at this interval
            student_vars = [x[exam, interv] for exam in exams_for_student]
            if student_vars:
                model.AddAtMostOne(student_vars)

    # 4. Solve
    solver = cp_model.CpSolver()
    # Optional: Set a time limit to prevent hanging on large instances
    solver.parameters.max_time_in_seconds = 60.0 
    solver.parameters.num_search_workers = 8 # Use multiple threads

    status = solver.Solve(model)

    result = dict()
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"Solution Status: {solver.StatusName(status)}")
        print(f"Objective Value: {solver.ObjectiveValue()}")
        for exam in range(num_exams):
            for interv in range(intervals):
                if solver.Value(x[exam, interv]) == 1:
                    result[exam] = interv
                    # Uncomment below for detailed logging
                    # print(f"exam {exam}, with {len(exam_students[exam])} students, is allocated to interval {interv}")
        return result
    else:
        print("No solution found.")
        return result    


if __name__ == "__main__":
    num_exams = 300
    num_students = 2000
    student_exams, exam_students = generate_student_exam_relation(num_exams, num_students)
    weights = generate_intervals_weights()
    intervals = 70
    result = solver(student_exams, exam_students, weights, num_exams, num_students, intervals)
    check = check_feasibility(result, student_exams, exam_students, weights, num_exams, num_students, intervals)
    print(f"Pass feasibility check? {check}")
    if check:
        if result:  # only when checked!
            plot_all_visualizations(result, student_exams, exam_students, weights, intervals)