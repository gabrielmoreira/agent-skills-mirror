---
name: interview-calendar
description: Use when I ask for an interview calendar, an interview schedule or interview clashes for a week. Builds a Monday-to-Friday calendar from the interviews table and flags double-bookings.
---

# Interview calendar

Turn the list of interviews into a weekly calendar that a recruiter can read at a glance, and flag clashes.

## Input
- The interviews table (tblInterviews) with Interview_ID, Role, Interviewer, Interview_Date, Start_Time, Duration_Min, Mode and Room.
- A week start date (a Monday). If I do not give one, ask me for it before you start.

## Steps
1. Never change tblInterviews or any existing sheet.
2. Create a new sheet named Cal_<week start as yyyy-mm-dd>, e.g. Cal_2026-07-06. If it already exists, replace its contents.
3. In A1 write "Interview calendar - week of <week start as dd mmm yyyy>". In A2 write "Created by Copilot".
4. Build the grid from row 4: column A holds 30-minute time slots from 09:00 to 17:30; columns B to F are Monday to Friday, with the date in each header.
5. Place every interview of that week in each slot it covers (an interview of 60 minutes fills two slots). Show "Interviewer - Role (Mode)". If two interviews share a slot, show both, separated by " | ".
6. Colour Onsite interviews light blue and Video interviews light green.
7. Find clashes: two interviews on the same date that overlap in time AND have the same Interviewer, or are both Onsite in the same Room. Colour those calendar cells red.
8. Below the grid, add a table Clashes with Type (Interviewer or Room), Interview_ID 1, Interview_ID 2, Who or Room, Date and Time. If there are none, write "No clashes this week".
9. Next to it, add a Summary table: interviews per day, interviews per Interviewer and the week total.
10. Freeze the header row and time column, set column widths so the text is readable, and do not merge cells.

## Check before you finish
- The number of interviews placed equals the number of rows in tblInterviews for that week.
- Report the week total, the busiest day and every clash in your reply.
