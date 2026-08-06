"""Build the non-destructive Fata Morgana art master collection.

The source directory is intentionally ignored by Git. Every input is matched by
SHA-256, not filename, so accidental replacements and out-of-scope art fail the
build instead of quietly entering the desktop theme.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "pictures"
DEFAULT_OUTPUT_DIR = ROOT / "assets" / "art" / "fata-morgana"
MAX_LONG_EDGE = 2048
# Portraits are shared by Kitty and Rofi, whose wide interface surfaces cannot
# use a vertical-16:9 composition without discarding most of the illustration.
# The current approved maximum is fm-026 at 1.555; 1.60 leaves a small margin
# while rejecting the retired fm-032 composition at 1.777.
MAX_PORTRAIT_HEIGHT_TO_WIDTH = 1.60
SHARED_ROLES = ("kitty", "rofi", "mako", "lockscreen")
WALLPAPER_CANDIDATES = {
    "82fea3a44d36e42fbcc7fb5a1c2861272bf6005113ea0c2a0f88fef929a59b92": ("center", 20.9),
    "13f614c020b3824b394f65a75180db7e32e85f2be0c953659dd155d71acddc35": ("center", 19.5),
    "7148db18c753e55c576ad9aa7e29217986f7347c0d6222ca38d8878c69d4b735": ("center", 20.4),
    "5cbfc0ae80280a196e9316aa4068163ee431a90cc24565060127da8a6f95db04": ("native", 0.0),
    "95885c07024a23397d2054a75d316d6c0b1981e857c4aeccca8bed0c5bb5ea57": ("center", 21.9),
}


@dataclass(frozen=True)
class ArtworkSpec:
    index: int
    slug: str


SPECS = {
    "2a93f0fb6663687c7fbf5d546240448383eaf0989736ae27b2395f43514d12e7": ArtworkSpec(1, "red-masked-portrait"),
    "9d75bcfae3a1deb2d43c729ed438b9443b03e8d230d17137f6331d385fc4f92a": ArtworkSpec(2, "misty-forest-portrait"),
    "fc40ce6a9010956fcd92a435dac3423d89fe1883e64bedff4a732204654429b0": ArtworkSpec(4, "jacopo-crimson-portrait"),
    "ece6f3f387ce4e45811150987e717615709bc0d2d5d0ea02e8e9b5d46719d545": ArtworkSpec(5, "jacopo-and-clock"),
    "7494c771e7df01847e4439db36ea229009808cca3fd98fb48b1a8a78013b39c7": ArtworkSpec(6, "jacopo-at-table"),
    "f139c2acc048c8a73b09688e45f658e5c6f11d7f2f30debf5f9258531ebff6bf": ArtworkSpec(7, "mell-and-michel"),
    "2a7656318ae2588a5b0cb88c964ee4105e8e690ffca393036ebe7a5bf194e21b": ArtworkSpec(8, "white-haired-figure"),
    "72743674d9410e35ec48812e1045404eef3e23d487642e4631abcd412cb40199": ArtworkSpec(9, "michel-and-skull"),
    "330ddd6ebf907fa24dfbaaaeff8322afb46d90b7a597e3503461208d00709207": ArtworkSpec(10, "michel-and-white-haired-girl"),
    "fa07ca48f521b1160f88419f1b1f5bdee5922ddf7e5b5016d312d32990d8a7dc": ArtworkSpec(11, "tower-scene"),
    "3a95419565cf158247054146fd0656222034627be114a00a04d066ff90bbdf3e": ArtworkSpec(12, "crimson-portrait"),
    "28bacdd9f2d3dc5fc4f276265f38615c0d9e1c34701f383c028d63ca1a27f89e": ArtworkSpec(13, "entwined-figures"),
    "c853ee0de3333566276c228ec3337b2f48cefd9855c754cc7f9deb63ffe39775": ArtworkSpec(14, "quiet-portrait"),
    "e0bd2b8f25ddc1995b0f6a5ba15f42190e754dea965b3a943f18934ff1e7926d": ArtworkSpec(15, "bloodied-figure"),
    "82fea3a44d36e42fbcc7fb5a1c2861272bf6005113ea0c2a0f88fef929a59b92": ArtworkSpec(16, "violet-cloaked-portrait"),
    "7f6e227cc7247936baed7f2560baadb705fbb27c0a30340543610a2732d57326": ArtworkSpec(17, "reaching-light"),
    "94fb3eba0305d1eefb64ca7a963ed6cb7d98473fd9a51ce4f4e4d78de69af344": ArtworkSpec(18, "palm-and-tear"),
    "bed589bc8d31af31190135fa990429a5f58e63c4bcfdd073ad53fa4c2ea09245": ArtworkSpec(19, "grief-and-embrace"),
    "2444d196f8c1e4ddcc435ae753211e42ae151f385a929713e1af137fc40ea7d6": ArtworkSpec(20, "offering-hand"),
    "caa0c84a956cbb960f987caccbb086de2dc26f9ebec62a186fbe6e4020999059": ArtworkSpec(21, "black-and-white-tableau"),
    "766e94e222c3e8834fe8b3f948237c6dc4797f7f7b69d180fe1ad2516f81db7f": ArtworkSpec(22, "anguished-portrait"),
    "cba974f25ed0fe1f3209685f474b4dccf6699eb62acc5e4d6e494ead863bffa5": ArtworkSpec(23, "snowy-bride"),
    "045c2639bdac6599d85a600670534febed81a6fd6fd41044a353be973da60561": ArtworkSpec(24, "thorned-portrait"),
    "d102d855cbdb09d49251c18aba5e82cd8af4f401d19d7f2b4bcfcc0933a2d7b0": ArtworkSpec(25, "mell-forest-tableau"),
    "2a88f12aa1e709860e2dca6bfec7cd9539de4281558d9dc037f8f6b5c50c9669": ArtworkSpec(26, "shaft-of-light"),
    "c2cc355604e9d3a8486e58e21e2119e33eee1fb44e218c220bf5faa09bed0a41": ArtworkSpec(27, "chained-figures"),
    "e966c5aca7c50a7c49a5dcaef0ac3b341fd6849c05860e44f6153b8ffe9e6b7b": ArtworkSpec(28, "crimson-reaching-figure"),
    "ed18fc804c82667e1e79b6fa325935cb312d059772dd3f59d022189b3335d419": ArtworkSpec(30, "blue-aura-figure"),
    "13f614c020b3824b394f65a75180db7e32e85f2be0c953659dd155d71acddc35": ArtworkSpec(31, "sleeping-maid"),
    "9ca9b15992c36ef53eb394777fe20c1bfb73c87a21acbea2a413e7bcfb074ffa": ArtworkSpec(33, "snowfall-portrait"),
    "f057d786d53326a83bcc2cd40624b02f20500dd8b5bec81a27181793021a444d": ArtworkSpec(34, "rose-profile"),
    "7148db18c753e55c576ad9aa7e29217986f7347c0d6222ca38d8878c69d4b735": ArtworkSpec(35, "spotlight-figure"),
    "7a063a718b0b3b168177699a3cdf51f7217e768430aef1d249764dea60321e8d": ArtworkSpec(36, "sketched-pair"),
    "71218b18aad6e960897355ed1630c0f7b70c1a70acd3a9b6cd9e58287c441bf1": ArtworkSpec(37, "misty-blue-figure"),
    "5cbfc0ae80280a196e9316aa4068163ee431a90cc24565060127da8a6f95db04": ArtworkSpec(38, "moonlit-sleep"),
    "4cfb5c2d643b9635df8c8ec4249e6dde1435f753488bd35226fdbbe4d3466e6f": ArtworkSpec(39, "forest-fire"),
    "95885c07024a23397d2054a75d316d6c0b1981e857c4aeccca8bed0c5bb5ea57": ArtworkSpec(40, "butterfly-maid"),
    "238c236381b297703e2d77a2b4d1bba30ddb3ebea8330193169644a43536be08": ArtworkSpec(41, "blue-orb-portrait"),
    "8e5c640d86d30eae3c76e25bee0a7ddc3a20dd3acd83f68b440367471e911f0f": ArtworkSpec(42, "mansion-window"),
    "622cb31d899bbff7cf0dd27ddf00e9d5b344a7a22c4a5ac9a6cb57c8a7e70355": ArtworkSpec(43, "monochrome-gentleman"),
}

# User-retired raw inputs remain local in pictures/ but are deliberately not
# eligible for generation. Keeping their hashes explicit maintains a closed
# source inventory without mutating the user's originals.
RETIRED_SOURCE_HASHES = {
    "ab3b0b3161552c68639ccb123c185c81243a6087f0383bc8731f65b3bf00e2ec",
    "93d6a6a8151a270f98a0fdb228ef0de1e1654d3fc7f0a62712823c2eba0fb1c0",
    "baa4552abf2424034514ce12c42529beb7c0c2d13a9fbbada6571bb33c06afbe",
    "4554b79deaae70e3bc1e559e141c100348451953af9506bafbf0c0116e579d7e",
    "bb2c3e8848ded04bff98a28d1efe3c41438549945be9965a95af3dd20271c796",
    "7050edc0f251a3f4f60ce04db624ee0178280dc35f4ab48aa96fadbdc3736d8d",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def artwork_id(spec: ArtworkSpec) -> str:
    return f"fm-{spec.index:03d}"


def output_filename(spec: ArtworkSpec) -> str:
    return f"fata-morgana-{spec.index:03d}-{spec.slug}.jpg"


def source_files(input_dir: Path, selected_ids: set[str] | None = None) -> list[tuple[ArtworkSpec, str, Path]]:
    allowed_suffixes = {".jpg", ".jpeg", ".png", ".webp"}
    discovered = [path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() in allowed_suffixes]
    known_ids = {artwork_id(spec) for spec in SPECS.values()}
    if selected_ids is not None:
        unknown_ids = selected_ids - known_ids
        if unknown_ids:
            raise RuntimeError("unknown artwork IDs: " + ", ".join(sorted(unknown_ids)))
    records: list[tuple[ArtworkSpec, str, Path]] = []
    unexpected: list[Path] = []
    seen: set[str] = set()
    for path in discovered:
        source_hash = sha256(path)
        if source_hash in RETIRED_SOURCE_HASHES:
            continue
        spec = SPECS.get(source_hash)
        if spec is None:
            unexpected.append(path)
            continue
        if selected_ids is not None and artwork_id(spec) not in selected_ids:
            continue
        if source_hash in seen:
            unexpected.append(path)
            continue
        seen.add(source_hash)
        records.append((spec, source_hash, path))
    expected_hashes = {
        source_hash
        for source_hash, spec in SPECS.items()
        if selected_ids is None or artwork_id(spec) in selected_ids
    }
    missing = expected_hashes - seen
    if unexpected or missing:
        messages = []
        if unexpected:
            messages.append("unexpected or duplicate inputs: " + ", ".join(path.name for path in unexpected))
        if missing:
            messages.append("missing approved hashes: " + ", ".join(sorted(missing)))
        raise RuntimeError("; ".join(messages))
    return sorted(records, key=lambda record: record[0].index)


def dimensions(image: Image.Image) -> dict[str, int]:
    return {"width": image.width, "height": image.height}


def validate_shared_surface_aspect(image: Image.Image, source_path: Path) -> None:
    """Reject portraits that would discard excessive content in Kitty and Rofi."""
    ratio = image.height / image.width
    if ratio > MAX_PORTRAIT_HEIGHT_TO_WIDTH:
        raise RuntimeError(
            f"portrait {source_path.name} is too tall for shared UI surfaces: "
            f"{ratio:.3f} > {MAX_PORTRAIT_HEIGHT_TO_WIDTH:.2f}"
        )


def wallpaper_metadata(source_hash: str) -> dict[str, object]:
    candidate = WALLPAPER_CANDIDATES.get(source_hash)
    if candidate is None:
        return {"eligible": False}
    crop, loss_percent = candidate
    return {
        "eligible": True,
        "target_aspect_ratio": "16:9",
        "crop": crop,
        "estimated_crop_loss_percent": loss_percent,
    }


def build(input_dir: Path, output_dir: Path) -> None:
    records = source_files(input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_artwork = [
        build_entry(spec, source_hash, source_path, output_dir)
        for spec, source_hash, source_path in records
    ]
    manifest = {
        "schema_version": 1,
        "collection": "The House in Fata Morgana — user-supplied art masters",
        "normalization": {
            "orientation": "EXIF transpose",
            "color_space": "sRGB RGB",
            "metadata": "stripped",
            "max_long_edge_px": MAX_LONG_EDGE,
            "crop": "none",
            "upscale": "never",
        },
        "artwork": manifest_artwork,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(manifest_artwork)} normalized masters in {output_dir}")


def build_entry(spec: ArtworkSpec, source_hash: str, source_path: Path, output_dir: Path) -> dict[str, object]:
    filename = output_filename(spec)
    output_path = output_dir / filename
    with Image.open(source_path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    validate_shared_surface_aspect(image, source_path)
    source_dimensions = dimensions(image)
    image.thumbnail((MAX_LONG_EDGE, MAX_LONG_EDGE), Image.Resampling.LANCZOS)
    image.save(output_path, "JPEG", quality=94, subsampling=0, optimize=True, progressive=True)
    with Image.open(output_path) as rendered:
        rendered_dimensions = dimensions(rendered)
    return {
        "id": artwork_id(spec),
        "file": filename,
        "source_file": source_path.name,
        "source_sha256": source_hash,
        "source_dimensions": source_dimensions,
        "sha256": sha256(output_path),
        "dimensions": rendered_dimensions,
        "roles": list(SHARED_ROLES),
        "wallpaper": wallpaper_metadata(source_hash),
    }


def build_selected(input_dir: Path, output_dir: Path, selected_ids: set[str]) -> None:
    """Replace named approved masters without requiring unrelated raw inputs."""
    records = source_files(input_dir, selected_ids)
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("cannot perform a targeted rebuild without an existing manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artwork = manifest.get("artwork", [])
    if not isinstance(artwork, list) or not all(isinstance(entry, dict) for entry in artwork):
        raise RuntimeError("existing manifest artwork must be a list of objects")
    entries_by_id = {entry.get("id"): entry for entry in artwork}
    expected_ids = {artwork_id(spec) for spec in SPECS.values()}
    if len(artwork) != len(entries_by_id) or set(entries_by_id) != expected_ids:
        raise RuntimeError("existing manifest inventory is incomplete; run a full rebuild with all approved inputs")
    for spec, source_hash, source_path in records:
        entries_by_id[artwork_id(spec)] = build_entry(spec, source_hash, source_path, output_dir)
    manifest["artwork"] = [entries_by_id[artwork_id(spec)] for spec in sorted(SPECS.values(), key=lambda item: item.index)]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(records)} selected normalized master(s) in {output_dir}")


def verify(input_dir: Path, output_dir: Path) -> int:
    del input_dir  # Release validation must not require private raw sources.
    spec_by_id = {artwork_id(spec): (source_hash, spec) for source_hash, spec in SPECS.items()}
    expected = {output_filename(spec) for _, spec in spec_by_id.values()}
    actual = {path.name for path in output_dir.glob("*.jpg")} if output_dir.exists() else set()
    errors = []
    if expected != actual:
        errors.append(f"master set mismatch: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        errors.append("missing manifest.json")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("schema_version") != 1:
            errors.append("unexpected master manifest schema")
        artwork = manifest.get("artwork", [])
        if not isinstance(artwork, list) or not all(isinstance(entry, dict) for entry in artwork):
            errors.append("manifest artwork must be a list of objects")
            artwork = []
        entries_by_id = {entry.get("id"): entry for entry in artwork}
        if len(artwork) != len(entries_by_id) or set(entries_by_id) != set(spec_by_id):
            errors.append("manifest artwork IDs do not match the approved inventory")
        for entry_id, entry in entries_by_id.items():
            expected_record = spec_by_id.get(entry_id)
            if expected_record is None:
                continue
            source_hash, spec = expected_record
            expected_file = output_filename(spec)
            if entry.get("file") != expected_file:
                errors.append(f"manifest filename mismatch: {entry_id}")
                continue
            if entry.get("source_sha256") != source_hash:
                errors.append(f"manifest source checksum mismatch: {entry_id}")
            if not isinstance(entry.get("source_file"), str) or not entry["source_file"]:
                errors.append(f"manifest source filename missing: {entry_id}")
            if entry.get("wallpaper") != wallpaper_metadata(source_hash):
                errors.append(f"manifest wallpaper metadata mismatch: {entry_id}")
            path = output_dir / expected_file
            dimensions_record = entry.get("dimensions", {})
            width = dimensions_record.get("width")
            height = dimensions_record.get("height")
            if not path.is_file():
                errors.append(f"missing master file: {expected_file}")
                continue
            if not isinstance(width, int) or not isinstance(height, int):
                errors.append(f"invalid master dimensions in manifest: {expected_file}")
                continue
            if sha256(path) != entry.get("sha256"):
                errors.append(f"master checksum mismatch: {expected_file}")
            with Image.open(path) as image:
                if image.size != (width, height) or max(image.size) > MAX_LONG_EDGE or image.mode != "RGB":
                    errors.append(f"invalid master {path.name}: {image.mode} {image.size}")
                elif image.height / image.width > MAX_PORTRAIT_HEIGHT_TO_WIDTH:
                    errors.append(f"portrait too tall for shared UI surfaces: {path.name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Verified {len(expected)} normalized masters and manifest.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--ids", nargs="+", metavar="FM_ID", help="rebuild only named approved master IDs")
    parser.add_argument("--check", action="store_true", help="validate existing masters without writing files")
    args = parser.parse_args()
    input_dir = resolve_path(args.input_dir)
    output_dir = resolve_path(args.output_dir)
    if args.check:
        return verify(input_dir, output_dir)
    if not input_dir.is_dir():
        raise RuntimeError(f"input directory does not exist: {input_dir}")
    if args.ids:
        build_selected(input_dir, output_dir, set(args.ids))
    else:
        build(input_dir, output_dir)
    return verify(input_dir, output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
