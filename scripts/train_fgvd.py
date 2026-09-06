#!/usr/bin/env python3
"""
FGVD Dataset Converter & YOLOv8 Fine-Tuning Script
====================================================
Converts IIIT-H Fine-Grained Vehicle Detection (FGVD) annotations from
Pascal VOC XML format to YOLO .txt format, generates a data.yaml, and
launches a YOLOv8 training loop using the ITD pre-trained weights.

Usage:
    python scripts/train_fgvd.py

Dataset layout expected at C:\\IDD_FGVD:
    train/
        annos/   *.xml
        images/  *.jpg / *.png
    val/
        annos/   *.xml
        images/  *.jpg / *.png
"""

import os
import sys
import glob
import yaml
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import OrderedDict

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("train_fgvd")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Resolve paths relative to *this* repo, not the dataset
REPO_ROOT = Path(__file__).resolve().parent.parent          # Gujarat-Hackathon/

DATASET_ROOT = REPO_ROOT / "dataset" / "IDD_FGVD" / "IDD_FGVD"
SPLITS = ["train", "val"]

ITD_WEIGHTS = REPO_ROOT / "services" / "ai" / "itd_yolov8.pt"
FALLBACK_WEIGHTS = REPO_ROOT / "services" / "ai" / "yolov8n.pt"

YAML_PATH = DATASET_ROOT / "fgvd_data.yaml"


# Training hyper-parameters
EPOCHS = 50
IMGSZ = 320   # Dropped from 640 to half-resolution to save RAM
BATCH = 2     # Dropped from 8 to 2 to prevent OOM crash
PROJECT = str(REPO_ROOT / "services" / "ai" / "runs")
RUN_NAME = "fgvd_finetune"

# ---------------------------------------------------------------------------
# XML ➜ YOLO conversion helpers
# ---------------------------------------------------------------------------
def parse_voc_xml(xml_path: Path) -> dict:
    """
    Parse a single Pascal VOC XML annotation file.

    Returns
    -------
    dict with keys:
        width, height : int
        objects : list[dict]  – each dict has 'name', 'xmin', 'ymin', 'xmax', 'ymax'
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    size_el = root.find("size")
    if size_el is None:
        raise ValueError(f"No <size> tag in {xml_path}")

    width = int(size_el.findtext("width", "0"))
    height = int(size_el.findtext("height", "0"))

    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image dimensions ({width}x{height}) in {xml_path}")

    objects = []
    for obj in root.iter("object"):
        name = obj.findtext("name", "").strip()
        if not name:
            continue

        bndbox = obj.find("bndbox")
        if bndbox is None:
            continue

        xmin = float(bndbox.findtext("xmin", "0"))
        ymin = float(bndbox.findtext("ymin", "0"))
        xmax = float(bndbox.findtext("xmax", "0"))
        ymax = float(bndbox.findtext("ymax", "0"))

        objects.append({
            "name": name,
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax,
        })

    return {"width": width, "height": height, "objects": objects}


def voc_to_yolo(box: dict, img_w: int, img_h: int) -> tuple:
    """
    Convert a single VOC bounding box to YOLO normalised format.

    Parameters
    ----------
    box : dict with xmin, ymin, xmax, ymax (absolute pixels)
    img_w, img_h : image dimensions

    Returns
    -------
    (x_center, y_center, width, height)  – all normalised [0, 1]
    """
    x_center = ((box["xmin"] + box["xmax"]) / 2.0) / img_w
    y_center = ((box["ymin"] + box["ymax"]) / 2.0) / img_h
    w = (box["xmax"] - box["xmin"]) / img_w
    h = (box["ymax"] - box["ymin"]) / img_h

    # Clamp to [0, 1] to guard against sloppy annotations
    x_center = max(0.0, min(1.0, x_center))
    y_center = max(0.0, min(1.0, y_center))
    w = max(0.0, min(1.0, w))
    h = max(0.0, min(1.0, h))

    return x_center, y_center, w, h


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def build_class_map(splits: list[str]) -> OrderedDict:
    """
    First pass: scan every XML across all splits to collect *all* unique class
    names, then return a deterministic name → id mapping (sorted alphabetically).
    """
    class_names: set[str] = set()

    for split in splits:
        annos_dir = DATASET_ROOT / split / "annos"
        if not annos_dir.exists():
            logger.warning(f"Annotations directory not found: {annos_dir}")
            continue

        xml_files = list(annos_dir.glob("*.xml"))
        logger.info(f"[{split}] Scanning {len(xml_files)} XMLs for class names...")

        for xml_path in xml_files:
            try:
                data = parse_voc_xml(xml_path)
                for obj in data["objects"]:
                    class_names.add(obj["name"])
            except Exception as e:
                logger.warning(f"Skipping {xml_path.name}: {e}")

    # Deterministic ordering: alphabetical
    sorted_names = sorted(class_names)
    class_map = OrderedDict((name, idx) for idx, name in enumerate(sorted_names))
    logger.info(f"Discovered {len(class_map)} unique classes.")
    return class_map


def convert_split(split: str, class_map: OrderedDict) -> int:
    """
    Second pass: convert every XML in a split to a YOLO .txt label file.

    Returns the number of files successfully converted.
    """
    annos_dir = DATASET_ROOT / split / "annos"
    labels_dir = DATASET_ROOT / split / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)

    xml_files = sorted(annos_dir.glob("*.xml"))
    converted = 0
    skipped = 0

    for xml_path in xml_files:
        try:
            data = parse_voc_xml(xml_path)
        except Exception as e:
            logger.warning(f"Skipping {xml_path.name}: {e}")
            skipped += 1
            continue

        lines = []
        for obj in data["objects"]:
            cls_id = class_map.get(obj["name"])
            if cls_id is None:
                continue  # should never happen after build_class_map

            xc, yc, w, h = voc_to_yolo(obj, data["width"], data["height"])
            lines.append(f"{cls_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")

        # Write label file (same stem as the XML / image)
        label_path = labels_dir / (xml_path.stem + ".txt")
        with open(label_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        converted += 1

    logger.info(
        f"[{split}] Converted {converted} label files "
        f"({skipped} skipped) → {labels_dir}"
    )
    return converted


def generate_yaml(class_map: OrderedDict) -> Path:
    """
    Write the data.yaml required by YOLOv8's .train() method.
    """
    # Use forward slashes for cross-platform YOLO compatibility
    yaml_data = {
        "path": str(DATASET_ROOT).replace("\\", "/"),
        "train": "train/images",
        "val": "val/images",
        "nc": len(class_map),
        "names": list(class_map.keys()),
    }

    with open(YAML_PATH, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Generated data.yaml → {YAML_PATH}")
    logger.info(f"  nc    = {yaml_data['nc']}")
    logger.info(f"  train = {yaml_data['train']}")
    logger.info(f"  val   = {yaml_data['val']}")
    return YAML_PATH


def resolve_weights() -> str:
    """
    Return the best available weights path.
    Prefer ITD pre-trained weights; fall back to generic YOLOv8n.
    """
    if ITD_WEIGHTS.exists():
        logger.info(f"Using ITD pre-trained weights: {ITD_WEIGHTS}")
        return str(ITD_WEIGHTS)

    logger.warning(
        "ITD custom weights not found. Falling back to generic YOLOv8n."
    )

    if FALLBACK_WEIGHTS.exists():
        logger.info(f"Using fallback weights: {FALLBACK_WEIGHTS}")
        return str(FALLBACK_WEIGHTS)

    # Last resort: let ultralytics auto-download yolov8n.pt
    logger.warning("No local weights found — ultralytics will auto-download yolov8n.pt")
    return "yolov8n.pt"


def train(yaml_path: Path, weights: str):
    """
    Import YOLO and kick off the training loop.
    """
    from ultralytics import YOLO

    logger.info("=" * 60)
    logger.info("Starting YOLOv8 fine-tuning on FGVD dataset")
    logger.info(f"  Weights : {weights}")
    logger.info(f"  Data    : {yaml_path}")
    logger.info(f"  Epochs  : {EPOCHS}")
    logger.info(f"  ImgSize : {IMGSZ}")
    logger.info(f"  Batch   : {BATCH}")
    logger.info(f"  Project : {PROJECT}")
    logger.info(f"  Name    : {RUN_NAME}")
    logger.info("=" * 60)

    model = YOLO(weights)
    model.train(
        data=str(yaml_path),
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        project=PROJECT,
        name=RUN_NAME,
    )

    logger.info("Training complete! Results saved to %s/%s", PROJECT, RUN_NAME)


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------
def main():
    logger.info("FGVD Dataset Converter & Trainer")
    logger.info(f"Dataset root: {DATASET_ROOT}")

    # --- Pre-flight checks ---
    if not DATASET_ROOT.exists():
        logger.error(
            f"Dataset root not found: {DATASET_ROOT}\n"
            "Please download the IIIT-H FGVD dataset and place it at the expected path."
        )
        sys.exit(1)

    for split in SPLITS:
        annos = DATASET_ROOT / split / "annos"
        images = DATASET_ROOT / split / "images"
        if not annos.exists():
            logger.error(f"Missing annotations directory: {annos}")
            sys.exit(1)
        if not images.exists():
            logger.error(f"Missing images directory: {images}")
            sys.exit(1)

    # --- Step 1: Build a global class map ---
    class_map = build_class_map(SPLITS)
    if not class_map:
        logger.error("No classes found — are the XMLs in the expected location?")
        sys.exit(1)

    # --- Step 2: Convert annotations per split ---
    for split in SPLITS:
        convert_split(split, class_map)

    # --- Step 3: Generate data.yaml ---
    yaml_path = generate_yaml(class_map)

    # --- Step 4: Resolve weights & launch training ---
    weights = resolve_weights()
    train(yaml_path, weights)


if __name__ == "__main__":
    main()
