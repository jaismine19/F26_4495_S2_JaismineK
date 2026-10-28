# Work Log - Jaismine Kaur (300415820)

| Date | Hours | Description of work done |
|---|---|---|
| Sep 26, 2026 | 1.5 | Set up our shared project on GitHub: created the repository, invited Shashank as a collaborator, and made the first upload |
| Oct 9, 2026 | 1.0 | Read through the project to remind myself where we are, what the plan is, and what is due next |
| Oct 9, 2026 | 0.5 | Together with Shashank, created the project folders and the file that keeps large and private files out of GitHub |
| Oct 9, 2026 | 0.5 | Together with Shashank, downloaded the Vancouver crime data from the police open-data website and went through the quality report (928,362 rows, missing year 2022, 83K rows with no location) |
| Oct 9, 2026 | 0.25 | Helped write the document that explains our data - where it comes from, what each column means, and its known problems |
| Oct 9, 2026 | 0.25 | Read Shashank's first version of the security plan and gave feedback |
| Oct 9, 2026 | 0.25 | Together with Shashank, went through the data cleaning steps (removed repeated rows; 928,362 down to 893,851 rows) |
| Oct 9, 2026 | 0.25 | Read the privacy notes document and checked it over |
| Oct 9, 2026 | 0.25 | Updated the README progress table and uploaded the work to GitHub |
| Oct 11, 2026 | 1.0 | Set up the coding environment on my own computer and installed all the needed tools |
| Oct 11, 2026 | 1.0 | Ran the whole data preparation process myself from start to finish: download, quality check, and cleaning |
| Oct 11, 2026 | 0.5 | Read the three data preparation scripts and their reports so I understand how each step works |
| Oct 11, 2026 | 0.5 | Read the data explanation and privacy documents |
| Oct 11, 2026 | 0.5 | Opened the app and explored it: the overview page, the time-patterns page, and the add-incident page with its three user roles |
| Oct 11, 2026 | 0.5 | Read through the app's structure: how the pages connect, the login system, and how data is loaded |
| Oct 11, 2026 | 0.5 | Read the automated tests and ran them (14 passing) |
| Oct 11, 2026 | 0.5 | Made a small app change: removed the course-code label from the sidebar and uploaded it |
| Oct 11, 2026 | 1.5 | Explored the data for patterns: when crimes happen during the day (and found that violent crimes have their exact time hidden on purpose), and how COVID changed the numbers |
| Oct 11, 2026 | 1.0 | Wrote a notebook that documents 5 findings with charts |
| Oct 11, 2026 | 1.0 | Read about ways to explore data and thought about how to remove repeated rows |
| Oct 12, 2026 | 1.0 | Cleaned up the notebook: better headings and a clearer layout |
| Oct 12, 2026 | 0.5 | Prepared Progress Report #1: the hours table, the summary, the list of uploaded work, and the AI-use section |
| Oct 16, 2026 | 1.5 | Built the statistics page: two "is there a connection?" tests (crime type vs season, crime type vs day of week) with easy-to-read results and tables |
| Oct 16, 2026 | 3.0 | Chased and fixed a bug where dates were being saved in two different formats, which broke anything that used dates; fixed the saving side and made the reading side safe too |
| Oct 22, 2026 | 1.0 | Looked through the project to pick a feature I could build completely - from the screen to the database and back - for the mid-course demo; chose the Add Incident feature |
| Oct 22, 2026 | 1.5 | Built the Add Incident feature end to end: a form with checks, saved into a database with safe queries, each record stored with who added it and when, and shown in the app |
| Oct 22, 2026 | 1.0 | Wrote tests for the database, including trying fake "hacking" inputs to check they are stored as plain text and cannot break anything (51 tests passing) |
| Oct 22, 2026 | 1.5 | Combined my work with Shashank's overlapping changes (login lockout and the Audit Log page) and updated the Security page statuses |
| Oct 22, 2026 | 1.0 | Practiced the demo flow (login, roles, audit trail) and made a cheat sheet for the presentation |
| Oct 22, 2026 | 1.0 | Tested the Crime Map as if I were seeing it for the first time and listed what felt unclear (color meaning, hover info, circle sizes) |
| Oct 22, 2026 | 1.0 | Redesigned the map page for everyday users: a simple how-to guide, big-picture numbers, automatically written neighbourhood summaries, and a full details table |
| Oct 22, 2026 | 1.5 | Fixed the map interactivity: switched to a map tool whose hover popups and click-to-highlight work reliably |
| Oct 22, 2026 | 0.5 | Fixed the broken map background (the old free map provider started asking for an API key) by switching to a free street-map provider |
| Oct 22, 2026 | 1.0 | Fixed a crash that happened when a filter left no usable location data, and added a test so it cannot happen again (62 tests passing) |
| Oct 23, 2026 | 1.0 | Started planning the neighbourhood map feature: decided to show neighbourhood-level summaries instead of exact points to protect privacy, and sketched how the page should flow |
| Oct 23, 2026 | 1.5 | Worked on the location math: converted the data's map coordinates into latitude and longitude using standard formulas, and checked the results against known Vancouver places |
| Oct 23, 2026 | 1.0 | Planned the forecast feature: decided to predict monthly crime counts using the average of recent months, and to honestly show how wrong the guess has been |
| Oct 23, 2026 | 1.5 | Built the forecast feature: pick a crime type, see the next 12 months predicted, and see how accurate it was in the past compared with a "same as last year" guess |
| Oct 23, 2026 | 0.5 | Wrote tests for the forecast math (7 new tests; 69 passing in total) |
| Oct 23, 2026 | 0.5 | Added a "tech stack" section to the README and the Methodology page so the tools we use are clear to anyone |
| Oct 23, 2026 | 0.5 | Updated the README progress table and folder-structure section to match the current state of the project |
| Oct 24, 2026 | 1.0 | Wrote the neighbourhood grouping step: counts and a middle-point location for each neighbourhood, skipping coordinates outside Vancouver |
| Oct 24, 2026 | 1.0 | Added the grouping step: automatically put neighbourhoods with similar crime mixes together, so the map shows patterns instead of plain dots |
| Oct 25, 2026 | 1.5 | Built the Crime Map page in the app: filters, the interactive map with circles sized by count and colored by pattern group, hover details, and the group summary table |
| Oct 25, 2026 | 1.0 | Wrote tests for the map math and grouping, and fixed a bug where neighbourhoods with missing names crashed the page (61 tests passing) |
| Oct 26, 2026 | 0.5 | Walked through the map page from top to bottom with the demo in mind and updated the demo cheat sheet |
| Oct 27, 2026 | 0.5 | Recorded the screen video of the app for the mid-course demo |
| Oct 27, 2026 | 1.0 | Wrote the video script and split it into two halves - mine for the data and analysis, Shashank's for the security side |
| Oct 27, 2026 | 1.0 | Worked on the voiceover for the video - tested the computer voice, and adjusted the pacing and timing to match the screen |
| Oct 28, 2026 | 1.0 | Rewrote the voiceover script with clearer explanations in formal language |
| Oct 28, 2026 | 0.5 | Prepared a spoken summary of my part of the project to present to the instructor |
| Oct 28, 2026 | 0.5 | Final preparation for the mid-course demonstration - went through the whole app flow and checked every page |
