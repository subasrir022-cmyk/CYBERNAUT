from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


options = Options()

driver = webdriver.Chrome(options=options)

try:
    print("Starting Chrome...")

    driver.get("https://www.amazon.in/s?k=wireless+headphones")

    time.sleep(5)

    print("Page title:", driver.title)

    # Find product cards
    products = driver.find_elements(
        By.CSS_SELECTOR,
        "div[data-component-type='s-search-result']"
    )

    print("\nProducts Found:", len(products))
    print("-" * 50)

    for i, product in enumerate(products[:10], start=1):

        try:
            name = product.find_element(
                By.CSS_SELECTOR,
                "h2 span"
            ).text

        except:
            name = "Name not found"

        try:
            price = product.find_element(
                By.CSS_SELECTOR,
                "span.a-price-whole"
            ).text

        except:
            price = "Price not found"

        print(f"{i}. {name}")
        print(f"   Price: ₹{price}")
        print()

finally:
    driver.quit()
    print("Browser closed.")