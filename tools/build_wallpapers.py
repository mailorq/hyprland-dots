"""Build deterministic 16:9 wallpapers from approved Fata Morgana masters.

The script deliberately reads the committed artwork manifest rather than the
untracked raw-reference directory.  It can therefore make only the five assets
already approved for gentle 16:9 framing, never inventing a new crop candidate,
upscaling an image, or using a title outside the catalogue.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_candidates() -> list[dict[str, object]]:
    manifest = json.loads(MASTER_MANIFEST.read_text(encoding="utf-8"))
    candidates = [
        item
        for item in manifest["artwork"]
        if item.get("wallpaper", {}).get("eligible") is True
    ]
    if not candidates:
        raise RuntimeError("no approved wallpaper candidates in the master manifest")
    if {item["id"] for item in candidates} != {"fm-016", "fm-031", "fm-035", "fm-038", "fm-040"}:
        raise RuntimeError("wallpaper candidate inventory changed; review framing before export")
    if DEFAULT_WALLPAPER_ID not in {item["id"] for item in candidates}:
        raise RuntimeError("default wallpaper is not in the approved candidate inventory")
    return candidates


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
    return Path(str(item["file"])).stem + "-wallpaper-16x9.jpg"


def render_candidate(item: dict[str, object], output_dir: Path) -> dict[str, object]:
    source_path = MASTER_DIR / str(item["file"])
    if not source_path.is_file():
        raise RuntimeError(f"missing wallpaper master: {source_path}")
    with Image.open(source_path) as source:
        if source.mode != "RGB":
            raise RuntimeError(f"wallpaper master is not RGB: {source_path.name}")
        box = crop_box(source.width, source.height)
        rendered = source.crop(box)
    target_path = output_dir / output_filename(item)
    rendered.save(target_path, "JPEG", quality=94, subsampling=0, optimize=True, progressive=True)
    crop_area = rendered.width * rendered.height
    source_area = int(item["dimensions"]["width"]) * int(item["dimensions"]["height"])  # type: ignore[index]
    return {
        "id": item["id"],
        "file": target_path.name,
        "source_file": item["file"],
        "source_sha256": item["sha256"],
        "sha256": sha256(target_path),
        "dimensions": {"width": rendered.width, "height": rendered.height},
        "crop": item["wallpaper"]["crop"],  # type: ignore[index]
        "crop_box": {"left": box[0], "top": box[1], "right": box[2], "bottom": box[3]},
        "crop_loss_percent": round((1 - crop_area / source_area) * 100, 1),
        "fit_mode": "cover",
        "default": item["id"] == DEFAULT_WALLPAPER_ID,
    }


def build(output_dir: Path) -> None:
    candidates = load_candidates()
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [render_candidate(item, output_dir) for item in candidates]
    manifest = {
        "schema_version": 1,
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
    candidates = load_candidates()
    expected = {output_filename(item) for item in candidates}
    actual = {path.name for path in output_dir.glob("*.jpg")} if output_dir.is_dir() else set()
    if expected != actual:
        errors.append(f"wallpaper set mismatch: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        errors.append("missing wallpaper manifest.json")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        records = manifest.get("wallpapers", [])
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
            if record.get("source_file") != candidate.get("file") or record.get("source_sha256") != candidate.get("sha256"):
                errors.append(f"wallpaper source provenance mismatch: {record.get('id')}")
            dimensions = record.get("dimensions", {})
            width = dimensions.get("width")
            height = dimensions.get("height")
            path = output_dir / str(record.get("file", ""))
            if not isinstance(width, int) or not isinstance(height, int) or width * TARGET_HEIGHT != height * TARGET_WIDTH:
                errors.append(f"wallpaper is not exact 16:9: {record.get('file')}")
            elif not path.is_file():
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
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    if args.check:
        return verify(output_dir)
    build(output_dir)
    return verify(output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
