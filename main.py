import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "7995739639:AAHwFkfjrh6-RZTCBV793imNmMDe6hn-GGo"

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a product category (e.g. 'led bulb') and I'll fetch IndiaMART products for you!")

async def fetch_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text(f"🔍 Scraping IndiaMART for: {query}...")

    url = f"https://dir.indiamart.com/search.mp?ss={query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    names = [tag.get_text(strip=True) for tag in soup.select(".prd-name")]
    prices = [tag.get_text(strip=True) for tag in soup.select(".price")]
    links = ['https://www.indiamart.com' + a['href'] for a in soup.select('.prd-name > a')]

    # Adjust lengths in case of mismatch
    length = min(len(names), len(prices), len(links))
    names, prices, links = names[:length], prices[:length], links[:length]

    if length == 0:
        await update.message.reply_text("⚠️ No products found. Try another category.")
        return

    df = pd.DataFrame({'Product Name': names, 'Price': prices, 'Link': links})
    file_path = f"{query.replace(' ', '_')}_indiamart.csv"
    df.to_csv(file_path, index=False)

    await update.message.reply_document(InputFile(file_path))

# Setup the bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_products))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
  
