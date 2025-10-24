# EchoTrace – Whispering Objects

EchoTrace is a proximity-responsive installation for museums and memory institutions. Whisper nodes share fragmentary audio stories as visitors approach; when enough fragments are experienced, a mystery object unlocks a shared finale. The project foregrounds discovery, embodied engagement, and collaborative meaning-making.

## Features

- **Distributed architecture** – One Raspberry Pi hub orchestrates four whisper nodes and one mystery node via MQTT.
- **Proximity storytelling** – VL53L1X sensors fade objects from whisper to full story zones, synchronising audio, LEDs, and optional haptics.
- **Narrative unlock** – Configurable fragment threshold reveals a finale that stitches visitor interpretations together.
- **Accessibility suite** – Captions, multilingual transcripts, high-contrast dashboard theme, sensory-friendly mode, mobility buffers, and per-node overrides.
- **Content packs** – Swap entire narrative sets with YAML metadata, MP3/WAV audio, and HTML transcripts for English, French, and Spanish audiences.
- **Offline analytics** – Daily CSV logs summarised in the dashboard: trigger counts, completion rate, heartbeat tallies, and recent events without collecting PII.

## Visitor Interactions

1. **Attraction** – Soft whispers and ambient LED glow invite approach.
2. **Embodied listening** – Crossing the threshold plays a fragment, synchronising haptic pulses and light cues.
3. **Collaborative sense-making** – Groups compare fragments, scan QR transcripts, and hypothesise the connecting narrative.
4. **Mystery reveal** – After the required number of unique fragments, the finale object unlocks, affirming or reshaping the shared story.
5. **Reflection** – Visitors revisit nodes or transcripts, noticing how accessibility settings change their experience.

## Admin Dashboard Highlights

- **Overview** – Current content pack, narrative state, and quick reset controls.
- **Nodes** – Heartbeat ages, default languages, fragment assignments, config push form, reboot placeholder.
- **Accessibility** – Apply presets, tweak global toggles, and manage per-node overrides with immediate MQTT pushes.
- **Content** – Choose packs, review fragment URLs for QR printing, confirm language coverage.
- **Calibration** – Reference proximity thresholds for on-floor adjustments.
- **Analytics** – Download CSV logs and view aggregated metrics (trigger counts, completion rate, mean trigger interval, recent events).

## Hardware Checklist

| Role | Core Hardware |
|------|----------------|
| Hub | Raspberry Pi 4/5, 32 GB microSD, Mosquitto MQTT broker, Flask dashboard |
| Whisper Nodes (×4) | Raspberry Pi Zero 2 W, VL53L1X sensor, LED + resistor, Class-D amp + speaker, optional haptic motor |
| Mystery Node (×1) | Same as whisper node plus finale audio content |
| Fabrication | 3D-printed bezels/LED holders (STL), laser-cut panels (DXF), cable management, mounting hardware |

See `docs/hardware_setup.md` for detailed wiring, service installation, and maintenance guidance.

## Content Packs

- Organised under `content-packs/<pack-name>/` with `pack.yaml`, `audio/`, and `transcripts/` directories.
- `pack.yaml` maps node IDs to roles and language variants.
- HTML transcripts are served at `/transcripts/<pack>/<filename>.html` for QR labels.
- Reference `docs/content_pack_guide.md` for authoring best practices.

## Accessibility Suite

- Global toggles (captions, high contrast, sensory friendly, safety limiter, mobility buffer, quiet hours).
- Presets for hard of hearing, low vision, sensory-friendly, and mobility-aware programs.
- Per-node overrides for LED behaviour, mobility buffer, playback pace, repeat count, limiter, and volume.
- Accessibility profiles persist in YAML and deploy instantly to nodes.

## Analytics & Privacy

- Events logged: `heartbeat_received`, `fragment_triggered`, `narrative_unlocked`, `config_push_ok`, `config_push_timeout`, `admin_action`.
- Dashboard summary computes trigger counts, heartbeat tallies, completion rate, and recent events without storing visitor identities.
- CSV exports remain on the hub unless an administrator downloads them for evaluation (see `docs/evaluation_metrics.md`).

## Educational & Learning Goals

- Encourage constructivist, inquiry-based storytelling aligned with Falk & Dierking’s Contextual Model.
- Support embodied cognition through multimodal feedback.
- Foster collaborative interpretation by distributing narrative fragments across space.
- Provide accessible pathways (captions, pacing, tactile cues) so all visitors can contribute to the finale.

## Quick Start (Development)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ruff check . && mypy . && pytest
```

- `make run-hub` – Launch dashboard and listener (development mode; requires Flask/Waitress).
- `make run-node` – Start a mocked node service loop (uses fallback hardware mocks from `tests/conftest.py`).

## Deployment Steps (Production)

1. Install repository to `/opt/echotrace` on the hub and `/opt/echotrace-node` on each node.
2. Create Python virtual environments and install dependencies.
3. Configure environment variables in `/etc/default/echotrace` (e.g., `ECHOTRACE_ADMIN_USER`, `ECHOTRACE_ADMIN_PASS`).
4. Copy systemd units (`system/hub.service`, `system/node.service`), adjust paths if needed, then enable with `sudo systemctl enable --now ...`.
5. Place content packs under `content-packs/`, confirm audio paths, and select the active pack via the dashboard.

## Roadmap

1. Integrate live calibration feedback loops for sensor tuning.
2. Add concurrent visitor arbitration when multiple users trigger the same node.
3. Explore optional I2S DAC support and bone-conduction audio for immersive accessibility.

## License

Released under the MIT License. See `LICENSE` for details.
