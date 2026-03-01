# Exam Timetabling Problem

This project solves the Course Exam Assignment Problem using Google's **OR-Tools** (specifically the CP-SAT solver). The goal is to schedule exams for multiple courses into available time slots while minimizing student dissatisfaction and avoiding scheduling conflicts.

## Problem Overview

We have **500 course exams** and **3000 students**. There are **70 available time slots** (intervals). 
- Each course is ensured to have at least one student enrolled.
- Each time slot has a pre-defined **cost weight**. 
- The cost represents student welfare (e.g., students dislike early morning exams, weekend exams, or late-night exams).
- If a course is assigned to a slot, the cost incurred is proportional to the number of students taking that course multiplied by the slot's weight.

**Goal:** Assign each course exam to a time slot such that the **total weighted cost is minimized**.

## Constraints

1. **Course Assignment:** Every course exam must be assigned to exactly one time slot.
2. **Student Conflict:** No student can have two exams simultaneously in the same time slot.
3. **Course Load:** Students take a varying number of courses (ranging from 2 to 10).

## Mathematical Modeling

We model this as a **Binary Integer Programming** problem solved via Constraint Programming (CP-SAT).

### Decision Variables
Let $x_{c,s}$ be a binary variable:
$$
x_{c,s} = 
\begin{cases} 
1 & \text{if Course } c \text{ is assigned to Slot } s \\
0 & \text{otherwise}
\end{cases}
$$
Where $c \in \{0, \dots, 499\}$ and $s \in \{0, \dots, 69\}$.

### Objective Function
Minimize the total dissatisfaction cost:
$$
\text{Minimize } Z = \sum_{c} \sum_{s} (x_{c,s} \times \text{Weight}_s \times \text{NumStudents}_c)
$$

### Constraints
1. **Exactly One Slot per Course:**
   $$ \sum_{s} x_{c,s} = 1 \quad \forall c $$
2. **No Student Conflicts:**
   For every student $k$ and every slot $s$, the student cannot be taking more than one exam:
   $$ \sum_{c \in \text{Courses}_k} x_{c,s} \le 1 \quad \forall k, \forall s $$

## Implementation Details

- **Solver:** Google OR-Tools `cp_model` (CP-SAT Solver).
- **Language:** Python 3.
- **Variables:** `NewBoolVar` is used for $x_{c,s}$.
- **Constraints:** 
  - `AddExactlyOne` ensures course assignment.
  - `AddAtMostOne` efficiently handles student conflict constraints.
- **Optimization:** The solver is configured to use multiple search workers (`num_search_workers = 8`) for faster convergence on multi-core machines.

## How to Run

1. **Install Dependencies:**
   ```bash
   pip install ortools numpy
   ```