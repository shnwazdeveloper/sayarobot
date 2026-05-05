import asyncio
import os
import re
import shutil
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, emoji, enums, filters
from pyrogram.errors import BadRequest, PeerIdInvalid, StickersetInvalid
from pyrogram.file_id import FileId
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import (
    AddStickerToSet,
    CreateStickerSet,
    RemoveStickerFromSet,
)
from pyrogram.raw.types import (
    DocumentAttributeFilename,
    InputDocument,
    InputMediaUploadedDocument,
    InputStickerSetItem,
    InputStickerSetShortName,
)
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message

from Curse import MESSAGE_DUMP, PREFIX_HANDLER
from Curse.bot_class import app
from Curse.extras.https import fetch
from Curse.extras.localization import use_chat_lang
from Curse.utils.custom_filters import command
from Curse.vars import Config

def get_emoji_regex():
    e_list = [
        getattr(emoji, e).encode("unicode-escape").decode("ASCII")
        for e in dir(emoji)
        if not e.startswith("_")
    ]
    # to avoid re.error excluding char that start with '*'
    e_sort = sorted([x for x in e_list if not x.startswith("*")], reverse=True)
    # Sort emojis by length to make sure multi-character emojis are
    # matched first
    pattern_ = f"({'|'.join(e_sort)})"
    return re.compile(pattern_)

C_HANDLER = PREFIX_HANDLER
EMOJI_PATTERN = get_emoji_regex()
SUPPORTED_TYPES = ["jpeg", "png", "webp"]


@app.on_message(filters.command(["getsticker"], C_HANDLER), group=111)
@use_chat_lang()
async def getsticker_(self: Client, ctx: Message, strings):
    if not ctx.reply_to_message or not ctx.reply_to_message.sticker:
        return await ctx.reply(strings("not_sticker"))

    sticker = ctx.reply_to_message.sticker

    if sticker.is_animated or sticker.is_video:
        return await ctx.reply(strings("no_anim_stick"))

    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, "getsticker")
        os.makedirs(path, exist_ok=True)

        sticker_file = await self.download_media(
            message=ctx.reply_to_message,
            file_name=os.path.join(path, f"{sticker.file_unique_id}.png"),
        )

        await ctx.reply_to_message.reply_document(
            document=sticker_file,
            caption=f"<b>Emoji:</b> {sticker.emoji}\n"
                    f"<b>Sticker ID:</b> <code>{sticker.file_id}</code>\n\n"
                    f"<b>Sent by:</b> @{self.me.username}",
        )

@app.on_message(filters.command("getvidsticker"), group=222)
async def _vidstick(_, message):
    chat_id = message.chat.id
    replied = message.reply_to_message
    if replied and replied.sticker:
        if not replied.sticker.is_video:
            return await message.reply_text("Use /getsticker if sticker is not video.")
        file_id = replied.sticker.file_id
        new_file = await _.download_media(file_id, file_name="sticker.mp4")
        await _.send_animation(chat_id, new_file)
        os.remove(new_file)
    else:
        await message.reply_text("Please reply to a video sticker to upload it's MP4.")


@app.on_message(filters.command("getvideo"), group=333)
async def _vidstick(_, message):
    chat_id = message.chat.id
    replied = message.reply_to_message
    if replied and replied.animation:
        file_id = replied.animation.file_id
        new_file = await _.download_media(file_id, file_name="video.mp4")
        print(new_file)
        await _.send_video(chat_id, video=open(new_file, "rb"))
        os.remove(new_file)
    else:
        await message.reply_text("Please reply to a gif for me to get it's video.")


@app.on_message(filters.command(["stickerid"], C_HANDLER) & filters.reply, group=444)
async def getstickerid(_, ctx: Message):
    if ctx.reply_to_message.sticker:
        await ctx.reply(
            "The ID of this sticker is: <code>{stickerid}</code>".format(
                stickerid=ctx.reply_to_message.sticker.file_id
            )
        )


@app.on_message(filters.command(["unkang"], C_HANDLER) & filters.reply, group=555)
@use_chat_lang()
async def unkangs(self: Client, ctx: Message, strings):
    if not ctx.from_user:
        return await ctx.reply("You're anon, unkang in my PM")
    if sticker := ctx.reply_to_message.sticker:
        if str(ctx.from_user.id) not in sticker.set_name:
            return await ctx.reply("This sticker is not your pack, don't do it..")
        pp = await ctx.reply(strings("unkang_msg"))
        try:
            decoded = FileId.decode(sticker.file_id)
            sticker = InputDocument(
                id=decoded.media_id,
                access_hash=decoded.access_hash,
                file_reference=decoded.file_reference,
            )
            await self.invoke(RemoveStickerFromSet(sticker=sticker))
            await pp.edit(strings("unkang_success"))
        except Exception as e:
            await pp.edit(strings("unkang_error").format(e=e))
    else:
        await ctx.reply(strings("unkang_help").format(c=self.me.username))


@app.on_message(filters.command(["kang", "steal"]) & filters.group, group=666)
@use_chat_lang()
async def kang_sticker(self: Client, ctx: Message, strings):
    if not ctx.from_user:
        return await ctx.reply(strings("anon_warn"))

    prog_msg = await ctx.reply(strings("kang_msg"))

    sticker_emoji = ""
    packnum = 0
    packname_found = False
    resize = False
    animated = False
    videos = False
    convert = False

    reply = ctx.reply_to_message
    user = await self.resolve_peer(ctx.from_user.username or ctx.from_user.id)

    if reply and reply.media:
        if reply.photo:
            resize = True
        elif reply.animation:
            animated = True
        elif reply.video:
            videos = True
            convert = True
        elif reply.document:
            mt = reply.document.mime_type or ""
            if "image" in mt:
                resize = True
            elif "tgsticker" in mt:
                animated = True
            elif "video" in mt:
                videos = True
                convert = True
        elif reply.sticker:
            if not reply.sticker.file_name:
                return await prog_msg.edit(strings("stick_no_name"))
            sticker_emoji = reply.sticker.emoji or sticker_emoji
            animated = reply.sticker.is_animated
            videos = reply.sticker.is_video
            if videos:
                convert = False
            elif not reply.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            return await prog_msg.edit(strings("kang_help"))

        pack_prefix = "anim" if animated else "vid" if videos else "a"
        packname = f"{pack_prefix}_{ctx.from_user.id}_by_{self.me.username}"

        if len(ctx.command) > 1 and ctx.command[1].isdigit():
            packnum = ctx.command.pop(1)
            packname = f"{pack_prefix}{packnum}_{ctx.from_user.id}_by_{self.me.username}"

        if len(ctx.command) > 1:
            sticker_emoji = (
                "".join(set(EMOJI_PATTERN.findall("".join(ctx.command[1:])))) or sticker_emoji
            )

        filename = await self.download_media(reply)
        if not filename:
            return await prog_msg.delete()

    else:
        return await prog_msg.edit(strings("kang_help"))

    try:
        if resize:
            filename = resize_image(filename)
        elif convert:
            filename = await convert_video(filename)
            if filename is False:
                return await prog_msg.edit("Conversion Error", del_in=6)

        max_stickers = 120
        while not packname_found:
            try:
                stickerset = await self.invoke(GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname), hash=0))
                if stickerset.set.count >= max_stickers:
                    packnum += 1
                    packname = f"{pack_prefix}{packnum}_{ctx.from_user.id}_by_{self.me.username}"
                else:
                    packname_found = True
            except StickersetInvalid:
                break

        file = await self.save_file(filename)
        media = await self.invoke(
            SendMedia(
                peer=await self.resolve_peer(MESSAGE_DUMP),
                media=InputMediaUploadedDocument(
                    file=file,
                    mime_type=self.guess_mime_type(filename),
                    attributes=[DocumentAttributeFilename(file_name=filename)],
                ),
                message=f"#Sticker kang by UserID -> {ctx.from_user.id}",
                random_id=self.rnd_id(),
            )
        )
        msg_ = media.updates[-1].message
        stkr_file = msg_.media.document

        if packname_found:
            await prog_msg.edit(strings("exist_pack"))
            await self.invoke(
                AddStickerToSet(
                    stickerset=InputStickerSetShortName(short_name=packname),
                    sticker=InputStickerSetItem(
                        document=InputDocument(
                            id=stkr_file.id,
                            access_hash=stkr_file.access_hash,
                            file_reference=stkr_file.file_reference,
                        ),
                        emoji=sticker_emoji,
                    ),
                )
            )
        else:
            await prog_msg.edit(strings("new_packs"))
            stkr_title = f"{ctx.from_user.first_name}'sPack"
            if packnum:
                stkr_title += f" v{packnum}"

            await self.invoke(
                CreateStickerSet(
                    user_id=user,
                    title=stkr_title,
                    short_name=packname,
                    stickers=[
                        InputStickerSetItem(
                            document=InputDocument(
                                id=stkr_file.id,
                                access_hash=stkr_file.access_hash,
                                file_reference=stkr_file.file_reference,
                            ),
                            emoji=sticker_emoji,
                        )
                    ],
                )
            )

    except BadRequest:
        return await prog_msg.edit(strings("pack_full"))
    except Exception as all_e:
        await prog_msg.edit(f"{all_e.__class__.__name__} : {all_e}")
    else:
        view_pack_btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton(strings("viewpack"), url=f"https://t.me/addstickers/{packname}")]]
        )
        await prog_msg.edit(strings("kang_success").format(emot=sticker_emoji), reply_markup=view_pack_btn)
        await self.delete_messages(chat_id=MESSAGE_DUMP, message_ids=msg_.id, revoke=True)
        try:
            os.remove(filename)
        except OSError:
            pass


def resize_image(filename: str) -> str:
    im = Image.open(filename)
    maxsize = 512
    scale = maxsize / max(im.width, im.height)
    sizenew = (int(im.width * scale), int(im.height * scale))
    im = im.resize(sizenew, Image.NEAREST)
    downpath, f_name = os.path.split(filename)
    # not hardcoding png_image as "sticker.png"
    png_image = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.png")
    im.save(png_image, "PNG")
    if png_image != filename:
        os.remove(filename)
    return png_image


async def convert_video(filename: str) -> str:
    downpath, f_name = os.path.split(filename)
    webm_video = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.webm")
    cmd = [
        "ffmpeg",
        "-loglevel",
        "quiet",
        "-i",
        filename,
        "-t",
        "00:00:03",
        "-vf",
        "fps=30",
        "-c:v",
        "vp9",
        "-b:v:",
        "500k",
        "-preset",
        "ultrafast",
        "-s",
        "512x512",
        "-y",
        "-an",
        webm_video,
    ]

    proc = await asyncio.create_subprocess_exec(*cmd)
    # Wait for the subprocess to finish
    await proc.communicate()

    if webm_video != filename:
        os.remove(filename)
    return webm_video


@app.on_message(filters.command(["mmf"], C_HANDLER), group=777)
async def handler(client, message):
    if not message.reply_to_message:
        await message.reply("Reply to an image or a sticker to memify it!")
        return

    reply_message = message.reply_to_message
    if not reply_message.media:
        await message.reply("Provide some text please.")
        return

    file = await client.download_media(reply_message)
    msg = await message.reply("Memifying this image! Please wait.")

    text = message.text.split("/mmf ", maxsplit=1)[1].strip()
    if len(text) < 1:
        return await msg.edit("You might want to try `/mmf text`")

    meme = await draw_text(file, text)
    await client.send_document(message.chat.id, document=meme)
    await msg.delete()
    os.remove(meme)


async def draw_text(image_path, text):
    img = Image.open(image_path)
    os.remove(image_path)
    i_width, i_height = img.size

    if os.name == "nt":
        fnt = "arial.ttf"
    else:
        fnt = "./Curse/extras/default.ttf"
    m_font = ImageFont.truetype(fnt, int((70 / 640) * i_width))

    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ""

    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5

    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = draw.textsize(u_text, font=m_font)

            draw.text(
                xy=(((i_width - u_width) / 2) - 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(((i_width - u_width) / 2) + 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=((i_width - u_width) / 2, int(((current_h / 640) * i_width)) - 2),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(((i_width - u_width) / 2), int(((current_h / 640) * i_width)) + 2),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=((i_width - u_width) / 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(255, 255, 255),
            )

            current_h += u_height + pad

    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            u_width, u_height = draw.textsize(l_text, font=m_font)

            draw.text(
                xy=(
                    ((i_width - u_width) / 2) - 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    ((i_width - u_width) / 2) + 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) - 2,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) + 2,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(255, 255, 255),
            )

            current_h += u_height + pad

    image_name = "memify.webp"
    webp_file = os.path.join(image_name)
    img.save(webp_file, "webp")
    return webp_file


@app.on_message(command(["stickerinfo", "stinfo"], C_HANDLER), group=888)
async def give_st_info(c: app, m: Message):
    if not m.reply_to_message:
        await m.reply_text("Reply to a sticker")
        return
    elif not m.reply_to_message.sticker:
        await m.reply_text("Reply to a sticker")
        return
    st_in = m.reply_to_message.sticker
    st_type = "Normal"
    if st_in.is_animated:
        st_type = "Animated"
    elif st_in.is_video:
        st_type = "Video"
    st_to_gib = f"""[Sticker]({m.reply_to_message.link}) info:
 𝗙𝗜𝗟𝗘 𝗜𝗗 : `{st_in.file_id}`
 𝗙𝗜𝗟𝗘 𝗡𝗔𝗠𝗘 : {st_in.file_name}
 𝗙𝗜𝗟𝗘 𝗨𝗡𝗜𝗤𝗨𝗘 𝗜𝗗 : `{st_in.file_unique_id}`
 𝗗𝗔𝗧𝗘 𝗔𝗡𝗗 𝗧𝗜𝗠𝗘 𝗢𝗙 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗖𝗥𝗘𝗔𝗧𝗘𝗗 : `{st_in.date}`
 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗧𝗬𝗣𝗘 : `{st_type}`
 𝗘𝗠𝗢𝗝𝗜 : {st_in.emoji}
 𝗣𝗔𝗖𝗞 𝗡𝗔𝗠𝗘 : {st_in.set_name}
"""
    kb = IKM(
        [
            [
                IKB(
                    " 𝗔𝗱𝗱 𝘀𝘁𝗶𝗰𝗸𝗲𝗿 𝗽𝗮𝗰𝗸",
                    url=f"https://t.me/addstickers/{st_in.set_name}",
                )
            ]
        ]
    )
    await m.reply_text(st_to_gib, reply_markup=kb)
    return


__PLUGIN__ = "Stickers"
__alt_name__ = ["sticker", "kang"]

__HELP__ = """
** User Commands:**

 /kang (/steal) < emoji >: Reply to a sticker or any supported media.
 /pkang: Reply to a image type sticker to get full pack.
 /stickerinfo (/stinfo) : Reply to any sticker to get it's info.
 /stickerid Reply to a sticker message to get the sticker ID and emoji.
 /stickers < query >: Search for sticker packs based on the given query.
 /getsticker: Reply to a sticker message to get the sticker as a document.
 /getvidsticker: Reply to a video sticker message to get the video as an animation.
 /getvideo: Reply to a GIF message to get the GIF as a video.
 /unkang: Reply to a sticker created by the bot to remove it from your pack.
 /mmf < your text >: Reply to a normal sticker or a photo or video file to memify it. If you want to right text at bottom use `;right your message`
    ■ For e.g.
    ○ /mmf Hello freinds : this will add text to the top
    ○ /mmf Hello ; freinds : this will add Hello to the top and freinds at the bottom
    ○ /mmf ; Hello friends : this will add text at the bottom

**Note**
mmf and getsticker only support photo and normal stickers for now.
"""
