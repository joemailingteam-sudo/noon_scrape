import asyncio
import csv
import json
from playwright.async_api import async_playwright


async def scrape_noon(query="ps5", output="csv", max_pages=2):
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            products = []

            for page_num in range(1, max_pages + 2):
                print(f"Scrape page {page_num}......")
                URL = f"www.noon.com"
                await page.goto(URL, wait_until="domcontentloaded", timeout=6000)

                # wait for products to loaded
                try:
                    await page.wait_for_selector(
                        "div._linkWrapper_1ts6x_1", timeout=10000
                    )
                except Exception:
                    print(f"No products found on page {page_num}. Ending escrape")
                    break

                product_elements = await page.query_selector_all(
                    "div._linkWrapper_1ts6x_1",
                )

                for product in product_elements:
                    try:
                        title_element = await product.query_selector("._title_i1yaq_19")
                        price_element = await product.query_selector(
                            "._amount_1o2w0_59"
                        )
                        rating_element = await product.query_selector(
                            "._textCtr_1r83y_16"
                        )
                        link_element = await product.get_attribute(
                            "a._productBoxLink_1ts6x_5"
                        )

                        title = (
                            await title_element.inner_text() if title_element else "N/A"
                        )

                        price = (
                            await price_element.inner_text() if price_element else "N/A"
                        )

                        rating = (
                            await rating_element.inner_text()
                            if rating_element
                            else "N/A"
                        )

                        link = (
                            await link_element.get_attribute("href")
                            if link_element
                            else "N/A"
                        )

                        if link != "N/A" and not link.startswith("http"):
                            link = f"https://www.noon.com{link}"

                        products.append(
                            {
                                "title": title.strip(),
                                "price": price.strip(),
                                "rating": rating.strip(),
                                "link": link.strip(),
                            }
                        )

                    except Exception as e:
                        print(f"Error extracting product data: {e}")
                        continue

                # Save Data

                file_name = f"{query}_products.{output}"

                if output == "csv":
                    with open(file_name, "w", newline="", encoding="utf-8") as file:
                        fieldnames = ["title", "price", "rating", "link"]
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(products)

                elif output == "json":
                    with open(file_name, "w", encoding="utf-8") as file:
                        json.dump(products, file, indent=4, ensure_ascii=False)

                print(
                    f"Succefully scraped {len(products)} products across pages data saven in {file_name}"
                )

            await browser.close()

        except Exception as e:
            print(f"An error occured: {e}")


asyncio.run(scrape_noon(query="ps5", output="csv", max_pages=2))
