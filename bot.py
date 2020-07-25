from telegram.ext import commands, MessageHandler, Filters
import telegram

import io
import logging
import guesslang
from pygments import highlight
from pygments.lexers import get_lexer_by_name, ClassNotFound
from pygments.formatters.img import ImageFormatter
from pygments.styles.paraiso_dark import ParaisoDarkStyle

import config


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


description = """
Hi! I'm a bot that will highlight code for you.

Just use /code with some code, and I'll try to detect a language and highlight it.
You can optionally specify a language before the code.
"""

bot = commands.Bot(token=config.token, description=description, owner_ids=[1389169565])

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

    # Attempt to get the language of the code
    try:
        lexer = get_lexer_by_name(first_word, stripall=True)
        language = None
        body = body[len(first_word) :]
    except ClassNotFound:
        language = guesser.language_name(body)
        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except ClassNotFound:
            ctx.send("Sorry, could not detect language.")
            return

    formatter = ImageFormatter(
        image_format="PNG",
        font_size=24,
        style=ParaisoDarkStyle,
        line_number_bg=0x261825,
        font_name="Consolas",
    )

    file = io.BytesIO()
    result = highlight(body, lexer, formatter, outfile=file)

    file.seek(0)

    if language:
        ctx.send(f"Detected language: {language}", photo=file)

    else:
        ctx.send(photo=file)


bot.run()
