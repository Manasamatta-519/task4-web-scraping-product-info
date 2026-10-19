"""
SkillCraft Technology Internship - Task 4
Web scraping product information and saving it to CSV.

Website: https://books.toscrape.com/
Educational practice website.
"""

import csv
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

START_URL = "https://books.toscrape.com/"
OUTPUT_FILE = "products.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LearningWebScraper/1.0)"
}

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def scrape_products():
    """Scrape product information from all listing pages."""
    page_url = START_URL
    products = []

    while page_url:
        print("Scraping:", page_url)

        response = requests.get(page_url, headers=HEADERS, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        product_cards = soup.select("article.product_pod")

        for card in product_cards:
            title_link = card.select_one("h3 a")
            price_element = card.select_one(".price_color")
            rating_element = card.select_one("p.star-rating")
            availability_element = card.select_one(".availability")

            if not title_link or not price_element:
                continue

            title = title_link.get("title", title_link.get_text(strip=True))
            product_url = urljoin(page_url, title_link.get("href", ""))

            rating_class = ""
            if rating_element:
                classes = rating_element.get("class", [])
                rating_class = next(
                    (name for name in classes if name != "star-rating"),
                    ""
                )

            availability = (
                " ".join(availability_element.get_text(" ", strip=True).split())
                if availability_element else "Not listed"
            )

            products.append({
                "product_name": title,
                "price": price_element.get_text(strip=True),
                "rating": RATING_MAP.get(rating_class, "Not listed"),
                "availability": availability,
                "product_url": product_url,
            })

        # Find the next page, if one exists.
        next_link = soup.select_one("li.next a")
        if next_link:
            page_url = urljoin(page_url, next_link.get("href", ""))
            time.sleep(0.5)  # Small pause between page requests.
        else:
            page_url = None

    return products


def save_to_csv(products):
    """Write product records to a CSV file."""
    fieldnames = [
        "product_name",
        "price",
        "rating",
        "availability",
        "product_url",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)


def main():
    try:
        products = scrape_products()
        save_to_csv(products)
        print(f"\nCompleted successfully!")
        print(f"Products saved: {len(products)}")
        print(f"CSV file: {OUTPUT_FILE}")
    except requests.RequestException as error:
        print("A network or website request error occurred:", error)
        print("Check your internet connection and try again.")
    except OSError as error:
        print("Could not save the CSV file:", error)


if __name__ == "__main__":
    main()
