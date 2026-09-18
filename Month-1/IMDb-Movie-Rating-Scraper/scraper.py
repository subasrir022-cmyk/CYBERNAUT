from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json
import time
import re
HEADLESS_MODE = False
options = Options()
options.add_argument("--start-maximized")

if HEADLESS_MODE:
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

print("Chrome started successfully!")
driver.get("https://www.imdb.com/chart/top/")

print("IMDb page opened!")
time.sleep(8)
if not HEADLESS_MODE:
    input(
        "Complete IMDb verification in Chrome, "
        "then press ENTER here..."
    )
    print("Verification completed!")
else:
    print("Headless mode ON - skipping manual verification step.")

print("Current page title:", driver.title)

time.sleep(3)
script = """
return JSON.stringify(
    Array.from(
        document.querySelectorAll(
            'li.ipc-metadata-list-summary-item'
        )
    ).map(function(movie) {

        var text = movie.innerText;
        var rankMatch = text.match(
            /#(\\d+)/
        );

        var rank = rankMatch
            ? parseInt(rankMatch[1])
            : null;
        var title = "";

        var titleElement = movie.querySelector(
            'h3.ipc-title__text'
        );

        if (titleElement) {

            title = titleElement.innerText
                .replace(/^\\d+\\.\\s*/, "")
                .trim();
        } else {

            var titleLink = movie.querySelector(
                'a.ipc-title-link-wrapper'
            );

            if (titleLink) {

                title = titleLink.innerText
                    .replace(/^\\d+\\.\\s*/, "")
                    .trim();
            }
        }
        var year = null;

        var allElements = movie.querySelectorAll(
            '*'
        );

        for (
            var i = 0;
            i < allElements.length;
            i++
        ) {

            var elementText =
                allElements[i].textContent.trim();

            if (
                /^(19|20)\\d{2}$/.test(
                    elementText
                )
            ) {

                year = parseInt(elementText);

                break;
            }
        }
        var rating = null;

        var ratingElement = movie.querySelector(
            'span.ipc-rating-star--rating'
        );

        if (ratingElement) {

            rating = parseFloat(
                ratingElement.textContent.trim()
            );
        }
        return {
            rank: rank,
            title: title,
            year: year,
            rating: rating
        };

    })
);
"""
result = driver.execute_script(script)
movie_data = json.loads(result)


print(
    "Number of movies extracted:",
    len(movie_data)
)
driver.quit()

print("Browser closed!")
df = pd.DataFrame(movie_data)
df.to_csv(
    "imdb_movies.csv",
    index=False
)

print("CSV file created successfully!")

print(
    "Total movies saved:",
    len(df)
)
print("\nFirst 5 movies:")

print(df.head())



#python scraper.py