# AI Generated script for compressing / optimizing the images

import os
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install it using: pip install pillow")
    sys.exit(1)

def format_size(size_bytes):
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} B"

def process_single_image(args):
    file_path_str, mode = args
    file_path = Path(file_path_str)
    orig_size = file_path.stat().st_size
    out_path = file_path.with_suffix(".webp")

    with Image.open(file_path) as img:
        save_kwargs = {
            "format": "WEBP",
            "method": 6,
        }

        if mode == "lossless":
            save_kwargs["lossless"] = True
        elif mode == "near-lossless":
            save_kwargs["lossless"] = True
            save_kwargs["quality"] = 75
        else:
            save_kwargs["quality"] = 88

        if img.mode not in ("RGB", "RGBA"):
            if "transparency" in img.info or img.mode in ("LA", "P", "PA"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")

        img.save(out_path, **save_kwargs)

    new_size = out_path.stat().st_size
    return file_path.name, orig_size, new_size

def convert_pngs_to_webp(images_dir, mode="perceptual"):
    directory = Path(images_dir)
    if not directory.exists():
        print(f"Directory not found: {images_dir}")
        return

    png_files = sorted(list(directory.glob("*.png")))
    if not png_files:
        print(f"No PNG files found in {images_dir}")
        return

    cpu_count = os.cpu_count() or 4
    print(f"Found {len(png_files)} PNG files in {directory.resolve()}")

    if mode == "lossless":
        label = "Bit-exact Lossless"
    elif mode == "near-lossless":
        label = "WebP Near-Lossless Preprocessing (Lossless + Q75 filter)"
    else:
        label = "Perceptually Lossless (High-Fidelity Q88, ~90% savings)"

    print(f"Mode: {label} (Workers: {cpu_count})\n")

    tasks = [(str(f), mode) for f in png_files]
    total_orig_bytes = 0
    total_new_bytes = 0

    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        futures = [executor.submit(process_single_image, task) for task in tasks]
        for future in as_completed(futures):
            name, orig_size, new_size = future.result()
            total_orig_bytes += orig_size
            total_new_bytes += new_size
            saved_bytes = orig_size - new_size
            saved_pct = (saved_bytes / orig_size * 100) if orig_size > 0 else 0

            print(
                f"✓ {name:<26} "
                f"{format_size(orig_size):>9} -> {format_size(new_size):>9} "
                f"({saved_pct:>5.1f}% saved)"
            )

    net_saved = total_orig_bytes - total_new_bytes
    net_pct = (net_saved / total_orig_bytes * 100) if total_orig_bytes > 0 else 0
    print("\n" + "=" * 60)
    print(f"Total Original: {format_size(total_orig_bytes)}")
    print(f"Total WebP:     {format_size(total_new_bytes)}")
    print(f"Net Saved:      {format_size(net_saved)} ({net_pct:.1f}% reduction)")
    print("=" * 60)

if __name__ == "__main__":
    if "--lossless" in sys.argv:
        selected_mode = "lossless"
    elif "--near-lossless" in sys.argv:
        selected_mode = "near-lossless"
    else:
        selected_mode = "perceptual"

    script_dir = Path(__file__).resolve().parent
    target_dir = script_dir.parent.parent / "public" / "images"
    convert_pngs_to_webp(target_dir, mode=selected_mode)
