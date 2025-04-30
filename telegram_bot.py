from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, filters, MessageHandler
from flight_search import AmadeusAPI
from data_manager import DataHandler

class TelegramBot:
    def __init__(self):

        self.token = os.getenv("TOKEN_BOT")
        self.button = InlineKeyboardButton
        self.app = ApplicationBuilder().token(f"{self.token}").build()
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [self.button("Search flight", callback_data= "search_flight")],
            [self.button("Flight_check", callback_data="flight_check")],
            [self.button("Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Hello, what do you want to do?", reply_markup=reply_markup)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "search_flight":
            await query.edit_message_text("Write the city to fly from: (only the city)")
            context.user_data["step"] = "awaiting_origin"
        elif query.data == "flight_check":
            await query.edit_message_text(text="Looking for cheap flight...")
            handler = DataHandler()
            message = handler.check_and_update_sheets()
            data = DataHandler().google_data()

            if message:
                for msg in message:
                    await query.edit_message_text(text=msg)
            else:
                for row in data:
                    if row["price"] != "":
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"No flight prices lower than expected."
                                                                                              f" but this is what we already found for you: "
                                                                                              f"from {row["origin"]} to {row["destination"]} - {row["price"]}")
        elif query.data == "help":
            await query.edit_message_text("Tell me the city you want to fly from and i will find some flight for you")

    async def handle_message(self, update: Update, contex: ContextTypes.DEFAULT_TYPE):
        current_step = contex.user_data.get("step")
        api = AmadeusAPI()
        if current_step == "awaiting_origin":
            contex.user_data["origin"] = update.message.text
            await update.message.reply_text("Where do you want to go? (only the city)")
            contex.user_data["step"] = "awaiting_destination"

        elif current_step == "awaiting_destination":
            contex.user_data["destination"] = update.message.text
            await update.message.reply_text("how much do you want to spend? (just the number)")
            contex.user_data["step"] = "awaiting_budget"

        elif current_step == "awaiting_budget":
            contex.user_data["budget"] = update.message.text
            await update.message.reply_text("When do you want to go? (format: YYYY-MM-DD")
            contex.user_data["step"] = "awaiting_date"

        elif current_step == "awaiting_date":
            contex.user_data["date"] = update.message.text
            origin = api.city_to_iata(city=contex.user_data["origin"])
            destination = api.city_to_iata(city=contex.user_data["destination"])
            budget = contex.user_data["budget"]
            date = contex.user_data["date"]
            response = api.make_request(origin=origin,destination=destination,maxprice=budget,departure_date=date)
            i = response["data"][0]["itineraries"][0]["segments"][0]
            await update.message.reply_text(f"This is what i found: Flight from {i["departure"]["iataCode"]} to {i["arrival"]["iataCode"]} for"
                                            f"{response["data"][0]["price"]["total"]}{response["data"][0]["price"]["currency"]}")

    def run(self):
        self.app.run_polling()
