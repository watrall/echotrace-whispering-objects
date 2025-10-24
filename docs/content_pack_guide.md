# Content Pack Authoring Guide

EchoTrace content packs package audio fragments, multilingual transcripts, and node role metadata so galleries can swap narrative sets without code changes.

## Directory Layout

```
content-packs/
  sample-pack/
    pack.yaml
    audio/
      object1_en.mp3
      ...
    transcripts/
      object1_en.html
      ...
```

Create one folder per pack. Place `pack.yaml` at the root alongside `audio/` and `transcripts/` directories that mirror the filenames declared in the YAML.

## pack.yaml Schema

```yaml
name: sample-pack
nodes:
  object1:
    role: whisper   # whisper | mystery
    default_language: en
  mystery:
    role: mystery
    default_language: en
media:
  object1:
    en:
      audio: audio/object1_en.mp3
      transcript: transcripts/object1_en.html
    fr:
      audio: audio/object1_fr.mp3
      transcript: transcripts/object1_fr.html
  mystery:
    en:
      audio: audio/mystery_en.mp3
      transcript: transcripts/mystery_en.html
```

### Nodes

- `role` defines how the node behaves: `whisper` objects emit fragments when visitors approach, `mystery` unlocks only after enough fragments have triggered.
- `default_language` is used when a requested fragment is unavailable in the visitor’s chosen language.

### Media Map

- Each node lists available languages.
- `audio` references a WAV or MP3 file relative to the pack directory.
- `transcript` points to a static HTML transcript that the hub publishes as a QR-accessible page (`/transcripts/<pack>/<filename>.html`).

Include English (`en`) plus any additional languages you support (default project includes `fr` and `es`).

## Audio & Transcript Authoring Tips

- Keep audio files under ~2 minutes to suit gallery dwell times.
- Normalise audio levels consistently across nodes; the node safety limiter will scale down if required.
- Write transcripts as short-form HTML documents with descriptive headings and access notes. Avoid inline scripts or external references.

## Deploying a Pack

1. Copy the pack directory into `content-packs/` on the hub.
2. Visit the dashboard’s **Content** tab and select the pack from the dropdown. The hub validates paths and broadcasts any updated fragments to nodes.
3. Print or update QR labels for each object using the transcript URLs shown in the dashboard.

## Testing With Mocks

During development you can load a pack on your workstation; the Flask dashboard serves transcripts locally, and unit tests exercise the content manager to confirm all assets resolve correctly.
