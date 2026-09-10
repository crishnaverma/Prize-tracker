from flask import Flask, request, render_template
from playwright.sync_api import sync_playwright
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from multiprocessing import Process, Manager

app = Flask(__name__)


CACHE = {}         
CACHE_EXPIRY = 300 


def get_from_cache(product_name):
    if product_name in CACHE:
        data, saved_time = CACHE[product_name]
        if (time.time() - saved_time) < CACHE_EXPIRY:
            print("⚡ Returning cached result:", product_name)
            return data
        else:
            del CACHE[product_name]  # Expired
    return None


def save_to_cache(product_name, data):
    CACHE[product_name] = (data, time.time())



_play = sync_playwright().start()

_prebrowser = _play.chromium.launch(
    headless=False,
    args=[
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox"
    ]
)



def get_croma_playwright(product_name):

    # PRELOAD: reuse same browser instance
    context = _prebrowser.new_context()
    page = context.new_page()

    try:
        page.goto("https://www.croma.com/", timeout=60000)

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
            context.close()
            return None

        page.fill(search_selector, product_name)
        page.keyboard.press("Enter")

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
            context.close()
            return None

        #  Reduced scroll time → instant lazy-load trigger
        page.evaluate("window.scrollBy(0, 2500)")  
        time.sleep(0.3)

        product = page.query_selector(product_selector)
        if not product:
            context.close()
            return None

        title = product.query_selector("h3.product-title").inner_text().strip()
        price = product.query_selector("span.amount").inner_text().strip()
        image = product.query_selector("img").get_attribute("src")
        link = product.query_selector("a").get_attribute("href")

        if link.startswith("/"):
            link = "https://www.croma.com" + link

        context.close()

        return {
            "title": title,
            "price": price,
            "image": image,
            "link": link
        }

    except Exception as e:
        print("CROMA ERROR:", e)
        context.close()
        return None




def get_flipkart_live(product_name):
    driver = None
    try:
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = uc.Chrome(options=options)

        url = "https://www.flipkart.com/search?q=" + product_name.replace(" ", "+")
        driver.get(url)

        title_el = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-7-12 div"))
        )

        card = title_el.find_element(By.XPATH, "./ancestor::a")

        title = title_el.text.strip()
        link = card.get_attribute("href")

        try:
            price = card.find_element(By.CSS_SELECTOR, "div.col-5-12.mao5dl div").text
        except:
            price = "N/A"

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




def run_scraper(func, product, return_dict, key):
    try:
        return_dict[key] = func(product)
    except:
        return_dict[key] = None




@app.route("/")
def home():
    return render_template("index.html")


@app.route("/track", methods=["POST"])
def track():
    product = request.form["content"].strip()


    cached = get_from_cache(product)
    if cached:
        return render_template(
            "results.html",
            product=product,
            flipkart=cached["flipkart"],
            croma=cached["croma"]
        )


    with Manager() as manager:
        return_dict = manager.dict()

        p1 = Process(target=run_scraper, args=(get_flipkart_live, product, return_dict, "flipkart"))
        p2 = Process(target=run_scraper, args=(get_croma_playwright, product, return_dict, "croma"))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        flipkart = return_dict.get("flipkart")
        croma = return_dict.get("croma")

        # Save in cache
        save_to_cache(product, {
            "flipkart": flipkart,
            "croma": croma
        })

    return render_template(
        "results.html",
        product=product,
        flipkart=flipkart,
        croma=croma
    )


if __name__ == "__main__":
    app.run(debug=True)
