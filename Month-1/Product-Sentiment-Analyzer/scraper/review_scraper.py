from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time


# -----------------------------
# Chrome Setup
# -----------------------------

options = Options()

driver = webdriver.Chrome(options=options)

reviews_data = []

try:

    # -----------------------------
    # STEP 1: Open Amazon Search
    # -----------------------------

    print("Starting Chrome...")

    search_url = "https://www.amazon.in/s?k=wireless+headphones"

    driver.get(search_url)

    time.sleep(5)

    print("Page title:", driver.title)

    # -----------------------------
    # STEP 2: Find Product Cards
    # -----------------------------

    products = driver.find_elements(
        By.CSS_SELECTOR,
        "div[data-component-type='s-search-result']"
    )

    print("Products found:", len(products))

    product_list = []

    # -----------------------------
    # STEP 3: Collect ASIN + Name
    # -----------------------------

    for product in products[:5]:

        asin = product.get_attribute("data-asin")

        if not asin:
            continue

        try:
            product_name = product.find_element(
                By.CSS_SELECTOR,
                "h2"
            ).text.strip()

        except:
            product_name = "Unknown Product"

        product_list.append({
            "asin": asin,
            "product": product_name
        })


    print("\nProducts collected:")
    print("-" * 50)

    for item in product_list:
        print(
            "Product:",
            item["product"][:60]
        )
        print(
            "ASIN:",
            item["asin"]
        )


    # -----------------------------
    # STEP 4: Open Review Pages
    # -----------------------------

    for item in product_list:

        product_name = item["product"]
        asin = item["asin"]

        print("\n======================================")
        print("Product:", product_name)
        print("ASIN:", asin)
        print("======================================")

        review_url = (
            f"https://www.amazon.in/product-reviews/"
            f"{asin}/?reviewerType=all_reviews"
        )

        print("Opening review page...")

        driver.get(review_url)

        time.sleep(5)

        print("Page title:", driver.title)
        print("Current URL:", driver.current_url)

        # -----------------------------
        # STEP 5: Find Reviews
        # -----------------------------

        reviews = driver.find_elements(
            By.CSS_SELECTOR,
            "span[data-hook='review-body']"
        )

        print("Reviews found:", len(reviews))

        # -----------------------------
        # STEP 6: Save Reviews
        # -----------------------------

        for review in reviews[:5]:

            review_text = review.text.strip()

            if review_text:

                reviews_data.append({
                    "product": product_name,
                    "asin": asin,
                    "review": review_text
                })


finally:

    driver.quit()

    print("\nBrowser closed.")


# -----------------------------
# STEP 7: Create DataFrame
# -----------------------------

df = pd.DataFrame(reviews_data)


# -----------------------------
# STEP 8: Save CSV
# -----------------------------

df.to_csv(
    "data/scraped_reviews.csv",
    index=False
)


print("\n======================================")
print("REVIEW SCRAPING COMPLETED")
print("======================================")

print("Total reviews collected:", len(df))


if len(df) > 0:

    print("\nCollected Reviews:")
    print(df)

else:

    print("\nNo reviews were collected.")