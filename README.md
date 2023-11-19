# Ophthalmology On-Call Schedule Generator for 2023-2024

These scripts were generated with the assistance of ChatGPT-4 to create an on-call schedule for 5 ophthalmology residents at Yale New Haven Hospital for the 2023-2024 academic year.

The steps involved in generating this code with the assistance of ChatGPT-4 for those with minimal programming background have been written up in a manuscript which is currently under review.

## Instructions for Use

Below are instructions on how to use the provided code to automatically generate the call schedule, validate the call schedule, and transform the schedule into a format which can be uploaded directly to Google Calendar.

1. **`requirements.txt`**: 
   - Contains a list of the required libraries and their versions which need to be installed before running the code.

2. **`resident_unavailable_dates.csv`**: 
   - A CSV file containing the dates each resident is unavailable for call. 
   - Dates must be formatted as `YYYY-MM-DD`.
   - Unavailable dates should be listed in the columns under each doctor's name.

3. **`holidays.csv`**: 
   - A CSV file containing dates that should not be included in the schedule (Holidays covered by a different scheduling system).
   - Dates should be listed in column A under 'excluded dates' in the `YYYY-MM-DD` format.

### Running the Scripts

1. **Run `generate_schedule.py` first**:
   - Generates a CSV file titled `schedule.csv`, which is the call schedule adhering to specific constraints.
   - Imports `resident_unavailable_dates.csv` and `holidays.csv` to ensure residents are not working on their unavailable dates and holidays.
   - To alter the schedule's date range, change the `start_date` variable on line 164 and the `end_date` variable on line 165.

2. **Run `validation.py` second**:
   - Validates that residents are not working on their unavailable dates and holidays are excluded.
   - Prints the distribution of weekday call, Saturday call, and Sunday call.

3. **Run `generate_gcalendar` next**:
   - Transforms `schedule.csv` into a format for Google Calendar upload.
   - Produces `google_calendar_schedule.csv`.
   - Modify the doctor name legend so that numbers on `schedule.csv` correspond to resident names as per `resident_unavailable_dates.csv`.

### Web App with User Interface!

Those who wish to generate their own call schedules through a user interface, rather than executing python code, can use our [website](https://yaleophthopgy2callschedule.streamlit.app/).

Please note that files specifying residents unavailable dates and holidays must be csv files formatted as is specified above for **`resident_unavailable_dates.csv`** and **`holidays.csv`**. Users may reference these spreadsheets as a guide for formatting when developing their own personalized csv files.

## Support

For questions regarding the code, users can email the developer, Mac Singer, at [maxwell.singer@yale.edu](mailto:maxwell.singer@yale.edu).
