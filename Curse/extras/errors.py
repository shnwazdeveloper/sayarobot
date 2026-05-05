import os
import traceback
from datetime import datetime
from functools import wraps

from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden

from Curse import MESSAGE_DUMP


def capture_err(func):
    @wraps(func)
    async def capture(client, message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except ChatWriteForbidden:
            await client.leave_chat(message.chat.id)
        except Exception as err:
            exc = traceback.format_exc()
            error_feedback = "ERROR | {} | {}\n\n{}\n\n{}\n".format(
                message.from_user.id if message.from_user else 0,
                message.chat.id if message.chat else 0,
                message.text or message.caption,
                exc,
            )
            day = datetime.today()
            tgl_now = datetime.now()

            cap_day = f"{day.strftime('%A')}, {tgl_now.strftime('%d %B %Y %H:%M:%S')}"
            await message.reply(
                "😭 An Internal Error Occurred while processing your Command, the Logs have been sent to the Owners of this Bot. Sorry for Inconvenience..."
            )
            log_file_path = f"crash_{tgl_now.strftime('%d %B %Y')}.log"
            with open(log_file_path, "w+", encoding="utf-8") as log:
                log.write(error_feedback)
            await client.send_document(
                MESSAGE_DUMP,
                log_file_path,
                caption=f"Crash Report of this Bot\n{cap_day}",
            )
            os.remove(log_file_path)
            raise err

    return capture
