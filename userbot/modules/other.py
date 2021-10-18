# Copyright (c) 2021 Man-Userbot
# Created by mrismanaziz
# FROM <https://github.com/mrismanaziz/Man-Userbot>
# t.me/SharingUserbot & t.me/Lunatic0de
#
# Thanks To Ultroid <https://github.com/TeamUltroid/Ultroid>
# Thanks To Geez-UserBot <https://github.com/vckyou/Geez-UserBot>

import os
from asyncio import sleep

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChannelParticipantsKicked

from userbot import ALIVE_NAME
from userbot import CMD_HANDLER as cmd
from userbot import CMD_HELP, bot
from userbot.events import man_cmd
from userbot.utils import edit_delete, edit_or_reply


@bot.on(man_cmd(outgoing=True, pattern=r"open(?: |$)(.*)"))
async def _(event):
    b = await event.client.download_media(await event.get_reply_message())
    with open(b, "r") as a:
        c = a.read()
    a = await event.edit("**Berhasil Membaca Berkas**")
    if len(c) > 4095:
        await a.edit("**File Terlalu Panjang Untuk dibaca**")
    else:
        await event.client.send_message(event.chat_id, f"`{c}`")
        await a.delete()
    os.remove(b)


@bot.on(man_cmd(outgoing=True, pattern=r"sendbot (.*)"))
async def _(event):
    if event.fwd_from:
        return
    chat = str(event.pattern_match.group(1).split(" ", 1)[0])
    link = str(event.pattern_match.group(1).split(" ", 1)[1])
    if not link:
        return await event.edit("**Maaf BOT Tidak Merespond.**")

    botid = await event.client.get_entity(chat)
    await event.edit("`Processing...`")
    async with bot.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=botid)
            )
            msg = await bot.send_message(chat, link)
            response = await response
            await bot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.reply(f"**Unblock Terlebih dahulu {chat} dan coba lagi.**")
            return
        except BaseException:
            await event.edit("**Tidak dapat menemukan bot itu 🥺**")
            await sleep(2)
            return await event.delete()

        await event.edit(f"**Pesan Terkirim:** `{link}`\n**Kepada: {chat}**")
        await bot.send_message(event.chat_id, response.message)
        await bot.send_read_acknowledge(event.chat_id)
        await event.client.delete_messages(conv.chat_id, [msg.id, response.id])


@bot.on(man_cmd(outgoing=True, pattern=r"unbanall$"))
async def _(event):
    await event.edit("`Searching Participant Lists...`")
    p = 0
    title = (await event.get_chat()).title
    async for i in event.client.iter_participants(
        event.chat_id,
        filter=ChannelParticipantsKicked,
        aggressive=True,
    ):
        try:
            await event.client.edit_permissions(event.chat_id, i, view_messages=True)
            p += 1
        except BaseException:
            pass
    await event.edit(f"**Berhasil unbanned** `{p}` **Orang di Grup {title}**")


@bot.on(man_cmd(outgoing=True, pattern=r"(?:dm)\s?(.*)?"))
async def _(event):
    p = event.pattern_match.group(1)
    m = p.split(" ")
    chat_id = m[0]
    try:
        chat_id = int(chat_id)
    except BaseException:
        pass
    mssg = await event.get_reply_message()
    if event.reply_to_msg_id:
        await event.client.send_message(chat_id, mssg)
        await event.edit("**Berhasil Mengirim Pesan Anda.**")
    msg = "".join(i + " " for i in m[1:])
    if msg == "":
        return
    try:
        await event.client.send_message(chat_id, msg)
        await event.edit("**Berhasil Mengirim Pesan Anda.**")
    except BaseException:
        await event.edit("**ERROR: Gagal Mengirim Pesan.**")


@bot.on(man_cmd(outgoing=True, pattern=r"fwdreply ?(.*)"))
async def _(e):
    message = e.pattern_match.group(1)
    if not e.reply_to_msg_id:
        return await edit_or_reply(e, "`Mohon Reply ke pesan seseorang.`")
    if not message:
        return await edit_or_reply(e, "`Tidak ditemukan pesan untuk disampaikan`")
    msg = await e.get_reply_message()
    fwd = await msg.forward_to(msg.sender_id)
    await fwd.reply(message)
    await edit_delete(e, "**Silahkan Check di Private**", 15)


@bot.on(man_cmd(outgoing=True, pattern=r"getlink(?: |$)(.*)"))
async def _(event):
    await event.edit("`Processing...`")
    try:
        e = await event.client(
            ExportChatInviteRequest(event.chat_id),
        )
    except ChatAdminRequiredError:
        return await bot.send_message(f"**Maaf {ALIVE_NAME} Bukan Admin 👮**")
    await event.edit(f"**Link Invite GC**: {e.link}")


@bot.on(man_cmd(outgoing=True, pattern=r"tmsg (.*)"))
async def _(event):
    k = await event.get_reply_message()
    if k:
        a = await bot.get_messages(event.chat_id, 0, from_user=k.sender_id)
        return await event.edit(
            f"**Total ada** `{a.total}` **Chat Yang dikirim Oleh** {u} **di Grup Chat ini**"
        )
    u = event.pattern_match.group(1)
    if not u:
        u = "me"
    a = await bot.get_messages(event.chat_id, 0, from_user=u)
    await event.edit(
        f"**Total ada `{a.total}` Chat Yang dikirim Oleh saya di Grup Chat ini**"
    )


@bot.on(man_cmd(outgoing=True, pattern=r"limit(?: |$)(.*)"))
async def _(event):
    await event.edit("`Processing...`")
    async with bot.conversation("@SpamBot") as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=178220800)
            )
            await conv.send_message("/start")
            response = await response
            await bot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.edit("**Mohon Unblock @SpamBot dan coba lagi**")
            return
        await event.edit(f"~ {response.message.message}")


CMD_HELP.update(
    {
        "open": f"**Plugin : **`open`\
        \n\n  •  **Syntax :** `{cmd}open`\
        \n  •  **Function : **Untuk Melihat isi File Menjadi Text yang dikirim menjadi pesan telegram.\
    "
    }
)


CMD_HELP.update(
    {
        "dm": f"**Plugin : **`dm`\
        \n\n  •  **Syntax :** `{cmd}dm` <username> <text>\
        \n  •  **Function : **Untuk mengirim chat dengan menggunakan userbot.\
        \n\n  •  **Syntax :** `{cmd}fwdreply` <username> <text>\
        \n  •  **Function : **Untuk meneruskan chat yang di reply dengan membalasnya ke pc.\
    "
    }
)


CMD_HELP.update(
    {
        "sendbot": f"**Plugin : **`sendbot`\
        \n\n  •  **Syntax :** `{cmd}sendbot` <username bot> <text>\
        \n  •  **Function : **Untuk mengirim ke bot dan mendapatkan respond chat dengan menggunakan userbot.\
    "
    }
)


CMD_HELP.update(
    {
        "tmsg": f"**Plugin : **`tmsg`\
        \n\n  •  **Syntax :** `{cmd}tmsg` <username/me>\
        \n  •  **Function : **Untuk Menghitung total jumlah chat yang sudah dikirim.\
    "
    }
)


CMD_HELP.update(
    {
        "getlink": f"**Plugin : **`getlink`\
        \n\n  •  **Syntax :** `{cmd}getlink`\
        \n  •  **Function : **Untuk Mendapatkan link invite grup chat.\
    "
    }
)


CMD_HELP.update(
    {
        "unbanall": f"**Plugin : **`unbanall`\
        \n\n  •  **Syntax :** `{cmd}unbanall`\
        \n  •  **Function : **Untuk Menghapus Semua Pengguna yang dibanned di Daftar Banned GC.\
    "
    }
)

CMD_HELP.update(
    {
        "limit": f"**Plugin : **`limit`\
        \n\n  •  **Syntax :** `{cmd}limit`\
        \n  •  **Function : **Untuk Mengecek akun anda sedang terkena limit atau tidak dengan menggunakan @spambot.\
    "
    }
)
