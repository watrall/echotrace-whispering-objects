"""Tests for the content manager."""

from __future__ import annotations

from pathlib import Path

import yaml

from hub.content_manager import ContentManager


def test_content_manager_loads_pack(tmp_path: Path) -> None:
    """Ensure a content pack is parsed and fragment lookup works."""
    pack_dir = tmp_path / "sample-pack"
    transcripts_dir = pack_dir / "transcripts"
    audio_dir = pack_dir / "audio"
    transcripts_dir.mkdir(parents=True)
    audio_dir.mkdir(parents=True)

    (audio_dir / "object1_en.mp3").write_text("dummy audio", encoding="utf-8")
    (transcripts_dir / "object1_en.html").write_text("<p>Transcript</p>", encoding="utf-8")

    pack_yaml = {
        "name": "sample-pack",
        "nodes": {
            "object1": {"role": "whisper", "default_language": "en"},
        },
        "media": {
            "object1": {
                "en": {
                    "audio": "audio/object1_en.mp3",
                    "transcript": "transcripts/object1_en.html",
                },
            },
        },
    }
    (pack_dir / "pack.yaml").write_text(yaml.safe_dump(pack_yaml), encoding="utf-8")

    manager = ContentManager(packs_root=tmp_path)
    manager.load_pack("sample-pack")

    fragment_path = manager.get_fragment_for_node("object1", "en")
    assert fragment_path == audio_dir / "object1_en.mp3"

    transcript_url = manager.get_transcript_url("object1", "en")
    assert transcript_url.endswith("/object1_en.html")


def test_content_manager_language_fallback(tmp_path: Path) -> None:
    """Verify requested language falls back to node default when missing."""
    pack_dir = tmp_path / "fallback-pack"
    transcripts_dir = pack_dir / "transcripts"
    audio_dir = pack_dir / "audio"
    transcripts_dir.mkdir(parents=True)
    audio_dir.mkdir(parents=True)

    (audio_dir / "object1_en.mp3").write_text("dummy audio", encoding="utf-8")
    (transcripts_dir / "object1_en.html").write_text("<p>Transcript</p>", encoding="utf-8")

    pack_yaml = {
        "name": "fallback-pack",
        "nodes": {
            "object1": {"role": "whisper", "default_language": "en"},
        },
        "media": {
            "object1": {
                "en": {
                    "audio": "audio/object1_en.mp3",
                    "transcript": "transcripts/object1_en.html",
                },
            },
        },
    }
    (pack_dir / "pack.yaml").write_text(yaml.safe_dump(pack_yaml), encoding="utf-8")

    manager = ContentManager(packs_root=tmp_path)
    manager.load_pack("fallback-pack")

    fragment_path = manager.get_fragment_for_node("object1", "fr")
    assert fragment_path == audio_dir / "object1_en.mp3"
