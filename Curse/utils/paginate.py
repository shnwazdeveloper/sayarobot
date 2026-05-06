from math import ceil
from typing import List

from pyrogram.types import InlineKeyboardButton

from Curse.utils.text_style import smallcaps


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def _module_name(module_key):
    return module_key.split(".", 1)[1] if "." in module_key else module_key


def paginate_modules(
    page_n: int,
    module_dict: List[str],
    prefix: str,
    button_vertically: int = 2,
    button_horizontally: int = 3,
) -> List[List[EqInlineKeyboardButton]]:
    modules = sorted(
        [
            EqInlineKeyboardButton(
                smallcaps(_module_name(x).replace("_", " ").title()),
                callback_data=f"{prefix}_module({_module_name(x).lower()})",
            )
            for x in module_dict
        ]
    )
    back_row = [EqInlineKeyboardButton(smallcaps("Back"), callback_data="start_back")]

    if not modules:
        return [back_row]

    pairs = [modules[i * button_horizontally : (i + 1) * button_horizontally] for i in range((len(modules) + button_horizontally - 1) // button_horizontally)]

    max_num_pages = ceil(len(pairs) / button_vertically)
    modulo_page = page_n % max_num_pages

    if len(pairs) > button_vertically:
        pairs = pairs[modulo_page * button_vertically : button_vertically * (modulo_page + 1)] + [
            [
                EqInlineKeyboardButton(
                    smallcaps("Prev"), callback_data=f"{prefix}_prev({modulo_page})"
                ),
                EqInlineKeyboardButton(smallcaps("Back"), callback_data="start_back"),
                EqInlineKeyboardButton(
                    smallcaps("Next"), callback_data=f"{prefix}_next({modulo_page})"
                ),
            ]
        ]

    else:
        pairs += [back_row]

    return pairs
