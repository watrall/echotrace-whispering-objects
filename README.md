# EchoTrace – Whispering Objects

EchoTrace is an interactive, proximity-responsive storytelling installation created for museums, galleries, and cultural heritage sites. It turns physical objects into whispering narrators that share fragments of a larger story when visitors draw near. Each “whisper node” uses a Raspberry Pi, a distance sensor, an LED, and a speaker to respond to visitor movement and create an immersive, multisensory experience of discovery and reflection.

As visitors explore, they hear parts of a hidden narrative scattered across several artifacts. When enough fragments have been heard, a “mystery object” plays the final chapter that connects the pieces into a shared conclusion. Every approach, pause, and gesture becomes part of the interpretive process. Visitors learn through movement as well as through listening and conversation.

For museum staff, EchoTrace is designed to be practical and adaptable. It includes a simple browser-based dashboard for managing accessibility options, calibrating sensors, loading new story content, and viewing anonymized visitor analytics. Everything runs locally on a museum network without the need for internet access. By combining physical computing, narrative design, and inclusive digital practice, EchoTrace shows how technology can deepen learning and engagement in informal educational environments.

---

## Features

- **Distributed architecture (hub and nodes)**  
  The system includes a central “hub” Raspberry Pi and five “node” devices, four whisper objects and one mystery object. The hub manages coordination, content, and analytics, while each node handles local sensing and playback. Communication happens through **MQTT (Message Queuing Telemetry Transport)**, a lightweight messaging protocol commonly used in Internet of Things systems. In EchoTrace, MQTT allows fast, reliable communication across a local Wi-Fi network even when there is no internet connection.

- **Proximity-responsive storytelling**  
  Each node uses a **VL53L1X time-of-flight sensor** to detect distance. At first the object emits a faint whisper, an indistinct ambient sound. As a visitor comes closer, the story becomes clear and fully audible. This changing soundscape encourages visitors to move and listen carefully, turning physical space into part of the learning experience.

- **Narrative unlock system**  
  The hub tracks which story fragments have been triggered. When a configurable number of unique fragments have been heard, it signals the “mystery object” to play the final audio segment. This design invites collaboration, since no single visitor can hear all fragments alone, and it connects individual discoveries to a collective ending.

- **Accessibility and inclusion**  
  EchoTrace can be tailored for different visitor needs. Features include captions and transcripts accessed through QR codes, multilingual content in English, French, and Spanish, adjustable sound and light cues, high-contrast visual options for the dashboard, and sensory-friendly settings that reduce light and sound intensity. Presets allow staff to select “hard of hearing,” “low vision,” “sensory-friendly,” or “mobility-aware” profiles quickly.

- **Modular content packs**  
  Story content is organized in replaceable packs that include YAML metadata, MP3 or WAV audio, and multilingual HTML transcripts. Staff can switch stories or languages without editing the code. The modular structure makes the installation reusable across exhibitions and adaptable to different collections or learning themes.

- **Offline analytics**  
  All visitor interactions, such as node activations and completion of the mystery story, are logged in local CSV files on the hub. The dashboard displays summary statistics such as trigger counts and completion rates. No personal data are collected, which ensures compliance with museum privacy standards.

---

## Visitor Interactions

1. **Attraction: the call of the whisper**  
   Faint murmurs and soft LED light draw attention from across the gallery. Each object appears quietly alive and invites approach through subtle sensory cues rather than instructions.

2. **Embodied listening: movement as participation**  
   When a visitor moves close, the whisper becomes a clear story fragment. The LED brightens or pulses, and a small vibration motor can provide a tactile rhythm. The visitor’s position and movement become part of how the story unfolds.

3. **Interpretation through exploration**  
   Each object shares only a portion of the story. Visitors compare what they have heard, revisit objects, and scan QR codes to read transcripts or translations. The experience becomes a form of narrative problem solving that mirrors museum interpretation and encourages personal meaning-making.

4. **Shared discovery and the mystery reveal**  
   After enough fragments have been triggered, either by one visitor or by several working together, the mystery object activates. It plays the conclusion that ties the story together and creates a shared moment of understanding.

5. **Reflection and return**  
   Many visitors revisit objects to re-listen after the finale. Repetition and reflection encourage deeper comprehension and reinforce the sense of participation and curiosity that define informal learning.

---

## Admin Dashboard Highlights

- **Overview** – Displays the current story pack, system status, and narrative progress including the number of triggered fragments.  
- **Nodes** – Shows live heartbeat signals, assigned audio files, and configuration options for each node.  
- **Accessibility** – Apply global presets, enable captions, or adjust lighting and pacing. All updates are sent instantly through MQTT.  
- **Content** – Load or change story packs, check translation coverage, and copy QR links to transcripts.  
- **Calibration** – View live distance readings to fine-tune sensor placement.  
- **Analytics** – Review engagement data in real time and export CSV summaries for evaluation.

---

## Hardware Checklist

| Role | Core Hardware |
|------|----------------|
| Hub | Raspberry Pi 4 or 5, 32 GB microSD, Mosquitto MQTT broker, Flask dashboard |
| Whisper Nodes (×4) | Raspberry Pi Zero 2 W, VL53L1X sensor, LED + resistor, small amplifier + speaker, optional haptic motor |
| Mystery Node (×1) | Same as whisper node with finale audio content |
| Fabrication | 3D-printed bezels or LED holders (STL), laser-cut panels (DXF), mounting hardware |

See `docs/hardware_setup.md` for detailed wiring, installation, and maintenance instructions.

---

## Content Packs

- Stored under `content-packs/<pack-name>/` with YAML metadata, audio files, and HTML transcripts.  
- Each pack defines node roles, languages, and file mappings.  
- Transcripts are served locally at `/transcripts/<pack>/<filename>.html` and can be linked through QR codes.  
- See `docs/content_pack_guide.md` for authoring and localization details.

---

## Accessibility Suite

- Global toggles for captions, high-contrast mode, sensory-friendly playback, volume limiter, mobility delay buffers, and quiet hours.  
- Presets for specific needs such as hearing, vision, sensory, or mobility support.  
- Per-node overrides for brightness, pacing, repetition, and volume.  
- Profiles are stored in YAML and deployed instantly through MQTT.

---

## Analytics and Privacy

- Logged events include `heartbeat_received`, `fragment_triggered`, `narrative_unlocked`, `config_push_ok`, `config_push_timeout`, and `admin_action`.  
- Dashboard summaries display counts, rates, and timing averages without storing any identifying data.  
- Data remain on the hub unless an administrator chooses to export them for evaluation.

---

## Educational and Learning Goals

- **Constructivist learning through storytelling**  
  Visitors build understanding by collecting and connecting story fragments. Each encounter becomes a small act of investigation that reflects how people construct knowledge in museums through curiosity and exploration.

- **Embodied cognition and spatial learning**  
  Learning happens through movement as well as thought. The sensors and feedback systems connect physical motion, attention, and interpretation, showing how bodies participate in meaning-making.

- **Collaborative and social learning**  
  No single visitor can access the whole story alone. The design invites conversation and sharing, encouraging groups to reconstruct the story together. This reflects social learning and the collaborative dimension of museum experiences.

- **Inclusive and multimodal participation**  
  Audio, light, vibration, and text work together so that visitors with different sensory or linguistic backgrounds can participate equally. Accessibility features demonstrate Universal Design for Learning principles in a physical, informal context.

- **Reflection and metacognition**  
  The final mystery object prompts visitors to consider how they pieced the story together. Revisiting earlier fragments encourages awareness of one’s own interpretation process and supports reflective learning.

---

## Quick Start (Development)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ruff check . && mypy . && pytest
