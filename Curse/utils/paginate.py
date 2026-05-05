from math import ceil
from typing import List
from pyrogram.types import InlineKeyboardButton

class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text

def paginate_modules(page_n: int, module_dict: List[str], prefix: str, button_vertically: int = 4, button_horizontally: int = 3) -> List[List[EqInlineKeyboardButton]]:
    modules = sorted(
        [
            EqInlineKeyboardButton(
                x.split('.')[1].title(),
                callback_data="{}_module({})".format(
                    prefix, x.split('.')[1].lower()
                ),
            )
            for x in module_dict
        ]
    )

    pairs = [modules[i * button_horizontally : (i + 1) * button_horizontally] for i in range((len(modules) + button_horizontally - 1) // button_horizontally)]

    max_num_pages = ceil(len(pairs) / button_vertically)
    modulo_page = page_n % max_num_pages

    if len(pairs) > button_vertically:
        pairs = pairs[modulo_page * button_vertically : button_vertically * (modulo_page + 1)] + [
            [
                EqInlineKeyboardButton(
                    "", callback_data="{}_prev({})".format(prefix, modulo_page)
                ),
                EqInlineKeyboardButton("Back", callback_data="start_back"),
                EqInlineKeyboardButton(
                    "", callback_data="{}_next({})".format(prefix, modulo_page)
                ),
            ]
        ]

    else:
        pairs += [[EqInlineKeyboardButton("", callback_data="start_back")]]

    return pairs
