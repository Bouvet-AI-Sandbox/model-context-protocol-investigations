# {Insert incident report title}

??? tip "Guideline for incident report title"

    Title should be a single line of text that includes:

    - Application - The application(s) affected
    - Incident type - Type of incident [Downtime, Instability]
    - Date - In format YYYY-MM-DD
    - (Optional) Timeperiode - How long the incident lasted
    - (Optional) Additional details - A few words understanable by the business about incident

    Incident types:

    - Downtime - Service is unavailable for all end-users
    - Instability - Service is degraded or unavailable for some end-users
    - Data quality - Issues in the data quality or synchronization between systems
    - Security - Security related incident

??? example "Title examples"
    {application-name} downtime for 1 hour on {date-YYYY-MM-DD}

    {module-name} in {application-name} experienced instability during weekend from {date-YYYY-MM-DD}  

## Executive summary
{Insert short description using "business language"}

??? tip "Guideline for executive summary"
    The target audience is the business product owner and end-users.

    The executive summary should include the following: 

    - What happened 
    - Business and user impact
        - Including how we communicated
    - Resolution
    - Learnings

??? example "Executive summary examples"
    On {date}, {application-name} experienced significant service disruptions that impacted end-users from {start-time} CET to {end-time}CET. 

    In this time periode, the {application-name} was unavailable to end-users. A service message for end-users was in place at {time-HHMM}.

    The issue was caused by {root-cause} internal. Actions have been identified to reduce the likelihood of this issue occurring in the future.

    We apologize for the any inconvenience this may have caused and will use this report to learn from the event.

## Root cause / What went wrong and why?
{Insert a detailed description of the root cause with relevant links}

??? tip "Guideline for executive summary"
    The target audience is technical product owner, tech leads for other teams within the portfolio and the delivery team itself.

## Timeline / Response
This section provides a timeline of events from the incident occured to it was resolved. 

| Date      | Time          | Event             | Description                                   |
|-----------|---------------|-------------------|-----------------------------------------------|
|           |{Insert HH:MM} |{Insert event type}|{Insert details}                               |
|           |               |                   |                                               |
|           |               |                   |                                               |


??? tip "Guideline for timeline"
    Include details such as:
    
    - How the incident was detected
    - How we communicated with end-users and stakeholders
    - How we responded and organized the work
    - Findings related to the root cause

??? example "Alternative - Use list-based template"
    Timeline of events:

    - {time-HHMM}: ...
    - {time-HHMM}:: ...

## Actions and learnings
Actions have been initiated to address the underlying root cause of the incident and to reduce the likelihood of similar incidents in the future:

- {Insert actions with links to backlog items}

Lessons learned: 

- {Insert lessons learned}