from telegram.ext import (
    commands,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)
import telegram

from collections import deque
import datetime
import logging
import guesslang
from pygments.lexers import get_lexer_by_name, guess_lexer, ClassNotFound

import config
from utils.bot import Bot
from utils.code import Code
from utils.utils import generate_image, build_menu


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


description = """
Hi! I'm a bot that will highlight code for you.

Just use /code with some code, and I'll try to detect a language and highlight it.
You can optionally specify a language before the code.
"""

bot = Bot(token=config.token, description=description, owner_ids=[1389169565])

bot.code_cache = deque(maxlen=500)
# chat_id: Code
bot.ongoing_changes = {}

LANGUAGE = 0


# Creating a predefined button list
buttons = [
    telegram.InlineKeyboardButton("Change Language", callback_data="change_lang")
]
change_lang_markup = telegram.InlineKeyboardMarkup(build_menu(buttons, n_cols=1))


# Adding the callback query handler for the "Change Language" button
def button(update, context):
    query = update.callback_query

    if update.effective_chat.id in bot.ongoing_changes:
        query.answer(
            "You can only change once language at once.", show_alert=True
        )
        return ConversationHandler.END

    if update.effective_chat.type != "private":
        query.answer(
            "Sorry, that option is unavailable for this message.", show_alert=True
        )
        return ConversationHandler.END

    code = None

    for _code in bot.code_cache:
        if _code.message_id == update.effective_message.message_id:
            code = _code

    if not code:
        query.answer(
            "Sorry, that option is no longer available for this message.",
            show_alert=True,
        )
        return ConversationHandler.END

    query.answer()
    update.effective_message.reply_text("Please enter a new language")

    bot.ongoing_changes[update.effective_chat.id] = code

    return LANGUAGE


def change_language(update, context):
    code = bot.ongoing_changes.pop(update.effective_chat.id)

    if not code:
        update.message.reply_text("Sorry, an unexpected error occured.")
        return ConversationHandler.END

    text = update.message.text

    try:
        lexer = get_lexer_by_name(text, stripall=True)
        language = lexer.name
    except ClassNotFound:
        update.message.reply_text("Unrecognized language. Sorry.")
        return ConversationHandler.END

    file = generate_image(code.code, lexer)

    update.message.reply_photo(
        photo=file, caption=f"Language: {language}", reply_markup=change_lang_markup
    )

    code.language = language
    bot.code_cache.append(code)

    return ConversationHandler.END


callback_query_handler = CallbackQueryHandler(button)
conv_handler = ConversationHandler(
    entry_points=[callback_query_handler],
    states={LANGUAGE: [MessageHandler(Filters.text, change_language)],},
    fallbacks=[],
)

bot.dispatcher.add_handler(conv_handler)


guesser = guesslang.Guess()


@bot.command(
    aliases=["codeblock"],
    examples=[
        "py print('Hello World!')",
        "import random\nfor i in range(5):\nprint(random.choice('yes', 'no'))",
    ],
)
def code(ctx, *, body):
    """Highlight code and send it in chat

    You can optionally specify a language, or let me detect it.
    """
    words = body.split()
    first_word = words[0]
    detected = False

    # Attempt to get the language of the code
    try:
        lexer = get_lexer_by_name(first_word, stripall=True)
        language = lexer.name
        body = body[len(first_word) :]
    except ClassNotFound:
        language = guesser.language_name(body)
        try:
            lexer = get_lexer_by_name(language, stripall=True)
            detected = True
        except ClassNotFound:
            try:
                lexer = guess_lexer(body)
                language = lexer.name
                detected = True
            except ClassNotFound:
                ctx.send("Sorry, could not detect language.")
                return

    file = generate_image(body, lexer)

    if ctx.chat.type == "private":
        reply_markup = change_lang_markup

    else:
        reply_markup = None

    if detected:
        message = ctx.send(
            f"Detected language: {language}", photo=file, reply_markup=reply_markup,
        )

    else:
        message = ctx.send(f"Language: {language}", photo=file, reply_markup=reply_markup)

    code = Code(body, language, message.message_id, ctx.chat.id, ctx.user.id)
    bot.code_cache.append(code)


bot.run()
