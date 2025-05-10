import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Set up your Telegram Bot Token
BOT_TOKEN = "7995739639:AAHwFkfjrh6-RZTCBV793imNmMDe6hn-GGo"  # Replace with your actual Telegram Bot Token

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ScraperAPI key (replace with your actual key)
API_KEY = "your-scraperapi-key-here"  # Replace with your ScraperAPI key
BASE_URL = "http://api.scraperapi.com"

# Function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a product category (e.g. 'led bulb') and I'll fetch IndiaMART products for you!")

# Function to handle incoming messages and scrape products
async def fetch_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text(f"🔍 Scraping IndiaMART for: {query}...")

    # ScraperAPI request parameters
    params = {
        'api_key': c92b09864c1f30d7ae51295c6812cce2,  # Your ScraperAPI key
        'url': f'https://dir.indiamart.com/search.mp?ss={query.replace(" ", "+")}',  # IndiaMART search URL
    }

    try:
        # Make the request through ScraperAPI
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Check for HTTP errors
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"⚠️ Error occurred while fetching data: {e}")
        return

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find product cards using the appropriate CSS selectors
    product_cards = soup.select(".prd-listing, .product-info, .r-cl")
    
    if not product_cards:
        await update.message.reply_text("⚠️ No product cards found. Please check the page structure or try again later.")
        return
    
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
        await update.message.reply_text("⚠️ No products found for your search.")
        return

    # Create a DataFrame and save it as a CSV
    df = pd.DataFrame(product_data, columns=["Product Name", "Price", "Link"])
    file_path = f"{query.replace(' ', '_')}_indiamart.csv"
    df.to_csv(file_path, index=False)

    # Send the CSV file to the user
    await update.message.reply_document(InputFile(file_path))

# Main function to set up the bot and run the handlers
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_products))
    print("✅ Bot is running...")
    app.run_polling()

# Run the bot
if __name__ == "__main__":
    main()
    
