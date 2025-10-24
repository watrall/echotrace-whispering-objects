# EchoTrace – Whispering Objects

EchoTrace is a distributed museum installation where proximity cues bring collection objects to life. Four “whisper” nodes share fragmentary stories as visitors lean in; once enough fragments are experienced, a “mystery” object unlocks a collective finale.

## Repository Highlights

- **Hub services** – Flask dashboard, MQTT orchestration, accessibility controls, and offline analytics (see `hub/`).
- **Node firmware** – Python services for proximity sensing, LED/haptic feedback, and audio playback on Raspberry Pi Zero 2 W devices (see `pi_nodes/`).
- **Content packs** – Structured narrative bundles with multilingual audio and HTML transcripts. The sample pack demonstrates four whisper objects plus a finale (`content-packs/sample-pack`).
- **Docs & fabrication** – Guides for interpretation, accessibility, evaluation metrics, and hardware fabrication.

## Visitor-Facing Accessibility

Staff can toggle captions, high-contrast dashboard modes, sensory-friendly pacing, quiet hours, and per-node overrides. Each audio fragment has a QR-linked HTML transcript served from the hub at `/transcripts/<pack>/<filename>.html`.

## Offline Analytics

The hub writes daily CSV logs capturing health beacons, fragment triggers, narrative unlocks, and admin actions. The analytics dashboard summarises counts by node, estimated dwell time between triggers, and the most recent events to support reflective facilitation. CSV exports remain offline unless a facilitator downloads them manually.

> **Development status:** The repository is under active construction in sequential chunks. Features and documentation will continue to expand.
