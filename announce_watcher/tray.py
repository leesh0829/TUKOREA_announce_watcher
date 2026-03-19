from __future__ import annotations


def run_tray_app() -> None:
    try:
        import pystray  # type: ignore
        from PIL import Image, ImageDraw  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise RuntimeError(
            "Tray mode requires optional dependencies 'pystray' and 'Pillow'. Install them first."
        ) from exc

    image = Image.new("RGB", (64, 64), color=(33, 150, 243))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill=(255, 255, 255))

    icon = pystray.Icon("announce_watcher", image, "TUKOREA Announce Watcher")
    icon.run()
