# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# thanks to the owner of X-tra-Telegram for tts fix
#
# Recode by @mrismanaziz
# FROM Man-Userbot
# t.me/SharingUserbot
#
""" Userbot module containing various scrapers. """

import asyncio
import io
import json
import os
import re
import shutil
import time
from asyncio import sleep
from re import findall, match
from time import sleep
from urllib.parse import quote_plus

import asyncurban
import barcode
import emoji
import qrcode
import requests
from barcode.writer import ImageWriter
from bs4 import BeautifulSoup
from emoji import get_emoji_regexp
from googletrans import LANGUAGES, Translator
from gtts import gTTS
from gtts.lang import tts_langs
from requests import get
from search_engine_parser import BingSearch, GoogleSearch, YahooSearch
from search_engine_parser.core.exceptions import NoResultsOrTrafficError
from telethon.tl.types import DocumentAttributeAudio, MessageMediaPhoto
from wikipedia import summary
from wikipedia.exceptions import DisambiguationError, PageError
from youtube_dl import YoutubeDL
from youtube_dl.utils import (
    ContentTooShortError,
    DownloadError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)
from youtube_search import YoutubeSearch

from userbot import (
    BOTLOG,
    BOTLOG_CHATID,
    CMD_HELP,
    LOGS,
    OCR_SPACE_API_KEY,
    REM_BG_API_KEY,
    TEMP_DOWNLOAD_DIRECTORY,
    bot,
)
from userbot.events import register
from userbot.utils import (
    chrome,
    edit_delete,
    edit_or_reply,
    googleimagesdownload,
    options,
    progress,
)

CARBONLANG = "auto"
TTS_LANG = "id"
TRT_LANG = "id"
TEMP_DOWNLOAD_DIRECTORY = "/root/userbot/.bin"


async def ocr_space_file(
    filename, overlay=False, api_key=OCR_SPACE_API_KEY, language="eng"
):

    payload = {
        "isOverlayRequired": overlay,
        "apikey": api_key,
        "language": language,
    }
    with open(filename, "rb") as f:
        r = requests.post(
            "https://api.ocr.space/parse/image",
            files={filename: f},
            data=payload,
        )
    return r.json()


@register(outgoing=True, pattern=r"^\.crblang (.*)")
async def setlang(prog):
    global CARBONLANG
    CARBONLANG = prog.pattern_match.group(1)
    await prog.edit(f"Bahasa untuk carbon.now.sh mulai {CARBONLANG}")


@register(outgoing=True, pattern="^.carbon")
async def carbon_api(e):
    """A Wrapper for carbon.now.sh"""
    await e.edit("`Processing..`")
    CARBON = "https://carbon.now.sh/?l={lang}&code={code}"
    global CARBONLANG
    textx = await e.get_reply_message()
    pcode = e.text
    if pcode[8:]:
        pcode = str(pcode[8:])
    elif textx:
        pcode = str(textx.message)  # Importing message to module
    code = quote_plus(pcode)  # Converting to urlencoded
    await e.edit("`Processing..\n25%`")
    if os.path.isfile("/root/userbot/.bin/carbon.png"):
        os.remove("/root/userbot/.bin/carbon.png")
    url = CARBON.format(code=code, lang=CARBONLANG)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = GOOGLE_CHROME_BIN
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    prefs = {"download.default_directory": "/root/userbot/.bin"}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER, options=chrome_options)
    driver.get(url)
    await e.edit("`Processing..\n50%`")
    download_path = "/root/userbot/.bin"
    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": download_path},
    }
    driver.execute("send_command", params)
    driver.find_element_by_xpath("//button[contains(text(),'Export')]").click()
    # driver.find_element_by_xpath("//button[contains(text(),'4x')]").click()
    # driver.find_element_by_xpath("//button[contains(text(),'PNG')]").click()
    await e.edit("`Processing..\n75%`")
    # Waiting for downloading
    while not os.path.isfile("/root/userbot/.bin/carbon.png"):
        await sleep(0.5)
    await e.edit("`Processing..\n100%`")
    file = "/root/userbot/.bin/carbon.png"
    await e.edit("`Uploading..`")
    await e.client.send_file(
        e.chat_id,
        file,
        caption="Made using [Carbon](https://carbon.now.sh/about/),\
        \na project by [Dawn Labs](https://dawnlabs.io/)",
        force_document=True,
        reply_to=e.message.reply_to_msg_id,
    )

    os.remove("/root/userbot/.bin/carbon.png")
    driver.quit()
    # Removing carbon.png after uploading
    await e.delete()  # Deleting msg


@register(outgoing=True, pattern=r"^\.img (.*)")
async def img_sampler(event):
    """For .img command, search and return images matching the query."""
    await event.edit("`Sedang Mencari Gambar Yang Anda Cari...`")
    query = event.pattern_match.group(1)
    lim = findall(r"lim=\d+", query)
    try:
        lim = lim[0]
        lim = lim.replace("lim=", "")
        query = query.replace("lim=" + lim[0], "")
    except IndexError:
        lim = 15
    response = googleimagesdownload()

    # creating list of arguments
    arguments = {
        "keywords": query,
        "limit": lim,
        "format": "jpg",
        "no_directory": "no_directory",
    }

    # passing the arguments to the function
    paths = response.download(arguments)
    lst = paths[0][query]
    await event.client.send_file(
        await event.client.get_input_entity(event.chat_id), lst
    )
    shutil.rmtree(os.path.dirname(os.path.abspath(lst[0])))
    await event.delete()


@register(outgoing=True, pattern=r"^\.currency ([\d\.]+) ([a-zA-Z]+) ([a-zA-Z]+)")
async def moni(event):
    c_from_val = float(event.pattern_match.group(1))
    c_from = (event.pattern_match.group(2)).upper()
    c_to = (event.pattern_match.group(3)).upper()
    try:
        response = get(
            "https://api.frankfurter.app/latest",
            params={"from": c_from, "to": c_to},
        ).json()
    except Exception:
        await event.edit("**Error: API is down.**")
        return
    if "error" in response:
        await event.edit(
            "**sepertinya ini  mata uang asing, yang tidak dapat saya konversi sekarang.**"
        )
        return
    c_to_val = round(c_from_val * response["rates"][c_to], 2)
    await event.edit(f"**{c_from_val} {c_from} = {c_to_val} {c_to}**")


@register(outgoing=True, pattern=r"^\.google ([\s\S]*)")
async def gsearch(q_event):
    man = await edit_or_reply(q_event, "`Processing...`")
    match = q_event.pattern_match.group(1)
    page = re.findall(r"-p\d+", match)
    lim = re.findall(r"-l\d+", match)
    try:
        page = page[0]
        page = page.replace("-p", "")
        match = match.replace("-p" + page, "")
    except IndexError:
        page = 1
    try:
        lim = lim[0]
        lim = lim.replace("-l", "")
        match = match.replace("-l" + lim, "")
        lim = int(lim)
        if lim <= 0:
            lim = int(5)
    except IndexError:
        lim = 5
    smatch = match.replace(" ", "+")
    search_args = (str(smatch), int(page))
    gsearch = GoogleSearch()
    bsearch = BingSearch()
    ysearch = YahooSearch()
    try:
        gresults = await gsearch.async_search(*search_args)
    except NoResultsOrTrafficError:
        try:
            gresults = await bsearch.async_search(*search_args)
        except NoResultsOrTrafficError:
            try:
                gresults = await ysearch.async_search(*search_args)
            except Exception as e:
                return await edit_delete(man, f"**ERROR:**\n`{e}`", time=10)
    msg = ""
    for i in range(lim):
        if i > len(gresults["links"]):
            break
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"👉 [{title}]({link})\n`{desc}`\n\n"
        except IndexError:
            break
    await edit_or_reply(
        man,
        "**Keyword Google Search:**\n`" + match + "`\n\n**Results:**\n" + msg,
        link_preview=False,
        aslink=True,
        linktext=f"**Hasil Pencarian untuk Keyword** `{match}` **adalah** :",
    )


@register(outgoing=True, pattern=r"^\.wiki (.*)")
async def wiki(wiki_q):
    """For .wiki command, fetch content from Wikipedia."""
    match = wiki_q.pattern_match.group(1)
    try:
        summary(match)
    except DisambiguationError as error:
        await wiki_q.edit(f"Ditemukan halaman yang tidak ambigu.\n\n{error}")
        return
    except PageError as pageerror:
        await wiki_q.edit(f"Halaman tidak ditemukan.\n\n{pageerror}")
        return
    result = summary(match)
    if len(result) >= 4096:
        with open("output.txt", "w+") as file:
            file.write(result)
        await wiki_q.client.send_file(
            wiki_q.chat_id,
            "output.txt",
            thumb="userbot/resources/logo.jpg",
            reply_to=wiki_q.id,
            caption="**Output terlalu besar, dikirim sebagai file**",
        )
        if os.path.exists("output.txt"):
            os.remove("output.txt")
        return
    await wiki_q.edit("**Search:**\n`" + match + "`\n\n**Result:**\n" + result)


@register(outgoing=True, pattern=r"^\.ud (.*)")
async def _(event):
    if event.fwd_from:
        return
    await event.edit("processing...")
    word = event.pattern_match.group(1)
    urban = asyncurban.UrbanDictionary()
    try:
        mean = await urban.get_word(word)
        await event.edit(
            "Text: **{}**\n\nBerarti: **{}**\n\nContoh: __{}__".format(
                mean.word, mean.definition, mean.example
            )
        )
    except asyncurban.WordNotFoundError:
        await event.edit("Tidak ada hasil untuk **" + word + "**")


@register(outgoing=True, pattern=r"^\.tts(?: |$)([\s\S]*)")
async def text_to_speech(query):
    """For .tts command, a wrapper for Google Text-to-Speech."""
    textx = await query.get_reply_message()
    message = query.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        return await query.edit(
            "**Berikan teks atau balas pesan untuk Text-to-Speech!**"
        )

    try:
        gTTS(message, lang=TTS_LANG)
    except AssertionError:
        return await query.edit(
            "**Teksnya kosong.**\n"
            "Tidak ada yang tersisa untuk dibicarakan setelah pra-pemrosesan, pembuatan token, dan pembersihan."
        )
    except ValueError:
        return await query.edit("**Bahasa tidak didukung.**")
    except RuntimeError:
        return await query.edit("**Error saat memuat kamus bahasa.**")
    tts = gTTS(message, lang=TTS_LANG)
    tts.save("k.mp3")
    with open("k.mp3", "rb") as audio:
        linelist = list(audio)
        linecount = len(linelist)
    if linecount == 1:
        tts = gTTS(message, lang=TTS_LANG)
        tts.save("k.mp3")
    with open("k.mp3", "r"):
        await query.client.send_file(query.chat_id, "k.mp3", voice_note=True)
        os.remove("k.mp3")
        await query.delete()


@register(outgoing=True, pattern=r"^\.tr(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    if "trim" in event.raw_text:

        return
    input_str = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str or "id"
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.edit("**.tr <kode bahasa>** sambil reply ke pesan")
        return
    text = emoji.demojize(text.strip())
    lan = lan.strip()
    translator = Translator()
    try:
        translated = translator.translate(text, dest=lan)
        after_tr_text = translated.text
        output_str = """**DITERJEMAHKAN** dari `{}` ke `{}`
{}""".format(
            translated.src, lan, after_tr_text
        )
        await event.edit(output_str)
    except Exception as exc:
        await event.edit(str(exc))


@register(pattern=r"\.lang (tr|tts) (.*)", outgoing=True)
async def lang(value):
    """For .lang command, change the default langauge of userbot scrapers."""
    util = value.pattern_match.group(1).lower()
    if util == "tr":
        scraper = "Translator"
        global TRT_LANG
        arg = value.pattern_match.group(2).lower()
        if arg in LANGUAGES:
            TRT_LANG = arg
            LANG = LANGUAGES[arg]
        else:
            await value.edit(
                f"**Kode Bahasa tidak valid !!**\n**Kode bahasa yang tersedia**:\n\n`{LANGUAGES}`"
            )
            return
    elif util == "tts":
        scraper = "Text to Speech"
        global TTS_LANG
        arg = value.pattern_match.group(2).lower()
        if arg in tts_langs():
            TTS_LANG = arg
            LANG = tts_langs()[arg]
        else:
            await value.edit(
                f"**Kode Bahasa tidak valid!!**\n**Kode bahasa yang tersedia**:\n\n`{tts_langs()}`"
            )
            return
    await value.edit(
        f"**Bahasa untuk** `{scraper}` **diganti menjadi** `{LANG.title()}`"
    )
    if BOTLOG:
        await value.client.send_message(
            BOTLOG_CHATID,
            f"**Bahasa untuk** `{scraper}` **diganti menjadi** `{LANG.title()}`",
        )


@register(outgoing=True, pattern=r"^\.yt (\d*) *(.*)")
async def yt_search(video_q):
    """For .yt command, do a YouTube search from Telegram."""
    if video_q.pattern_match.group(1) != "":
        counter = int(video_q.pattern_match.group(1))
        if counter > 10:
            counter = int(10)
        if counter <= 0:
            counter = int(1)
    else:
        counter = int(5)

    query = video_q.pattern_match.group(2)
    if not query:
        await video_q.edit("`Masukkan keyword untuk dicari`")
    await video_q.edit("`Processing...`")

    try:
        results = json.loads(YoutubeSearch(query, max_results=counter).to_json())
    except KeyError:
        return await video_q.edit(
            "`Pencarian Youtube menjadi lambat.\nTidak dapat mencari keyword ini!`"
        )

    output = f"**Pencarian Keyword:**\n`{query}`\n\n**Hasil:**\n\n"

    for i in results["videos"]:
        try:
            title = i["title"]
            link = "https://youtube.com" + i["url_suffix"]
            channel = i["channel"]
            duration = i["duration"]
            views = i["views"]
            output += f"[{title}]({link})\nChannel: `{channel}`\nDuration: {duration} | {views}\n\n"
        except IndexError:
            break

    await video_q.edit(output, link_preview=False)


@register(outgoing=True, pattern=r".yt(audio|video) (.*)")
async def download_video(v_url):
    """For .yt command, download media from YouTube and many other sites."""
    dl_type = v_url.pattern_match.group(1).lower()
    url = v_url.pattern_match.group(2)

    await v_url.edit("`Preparing to download...`")
    video = False
    audio = False

    if dl_type == "audio":
        opts = {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "writethumbnail": True,
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "outtmpl": "%(id)s.%(ext)s",
            "quiet": True,
            "logtostderr": False,
        }
        audio = True

    elif dl_type == "video":
        opts = {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            ],
            "outtmpl": "%(id)s.%(ext)s",
            "logtostderr": False,
            "quiet": True,
        }
        video = True

    try:
        await v_url.edit("`Fetching data, please wait..`")
        with YoutubeDL(opts) as rip:
            rip_data = rip.extract_info(url)
    except DownloadError as DE:
        return await v_url.edit(f"`{str(DE)}`")
    except ContentTooShortError:
        return await v_url.edit("`The download content was too short.`")
    except GeoRestrictedError:
        return await v_url.edit(
            "`Video is not available from your geographic location "
            "due to geographic restrictions imposed by a website.`"
        )
    except MaxDownloadsReached:
        return await v_url.edit("`Max-downloads limit has been reached.`")
    except PostProcessingError:
        return await v_url.edit("`There was an error during post processing.`")
    except UnavailableVideoError:
        return await v_url.edit("`Media is not available in the requested format.`")
    except XAttrMetadataError as XAME:
        return await v_url.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
    except ExtractorError:
        return await v_url.edit("`There was an error during info extraction.`")
    except Exception as e:
        return await v_url.edit(f"{str(type(e)): {str(e)}}")
    c_time = time.time()
    if audio:
        await v_url.edit(
            f"**Sedang Mengupload Lagu:**\n`{rip_data.get('title')}`"
            f"\nby **{rip_data.get('uploader')}**"
        )
        f_name = rip_data.get("id") + ".mp3"
        with open(f_name, "rb") as f:
            result = await upload_file(
                client=v_url.client,
                file=f,
                name=f_name,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, v_url, c_time, "Uploading..", f"{rip_data['title']}.mp3"
                    )
                ),
            )
        img_extensions = ["jpg", "jpeg", "webp"]
        img_filenames = [
            fn_img
            for fn_img in os.listdir()
            if any(fn_img.endswith(ext_img) for ext_img in img_extensions)
        ]
        thumb_image = img_filenames[0]
        metadata = extractMetadata(createParser(f_name))
        duration = 0
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        await v_url.client.send_file(
            v_url.chat_id,
            result,
            supports_streaming=True,
            attributes=[
                DocumentAttributeAudio(
                    duration=duration,
                    title=rip_data.get("title"),
                    performer=rip_data.get("uploader"),
                )
            ],
            thumb=thumb_image,
        )
        os.remove(thumb_image)
        os.remove(f_name)
        await v_url.delete()
    elif video:
        await v_url.edit(
            f"**Sedang Mengupload Video:**\n`{rip_data.get('title')}`"
            f"\nby **{rip_data.get('uploader')}**"
        )
        f_name = rip_data.get("id") + ".mp4"
        with open(f_name, "rb") as f:
            result = await upload_file(
                client=v_url.client,
                file=f,
                name=f_name,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, v_url, c_time, "Uploading..", f"{rip_data['title']}.mp4"
                    )
                ),
            )
        thumb_image = await get_video_thumb(f_name, "thumb.png")
        metadata = extractMetadata(createParser(f_name))
        duration = 0
        width = 0
        height = 0
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")
        await v_url.client.send_file(
            v_url.chat_id,
            result,
            thumb=thumb_image,
            attributes=[
                DocumentAttributeVideo(
                    duration=duration,
                    w=width,
                    h=height,
                    supports_streaming=True,
                )
            ],
            caption=rip_data["title"],
        )
        os.remove(f_name)
        os.remove(thumb_image)
        await v_url.delete()


def deEmojify(inputString):
    """Remove emojis and other non-safe characters from string"""
    return get_emoji_regexp().sub("", inputString)


@register(outgoing=True, pattern=r"^\.rbg(?: |$)(.*)")
async def kbg(remob):
    """For .rbg command, Remove Image Background."""
    if REM_BG_API_KEY is None:
        await remob.edit(
            "`Error: Remove.BG API key missing! Add it to environment vars or config.env.`"
        )
        return
    input_str = remob.pattern_match.group(1)
    message_id = remob.message.id
    if remob.reply_to_msg_id:
        message_id = remob.reply_to_msg_id
        reply_message = await remob.get_reply_message()
        await remob.edit("`Processing..`")
        try:
            if isinstance(
                reply_message.media, MessageMediaPhoto
            ) or "image" in reply_message.media.document.mime_type.split("/"):
                downloaded_file_name = await remob.client.download_media(
                    reply_message, TEMP_DOWNLOAD_DIRECTORY
                )
                await remob.edit("`Removing background from this image..`")
                output_file_name = await ReTrieveFile(downloaded_file_name)
                os.remove(downloaded_file_name)
            else:
                await remob.edit("`Bagaimana cara menghapus latar belakang ini ?`")
        except Exception as e:
            await remob.edit(str(e))
            return
    elif input_str:
        await remob.edit(
            f"`Removing background from online image hosted at`\n{input_str}"
        )
        output_file_name = await ReTrieveURL(input_str)
    else:
        await remob.edit("`Saya butuh sesuatu untuk menghapus latar belakang.`")
        return
    contentType = output_file_name.headers.get("content-type")
    if "image" in contentType:
        with io.BytesIO(output_file_name.content) as remove_bg_image:
            remove_bg_image.name = "removed_bg.png"
            await remob.client.send_file(
                remob.chat_id,
                remove_bg_image,
                caption="Support @SharingUserbot",
                force_document=True,
                reply_to=message_id,
            )
            await remob.delete()
    else:
        await remob.edit(
            "**Error (Invalid API key, I guess ?)**\n`{}`".format(
                output_file_name.content.decode("UTF-8")
            )
        )


# this method will call the API, and return in the appropriate format
# with the name provided.
async def ReTrieveFile(input_file_name):
    headers = {
        "X-API-Key": REM_BG_API_KEY,
    }
    files = {
        "image_file": (input_file_name, open(input_file_name, "rb")),
    }
    return requests.post(
        "https://api.remove.bg/v1.0/removebg",
        headers=headers,
        files=files,
        allow_redirects=True,
        stream=True,
    )


async def ReTrieveURL(input_url):
    headers = {
        "X-API-Key": REM_BG_API_KEY,
    }
    data = {"image_url": input_url}
    return requests.post(
        "https://api.remove.bg/v1.0/removebg",
        headers=headers,
        data=data,
        allow_redirects=True,
        stream=True,
    )


@register(pattern=r"^\.ocr (.*)", outgoing=True)
async def ocr(event):
    if not OCR_SPACE_API_KEY:
        return await event.edit(
            "`Error: OCR.Space API key is missing! Add it to environment variables or config.env.`"
        )
    await event.edit("`Sedang Membaca...`")
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    lang_code = event.pattern_match.group(1)
    downloaded_file_name = await bot.download_media(
        await event.get_reply_message(), TEMP_DOWNLOAD_DIRECTORY
    )
    test_file = await ocr_space_file(filename=downloaded_file_name, language=lang_code)
    try:
        ParsedText = test_file["ParsedResults"][0]["ParsedText"]
    except BaseException:
        await event.edit(
            "`Tidak bisa membacanya.`\n`Saya rasa saya perlu kacamata baru.`"
        )
    else:
        await event.edit(f"`Inilah yang bisa saya baca darinya:`\n\n{ParsedText}")
    os.remove(downloaded_file_name)


@register(pattern=r"^\.decode$", outgoing=True)
async def parseqr(qr_e):
    """For .decode command, get QR Code/BarCode content from the replied photo."""
    downloaded_file_name = await qr_e.client.download_media(
        await qr_e.get_reply_message()
    )
    # parse the Official ZXing webpage to decode the QRCode
    command_to_exec = [
        "curl",
        "-X",
        "POST",
        "-F",
        "f=@" + downloaded_file_name + "",
        "https://zxing.org/w/decode",
    ]
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    os.remove(downloaded_file_name)
    if not t_response:
        LOGS.info(e_response)
        LOGS.info(t_response)
        return await qr_e.edit("Gagal untuk decode.")
    soup = BeautifulSoup(t_response, "html.parser")
    qr_contents = soup.find_all("pre")[0].text
    await qr_e.edit(qr_contents)


@register(pattern=r"^\.barcode(?: |$)([\s\S]*)", outgoing=True)
async def bq(event):
    """For .barcode command, genrate a barcode containing the given content."""
    await event.edit("`Processing..`")
    input_str = event.pattern_match.group(1)
    message = "SYNTAX: `.barcode <long text to include>`"
    reply_msg_id = event.message.id
    if input_str:
        message = input_str
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        reply_msg_id = previous_message.id
        if previous_message.media:
            downloaded_file_name = await event.client.download_media(previous_message)
            m_list = None
            with open(downloaded_file_name, "rb") as fd:
                m_list = fd.readlines()
            message = "".join(m.decode("UTF-8") + "\r\n" for m in m_list)
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message
    else:
        return event.edit("SYNTAX: `.barcode <long text to include>`")

    bar_code_type = "code128"
    try:
        bar_code_mode_f = barcode.get(bar_code_type, message, writer=ImageWriter())
        filename = bar_code_mode_f.save(bar_code_type)
        await event.client.send_file(event.chat_id, filename, reply_to=reply_msg_id)
        os.remove(filename)
    except Exception as e:
        return await event.edit(str(e))
    await event.delete()


@register(pattern=r"^\.makeqr(?: |$)([\s\S]*)", outgoing=True)
async def make_qr(makeqr):
    """For .makeqr command, make a QR Code containing the given content."""
    input_str = makeqr.pattern_match.group(1)
    message = "SYNTAX: `.makeqr <long text to include>`"
    reply_msg_id = None
    if input_str:
        message = input_str
    elif makeqr.reply_to_msg_id:
        previous_message = await makeqr.get_reply_message()
        reply_msg_id = previous_message.id
        if previous_message.media:
            downloaded_file_name = await makeqr.client.download_media(previous_message)
            m_list = None
            with open(downloaded_file_name, "rb") as file:
                m_list = file.readlines()
            message = "".join(media.decode("UTF-8") + "\r\n" for media in m_list)
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(message)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("img_file.webp", "PNG")
    await makeqr.client.send_file(
        makeqr.chat_id, "img_file.webp", reply_to=reply_msg_id
    )
    os.remove("img_file.webp")
    await makeqr.delete()


@register(pattern=r"^\.ss (.*)", outgoing=True)
async def capture(url):
    """For .ss command, capture a website's screenshot and send the photo."""
    await url.edit("`Processing...`")
    chrome_options = await options()
    chrome_options.add_argument("--test-type")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.arguments.remove("--window-size=1920x1080")
    driver = await chrome(chrome_options=chrome_options)
    input_str = url.pattern_match.group(1)
    link_match = match(r"\bhttps?://.*\.\S+", input_str)
    if link_match:
        link = link_match.group()
    else:
        return await url.edit("`I need a valid link to take screenshots from.`")
    driver.get(link)
    height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.body.offsetHeight, "
        "document.documentElement.clientHeight, document.documentElement.scrollHeight, "
        "document.documentElement.offsetHeight);"
    )
    width = driver.execute_script(
        "return Math.max(document.body.scrollWidth, document.body.offsetWidth, "
        "document.documentElement.clientWidth, document.documentElement.scrollWidth, "
        "document.documentElement.offsetWidth);"
    )
    driver.set_window_size(width + 125, height + 125)
    wait_for = height / 1000
    await url.edit(
        "`Generating screenshot of the page...`"
        f"\n`Height of page = {height}px`"
        f"\n`Width of page = {width}px`"
        f"\n`Waiting ({int(wait_for)}s) for the page to load.`"
    )
    await sleep(int(wait_for))
    im_png = driver.get_screenshot_as_png()
    # saves screenshot of entire page
    driver.quit()
    message_id = url.message.id
    if url.reply_to_msg_id:
        message_id = url.reply_to_msg_id
    with io.BytesIO(im_png) as out_file:
        out_file.name = "screencapture.png"
        await url.edit("`Uploading screenshot as file..`")
        await url.client.send_file(
            url.chat_id,
            out_file,
            caption=input_str,
            force_document=True,
            reply_to=message_id,
        )
        await url.delete()


CMD_HELP.update(
    {
        "tts": "**Plugin : **`tts`\
        \n\n  •  **Syntax :** `.tts` <text/reply>\
        \n  •  **Function : **Menerjemahkan teks ke ucapan untuk bahasa yang disetel. \
        \n\n  •  **NOTE :** Gunakan .lang tts <kode bahasa> untuk menyetel bahasa untuk tr **(Bahasa Default adalah bahasa Indonesia)**\
    "
    }
)


CMD_HELP.update(
    {
        "translate": "**Plugin : **`Terjemahan`\
        \n\n  •  **Syntax :** `.tr` <text/reply>\
        \n  •  **Function : **Menerjemahkan teks ke bahasa yang disetel.\
        \n\n  •  **NOTE :** Gunakan .lang tr <kode bahasa> untuk menyetel bahasa untuk tr **(Bahasa Default adalah bahasa Indonesia)**\
    "
    }
)


CMD_HELP.update(
    {
        "carbon": "**Plugin : **`carbon`\
        \n\n  •  **Syntax :** `.carbon` <text/reply>\
        \n  •  **Function : **Percantik kode Anda menggunakan carbon.now.sh\
        \n\n  •  **NOTE :** Gunakan .crblang <text> untuk menyetel bahasa kode Anda.\
    "
    }
)


CMD_HELP.update(
    {
        "removebg": "**Plugin : **`removebg`\
        \n\n  •  **Syntax :** `.rbg` <Tautan ke Gambar> atau balas gambar apa pun (Peringatan: tidak berfungsi pada stiker.)\
        \n  •  **Function : **Menghapus latar belakang gambar, menggunakan API remove.bg\
    "
    }
)


CMD_HELP.update(
    {
        "ocr": "**Plugin : **`ocr`\
        \n\n  •  **Syntax :** `.ocr` <kode bahasa>\
        \n  •  **Function : **Balas gambar atau stiker untuk mengekstrak teks media tersebut.\
    "
    }
)


CMD_HELP.update(
    {
        "youtube": "**Plugin : **`youtube`\
        \n\n  •  **Syntax :** `.yt` <jumlah> <query>\
        \n  •  **Function : **Melakukan Pencarian YouTube. Dapat menentukan jumlah hasil yang dibutuhkan (default adalah 5)\
    "
    }
)


CMD_HELP.update(
    {
        "google": "**Plugin : **`google`\
        \n\n  •  **Syntax :** `.google` <flags> <query>\
        \n  •  **Function : **Untuk Melakukan pencarian di google (default 5 hasil pencarian)\
        \n  •  **Flags :** `-l` **= Untuk jumlah hasil pencarian.**\
        \n  •  **Example :** `.google -l4 mrismanaziz` atau `.google mrismanaziz`\
    "
    }
)


CMD_HELP.update(
    {
        "wiki": "**Plugin : **`wiki`\
        \n\n  •  **Syntax :** `.wiki` <query>\
        \n  •  **Function : **Melakukan pencarian di Wikipedia.\
    "
    }
)


CMD_HELP.update(
    {
        "barcode": "**Plugin : **`barcode`\
        \n\n  •  **Syntax :** `.barcode` <content>\
        \n  •  **Function :** Buat Kode Batang dari konten yang diberikan.\
        \n\n  •  **Example :** `.barcode www.google.com`\
        \n\n  •  **Syntax :** `.makeqr` <content>\
        \n  •  **Function :** Buat Kode QR dari konten yang diberikan.\
        \n\n  •  **Example :** `.makeqr www.google.com`\
        \n\n  •  **NOTE :** Gunakan .decode <reply to barcode / qrcode> untuk mendapatkan konten yang didekodekan.\
    "
    }
)


CMD_HELP.update(
    {
        "image_search": "**Plugin : **`image_search`\
        \n\n  •  **Syntax :** `.img` <search_query>\
        \n  •  **Function : **Melakukan pencarian gambar di Google dan menampilkan 15 gambar.\
    "
    }
)


CMD_HELP.update(
    {
        "ytdl": "**Plugin : **`ytdl`\
        \n\n  •  **Syntax :** `.ytaudio` <url>\
        \n  •  **Function : **Untuk Mendownload lagu dari YouTube.\
        \n\n  •  **Syntax :** `.ytvideo` <url>\
        \n  •  **Function : **Untuk Mendownload video dari YouTube.\
    "
    }
)


CMD_HELP.update(
    {
        "screenshot": "**Plugin : **`screenshot`\
        \n\n  •  **Syntax :** `.ss` <url>\
        \n  •  **Function : **Mengambil tangkapan layar dari situs web dan mengirimkan tangkapan layar.\
        \n  •  **Example  : .ss http://www.google.com\
    "
    }
)


CMD_HELP.update(
    {
        "currency": "**Plugin : **`currency`\
        \n\n  •  **Syntax :** `.currency` <amount> <from> <to>\
        \n  •  **Function : **Mengonversi berbagai mata uang untuk Anda.\
    "
    }
)


CMD_HELP.update(
    {
        "ud": "**Plugin : **`Urban Dictionary`\
        \n\n  •  **Syntax :** `.ud` <query>\
        \n  •  **Function : **Melakukan pencarian di Urban Dictionary.\
    "
    }
)
