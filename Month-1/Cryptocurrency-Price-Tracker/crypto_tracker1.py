from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime
import os
import time
options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

file_name = "crypto_prices.csv"
if not os.path.exists(file_name):
    pd.DataFrame(columns=[
        "Time",
        "Name",
        "Symbol",
        "Price",
        "24h Change",
        "Market Cap"
    ]).to_csv(file_name, index=False)
while True:

    print("\nCollecting cryptocurrency prices...")
    driver.get("https://coinmarketcap.com/")

    time.sleep(5)
    rows = driver.find_elements("css selector", "table tbody tr")

    data = []
    for row in rows[1:11]:

        try:
            text = row.text.split("\n")

            name = text[1]
            symbol = text[2]
            price = text[4]

            changes = text[5].split()
            change_24h = changes[0]

            market_cap = text[6]

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            data.append({
                "Time": timestamp,
                "Name": name,
                "Symbol": symbol,
                "Price": price,
                "24h Change": change_24h,
                "Market Cap": market_cap
            })

        except Exception:
            continue
    df = pd.DataFrame(data)
    if not df.empty:
        df.to_csv(
            file_name,
            mode="a",
            header=False,
            index=False
        )

        print("Data saved successfully!")
        print(df[[
            "Name",
            "Symbol",
            "Price",
            "24h Change"
        ]])
    print("\nNext update in 30 seconds...")
    time.sleep(30)