from telegram.ext import commands, MessageHandler, Filters
import telegram

import io
import logging
import guesslang
import html
from pygments import highlight
from pygments.lexers import get_lexer_by_name, ClassNotFound
from pygments.formatters.img import ImageFormatter
from pygments.styles.paraiso_dark import ParaisoDarkStyle

import config


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class Bot(commands.Bot):
    """Subclass that connects to a db on start and close"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = None

    def remove_mentions(self, string):
        string = list(string)

        for i, letter in enumerate(string):
            if letter == "@":
                string[i] = "@\N{ZERO WIDTH JOINER}"

        return "".join(string)

    def get_command_signature(self, command):
        alias = command.name
        return "/%s %s" % (alias, command.signature)

    def format_command(self, command):
        help_text = []

        signature = self.get_command_signature(command)
        help_text.append(html.escape(f"Usage: {signature}"))

        if command.description:
            help_text.append(html.escape(command.description))

        if command.help:
            help_text.append(html.escape(command.help))

        if command.examples:
            help_text.append("")  # blank line
            help_text.append("<b>Examples:</b>")

            for example in command.examples:
                help_text.append(html.escape(f"• /{command.name} {example}"))

        return "\n".join(help_text)

    def on_command_error(self, ctx, error):
        # print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
        # traceback.print_exception(
        #     type(error), error, error.__traceback__, file=sys.stderr
        # )

        cmd = self.format_command(ctx.command)

        if hasattr(ctx, "handled"):
            return

        elif isinstance(error, commands.ArgumentParsingError):
            ctx.send(f"\N{CROSS MARK} {error}")

        elif isinstance(error, commands.BadArgument):
            formatted = self.remove_mentions(str(error))
            ctx.send(f"\N{CROSS MARK} {html.escape(formatted)}\n\n{cmd}", parse_mode="HTML")

        elif isinstance(error, commands.MissingRequiredArgument):
            message = f"Missing a required argument: <code>{html.escape(error.param.name)}</code>"
            ctx.send(ctx.send(f"\N{CROSS MARK} {message}\n\n{cmd}", parse_mode="HTML"))

        elif isinstance(error, commands.CommandInvokeError):
            message = (
                "\N{WARNING SIGN} <b>Unexpected Error</b>\n\n"
                "An unexpected error has occured:"
                f'<pre><code class="language-python">\n{html.escape(str(error))}</code></pre>'
                "The owner of the bot has been notified."
            )
            ctx.send(message, parse_mode="HTML")


description = """
Hi! I'm a bot that will highlight code for you.

Just use /code with some code, and I'll try to detect a language and highlight it.
You can optionally specify a language before the code.
"""

bot = Bot(token=config.token, description=description, owner_ids=[1389169565])

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
