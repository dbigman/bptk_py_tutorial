# KPI Specifications — HMLV Manufacturing Simulator (MVP)

This document lists the canonical KPI definitions used by the simulator and reporting pipeline.

1. OTD % (On-Time Delivery)
   - Definition: percent of jobs with completion_time <= due_date
   - Sampling: all jobs
   - Units: percent

2. Lead Time
   - Avg Lead Time: mean(completion_time - release_time)
   - P90 Lead Time: 90th percentile of (completion_time - release_time)
   - Sampling: all jobs
   - Units: time (hours/days)

3. WIP (Work In Progress)
   - Definition: time-averaged count of jobs in system over run horizon
   - Units: jobs

4. Utilization (Machine / Labor)
   - Definition: busy_time / available_time per resource
   - Units: percent

5. Setup Hours
   - Definition: sum of setup_time across all machine events
   - Units: hours

6. Scrap / Rework Rate
   - Definition: rework_count / inspected_count
   - Units: percent

Export:
- KPI reports must be exportable as compact CSV with header rows and as a JSON KPIReport object for downstream consumption.