import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Sample list of proxies (Add as many as you like)
PROXIES = [
    "http://username:password@proxy1.com:8080",
    "http://username:password@proxy2.com:8080",
    "http://username:password@proxy3.com:8080",
    "http://username:password@proxy4.com:8080",
    "http://username:password@proxy5.com:8080",
    "http://username:password@proxy6.com:8080",
    "http://username:password@proxy7.com:8080",
    "http://username:password@proxy8.com:8080",
    "http://username:password@proxy9.com:8080",
    "http://username:password@proxy10.com:8080",
    "http://username:password@proxy11.com:8080",
    "http://username:password@proxy12.com:8080",
    "http://username:password@proxy13.com:8080",
    "http://username:password@proxy14.com:8080",
    "http://username:password@proxy15.com:8080"
]

# User-agent randomizer
ua = UserAgent()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a product category (e.g. 'led bulb') and I'll fetch IndiaMART products for you!")

async def fetch_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text(f"🔍 Scraping IndiaMART for: {query}...")

    # Randomly select a proxy from the list
    proxy = random.choice(PROXIES)
    headers = {
        'User-Agent': ua.random  # Random user-agent
    }

    url = f"https://dir.indiamart.com/search.mp?ss={query.replace(' ', '+')}"
    
    # Use the proxy in the request
    response = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy})
    soup = BeautifulSoup(response.text, 'html.parser')

    product_cards = soup.select(".prd-listing, .product-info, .r-cl")
    product_data = []

    for card in product_cards:
        name_tag = card.select_one(".prd-name, .product-title, h2")
        price_tag = card.select_one(".price, .p-v, .price-info")
        link_tag = card.select_one("a")

        name = name_tag.get_text(strip=True) if name_tag else "N/A"
        price = price_tag.get_text(strip=True) if price_tag else "N/A"
        link = "https://www.indiamart.com" + link_tag['href'] if link_tag and link_tag.has_attr("href") else "N/A"

        if name != "N/A":
            product_data.append([name, price, link])

    if not product_data:
        await update.message.reply_text("⚠️ No products found. IndiaMART may have changed its structure or blocked scraping.")
        return

    df = pd.DataFrame(product_data, columns=["Product Name", "Price", "Link"])
    file_path = f"{query.replace(' ', '_')}_indiamart.csv"
    df.to_csv(file_path, index=False)

    await update.message.reply_document(InputFile(file_path))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_products))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
