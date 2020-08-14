import io

from pygments import highlight
from pygments.formatters.img import ImageFormatter
from styles.dracula import DraculaStyle


def generate_image(body, lexer, *, font="Consolas"):
    """Generates the highlighted image given the code and a lexer"""
    formatter = ImageFormatter(
        image_format="PNG",
        font_size=24,
        line_pad=8,
        style=DraculaStyle,
        line_number_bg="#282a36",
        line_number_fg="#69696E",
        line_number_pad=12,
        font_name=font,
    )

    file = io.BytesIO()
    result = highlight(body, lexer, formatter, outfile=file)

    file.seek(0)

    return file


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu
