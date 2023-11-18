These scripts were generated with the assistance of ChatGPT-4 to create an on-call schedule for 5 ophthalmology residents at Yale New Haven Hospital. 

The steps involved to generate this code with the assistance of ChatGPT-4 for those with minimal programming background has been written up in a manuscript
which is currently under review.

Below are instructions on how to use the below code to automatically generate the call schedule, validate the call schedule, and transform the schedule
into a format which can be uploaded directly to google calendar.

requirements.txt contains a list of the required libraries and their versions which need to be installed before running the code.

resident_unavailable_dates.csv is a csv file which contains the dates that each resident is unavailable to be on call. The dates must be formatted in the following
format: YYYY-MM-DD. Unavailable dates must be listed in the columns under each doctor.

holidays.csv is a csv file which contains the dates which should not be included on the schedule (Holidays were covered according to a different scheduling system).
They must be listed in column A under excluded dates in the same date format as defined above.

Run generate_schedule.py first. This script generates a csv filed titled schedule.csv which is a call schedule according to certain constraints. It imports
resident_unavailable_dates.csv and holidays.csv to guarantee residents are not working on their unavailable dates and holidays are not included in the schedule.

Run validation.py second. This script will confirm that residents are not working on their unavailable dates and holidays are not included in the schedule and will
print the distribution of weekday call, saturday call, and sunday call.

Run generate_gcalendar next to transform schedule.csv into a format that can be uploaded directly to google calendar. The output csv is google_calendar_schedule.csv.
The doctor name legend should be changed so that the numbers on schedule.csv are replaced with resident names. 0 corresponds to Doctor 1 in the resident_unavailable_dates.csv
spreadsheet, 1 to Doctor 2, 2 to Doctor 3, 3 to Doctor 4, and 4 to Doctor 5.

For questions regarding the code, users can email the developer Mac Singer at maxwell.singer@yale.edu..