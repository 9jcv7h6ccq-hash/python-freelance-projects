import os
import shutil
from pathlib import Path


# تعريف الامتدادات لكل نوع
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
PDF_EXT = {".pdf"}
VIDEO_EXT = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}


def get_category(file_path: Path) -> str:
    """تحديد نوع الملف حسب الامتداد."""
    ext = file_path.suffix.lower()
    if ext in IMAGE_EXT:
        return "Images"
    if ext in PDF_EXT:
        return "PDFs"
    if ext in VIDEO_EXT:
        return "Videos"
    return "Others"


def organize_folder(folder: Path) -> None:
    """تنظيم الملفات داخل المجلد إلى مجلدات فرعية حسب النوع."""
    if not folder.exists() or not folder.is_dir():
        print("المسار ليس مجلدًا صالحًا.")
        return

    moved_count = 0

    for item in folder.iterdir():
        # نتجاهل المجلدات التي سننشئها، ونتجاهل المجلدات عمومًا
        if item.is_dir():
            continue

        category = get_category(item)
        target_dir = folder / category
        target_dir.mkdir(exist_ok=True)

        target_path = target_dir / item.name

        # إذا كان الملف بنفس الاسم موجود مسبقاً، نضيف رقم حتى لا يُستبدل
        if target_path.exists():
            base = item.stem
            ext = item.suffix
            counter = 1
            while True:
                new_name = f"{base}_{counter}{ext}"
                candidate = target_dir / new_name
                if not candidate.exists():
                    target_path = candidate
                    break
                counter += 1

        shutil.move(str(item), str(target_path))
        moved_count += 1
        print(f"نقل: {item.name}  -->  {target_path.relative_to(folder)}")

    print(f"\nتم تنظيم المجلد. عدد الملفات المنقولة: {moved_count}")


def main() -> None:
    print("=== File Organizer Script ===")
    print("هذا البرنامج ينظم الملفات داخل مجلد حسب النوع:")
    print("- Images")
    print("- PDFs")
    print("- Videos")
    print("- Others\n")

    path_str = input("اكتب مسار المجلد (أو اتركه فارغًا لاستخدام المجلد الحالي): ").strip()
    if path_str:
        folder = Path(path_str).expanduser().resolve()
    else:
        folder = Path.cwd()

    print(f"\nسيتم تنظيم المجلد: {folder}")
    confirm = input("متأكد؟ (y/n): ").strip().lower()
    if confirm not in {"y", "yes", "نعم"}:
        print("تم الإلغاء.")
        return

    organize_folder(folder)


if __name__ == "__main__":
    main()
