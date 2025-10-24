# Evaluation Metrics

EchoTrace collects lightweight analytics so facilitators can tune visitor support without capturing personally identifiable information (PII). All metrics remain offline on the hub and can be exported manually as CSV for evaluation sessions.

## Logged Events

The hub records the following event types in `hub/logs/YYYY-MM-DD_events.csv`:

- `heartbeat_received` – node health beacons (used to monitor uptime and spot disconnected devices).
- `fragment_triggered` – proximity entrances that start whisper audio at a node.
- `narrative_unlocked` – moments when enough fragments have been experienced to unlock the mystery object.
- `config_push_ok` / `config_push_timeout` – administrative pushes sent from the dashboard and whether nodes acknowledged them.
- `admin_action` – staff interventions such as manual narrative resets.

Each line captures the ISO 8601 timestamp, the event name, an optional node identifier, and a detail payload (JSON string or short message).

## Derived Metrics

The dashboard summarises the latest log with:

- **Trigger counts by node** – how often each object attracted visitors during the logging window.
- **Narrative completion rate** – the ratio of `narrative_unlocked` events to fragment triggers (capped at 100%).
- **Average trigger interval** – an approximate dwell indicator derived from time between consecutive fragment triggers.
- **Heartbeat tally** – reassurance that all nodes remain responsive.
- **Recent events list** – the ten most recent log entries for rapid troubleshooting.

These summaries are recomputed on request; no historical aggregation is stored beyond the raw CSVs.

## Privacy and Ethics

- No visitor identifiers, photos, audio recordings, or typed input are collected.
- CSV files remain on the Raspberry Pi hub; exporting requires staff action via the dashboard.
- Staff can clear the CSV directory or archive files between exhibitions if needed.
- Data is intended for formative evaluation: identifying popular objects, diagnosing node failures, and monitoring the pacing of collaborative discovery.

## Recommended Evaluation Practice

1. **Baseline Observation** – Run the installation for a day and export the CSV to note visitation patterns.
2. **Intervention Tracking** – When updating content packs, accessibility presets, or gallery layout, flag the action with an `admin_action` note and compare logs before/after the change.
3. **Reflective Debrief** – Pair the quantitative summaries with qualitative gallery observations to interpret how visitors collaborated, lingered, or skipped stations.
4. **Retention Policy** – Store exported CSVs securely, ideally anonymised with context labels (date, exhibition, facilitator) and delete them from the hub once transferred.

By combining these metrics with observational data, educators can tune EchoTrace to support curiosity-driven, collaborative meaning-making while upholding community privacy expectations.
