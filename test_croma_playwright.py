from flask import Flask, request, render_template
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import urljoin


app = Flask(__name__)


# =====================================================================
#                           CROMA SCRAPER (PLAYWRIGHT)
# =====================================================================
def get_croma_playwright(product_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,   # IMPORTANT: Croma blocks headless mode
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]
        )

        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto("https://www.croma.com/", timeout=60000)

            # Search box possible selectors
            search_selectors = [
                "input#searchV2",
                "input[type='search']",
                "input[placeholder*='Search']",
                "input.search-input"
            ]

            search_selector = None
            for sel in search_selectors:
                try:
                    page.wait_for_selector(sel, timeout=4000)
                    if page.is_visible(sel):
                        search_selector = sel
                        break
                except:
                    continue

            if not search_selector:
                browser.close()
                return None

            # Type and search
            page.fill(search_selector, product_name)
            page.keyboard.press("Enter")

            # Product selectors
            product_selectors = [
                "li.product-item",
                "div.product__list__item",
                ".product-card"
            ]

            product_selector = None
            for sel in product_selectors:
                try:
                    page.wait_for_selector(sel, timeout=60000)
                    product_selector = sel
                    break
                except:
                    continue

            if not product_selector:
                browser.close()
                return None

            # Scroll for lazy-loaded images
            for _ in range(10):
                page.mouse.wheel(0, 1500)
                time.sleep(0.2)

            product = page.query_selector(product_selector)
            if not product:
                browser.close()
                return None

            title = product.query_selector("h3.product-title").inner_text().strip()
            price = product.query_selector("span.amount").inner_text().strip()
            image = product.query_selector("img").get_attribute("src")

            link = product.query_selector("a").get_attribute("href")
            if link.startswith("/"):
                link = "https://www.croma.com" + link

            browser.close()

            return {
                "title": title,
                "price": price,
                "image": image,
                "link": link
            }

        except:
            browser.close()
            return None



# =====================================================================
#                           FLIPKART SCRAPER (SELENIUM)
def get_flipkart_live(product_name):
    driver = None
    try:
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # REMOVE headless for reliability
        # options.add_argument("--headless=new")

        driver = uc.Chrome(options=options)

        url = "https://www.flipkart.com/search?q=" + product_name.replace(" ", "+")
        driver.get(url)

        # NEW SELECTORS BASED ON YOUR SCREENSHOT
        title_el = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div.col-7-12 div"
            ))
        )

        # product card (ancestor <a>)
        card = title_el.find_element(By.XPATH, "./ancestor::a")

        title = title_el.text.strip()
        link = card.get_attribute("href")

        # PRICE
        try:
            price = card.find_element(By.CSS_SELECTOR, "div.col-5-12.mao5dl div").text
        except:
            price = "N/A"

        # IMAGE
        try:
            image = card.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
        except:
            image = None

        driver.quit()

        return {
            "title": title,
            "price": price,
            "image": image,
            "link": link
        }

    except Exception as e:
        print("FLIPKART ERROR:", e)
        if driver:
            try:
                driver.quit()
            except:
                pass
        return None




# =====================================================================
#                           FLASK ROUTES
# =====================================================================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/track", methods=["POST"])
def track():
    product = request.form["content"].strip()

    flipkart = get_flipkart_live(product)
    croma = get_croma_playwright(product)

    return render_template(
        "results.html",
        product=product,
        flipkart=flipkart,
        croma=croma
    )


if __name__ == "__main__":
    app.run(debug=True)