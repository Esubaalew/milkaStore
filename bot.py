from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# Initialize the bot with your token
bot_token = '7543719732:AAH8cIPr_xv9oaxtzw21EmnDd0LhJXVfCPs'


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    product_id = 2  # Example product ID (this should be dynamic for each product)

    # Create the WebApp URL with the product_id as a query parameter
    webapp_url = f"https://apiorderbot.onrender.com/api/webapp/?product_id={product_id}"

    # Create a button to launch the WebApp
    keyboard = [
        [InlineKeyboardButton(text="Order Now", web_app=WebAppInfo(url=webapp_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the WebApp button to the user
    await update.message.reply_text(
        text="Check out this amazing product! Click the button below to order.",
        reply_markup=reply_markup
    )

    # Send the message with the WebApp button to the channel
    channel_id = "-1002437698028"  # Your Telegram channel ID
    try:
        await context.bot.send_message(
            chat_id=channel_id,
            text="Check out this amazing product! Click the button below to order.",
            reply_markup=reply_markup
        )
    except Exception as e:
        # Detailed error handling
        print(f"Error sending message to channel: {e}")
        if 'Button_type_invalid' in str(e):
            print("Button type invalid. Check the WebApp button configuration.")


# Create the Application and add the command handler
application = Application.builder().token(bot_token).build()

# Add the command handler
application.add_handler(CommandHandler("start", start))

# Start the bot
application.run_polling()
