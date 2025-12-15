import argparse
from pathlib import Path
import cv2
from ultralytics import YOLO

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

def iter_images(p: Path):
    if p.is_file():
        if p.suffix.lower() in IMG_EXTS:
            yield p
        return
    for f in sorted(p.rglob("*")):
        if f.is_file() and f.suffix.lower() in IMG_EXTS:
            yield f

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--weights",
        default="../best_model_weights/best.pt",
        help="Path to trained YOLOv8 weights"
    )
    ap.add_argument(
        "--source",
        default="./Input/",
        help="Image file or directory"
    )
    ap.add_argument(
        "--out",
        default="./Output/",
        help="Output directory"
    )
    ap.add_argument(
        "--conf",
        type=float,
        default=0.6,
        help="Confidence threshold"
    )
    ap.add_argument(
        "--device",
        default="0",
        help="Jetson GPU device (default: 0)"
    )
    args = ap.parse_args()

    weights = Path(args.weights)
    source = Path(args.source)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(weights))

    images = list(iter_images(source))
    if not images:
        raise SystemExit(f"No images found in: {source}")

    for img in images:
        results = model.predict(
            source=str(img),
            imgsz=640,          # forced to training resolution
            conf=args.conf,
            device=args.device,
            verbose=False
        )

        annotated = results[0].plot()
        out_path = outdir / img.name
        cv2.imwrite(str(out_path), annotated[:, :, ::-1])
        print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()
