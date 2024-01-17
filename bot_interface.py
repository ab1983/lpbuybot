import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import database_manager
import eth_chain_interaction

# Define conversation states
TOKEN_ADDRESS, CONFIRM_PAIR, LIQUIDITY_AMOUNT, LOCK_PERIOD, RECEIVE_ETH_ADDRESS = range(5)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text('Welcome! Please provide your token contract address.')
    return TOKEN_ADDRESS

def token_address(update, context):
    token_address = update.message.text
    pair_details = eth_chain_interaction.get_lp_token_details(token_address)

    if pair_details is None or 'error' in pair_details:
        update.message.reply_text('An error occurred. Please try again.')
        return TOKEN_ADDRESS
    else:
        context.user_data['token_address'] = token_address
        context.user_data['pair_details'] = pair_details
        pair_text = f"{pair_details['token0']}/{pair_details['token1']} LP Pair found. Confirm?"
        keyboard = [[InlineKeyboardButton("Confirm", callback_data='confirm'), InlineKeyboardButton("Cancel", callback_data='cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(pair_text, reply_markup=reply_markup)
        return CONFIRM_PAIR

def confirm_pair(update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'confirm':
        query.edit_message_text(text="Confirmed. Please enter the initial liquidity pool amount in ETH.")
        return LIQUIDITY_AMOUNT
    else:
        query.edit_message_text(text="Operation cancelled. Start over by sending /start.")
        return ConversationHandler.END

def liquidity_amount(update, context):
    lp_amount = update.message.text
    if lp_amount.replace('.', '', 1).isdigit() and float(lp_amount) > 0:
        context.user_data['liquidity_amount'] = lp_amount
        update.message.reply_text('Please enter the lock period in months.')
        return LOCK_PERIOD
    else:
        update.message.reply_text('Invalid amount. Please enter a valid number.')
        return LIQUIDITY_AMOUNT

def lock_period(update, context):
    lock_period = update.message.text
    if lock_period.isdigit() and int(lock_period) > 0:
        context.user_data['lock_period'] = lock_period
        update.message.reply_text('Enter the Ethereum address where you want to receive ETH.')
        return RECEIVE_ETH_ADDRESS
    else:
        update.message.reply_text('Invalid period. Please enter a valid number of months.')
        return LOCK_PERIOD

def receive_eth_address(update, context):
    eth_address = update.message.text
    if eth_chain_interaction.web3.isAddress(eth_address):
        context.user_data['eth_address'] = eth_address
        # Send proposal via Telegram DM (implementation depends on your proposal logic)
        update.message.reply_text(f'Proposal sent to your DM. Please check and accept if you agree.')
        # Logic to send proposal and handle user's response (acceptance)
        return ConversationHandler.END
    else:
        update.message.reply_text('Invalid Ethereum address. Please enter a valid address.')
        return RECEIVE_ETH_ADDRESS

def cancel(update, context):
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

def main():
    TOKEN = '6852482709:AAHRTuYXLy0puNqklIkwSvZpgicibSKOPwE'
    updater = Updater(TOKEN, use_context=True)
    print(f"Bot Token: {TOKEN}")  # For debugging; remove in production
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TOKEN_ADDRESS: [MessageHandler(filters.text, token_address)],
            CONFIRM_PAIR: [CallbackQueryHandler(confirm_pair)],
            LIQUIDITY_AMOUNT: [MessageHandler(filters.text, liquidity_amount)],
            LOCK_PERIOD: [MessageHandler(filters.text, lock_period)],
            RECEIVE_ETH_ADDRESS: [MessageHandler(filters.text, receive_eth_address)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
