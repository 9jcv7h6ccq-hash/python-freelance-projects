import csv
from pathlib import Path
from typing import List


def read_csv(path: Path) -> tuple[List[str], list[list[str]]]:
    """قراءة CSV وإرجاع (رؤوس الأعمدة, الصفوف)."""
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return [], []
    header = rows[0]
    data = rows[1:]
    return header, data


def remove_empty_rows(header: List[str], rows: list[list[str]]) -> list[list[str]]:
    """حذف الصفوف التي تحتوي على قيمة فارغة في أي عمود."""
    cleaned: list[list[str]] = []
    for row in rows:
        # نعتبر الفراغ: نص فارغ أو مسافات فقط
        if all(col.strip() != "" for col in row):
            cleaned.append(row)
    return cleaned


def reorder_columns(header: List[str], rows: list[list[str]]) -> tuple[List[str], list[list[str]]]:
    """
    ترتيب الأعمدة أبجدياً حسب اسم العمود.
    يمكن مستقبلاً تعديلها ليكون الترتيب من إدخال المستخدم.
    """
    if not header:
        return header, rows

    # نبني فهرس من العمود إلى موقعه الجديد
    sorted_header = sorted(header)
    index_map = [header.index(col) for col in sorted_header]

    new_rows: list[list[str]] = []
    for row in rows:
        # نعيد ترتيب القيم حسب الترتيب الجديد للأعمدة
        new_row = [row[i] if i < len(row) else "" for i in index_map]
        new_rows.append(new_row)

    return sorted_header, new_rows


def write_csv(path: Path, header: List[str], rows: list[list[str]]) -> None:
    """كتابة البيانات إلى ملف CSV جديد."""
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(rows)


def main() -> None:
    print("=== CSV Data Cleaner ===")
    print("هذا البرنامج:")
    print("- يقرأ ملف CSV")
    print("- يحذف الصفوف التي تحتوي على قيم فارغة")
    print("- يرتب الأعمدة أبجديًا حسب اسم العمود")
    print("- يحفظ ملف CSV نظيف\n")

    input_name = input("اكتب اسم ملف CSV المراد تنظيفه (مثال: data.csv): ").strip()
    if not input_name:
        print("لم يتم إدخال اسم ملف.")
        return

    input_path = Path(input_name).expanduser().resolve()
    if not input_path.exists():
        print(f"الملف غير موجود: {input_path}")
        return

    header, rows = read_csv(input_path)
    if not header and not rows:
        print("الملف فارغ أو غير صالح.")
        return

    print(f"عدد الصفوف قبل التنظيف: {len(rows)}")
    rows = remove_empty_rows(header, rows)
    print(f"عدد الصفوف بعد حذف الفارغة: {len(rows)}")

    header, rows = reorder_columns(header, rows)
    print(f"تم ترتيب الأعمدة: {', '.join(header)}")

    default_output = input_path.with_name(input_path.stem + "_clean.csv")
    output_name = input(f"اسم ملف الإخراج (افتراضي: {default_output.name}): ").strip()
    if output_name:
        output_path = input_path.with_name(output_name)
    else:
        output_path = default_output

    write_csv(output_path, header, rows)
    print(f"\nتم حفظ الملف النظيف في: {output_path}")


if __name__ == "__main__":
    main()
