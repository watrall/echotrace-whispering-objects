"""Content pack management for the EchoTrace hub."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

import yaml

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class MediaAsset:
    """Describe audio and transcript resources for a node-language pair."""

    audio_path: Path
    transcript_path: Path
    transcript_filename: str


@dataclass
class ContentPack:
    """Rich representation of a content pack and its assets."""

    name: str
    root: Path
    nodes: Dict[str, Dict[str, str]]
    media: Dict[Tuple[str, str], MediaAsset]
    base_url: str


class ContentManager:
    """Provide helpers for locating and loading content packs."""

    def __init__(self, packs_root: Path | None = None, transcripts_base: str = "/transcripts") -> None:
        self._packs_root = packs_root or Path("content-packs")
        self._packs_root.mkdir(parents=True, exist_ok=True)
        self._transcripts_base = transcripts_base.rstrip("/")
        self._active_pack: Optional[ContentPack] = None

    def list_packs(self) -> List[str]:
        """Return discovered content pack directory names."""
        if not self._packs_root.exists():
            return []
        return sorted(item.name for item in self._packs_root.iterdir() if item.is_dir())

    def load_pack(self, name: str) -> ContentPack:
        """Load and validate the specified content pack."""
        pack_path = self._packs_root / name
        if not pack_path.exists():
            raise FileNotFoundError(f"Content pack '{name}' not found at {pack_path}")
        pack_yaml = pack_path / "pack.yaml"
        if not pack_yaml.exists():
            raise FileNotFoundError(f"pack.yaml missing for content pack '{name}'")

        try:
            with pack_yaml.open("r", encoding="utf-8") as handle:
                raw = yaml.safe_load(handle) or {}
        except yaml.YAMLError as exc:
            raise ValueError(f"Failed to parse pack.yaml for '{name}': {exc}") from exc

        pack_name = str(raw.get("name") or name)
        if pack_name != name:
            LOGGER.warning(
                "Pack name mismatch: directory '%s' vs metadata '%s'. Using directory name.",
                name,
                pack_name,
            )

        nodes = self._parse_nodes(raw.get("nodes", {}))
        media = self._parse_media(pack_path, raw.get("media", {}))
        base_url = f"{self._transcripts_base}/{name}"

        pack = ContentPack(name=name, root=pack_path, nodes=nodes, media=media, base_url=base_url)
        self._active_pack = pack
        return pack

    def get_fragment_for_node(self, node_id: str, language: str) -> Optional[Path]:
        """Return the audio fragment path for a given node and language."""
        pack = self._require_active_pack()
        asset = self._resolve_media_asset(pack, node_id, language)
        if asset is None:
            return None
        if not asset.audio_path.is_file():
            LOGGER.warning("Audio asset missing for %s (%s): %s", node_id, language, asset.audio_path)
            return None
        return asset.audio_path

    def get_transcript_url(self, node_id: str, language: str) -> Optional[str]:
        """Return the HTTP URL for a transcript, if available."""
        pack = self._require_active_pack()
        asset = self._resolve_media_asset(pack, node_id, language)
        if asset is None:
            return None
        if not asset.transcript_path.is_file():
            LOGGER.warning(
                "Transcript asset missing for %s (%s): %s",
                node_id,
                language,
                asset.transcript_path,
            )
            return None
        return f"{pack.base_url}/{asset.transcript_filename}"

    def _require_active_pack(self) -> ContentPack:
        if self._active_pack is None:
            raise RuntimeError("No content pack is currently loaded.")
        return self._active_pack

    def _resolve_media_asset(
        self,
        pack: ContentPack,
        node_id: str,
        language: str,
    ) -> Optional[MediaAsset]:
        asset = pack.media.get((node_id, language))
        if asset:
            return asset
        node_meta = pack.nodes.get(node_id)
        if not node_meta:
            LOGGER.warning("Node '%s' not defined in pack '%s'.", node_id, pack.name)
            return None
        default_lang = node_meta.get("default_language", language)
        asset = pack.media.get((node_id, default_lang))
        if asset:
            LOGGER.info(
                "Falling back to default language '%s' for node '%s' (requested '%s').",
                default_lang,
                node_id,
                language,
            )
        else:
            LOGGER.warning(
                "Media asset missing for node '%s' language '%s' (no fallback available).",
                node_id,
                language,
            )
        return asset

    def _parse_nodes(self, raw_nodes: Iterable | Mapping) -> Dict[str, Dict[str, str]]:
        nodes: Dict[str, Dict[str, str]] = {}
        if isinstance(raw_nodes, Mapping):
            iterator = raw_nodes.items()
        elif isinstance(raw_nodes, list):
            iterator = ((item.get("id"), item) for item in raw_nodes if isinstance(item, Mapping))
        else:
            LOGGER.warning("Unexpected nodes structure in content pack metadata.")
            return nodes

        for node_id, node_meta in iterator:
            if not node_id or not isinstance(node_meta, Mapping):
                LOGGER.warning("Invalid node entry encountered: %s", node_meta)
                continue
            role = str(node_meta.get("role", "")).strip()
            default_lang = str(node_meta.get("default_language", "")).strip()
            if role not in {"whisper", "mystery"}:
                LOGGER.warning("Node '%s' has unsupported role '%s'.", node_id, role)
                continue
            if not default_lang:
                LOGGER.warning("Node '%s' missing default_language.", node_id)
                continue
            nodes[node_id] = {
                "role": role,
                "default_language": default_lang,
            }
        return nodes

    def _parse_media(
        self,
        pack_path: Path,
        raw_media: Mapping[str, Mapping[str, Mapping[str, str]]],
    ) -> Dict[Tuple[str, str], MediaAsset]:
        media: Dict[Tuple[str, str], MediaAsset] = {}
        if not isinstance(raw_media, Mapping):
            LOGGER.warning("Media section missing or malformed in pack metadata.")
            return media

        for node_id, language_map in raw_media.items():
            if not isinstance(language_map, Mapping):
                LOGGER.warning("Media entry for node '%s' must be a mapping.", node_id)
                continue
            for lang, asset_meta in language_map.items():
                if not isinstance(asset_meta, Mapping):
                    LOGGER.warning("Media entry for %s (%s) must be a mapping.", node_id, lang)
                    continue
                audio_rel = asset_meta.get("audio")
                transcript_rel = asset_meta.get("transcript")
                if not audio_rel or not transcript_rel:
                    LOGGER.warning("Media entry for %s (%s) missing paths.", node_id, lang)
                    continue
                audio_path = (pack_path / audio_rel).resolve()
                transcript_path = (pack_path / transcript_rel).resolve()
                media[(node_id, lang)] = MediaAsset(
                    audio_path=audio_path,
                    transcript_path=transcript_path,
                    transcript_filename=transcript_path.name,
                )
                if not audio_path.exists():
                    LOGGER.warning("Audio file not found: %s", audio_path)
                if not transcript_path.exists():
                    LOGGER.warning("Transcript file not found: %s", transcript_path)
        return media


__all__ = ["ContentManager", "ContentPack", "MediaAsset"]
