# 🛒 Price Tracker Web App

A **Flask-based price comparison and product tracking web application** that searches for products across **Croma and Flipkart**, extracts real-time product information, and displays the results in a simple comparison interface.

The application uses **Playwright** for Croma scraping and **Selenium with Undetected ChromeDriver** for Flipkart scraping. Both websites are scraped concurrently to reduce the overall search time.

---

## 🚀 Features

* 🔎 Search for products by name
* 🛍️ Compare products from **Croma and Flipkart**
* 💰 Extract product prices
* 🖼️ Display product images
* 🔗 Provide direct product links
* ⚡ 5-minute result caching
* 🚀 Parallel scraping using multiprocessing
* 🌐 Flask-based web interface
* 🎭 Playwright-based Croma scraper
* 🤖 Selenium + Undetected ChromeDriver for Flipkart
* 🛡️ Handles scraper failures without crashing the application

---

## 🏗️ Project Architecture

```text
                         ┌─────────────────┐
                         │      User       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Flask Web App   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Search / Cache │
                         └────────┬────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
           ┌─────────────────┐        ┌─────────────────┐
           │    Flipkart     │        │      Croma      │
           │    Selenium     │        │    Playwright   │
           └────────┬────────┘        └────────┬────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Product Results │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Results Page    │
                         └─────────────────┘
```

---

## 🧰 Technologies Used

| Technology              | Purpose                   |
| ----------------------- | ------------------------- |
| Python                  | Core programming language |
| Flask                   | Web application backend   |
| Playwright              | Croma web scraping        |
| Selenium                | Flipkart web scraping     |
| Undetected ChromeDriver | Browser automation        |
| Multiprocessing         | Parallel execution        |
| HTML/CSS                | Frontend                  |
| Jinja2                  | Dynamic HTML rendering    |

---

## 📂 Project Structure

```text
Price-Tracker/
│
├── app.py
│
├── templates/
│   ├── index.html
│   └── results.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
│
├── requirements.txt
│
└── README.md
```

---

## ⚙️ How It Works

### 1. User enters a product

The user enters a product name in the search form.

Example:

```text
iPhone 15
```

The request is sent to:

```text
POST /track
```

---

### 2. Cache is checked

Before scraping, the application checks whether the product already exists in the cache.

```python
cached = get_from_cache(product)
```

The cache expiration time is:

```python
CACHE_EXPIRY = 300
```

which equals **5 minutes**.

If a valid cached result exists, the application immediately displays it without scraping again.

---

### 3. Parallel scraping

If the product is not cached, two processes are started:

```python
p1 = Process(
    target=run_scraper,
    args=(get_flipkart_live, product, return_dict, "flipkart")
)

p2 = Process(
    target=run_scraper,
    args=(get_croma_playwright, product, return_dict, "croma")
)
```

This allows Croma and Flipkart to be scraped concurrently.

---

### 4. Croma scraping

Croma is accessed using Playwright.

The scraper:

1. Opens Croma.
2. Finds the search box.
3. Enters the product name.
4. Searches for the product.
5. Waits for product results.
6. Extracts the first product.
7. Returns the product information.

The extracted information includes:

```python
{
    "title": title,
    "price": price,
    "image": image,
    "link": link
}
```

---

### 5. Flipkart scraping

Flipkart is accessed using Selenium and Undetected ChromeDriver.

The scraper:

1. Opens the Flipkart search page.
2. Searches for the requested product.
3. Waits for the product result.
4. Extracts the first matching product.
5. Retrieves its title, price, image, and URL.

---

### 6. Results are displayed

The final results are passed to:

```text
results.html
```

The user can then compare the available products.

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/price-tracker.git
cd price-tracker
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

```bash
playwright install
```

---

## 📄 requirements.txt

Example:

```text
Flask
playwright
selenium
undetected-chromedriver
```

You can generate the complete requirements file using:

```bash
pip freeze > requirements.txt
```

---

## ▶️ Running the Application

Start the Flask server:

```bash
python app.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000/
```

Open the URL in your browser and search for a product.

---

## 💡 Example

Search:

```text
Samsung Galaxy S24
```

The application searches:

```text
             Samsung Galaxy S24
                     │
             ┌───────┴───────┐
             ▼               ▼
         Flipkart          Croma
             │               │
             ▼               ▼
          Price            Price
          Image            Image
          Link             Link
             └───────┬───────┘
                     ▼
              Comparison Page
```

---

## ⚡ Performance Optimization

The application uses two main techniques to improve performance.

### Caching

Results are cached for 5 minutes:

```python
CACHE_EXPIRY = 300
```

This prevents repeated scraping for the same product.

### Multiprocessing

Croma and Flipkart scraping run independently:

```text
Process 1 → Flipkart
Process 2 → Croma
```

Therefore, the application does not need to completely finish scraping one website before starting the other.

---

## 🛠️ Error Handling

The scrapers use exception handling so that failures on one website do not terminate the entire application.

For example:

```python
try:
    ...
except Exception as e:
    print("CROMA ERROR:", e)
    return None
```

If a product cannot be found, the corresponding result can be returned as `None`.

---

## 🔮 Future Improvements

* [ ] Add Amazon support
* [ ] Add price history tracking
* [ ] Store prices in a database
* [ ] Create price-history graphs
* [ ] Add automatic price-drop notifications
* [ ] Add email notifications
* [ ] Add user accounts
* [ ] Add product watchlists
* [ ] Schedule automatic price checks
* [ ] Add multiple product results instead of only the first result
* [ ] Improve product matching between websites
* [ ] Add REST API using FastAPI
* [ ] Deploy the application to a cloud platform
* [ ] Add database support using PostgreSQL/MySQL

---

## ⚠️ Important Notes

This project relies on website structures and CSS selectors. If Croma or Flipkart changes its webpage structure, the scraping selectors may need to be updated.

For example:

```python
"input#searchV2"
```

and:

```python
"li.product-item"
```

are dependent on the current webpage structure.

The project should also be used responsibly and in accordance with the terms and policies of the websites being accessed.

---

## 🎓 Project Purpose

This project was developed to demonstrate practical skills in:

* Web development
* Python programming
* Flask
* Web scraping
* Browser automation
* Multiprocessing
* Caching
* Data extraction
* Frontend/backend integration

It is particularly useful as a **Python + Flask + Web Scraping portfolio project**.

---

## 👨‍💻 Author

**Krishna Verma**

B.Tech CSE — AI & Robotics

---

## ⭐ If You Like This Project

If this project helped you learn something, consider giving the repository a ⭐ on GitHub.
