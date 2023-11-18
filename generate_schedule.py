import csv
import datetime
from collections import deque
from typing import List
import random
import itertools
from pulp import LpProblem, LpVariable, LpBinary, LpMinimize, lpSum, LpInteger, PULP_CBC_CMD, LpStatus, value

DOCTOR_DATA_FILENAME = "resident_unavailable_dates.csv"
EXCLUDED_DATES_FILENAME = "holidays.csv"
OUTPUT_FILENAME = "schedule.csv"

TIME_LIMIT = 60  # Time limit in seconds (e.g., 600 seconds or 10 minutes)
ACCEPTABLE_GAP = 0.1  # Acceptable optimality gap as a fraction (e.g., 0.1 for a 10% gap)

class Doctor:
    def __init__(self, id):
        self.id = id
        self.unavailable_dates = []

def read_doctor_data(filename):
    doctor_data = {}
    with open(filename, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row

        for index, column in enumerate(zip(*reader)):
            doctor_data[index + 1] = [datetime.datetime.strptime(date, "%Y-%m-%d").date() for date in column if date]

    return doctor_data

def read_excluded_dates(filename):
    excluded_dates = []
    with open(filename, mode="r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            for date in row:
                if date:
                    excluded_dates.append(datetime.datetime.strptime(date, "%Y-%m-%d").date())
    return excluded_dates

def date_range(start_date, end_date):
    return [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]

def add_constraints(prob, doctors, schedule_vars, start_date, end_date, excluded_dates):

    num_doctors = len(doctors)
    days_range = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        # Create additional variables for consecutive weekends worked
    consecutive_weekends_worked = LpVariable.dicts("consecutive_weekends_worked", (range(num_doctors), days_range[:-1]), cat="Binary")

    for date in date_range(start_date, end_date):


        if date in excluded_dates:
            continue

        # Same doctor works on Friday and Sunday
        if date.weekday() == 4:  # Friday
            sunday = date + datetime.timedelta(days=2)
            if sunday <= end_date and sunday not in excluded_dates:
                for i in range(len(doctors)):
                    prob += schedule_vars[i][date] == schedule_vars[i][sunday]

        # Doctors should not work two days in a row (excluding Friday-Sunday)
        if date.weekday() != 5 and date + datetime.timedelta(days=1) <= end_date:
            next_day = date + datetime.timedelta(days=1)
            for i in range(len(doctors)):
                prob += schedule_vars[i][date] + schedule_vars[i][next_day] <= 1

        # Doctors should not work two weekends in a row
        if date.weekday() != 5 and date + datetime.timedelta(days=1) <= end_date:
            next_day = date + datetime.timedelta(days=1)
            for i in range(len(doctors)):
                prob += schedule_vars[i][date] + schedule_vars[i][next_day] <= 1

        # Doctors should not work if they worked two days before (excluding Sunday after working on Friday)
        if date.weekday() not in (0, 6) and date - datetime.timedelta(days=2) >= start_date:
            prev_day = date - datetime.timedelta(days=2)
            for i in range(len(doctors)):
                prob += schedule_vars[i][prev_day] + schedule_vars[i][date] <= 1

        #Doctors should not work two weekends in a row
        if date.weekday() == 4:  # Friday
            next_friday = date + datetime.timedelta(days=7)
            next_saturday = date + datetime.timedelta(days=8)
            prev_saturday = date - datetime.timedelta(days=1)
            for i in range(len(doctors)):
                if prev_saturday >= start_date and next_friday <= end_date:
                    prob += schedule_vars[i][prev_saturday] + schedule_vars[i][date] + schedule_vars[i][next_friday] <= 1
                if prev_saturday >= start_date and next_saturday <= end_date:
                    prob += schedule_vars[i][prev_saturday] + schedule_vars[i][date] + schedule_vars[i][next_saturday] <= 1

        if date.weekday() == 5:  # Saturday
            next_friday = date + datetime.timedelta(days=6)
            next_saturday = date + datetime.timedelta(days=7)
            for i in range(len(doctors)):
                if next_friday <= end_date:
                    prob += schedule_vars[i][date] + schedule_vars[i][next_friday] <= 1
                if next_saturday <= end_date:
                    prob += schedule_vars[i][date] + schedule_vars[i][next_saturday] <= 1


        # Ensure only one doctor is assigned per day
        prob += lpSum([schedule_vars[i][date] for i in range(len(doctors))]) == 1

        # Doctors should not work on their unavailable dates
        for i, doctor in enumerate(doctors):
            if date in doctor.unavailable_dates:
                prob += schedule_vars[i][date] == 0      


def is_date_excluded(date, excluded_dates):
    return date in excluded_dates

def write_schedule_to_csv(schedule, filename):
    with open(filename, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Doctor"])

        for entry in schedule:
            writer.writerow([entry[0].strftime("%Y-%m-%d"), entry[1]])

def generate_schedule_with_pulp(start_date, end_date, doctors, excluded_dates):
    prob = LpProblem("Doctor_Scheduling_Problem", LpMinimize)

    schedule_vars = LpVariable.dicts("schedule", (range(len(doctors)), date_range(start_date, end_date)), cat=LpBinary)

    weekday_diff_vars = LpVariable.dicts("weekday_diff", (range(len(doctors)), range(len(doctors))), lowBound=0, cat=LpInteger)
    friday_sunday_diff_vars = LpVariable.dicts("friday_sunday_diff", (range(len(doctors)), range(len(doctors))), lowBound=0, cat=LpInteger)
    saturday_diff_vars = LpVariable.dicts("saturday_diff", (range(len(doctors)), range(len(doctors))), lowBound=0, cat=LpInteger)

    weekday_shifts = [lpSum([schedule_vars[i][d] for d in date_range(start_date, end_date) if d.weekday() in (0, 1, 2, 3) and d not in excluded_dates]) for i in range(len(doctors))]
    friday_sunday_shifts = [lpSum([schedule_vars[i][d] for d in date_range(start_date, end_date) if d.weekday() in (4, 6) and d not in excluded_dates]) for i in range(len(doctors))]
    saturday_shifts = [lpSum([schedule_vars[i][d] for d in date_range(start_date, end_date) if d.weekday() == 5 and d not in excluded_dates]) for i in range(len(doctors))]

    # Objective function
    prob += lpSum([weekday_diff_vars[i][j] for i in range(len(doctors)) for j in range(i+1, len(doctors))]) \
          + lpSum([friday_sunday_diff_vars[i][j] for i in range(len(doctors)) for j in range(i+1, len(doctors))]) \
          + lpSum([saturday_diff_vars[i][j] for i in range(len(doctors)) for j in range(i+1, len(doctors))])

    # Constraints for the differences in the number of shifts
    for i in range(len(doctors)):
        for j in range(i + 1, len(doctors)):
            prob += weekday_diff_vars[i][j] >= weekday_shifts[i] - weekday_shifts[j]
            prob += weekday_diff_vars[i][j] >= weekday_shifts[j] - weekday_shifts[i]
            prob += friday_sunday_diff_vars[i][j] >= friday_sunday_shifts[i] - friday_sunday_shifts[j]
            prob += friday_sunday_diff_vars[i][j] >= friday_sunday_shifts[j] - friday_sunday_shifts[i]
            prob += saturday_diff_vars[i][j] >= saturday_shifts[i] - saturday_shifts[j]
            prob += saturday_diff_vars[i][j] >= saturday_shifts[j] - saturday_shifts[i]

    add_constraints(prob, doctors, schedule_vars, start_date, end_date, excluded_dates)

    prob.solve(PULP_CBC_CMD(maxSeconds=TIME_LIMIT, fracGap=ACCEPTABLE_GAP))
    schedule = [(date, i) for i in range(len(doctors)) for date in date_range(start_date, end_date) if value(schedule_vars[i][date]) == 1]
    sorted_schedule = sorted(schedule, key=lambda x: x[0])

    return sorted_schedule


def main():
    start_date = datetime.date(2023, 7, 1)
    end_date = datetime.date(2024, 6, 30)

    excluded_dates = read_excluded_dates(EXCLUDED_DATES_FILENAME)
    doctor_data = read_doctor_data(DOCTOR_DATA_FILENAME)

    MAX_ITERATIONS = 10000

    # Initialize doctors
    doctors = []
    for i in range(1, 6):
        doctor = Doctor(i)
        if i in doctor_data:
            doctor.unavailable_dates = doctor_data[i]
        doctors.append(doctor)

    schedule = generate_schedule_with_pulp(start_date, end_date, doctors, excluded_dates)
    write_schedule_to_csv(schedule, OUTPUT_FILENAME)
    print(f"Schedule successfully generated and saved to {OUTPUT_FILENAME}")

if __name__ == "__main__":
    main()
