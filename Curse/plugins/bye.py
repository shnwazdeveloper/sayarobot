from pyrogram import filters
import uuid
import math
import os
import requests

from Curse.bot_class import app 

@app.on_message(filters.left_chat_member)
async def _left_mem(client, message):
    user_id = message.left_chat_member.id

    # Get user information
    user = await client.get_users(user_id)
    first_name = user.first_name
    last_name = user.last_name or ""
    user_link = f"[{first_name} {last_name}](tg://user?id={user_id})"

    video_url = "https://envs.sh/Lwt.mp4"

    text = f"Good bye {user_link}"
    
    await client.send_video(
        chat_id=message.chat.id,
        video=video_url,
        caption=text
    )
