import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')


def setup_plot_style():
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  
    plt.rcParams['axes.unicode_minus'] = False
    plt.style.use('seaborn-v0_8-whitegrid')

def plot_slot_utilization(result, exam_students, weights, intervals=70, days=10, slots_per_day=7):
    """
    """
    setup_plot_style()
    slot_exams = defaultdict(int)
    slot_students = defaultdict(int)
    
    for exam, slot in result.items():
        slot_exams[slot] += 1
        slot_students[slot] += len(exam_students[exam])
    
    slots = np.arange(intervals)
    exams_counts = [slot_exams[s] for s in slots]
    students_counts = [slot_students[s] for s in slots]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8))
    
    
    bars1 = ax1.bar(slots, exams_counts, color='steelblue', alpha=0.8, label='exams')
    ax1.set_ylabel('Number of exams')
    ax1.set_title('exam Distribution per Time Slot')
    ax1.axhline(np.mean(exams_counts), color='red', linestyle='--', label=f'Avg: {np.mean(exams_counts):.2f}')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    
    ax2.plot(slots, students_counts, color='darkorange', marker='o', markersize=2, label='Students')
    ax2.set_xlabel('Time Slot Index (0-69)')
    ax2.set_ylabel('Number of Students Affected')
    ax2.set_title('Student Load per Time Slot')
    ax2.axhline(np.mean(students_counts), color='red', linestyle='--', label=f'Avg: {np.mean(students_counts):.2f}')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    
    for ax in [ax1, ax2]:
        for day in range(days):
            if day % 7 >= 5:  
                start = day * slots_per_day
                end = (day + 1) * slots_per_day
                ax.axvspan(start, end - 0.5, alpha=0.1, color='gray', label='Weekend' if ax == ax1 else "")
    
    plt.tight_layout()
    plt.savefig('./Notebooks/ExamSchedule/slot_utilization.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_cost_analysis(result, exam_students, weights, intervals=70):
    """
    """
    setup_plot_style()
    actual_costs = np.zeros(intervals)
    
    for exam, slot in result.items():
        actual_costs[slot] += weights[slot] * len(exam_students[exam])
    
    slots = np.arange(intervals)
    
    fig, ax = plt.subplots(figsize=(16, 6))
    
    
    ax.bar(slots, weights, alpha=0.4, color='gray', label='Slot Weight (Base Cost)')
    ax.plot(slots, actual_costs, color='red', linewidth=2, marker='.', label='Actual Cost Incurred')
    
    ax.set_xlabel('Time Slot Index')
    ax.set_ylabel('Cost')
    ax.set_title('Cost Analysis: Slot Weight vs Actual Cost')
    ax.legend()
    ax.grid(alpha=0.3)
    
    
    high_cost_slots = np.where(actual_costs > np.percentile(actual_costs, 90))[0]
    ax.scatter(high_cost_slots, actual_costs[high_cost_slots], color='red', s=50, zorder=5, label='Top 10% Cost Slots')
    
    plt.tight_layout()
    plt.savefig('./Notebooks/ExamSchedule/cost_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_student_load_distribution(result, student_exams, intervals=70, days=10, slots_per_day=7):
    """
    """
    setup_plot_style()
    student_loads = []
    consecutive_exams = []
    
    for student in range(len(student_exams)):
        slots_taken = sorted([result[c] for c in student_exams[student] if c in result])
        load = len(slots_taken)
        student_loads.append(load)
        
        
        consec = sum(1 for i in range(len(slots_taken)-1) if slots_taken[i+1] - slots_taken[i] == 1)
        consecutive_exams.append(consec)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    
    ax1.hist(student_loads, bins=range(1, 12), edgecolor='black', color='skyblue', alpha=0.8)
    ax1.set_xlabel('Number of Exams per Student')
    ax1.set_ylabel('Number of Students')
    ax1.set_title('Student Exam Load Distribution')
    ax1.grid(axis='y', alpha=0.3)
    
    
    ax2.hist(consecutive_exams, bins=range(0, 6), edgecolor='black', color='lightcoral', alpha=0.8)
    ax2.set_xlabel('Number of Consecutive Exam Pairs')
    ax2.set_ylabel('Number of Students')
    ax2.set_title('Consecutive Exam Burden')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('./Notebooks/ExamSchedule/student_load.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_weekly_heatmap(result, exam_students, weights, days=10, slots_per_day=7):
    """
    """
    setup_plot_style()
    
    
    heatmap_data = np.zeros((days, slots_per_day))
    time_labels = ['08:00', '10:30', '14:00', '16:30', '19:00', '21:30', '23:00']  
    
    for exam, slot in result.items():
        day = slot // slots_per_day
        time_idx = slot % slots_per_day
        cost = weights[slot] * len(exam_students[exam])
        heatmap_data[day, time_idx] += cost
    
    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto', interpolation='nearest')
    
    
    ax.set_xticks(np.arange(slots_per_day))
    ax.set_yticks(np.arange(days))
    ax.set_xticklabels(time_labels[:slots_per_day], rotation=45, ha='right')
    ax.set_yticklabels([f'Day {d+1}' for d in range(days)])
    

    cbar = plt.colorbar(im, ax=ax, label='Total Cost (Weight × Students)')
    
    
    for day in range(days):
        for t in range(slots_per_day):
            val = heatmap_data[day, t]
            if val > 0:
                ax.text(t, day, f'{val:.0f}', ha='center', va='center', fontsize=7, color='black')
    
    ax.set_title('Weekly Exam Schedule Heatmap (Cost Intensity)')
    ax.set_xlabel('Time of Day')
    ax.set_ylabel('Day')
    
    
    for day in range(days):
        if day % 7 >= 5:  
            ax.axhspan(day - 0.5, day + 0.5, alpha=0.15, color='blue', label='Weekend' if day == 5 else "")
    
    plt.tight_layout()
    plt.savefig('./Notebooks/ExamSchedule/fig/weekly_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_all_visualizations(result, student_exams, exam_students, weights, intervals=70):
    """
    """
    print("🎨 Generating visualizations...")
    plot_slot_utilization(result, exam_students, weights, intervals)
    print("✅ Slot utilization plot saved.")
    
    plot_cost_analysis(result, exam_students, weights, intervals)
    print("✅ Cost analysis plot saved.")
    
    plot_student_load_distribution(result, student_exams, intervals)
    print("✅ Student load plot saved.")
    
    plot_weekly_heatmap(result, exam_students, weights)
    print("✅ Weekly heatmap saved.")
    
    print("🎉 All visualizations completed! Check the generated PNG files.")