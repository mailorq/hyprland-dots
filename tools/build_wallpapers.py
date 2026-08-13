"""Build or verify deterministic 16:9 Fata Morgana wallpapers.

The script deliberately reads the committed artwork manifest rather than the
untracked raw-reference directory.  It can therefore make only the five assets
already approved for gentle 16:9 framing, never inventing a new crop candidate,
upscaling an image, or using a title outside the catalogue. The curated exports
are frozen for the v1.x line: this tool verifies them by default and requires an
explicit acknowledgement before it can write an image or its manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MASTER_DIR = ROOT / "assets" / "art" / "fata-morgana"
MASTER_MANIFEST = MASTER_DIR / "manifest.json"
OUTPUT_DIR = ROOT / "assets" / "wallpapers" / "fata-morgana"
TARGET_WIDTH = 16
TARGET_HEIGHT = 9
DEFAULT_WALLPAPER_ID = "fm-016"
# These five files are manually curated QHD exports.  They remain ordinary
# manifest-backed wallpaper candidates, but their image data is intentionally
# owned by the curator rather than regenerated from a reduced art master.
CURATED_EXPORT_DIMENSIONS = {
    "fm-016": (2560, 1440),
    "fm-031": (2560, 1440),
    "fm-035": (2560, 1440),
    "fm-038": (2560, 1440),
    "fm-040": (2560, 1440),
}
APPROVED_CANDIDATE_IDS = frozenset(CURATED_EXPORT_DIMENSIONS)
ARTWORK_ID_PATTERN = re.compile(r"fm-[0-9]{3}")
ARTWORK_FILENAME_PATTERN = re.compile(
    r"fata-morgana-(?P<index>[0-9]{3})-[a-z0-9]+(?:-[a-z0-9]+)*\.jpg"
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_artwork_filename(value: object) -> str:
    if not isinstance(value, str) or not ARTWORK_FILENAME_PATTERN.fullmatch(value):
        raise ValueError(f"invalid master artwork filename: {value!r}")
    return value


def validate_master_path(filename: object) -> Path:
    filename = validate_artwork_filename(filename)
    path = MASTER_DIR / filename
    try:
        path.resolve(strict=True).relative_to(MASTER_DIR.resolve())
    except (FileNotFoundError, ValueError) as error:
        raise ValueError(f"master artwork path escapes or is missing: {filename}") from error
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"master artwork must be a regular file: {filename}")
    return path


def validate_master_item(item: object) -> dict[str, object]:
    if not isinstance(item, dict):
        raise ValueError("master manifest contains a non-object artwork entry")
    artwork_id = item.get("id")
    filename = validate_artwork_filename(item.get("file"))
    filename_match = ARTWORK_FILENAME_PATTERN.fullmatch(filename)
    assert filename_match is not None
    if not isinstance(artwork_id, str) or not ARTWORK_ID_PATTERN.fullmatch(artwork_id):
        raise ValueError(f"invalid master artwork ID: {artwork_id!r}")
    if artwork_id != f"fm-{filename_match.group('index')}":
        raise ValueError(f"master artwork ID and filename index differ: {artwork_id} / {filename}")
    if not isinstance(item.get("sha256"), str) or not SHA256_PATTERN.fullmatch(item["sha256"]):
        raise ValueError(f"invalid master checksum: {artwork_id}")
    dimensions = item.get("dimensions")
    if not isinstance(dimensions, dict) or not all(
        isinstance(dimensions.get(axis), int) and dimensions[axis] > 0
        for axis in ("width", "height")
    ):
        raise ValueError(f"invalid master dimensions: {artwork_id}")
    wallpaper = item.get("wallpaper")
    if not isinstance(wallpaper, dict) or not isinstance(wallpaper.get("eligible"), bool):
        raise ValueError(f"invalid wallpaper metadata: {artwork_id}")
    if wallpaper["eligible"]:
        if wallpaper.get("target_aspect_ratio") != "16:9":
            raise ValueError(f"unsupported wallpaper aspect ratio: {artwork_id}")
        if wallpaper.get("crop") not in {"center", "native"}:
            raise ValueError(f"unsupported wallpaper crop policy: {artwork_id}")
        loss_percent = wallpaper.get("estimated_crop_loss_percent")
        if not isinstance(loss_percent, (int, float)) or not 0 <= loss_percent <= 100:
            raise ValueError(f"invalid wallpaper crop loss: {artwork_id}")
    validate_master_path(filename)
    return item


def load_candidates() -> list[dict[str, object]]:
    manifest = json.loads(MASTER_MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("master manifest schema must be version 1")
    artwork = manifest.get("artwork")
    if not isinstance(artwork, list):
        raise ValueError("master manifest artwork must be a list")
    validated = [validate_master_item(item) for item in artwork]
    ids = [str(item["id"]) for item in validated]
    if len(ids) != len(set(ids)):
        raise ValueError("master manifest contains duplicate artwork IDs")
    candidates = [item for item in validated if item["wallpaper"]["eligible"] is True]  # type: ignore[index]
    if not candidates:
        raise RuntimeError("no approved wallpaper candidates in the master manifest")
    if {item["id"] for item in candidates} != APPROVED_CANDIDATE_IDS:
        raise RuntimeError("wallpaper candidate inventory changed; review framing before export")
    if DEFAULT_WALLPAPER_ID not in {item["id"] for item in candidates}:
        raise RuntimeError("default wallpaper is not in the approved candidate inventory")
    return sorted(candidates, key=lambda item: str(item["id"]))


def crop_box(width: int, height: int) -> tuple[int, int, int, int]:
    """Return the largest centred integer 16:9 crop without resampling."""
    if width * TARGET_HEIGHT >= height * TARGET_WIDTH:
        crop_height = height
        crop_width = (height * TARGET_WIDTH // TARGET_HEIGHT) // TARGET_WIDTH * TARGET_WIDTH
    else:
        crop_width = width - width % TARGET_WIDTH
        crop_height = crop_width * TARGET_HEIGHT // TARGET_WIDTH
    if crop_width <= 0 or crop_height <= 0:
        raise RuntimeError(f"invalid wallpaper crop from {width}x{height}")
    left = (width - crop_width) // 2
    top = (height - crop_height) // 2
    return left, top, left + crop_width, top + crop_height


def output_filename(item: dict[str, object]) -> str:
    return Path(validate_artwork_filename(item["file"])).stem + "-wallpaper-16x9.jpg"


def render_candidate(item: dict[str, object], output_dir: Path) -> dict[str, object]:
    source_path = validate_master_path(item["file"])
    candidate_id = str(item["id"])
    target_path = output_dir / output_filename(item)
    with Image.open(source_path) as source:
        if source.mode != "RGB":
            raise RuntimeError(f"wallpaper master is not RGB: {source_path.name}")
        box = crop_box(source.width, source.height)

        if candidate_id in CURATED_EXPORT_DIMENSIONS:
            expected_dimensions = CURATED_EXPORT_DIMENSIONS[candidate_id]
            if not target_path.is_file():
                raise RuntimeError(f"missing curated wallpaper export: {target_path.name}")
            with Image.open(target_path) as curated:
                if curated.mode != "RGB" or curated.size != expected_dimensions:
                    raise RuntimeError(
                        f"curated wallpaper has invalid metadata: {target_path.name}; "
                        f"expected RGB {expected_dimensions[0]}x{expected_dimensions[1]}"
                    )
                rendered_dimensions = curated.size
            export_mode = "curated"
        else:
            rendered = source.crop(box)
            rendered.save(target_path, "JPEG", quality=94, subsampling=0, optimize=True, progressive=True)
            rendered_dimensions = rendered.size
            export_mode = "generated"

    crop_area = (box[2] - box[0]) * (box[3] - box[1])
    source_area = int(item["dimensions"]["width"]) * int(item["dimensions"]["height"])  # type: ignore[index]
    return {
        "id": item["id"],
        "file": target_path.name,
        "source_file": item["file"],
        "source_sha256": item["sha256"],
        "sha256": sha256(target_path),
        "dimensions": {"width": rendered_dimensions[0], "height": rendered_dimensions[1]},
        "crop": item["wallpaper"]["crop"],  # type: ignore[index]
        "crop_box": {"left": box[0], "top": box[1], "right": box[2], "bottom": box[3]},
        "crop_loss_percent": round((1 - crop_area / source_area) * 100, 1),
        "fit_mode": "cover",
        "export_mode": export_mode,
        "default": item["id"] == DEFAULT_WALLPAPER_ID,
    }


def build(output_dir: Path) -> None:
    candidates = load_candidates()
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [render_candidate(item, output_dir) for item in candidates]
    manifest = {
        "schema_version": 2,
        "collection": "The House in Fata Morgana — approved 16:9 wallpaper exports",
        "source": "assets/art/fata-morgana/manifest.json",
        "normalization": {
            "target_aspect_ratio": "16:9",
            "crop": "center only when approved",
            "upscale": "never",
            "metadata": "stripped",
        },
        "wallpapers": records,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Built {len(records)} approved 16:9 wallpapers in {output_dir}")


def verify(output_dir: Path) -> int:
    errors: list[str] = []
    try:
        candidates = load_candidates()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"invalid master manifest: {error}", file=sys.stderr)
        return 1
    expected = {output_filename(item) for item in candidates}
    actual = {path.name for path in output_dir.glob("*.jpg")} if output_dir.is_dir() else set()
    if expected != actual:
        errors.append(f"wallpaper set mismatch: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        errors.append("missing wallpaper manifest.json")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"invalid wallpaper manifest JSON: {error}")
            manifest = {}
        if not isinstance(manifest, dict):
            errors.append("wallpaper manifest root must be an object")
            manifest = {}
        if manifest.get("schema_version") != 2:
            errors.append("wallpaper manifest schema must be version 2")
        records = manifest.get("wallpapers", [])
        if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
            errors.append("wallpaper manifest entries must be objects")
            records = []
        candidate_by_id = {item["id"]: item for item in candidates}
        if {record.get("id") for record in records} != set(candidate_by_id):
            errors.append("wallpaper manifest candidate IDs do not match approved masters")
        defaults = [record.get("id") for record in records if record.get("default") is True]
        if defaults != [DEFAULT_WALLPAPER_ID]:
            errors.append("wallpaper manifest must name fm-016 as its only default")
        for record in records:
            candidate = candidate_by_id.get(record.get("id"))
            if candidate is None:
                continue
            expected_file = output_filename(candidate)
            if record.get("file") != expected_file:
                errors.append(f"wallpaper filename mismatch: {record.get('id')}")
                continue
            if record.get("source_file") != candidate.get("file") or record.get("source_sha256") != candidate.get("sha256"):
                errors.append(f"wallpaper source provenance mismatch: {record.get('id')}")
            dimensions = record.get("dimensions", {})
            if not isinstance(dimensions, dict):
                errors.append(f"invalid wallpaper dimensions: {record.get('id')}")
                continue
            width = dimensions.get("width")
            height = dimensions.get("height")
            path = output_dir / expected_file
            expected_mode = "curated" if record.get("id") in CURATED_EXPORT_DIMENSIONS else "generated"
            if record.get("export_mode") != expected_mode:
                errors.append(f"wallpaper export mode mismatch: {record.get('id')}")
            expected_dimensions = CURATED_EXPORT_DIMENSIONS.get(str(record.get("id")))
            if expected_dimensions is not None and (width, height) != expected_dimensions:
                errors.append(f"curated wallpaper dimensions mismatch: {record.get('file')}")
            if not isinstance(width, int) or not isinstance(height, int) or width * TARGET_HEIGHT != height * TARGET_WIDTH:
                errors.append(f"wallpaper is not exact 16:9: {record.get('file')}")
            elif not path.is_file() or path.is_symlink():
                errors.append(f"wallpaper listed but missing: {path.name}")
            elif sha256(path) != record.get("sha256"):
                errors.append(f"wallpaper checksum mismatch: {path.name}")
            else:
                with Image.open(path) as image:
                    if image.mode != "RGB" or image.size != (width, height):
                        errors.append(f"wallpaper image metadata mismatch: {path.name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Verified {len(expected)} approved 16:9 wallpapers and manifest.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--check", action="store_true", help="validate existing wallpapers without writing files")
    parser.add_argument(
        "--rebuild-frozen-assets",
        action="store_true",
        help="allow writes to frozen wallpaper exports and manifest; reserved for an approved asset revision",
    )
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    if args.check:
        if args.rebuild_frozen_assets:
            parser.error("--check cannot be combined with --rebuild-frozen-assets")
        return verify(output_dir)
    if not args.rebuild_frozen_assets:
        parser.error(
            "wallpaper writes are disabled by default; use --check or "
            "--rebuild-frozen-assets after an approved asset revision"
        )
    build(output_dir)
    return verify(output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
