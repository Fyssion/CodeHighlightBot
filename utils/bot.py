from telegram.ext import commands

import html


class Bot(commands.Bot):
    """Subclass that contains an error handler"""

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
        cmd = self.format_command(ctx.command)

        if hasattr(ctx, "handled"):
            return

        elif isinstance(error, commands.ArgumentParsingError):
            ctx.send(f"\N{CROSS MARK} {error}")

        elif isinstance(error, commands.BadArgument):
            formatted = self.remove_mentions(str(error))
            ctx.send(
                f"\N{CROSS MARK} {html.escape(formatted)}\n\n{cmd}", parse_mode="HTML"
            )

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
