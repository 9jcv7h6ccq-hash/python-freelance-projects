import csv
import os
import shutil
from pathlib import Path


def ask_path(prompt: str) -> Path:
    while True:
        p = input(prompt).strip()
        if not p:
            print("اكتب مسارًا صحيحًا.")
            continue
        path = Path(p).expanduser().resolve()
        return path


def confirm(prompt: str = "متأكد؟ (y/n): ") -> bool:
    v = input(prompt).strip().lower()
    return v in {"y", "yes", "نعم", "ok"}


# -------------------------
# 1) إعادة تسمية ملفات
# -------------------------


def rename_preview(files: list[Path], new_names: list[str]) -> None:
    print("\n--- معاينة إعادة التسمية ---")
    for f, n in zip(files, new_names):
        print(f"{f.name}  ->  {n}")


def op_rename_files() -> None:
    folder = ask_path("مسار المجلد الذي يحتوي الملفات: ")
    if not folder.exists() or not folder.is_dir():
        print("المسار ليس مجلدًا صالحًا.")
        return

    ext_filter = input("فلتر امتداد (مثال: .txt) أو Enter للكل: ").strip().lower()
    files = [p for p in folder.iterdir() if p.is_file() and (not ext_filter or p.suffix.lower() == ext_filter)]
    if not files:
        print("لا توجد ملفات مطابقة.")
        return

    print("\nاختر طريقة إعادة التسمية:")
    print("1) إضافة prefix/suffix")
    print("2) استبدال نص داخل الاسم")
    print("3) ترقيم تسلسلي (file_1, file_2...) مع الحفاظ على الامتداد")
    choice = input("اختر رقم: ").strip()

    new_names: list[str] = []

    if choice == "1":
        prefix = input("Prefix (اختياري): ").strip()
        suffix = input("Suffix (اختياري): ").strip()
        for f in files:
            new_names.append(f"{prefix}{f.stem}{suffix}{f.suffix}")
    elif choice == "2":
        old = input("النص المراد استبداله: ")
        new = input("النص الجديد: ")
        for f in files:
            new_names.append(f.name.replace(old, new))
    elif choice == "3":
        base = input("اسم أساسي (افتراضي: file): ").strip() or "file"
        start = input("بداية الترقيم (افتراضي: 1): ").strip()
        try:
            start_n = int(start) if start else 1
        except ValueError:
            start_n = 1
        width = input("عدد خانات الترقيم (مثال 3 => 001) أو Enter: ").strip()
        width_n = int(width) if width.isdigit() else 0
        for i, f in enumerate(files, start=start_n):
            num = str(i).zfill(width_n) if width_n else str(i)
            new_names.append(f"{base}_{num}{f.suffix}")
    else:
        print("اختيار غير صحيح.")
        return

    rename_preview(files, new_names)
    if not confirm("تنفيذ إعادة التسمية؟ (y/n): "):
        print("تم الإلغاء.")
        return

    # تنفيذ مع تجنب التعارضات
    used = set(p.name for p in folder.iterdir())
    for f, new_name in zip(files, new_names):
        target = folder / new_name
        if target.exists() and target.resolve() != f.resolve():
            # نضيف رقم لتجنب التعارض
            base = target.stem
            ext = target.suffix
            k = 1
            while True:
                candidate = folder / f"{base}_{k}{ext}"
                if not candidate.exists():
                    target = candidate
                    break
                k += 1
        used.add(target.name)
        f.rename(target)

    print("تمت إعادة التسمية بنجاح.")


# -------------------------
# 2) دمج ملفات
# -------------------------


def op_merge_text_files() -> None:
    folder = ask_path("مسار المجلد الذي يحتوي ملفات النص: ")
    if not folder.exists() or not folder.is_dir():
        print("المسار ليس مجلدًا صالحًا.")
        return

    ext = input("امتداد ملفات النص (افتراضي: .txt): ").strip().lower() or ".txt"
    files = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ext])
    if not files:
        print("لا توجد ملفات مطابقة.")
        return

    out_name = input("اسم ملف الإخراج (افتراضي: merged.txt): ").strip() or "merged.txt"
    out_path = folder / out_name

    print("\nسيتم دمج الملفات التالية بالترتيب:")
    for p in files:
        print(f"- {p.name}")

    if not confirm("تنفيذ الدمج؟ (y/n): "):
        print("تم الإلغاء.")
        return

    with out_path.open("w", encoding="utf-8") as out:
        for p in files:
            out.write(f"\n--- {p.name} ---\n")
            out.write(p.read_text(encoding="utf-8", errors="ignore"))
            out.write("\n")

    print(f"تم إنشاء: {out_path}")


def op_merge_csv_files() -> None:
    folder = ask_path("مسار المجلد الذي يحتوي ملفات CSV: ")
    if not folder.exists() or not folder.is_dir():
        print("المسار ليس مجلدًا صالحًا.")
        return

    files = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".csv"])
    if not files:
        print("لا توجد ملفات CSV.")
        return

    out_name = input("اسم ملف الإخراج (افتراضي: merged.csv): ").strip() or "merged.csv"
    out_path = folder / out_name

    print("\nسيتم دمج ملفات CSV التالية:")
    for p in files:
        print(f"- {p.name}")
    print("ملاحظة: يجب أن تكون رؤوس الأعمدة (Header) متطابقة.")

    if not confirm("تنفيذ الدمج؟ (y/n): "):
        print("تم الإلغاء.")
        return

    header = None
    total_rows = 0
    with out_path.open("w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)
        for p in files:
            with p.open("r", newline="", encoding="utf-8-sig") as in_f:
                reader = csv.reader(in_f)
                rows = list(reader)
                if not rows:
                    continue
                this_header = rows[0]
                if header is None:
                    header = this_header
                    writer.writerow(header)
                elif this_header != header:
                    print(f"توقّف: Header مختلف في الملف {p.name}")
                    return

                for r in rows[1:]:
                    writer.writerow(r)
                    total_rows += 1

    print(f"تم إنشاء: {out_path} (عدد الصفوف المدموجة: {total_rows})")


def op_merge_pdfs() -> None:
    try:
        from pypdf import PdfMerger  # type: ignore
    except Exception:
        print("لا يمكن دمج PDF بدون مكتبة pypdf.")
        print("ثبّت: pip install pypdf")
        return

    folder = ask_path("مسار مجلد ملفات PDF: ")
    if not folder.exists() or not folder.is_dir():
        print("المسار ليس مجلدًا صالحًا.")
        return

    files = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"])
    if not files:
        print("لا توجد ملفات PDF.")
        return

    out_name = input("اسم ملف الإخراج (افتراضي: merged.pdf): ").strip() or "merged.pdf"
    out_path = folder / out_name

    print("\nسيتم دمج ملفات PDF التالية:")
    for p in files:
        print(f"- {p.name}")

    if not confirm("تنفيذ الدمج؟ (y/n): "):
        print("تم الإلغاء.")
        return

    merger = PdfMerger()
    for p in files:
        merger.append(str(p))
    merger.write(str(out_path))
    merger.close()

    print(f"تم إنشاء: {out_path}")


# -------------------------
# 3) تحويل صيغ
# -------------------------


def op_convert_images() -> None:
    try:
        from PIL import Image  # type: ignore
    except Exception:
        print("تحويل الصور يحتاج مكتبة Pillow.")
        print("ثبّت: pip install pillow")
        return

    folder = ask_path("مسار مجلد الصور: ")
    if not folder.exists() or not folder.is_dir():
        print("المسار ليس مجلدًا صالحًا.")
        return

    src_ext = input("امتداد المصدر (مثال: .png): ").strip().lower()
    dst_ext = input("امتداد الهدف (مثال: .jpg): ").strip().lower()
    if not src_ext.startswith(".") or not dst_ext.startswith("."):
        print("اكتب الامتداد مع النقطة مثل .png")
        return

    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == src_ext]
    if not files:
        print("لا توجد ملفات مطابقة.")
        return

    out_dir_name = input("مجلد الإخراج (افتراضي: Converted): ").strip() or "Converted"
    out_dir = folder / out_dir_name
    out_dir.mkdir(exist_ok=True)

    print(f"\nسيتم تحويل {len(files)} ملف إلى {dst_ext} داخل {out_dir.name}")
    if not confirm("تنفيذ التحويل؟ (y/n): "):
        print("تم الإلغاء.")
        return

    converted = 0
    for p in files:
        out_path = out_dir / (p.stem + dst_ext)
        try:
            with Image.open(p) as img:
                if dst_ext in {".jpg", ".jpeg"}:
                    img = img.convert("RGB")
                    img.save(out_path, quality=90)
                else:
                    img.save(out_path)
            converted += 1
        except Exception as exc:
            print(f"فشل تحويل {p.name}: {exc}")

    print(f"تم التحويل. عدد الملفات المحولة: {converted}")


def main() -> None:
    while True:
        print(
            "\n=== Automation Script ===\n"
            "1) إعادة تسمية ملفات (Batch Rename)\n"
            "2) دمج ملفات نصية (Merge Text)\n"
            "3) دمج ملفات CSV (Merge CSV)\n"
            "4) دمج ملفات PDF (Merge PDF) [يتطلب pypdf]\n"
            "5) تحويل صيغ صور (Convert Images) [يتطلب Pillow]\n"
            "0) خروج\n"
        )
        choice = input("اختر رقم: ").strip()

        if choice == "1":
            op_rename_files()
        elif choice == "2":
            op_merge_text_files()
        elif choice == "3":
            op_merge_csv_files()
        elif choice == "4":
            op_merge_pdfs()
        elif choice == "5":
            op_convert_images()
        elif choice == "0":
            break
        else:
            print("اختيار غير صحيح.")


if __name__ == "__main__":
    main()
