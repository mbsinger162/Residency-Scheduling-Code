import csv

schedule_csv_path = "schedule.csv"

# Sample doctor name legend
doctor_name_legend = {
    0: "Resident Name 1",
    1: "Resident Name 2",
    2: "Resident Name 3",
    3: "Resident Name 4",
    4: "Resident Name 5",
}


def main():
# def main():
    # Read the schedule from the input CSV file
    with open(schedule_csv_path, "r") as infile:
        reader = csv.reader(infile)

        # Skip the header row
        next(reader)

        # Write the updated schedule to the output CSV file
        with open("google_calendar_schedule.csv", "w") as outfile:
            writer = csv.writer(outfile)

            # Write the header row
            writer.writerow(["Subject", "Start Date", "End Date", "All Day Event", "Description"])

            # Process the data rows
            for row in reader:
                date, doctor_id = row
                doctor_name = doctor_name_legend[int(doctor_id)]
                writer.writerow([f'On-call: {doctor_name}', date, date, "True", ""])

            
if __name__ == "__main__":
    main()
