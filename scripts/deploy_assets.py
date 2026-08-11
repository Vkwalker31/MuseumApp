from pathlib import Path
from PIL import Image

ASSETS = Path(r"C:\Users\kirya\.cursor\projects\d-BSUIR-5th-semester-STRWEB-LR2\assets")
PROJECTS = [
    Path(r"D:\BSUIR\5th semester\STRWEB\LR1\MuseumApp"),
    Path(r"D:\BSUIR\5th semester\STRWEB\LR2\MuseumApp"),
]

def save_resized(src: Path, dest: Path, size, fmt=None):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
        fitted = img.copy()
        fitted.thumbnail(size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA" if fitted.mode == "RGBA" else "RGB", size, (0, 0, 0, 0) if fitted.mode == "RGBA" else (255, 255, 255))
        offset = ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2)
        if fitted.mode == "RGBA":
            canvas.paste(fitted, offset, fitted)
        else:
            canvas.paste(fitted, offset)
        if fmt == "ICO":
            canvas.convert("RGBA").save(dest, format="ICO", sizes=[(32, 32), (16, 16)])
        else:
            canvas.save(dest, format=fmt or ("PNG" if dest.suffix.lower() == ".png" else "JPEG"), quality=92)

static_map = {
    "logo.png": ("images/logo.png", (256, 256)),
    "banner1.png": ("images/banners/banner1.png", (1200, 320)),
    "banner2.png": ("images/banners/banner2.png", (1200, 320)),
    "banner3.png": ("images/banners/banner3.png", (1200, 320)),
    "partner_hermitage.png": ("images/partners/partner_hermitage.png", (240, 240)),
    "partner_tretyakov.png": ("images/partners/partner_tretyakov.png", (240, 240)),
    "partner_louvre.png": ("images/partners/partner_louvre.png", (240, 240)),
}

media_map = {
    "service_adult.png": ("services/adult.png", (640, 400)),
    "service_audio.png": ("services/audio.png", (640, 400)),
    "service_weekend.png": ("services/weekend.png", (640, 400)),
    "service_child.png": ("services/child.png", (640, 400)),
    "news_exhibition.png": ("news/news_exhibition.png", (960, 540)),
    "news_restoration.png": ("news/news_restoration.png", (960, 540)),
    "news_night_tour.png": ("news/news_night_tour.png", (960, 540)),
    "contact_ivanov.png": ("contacts/contact_ivanov.png", (320, 320)),
    "contact_petrova.png": ("contacts/contact_petrova.png", (320, 320)),
    "contact_reception.png": ("contacts/contact_reception.png", (320, 320)),
}

for project in PROJECTS:
    static_root = project / "static"
    media_root = project / "media"
    for src_name, (rel, size) in static_map.items():
        src = ASSETS / src_name
        if src.exists():
            save_resized(src, static_root / rel, size)
    logo = static_root / "images/logo.png"
    if logo.exists():
        save_resized(logo, static_root / "favicon.ico", (32, 32), fmt="ICO")
    for src_name, (rel, size) in media_map.items():
        src = ASSETS / src_name
        if src.exists():
            save_resized(src, media_root / rel, size)

print("Images deployed to LR1 and LR2")
