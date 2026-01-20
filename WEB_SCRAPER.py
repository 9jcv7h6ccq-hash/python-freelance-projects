import csv
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"


@dataclass
class Product:
    title: str
    price: str
    availability: str
    url: str


def fetch_page(url: str) -> Optional[str]:
    """جلب صفحة HTML من الإنترنت."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        print(f"خطأ أثناء جلب الصفحة: {exc}")
        return None


def parse_products(html: str, page_url: str) -> List[Product]:
    """استخراج بيانات المنتجات (العنوان، السعر، الحالة، الرابط)."""
    soup = BeautifulSoup(html, "html.parser")
    products: List[Product] = []

    for article in soup.select("article.product_pod"):
        # العنوان
        a_tag = article.select_one("h3 a")
        if not a_tag:
            continue
        title = a_tag.get("title") or a_tag.get_text(strip=True)

        # السعر
        price_tag = article.select_one("p.price_color")
        price = price_tag.get_text(strip=True) if price_tag else ""

        # التوفر
        avail_tag = article.select_one("p.instock.availability")
        availability = avail_tag.get_text(strip=True) if avail_tag else ""

        # رابط المنتج (نسويها كاملة)
        href = a_tag.get("href", "")
        product_url = requests.compat.urljoin(page_url, href)

        products.append(Product(title=title, price=price, availability=availability, url=product_url))

    return products


def find_next_page(html: str, current_url: str) -> Optional[str]:
    """إرجاع رابط الصفحة التالية إن وجدت، وإلا None."""
    soup = BeautifulSoup(html, "html.parser")
    next_li = soup.select_one("li.next a")
    if not next_li:
        return None
    href = next_li.get("href", "")
    return requests.compat.urljoin(current_url, href)


def scrape_all_products(start_url: str) -> Iterable[Product]:
    """يتتبع جميع الصفحات ويجمع كل المنتجات."""
    current_url = start_url
    page_number = 1

    while current_url:
        print(f"جلب الصفحة {page_number}: {current_url}")
        html = fetch_page(current_url)
        if not html:
            break

        products = parse_products(html, current_url)
        print(f"عدد المنتجات في هذه الصفحة: {len(products)}")
        for p in products:
            yield p

        next_url = find_next_page(html, current_url)
        if not next_url or next_url == current_url:
            break

        current_url = next_url
        page_number += 1


def save_to_csv(products: Iterable[Product], filename: str) -> None:
    """حفظ البيانات في ملف CSV."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "price", "availability", "url"])
        count = 0
        for p in products:
            writer.writerow([p.title, p.price, p.availability, p.url])
            count += 1
    print(f"\nتم حفظ {count} منتج في الملف: {filename}")


def main() -> None:
    print("=== Web Scraping Script ===")
    print("سيتم سحب بيانات المنتجات (عنوان، سعر، توفر، رابط) من موقع تدريبي:")
    print(BASE_URL)
    print("ثم حفظها في ملف CSV.\n")

    filename = input("اكتب اسم ملف CSV (افتراضي: products.csv): ").strip()
    if not filename:
        filename = "products.csv"

    products = scrape_all_products(BASE_URL)
    save_to_csv(products, filename)


if __name__ == "__main__":
    main()
