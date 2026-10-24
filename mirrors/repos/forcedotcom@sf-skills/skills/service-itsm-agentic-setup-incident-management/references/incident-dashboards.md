# Feature: Incident Dashboards (delegated to two SORs, one per persona)

How the orchestrator runs the **Incident Dashboards** feature over `itsm-incident-dashboard-enablement`
(Incident Manager) and `itsm-incident-fulfiller-dashboard-enablement` (Incident Fulfiller). Each SOR's own
steps and guidance decide *how*; the orchestrator runs them itself under its **SOR hand-off protocol** and
owns every user-facing gate. This file adds what is specific to the dashboards.

1. Unless the user already said, ask which (`AskUserQuestion`): the **Incident Manager** dashboards (the
   Incident Manager dashboards and the Home page dashboards — `itsm-incident-dashboard-enablement`), the
   **Incident Fulfiller** dashboards (the fulfiller work view and the fulfiller Home page —
   `itsm-incident-fulfiller-dashboard-enablement`), or both. `discover` and `describe` each chosen SOR
   (e.g. "turn on incident manager dashboards", "turn on incident fulfiller dashboards").
2. Each SOR turns on two org preferences, one at a time. `check-dashboard-preference` first confirms that
   Dynamic Dashboards for IT Service (`service-cloud-itsm-dashboard`) reads exactly `ENABLED`; it turns on
   with IT Service Enablement, so never enable it or ask about it, and any other result stops the feature.
   Then read each preference, skip any already on, ask the SOR's question before each write that turns one
   on (`update-dashboard-preference`), and read each back (`verify-dashboard-preference`). Turn on only the
   persona the user chose.
3. After both preferences of a SOR are handled, run its `verify-dashboards-materialized` query. The
   dashboards deploy asynchronously, so report the titles it finds; if they are still missing after its
   retries, say the preference is set but the dashboards are not confirmed to exist, give the user the same
   query, and point them to All Dashboards (App Launcher → Dashboards). A user sees the dashboards only
   with the ITSM console-view permission (a separate grant). If the write returns a dynamic-dashboard limit
   error, report it: freeing a slot (converting a dynamic dashboard to static, or deleting an unused one) is
   a manual admin step — never retry or remediate it here.
