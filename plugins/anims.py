import asyncio
import random

from kelra.helpers import CMD, Quotly

DEFAULTUSER = "Nay"


NOBLE = [
    "╲╲╲┏━━┓╭━━━╮╱╱╱\n╲╲╲┗┓┏┛┃╭━╮┃╱╱╱\n╲╲╲╲┃┃┏┫┃╭┻┻┓╱╱\n╱╱╱┏╯╰╯┃╰┫┏━╯╱╱\n╱╱┏┻━┳┳┻━┫┗┓╱╱╱\n╱╱╰━┓┃┃╲┏┫┏┛╲╲╲\n╱╱╱╱┃╰╯╲┃┃┗━╮╲╲\n╱╱╱╱╰━━━╯╰━━┛╲╲",
    "┏━╮\n┃▔┃▂▂┏━━┓┏━┳━━━┓\n┃▂┣━━┻━╮┃┃▂┃▂┏━╯\n┃▔┃▔╭╮▔┃┃┃▔┃▔┗━┓\n┃▂┃▂╰╯▂┃┗╯▂┃▂▂▂┃\n┃▔┗━━━╮┃▔▔▔┃▔┏━╯\n┃▂▂▂▂▂┣╯▂▂▂┃▂┗━╮\n┗━━━━━┻━━━━┻━━━┛",
    "┏┓┏━┳━┳━┳━┓\n┃┗┫╋┣┓┃┏┫┻┫\n┗━┻━┛┗━┛┗━┛\n────­­­­­­­­­YOU────",
    "╦──╔╗─╗╔─╔ ─\n║──║║─║║─╠ ─\n╚═─╚╝─╚╝─╚ ─\n╦─╦─╔╗─╦╦   \n╚╦╝─║║─║║ \n─╩──╚╝─╚╝",
    "╔══╗....<3 \n╚╗╔╝..('\\../') \n╔╝╚╗..( •.• ) \n╚══╝..(,,)(,,) \n╔╗╔═╦╦╦═╗ ╔╗╔╗ \n║╚╣║║║║╩╣ ║╚╝║ \n╚═╩═╩═╩═╝ ╚══╝",
    "░I░L░O░V░E░Y░O░U░",
    "┈┈╭━╱▔▔▔▔╲━╮┈┈┈\n┈┈╰╱╭▅╮╭▅╮╲╯┈┈┈\n╳┈┈▏╰┈▅▅┈╯▕┈┈┈┈\n┈┈┈╲┈╰━━╯┈╱┈┈╳┈\n┈┈┈╱╱▔╲╱▔╲╲┈┈┈┈\n┈╭━╮▔▏┊┊▕▔╭━╮┈╳\n┈┃┊┣▔╲┊┊╱▔┫┊┃┈┈\n┈╰━━━━╲╱━━━━╯┈╳",
    "╔ღ═╗╔╗\n╚╗╔╝║║ღ═╦╦╦═ღ\n╔╝╚╗ღ╚╣║║║║╠╣\n╚═ღ╝╚═╩═╩ღ╩═╝",
    "╔══╗ \n╚╗╔╝ \n╔╝(¯'v'¯) \n╚══'.¸./\n╔╗╔═╦╦╦═╗ ╔╗╔╗ \n║╚╣║║║║╩╣ ║╚╝║ \n╚═╩═╩═╩═╝ ╚══╝",
    "╔╗ \n║║╔═╦═╦═╦═╗ ╔╦╗ \n║╚╣╬╠╗║╔╣╩╣ ║║║ \n╚═╩═╝╚═╝╚═╝ ╚═╝ \n╔═╗ \n║═╬═╦╦╦═╦═╦═╦═╦═╗ \n║╔╣╬║╔╣╩╬╗║╔╣╩╣╔╝ \n╚╝╚═╩╝╚═╝╚═╝╚═╩╝",
    "╔══╗ \n╚╗╔╝ \n╔╝╚╗ \n╚══╝ \n╔╗ \n║║╔═╦╦╦═╗ \n║╚╣║║║║╚╣ \n╚═╩═╩═╩═╝ \n╔╗╔╗ ♥️ \n║╚╝╠═╦╦╗ \n╚╗╔╣║║║║ \n═╚╝╚═╩═╝",
    "╔══╗╔╗  ♡ \n╚╗╔╝║║╔═╦╦╦╔╗ \n╔╝╚╗║╚╣║║║║╔╣ \n╚══╝╚═╩═╩═╩═╝\n­­­─────­­­­­­­­­YOU─────",
    "╭╮╭╮╮╭╮╮╭╮╮╭╮╮ \n┃┃╰╮╯╰╮╯╰╮╯╰╮╯ \n┃┃╭┳━━┳━╮╭━┳━━╮ \n┃┃┃┃╭╮┣╮┃┃╭┫╭╮┃ \n┃╰╯┃╰╯┃┃╰╯┃┃╰┻┻╮ \n╰━━┻━━╯╰━━╯╰━━━╯",
    "┊┊╭━╮┊┊┊┊┊┊┊┊┊┊┊ \n━━╋━╯┊┊┊┊┊┊┊┊┊┊┊ \n┊┊┃┊╭━┳╮╭┓┊╭╮╭━╮ \n╭━╋━╋━╯┣╯┃┊┃╰╋━╯ \n╰━╯┊╰━━╯┊╰━┛┊╰━━",
]


__MODULES__ = "Animasi"
__HELP__ = """<blockquote>Command Help **Animasi**</blockquote>

<blockquote expandable>        <u>**All command**</u>
    <u>**You can use this command for anims**</u>
        `{0}dino` `{0}nakal` `{0}ange` 
        `{0}kocok` `{0}hack` `{0}syg`
        `{0}kntl` `{0}ajg` `{0}heli`
        `{0}nah` `{0}piss` `{0}hmm`
        `{0}tank` `{0}awk` `{0}loveyou`
        `{0}lipkol` `{0}rumah` `{0}tembak`
        `{0}bundir` `{0}y` `{0}tq`</blockquote>
    
<b>   {1}</b>
"""


@CMD.UBOT("loveyou")
async def lopeyo(client, message):
    noble = random.randint(1, len(NOBLE) - 2)
    reply_text = NOBLE[noble]
    await message.reply(reply_text)


@CMD.UBOT("hmm")
async def hmmm(client, message):
    return await message.reply(
        "┈┈╱▔▔▔▔▔╲┈┈┈HM┈HM\n┈╱┈┈╱▔╲╲╲▏┈┈┈HMMM\n╱┈┈╱━╱▔▔▔▔▔╲━╮┈┈\n▏┈▕┃▕╱▔╲╱▔╲▕╮┃┈┈\n▏┈▕╰━▏▊▕▕▋▕▕━╯┈┈\n╲┈┈╲╱▔╭╮▔▔┳╲╲┈┈┈\n┈╲┈┈▏╭━━━━╯▕▕┈┈┈\n┈┈╲┈╲▂▂▂▂▂▂╱╱┈┈┈\n┈┈┈┈▏┊┈┈┈┈┊┈┈┈╲\n┈┈┈┈▏┊┈┈┈┈┊▕╲┈┈╲\n┈╱▔╲▏┊┈┈┈┈┊▕╱▔╲▕\n┈▏┈┈┈╰┈┈┈┈╯┈┈┈▕▕\n┈╲┈┈┈╲┈┈┈┈╱┈┈┈╱┈╲\n┈┈╲┈┈▕▔▔▔▔▏┈┈╱╲╲╲▏\n┈╱▔┈┈▕┈┈┈┈▏┈┈▔╲▔▔\n┈╲▂▂▂╱┈┈┈┈╲▂▂▂╱┈ ",
    )


@CMD.UBOT("kntl")
async def kntl(client, message):
    emoji = client.get_text(message)
    kontol = Quotly.GAMBAR_KONTOL
    if emoji:
        kontol = kontol.replace("⡀", emoji)
    await message.reply(kontol)


@CMD.UBOT("penis")
async def pns(client, message):
    emoji = client.get_text(message)
    titid = Quotly.GAMBAR_TITIT
    if emoji:
        titid = titid.replace("😋", emoji)
    await message.reply(titid)


@CMD.UBOT("heli")
async def helikopter(client, message):
    await message.reply(
        "▬▬▬.◙.▬▬▬ \n"
        "═▂▄▄▓▄▄▂ \n"
        "◢◤ █▀▀████▄▄▄▄◢◤ \n"
        "█▄ █ █▄ ███▀▀▀▀▀▀▀╬ \n"
        "◥█████◤ \n"
        "══╩══╩══ \n"
        "╬═╬ \n"
        "╬═╬ \n"
        "╬═╬ \n"
        "╬═╬ \n"
        "╬═╬ \n"
        "╬═╬ \n"
        "╬═╬ Hallo Semuanya :) \n"
        "╬═╬☻/ \n"
        "╬═╬/▌ \n"
        "╬═╬/ \\ \n",
    )


@CMD.UBOT("tembak")
async def dornembak(client, message):
    await message.reply(
        "_/﹋\\_\n" " (҂`_´)\n" "<,︻╦╤─ ҉\n" r"_/﹋\_" "\n<b>Mau Jadi Pacarku Gak?!</b>",
    )


@CMD.UBOT("bundir")
async def ngebundir(client, message):
    await message.reply(
        "`Dadah Semuanya...`          \n　　　　　|"
        "\n　　　　　| \n"
        "　　　　　| \n"
        "　　　　　| \n"
        "　　　　　| \n"
        "　　　　　| \n"
        "　　　　　| \n"
        "　　　　　| \n"
        "　／￣￣＼| \n"
        "＜ ´･ 　　 |＼ \n"
        "　|　３　 | 丶＼ \n"
        "＜ 、･　　|　　＼ \n"
        "　＼＿＿／∪ _ ∪) \n"
        "　　　　　 Ｕ Ｕ\n",
    )


@CMD.UBOT("awk")
async def awikwok(client, message):
    await message.reply(
        "────██──────▀▀▀██\n" "──▄▀█▄▄▄─────▄▀█▄▄▄\n" "▄▀──█▄▄──────█─█▄▄\n" "─▄▄▄▀──▀▄───▄▄▄▀──▀▄\n" "─▀───────▀▀─▀───────▀▀\n`Awkwokwokwok..`",
    )


@CMD.UBOT("y")
async def ysaja(client, message):
    await message.reply(
        "‡‡‡‡‡‡‡‡‡‡‡‡▄▄▄▄\n"
        "‡‡‡‡‡‡‡‡‡‡‡█‡‡‡‡█\n"
        "‡‡‡‡‡‡‡‡‡‡‡█‡‡‡‡█\n"
        "‡‡‡‡‡‡‡‡‡‡█‡‡‡‡‡█\n"
        "‡‡‡‡‡‡‡‡‡█‡‡‡‡‡‡█\n"
        "██████▄▄█‡‡‡‡‡‡████████▄\n"
        "▓▓▓▓▓▓█‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡█\n"
        "▓▓▓▓▓▓█‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡█\n"
        "▓▓▓▓▓▓█‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡█\n"
        "▓▓▓▓▓▓█‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡█\n"
        "▓▓▓▓▓▓█‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡‡█\n"
        "▓▓▓▓▓▓█████‡‡‡‡‡‡‡‡‡‡‡‡██\n"
        "█████‡‡‡‡‡‡‡██████████\n",
    )


@CMD.UBOT("tank")
async def tank(client, message):
    await message.reply(
        "█۞███████]▄▄▄▄▄▄▄▄▄▄▃ \n" "▂▄▅█████████▅▄▃▂…\n" "[███████████████████]\n" "◥⊙▲⊙▲⊙▲⊙▲⊙▲⊙▲⊙◤\n",
    )


@CMD.UBOT("babi")
async def babi(client, message):
    await message.reply(
        "┈┈┏━╮╭━┓┈╭━━━━╮\n" "┈┈┃┏┗┛┓┃╭┫Ngok ┃\n" "┈┈╰┓▋▋┏╯╯╰━━━━╯\n" "┈╭━┻╮╲┗━━━━╮╭╮┈\n" "┈┃▎▎┃╲╲╲╲╲╲┣━╯┈\n" "┈╰━┳┻▅╯╲╲╲╲┃┈┈┈\n" "┈┈┈╰━┳┓┏┳┓┏╯┈┈┈\n" "┈┈┈┈┈┗┻┛┗┻┛┈┈┈┈\n",
    )


@CMD.UBOT("ange")
async def piciieess(client, message):
    e = await message.edit("Ayanggg 😖")
    await asyncio.sleep(2)
    await e.edit("Aku Ange 😫")
    await asyncio.sleep(2)
    await e.edit("Ayuukk Picies Yang 🤤")


@CMD.UBOT("lipkol")
async def lipkoll(client, message):
    e = await message.edit("Ayanggg 😖")
    await asyncio.sleep(2)
    await e.edit("Kangeeen 👉👈")
    await asyncio.sleep(2)
    await e.edit("Pingiinn Slipkool Yaaang 🥺👉👈")


@CMD.UBOT("nakal")
async def nakall(client, message):
    e = await message.edit("Ayanggg ih🥺")
    await asyncio.sleep(2)
    await e.edit("Nakal Banget Dah Ayang 🥺")
    await asyncio.sleep(2)
    await e.edit("Aku Gak Like Ayang 😠")
    await asyncio.sleep(2)
    await e.edit("Pokoknya Aku Gak Like Ih 😠")


@CMD.UBOT("piss")
async def peace(client, message):
    await message.reply(
        "┈┈┈┈PEACE MAN┈┈┈┈\n" "┈┈┈┈┈┈╭╮╭╮┈┈┈┈┈┈\n" "┈┈┈┈┈┈┃┃┃┃┈┈┈┈┈┈\n" "┈┈┈┈┈┈┃┃┃┃┈┈┈┈┈┈\n" "┈┈┈┈┈┈┃┗┛┣┳╮┈┈┈┈\n" "┈┈┈┈┈╭┻━━┓┃┃┈┈┈┈\n" "┈┈┈┈┈┃╲┏━╯┻┫┈┈┈┈\n" "┈┈┈┈┈╰╮╯┊┊╭╯┈┈┈┈\n",
    )


@CMD.UBOT("spongebob")
async def spongebobss(client, message):
    await message.reply(
        "╲┏━┳━━━━━━━━┓╲╲\n" "╲┃◯┃╭┻┻╮╭┻┻╮┃╲╲\n" "╲┃╮┃┃╭╮┃┃╭╮┃┃╲╲\n" "╲┃╯┃┗┻┻┛┗┻┻┻┻╮╲\n" "╲┃◯┃╭╮╰╯┏━━━┳╯╲\n" "╲┃╭┃╰┏┳┳┳┳┓◯┃╲╲\n" "╲┃╰┃◯╰┗┛┗┛╯╭┃╲╲\n",
    )


@CMD.UBOT("kocok")
async def kocokk(client, message):
    e = await message.edit("KOCOKINNNN SAYANGG🥵")
    await asyncio.sleep(0.2)
    await e.edit("8✊===D")
    await asyncio.sleep(0.2)
    await e.edit("8=✊==D")
    await asyncio.sleep(0.2)
    await e.edit("8==✊=D")
    await asyncio.sleep(0.2)
    await e.edit("8===✊D")
    await asyncio.sleep(0.2)
    await e.edit("8==✊=D")
    await asyncio.sleep(0.2)
    await e.edit("8=✊==D")
    await asyncio.sleep(0.2)
    await e.edit("8✊===D")
    await asyncio.sleep(0.2)
    await e.edit("8=✊==D")
    await asyncio.sleep(0.2)
    await e.edit("8==✊=D")
    await asyncio.sleep(0.2)
    await e.edit("8===✊D")
    await asyncio.sleep(0.2)
    await e.edit("8==✊=D")
    await asyncio.sleep(0.2)
    await e.edit("8=✊==D")
    await asyncio.sleep(0.2)
    await e.edit("8✊===D")
    await asyncio.sleep(0.2)
    await e.edit("8=✊==D")
    await asyncio.sleep(0.2)
    await e.edit("8==✊=D")
    await asyncio.sleep(0.2)
    await e.edit("8===✊D")
    await asyncio.sleep(0.2)
    await e.edit("8==✊=D")
    await asyncio.sleep(0.2)
    await e.edit("8=✊==D")
    await asyncio.sleep(0.2)
    await e.edit("8===✊D💦")
    await asyncio.sleep(0.2)
    await e.edit("8==✊=D💦💦")
    await asyncio.sleep(0.2)
    await e.edit("8=✊==D💦💦💦")
    await asyncio.sleep(0.2)
    await e.edit("8✊===D💦💦💦💦")
    await asyncio.sleep(0.2)
    await e.edit("8===✊D💦💦💦💦💦")
    await asyncio.sleep(0.2)
    await e.edit("8==✊=D💦💦💦💦💦💦")
    await asyncio.sleep(0.2)
    await e.edit("8=✊==D💦💦💦💦💦💦💦")
    await asyncio.sleep(0.2)
    await e.edit("8✊===D💦💦💦💦💦💦💦💦")
    await asyncio.sleep(0.2)
    await e.edit("8===✊D💦💦💦💦💦💦💦💦💦")
    await asyncio.sleep(0.2)
    await e.edit("8==✊=D💦💦💦💦💦💦💦💦💦💦")
    await asyncio.sleep(0.2)
    await e.edit("**CROOTTTT**")
    await asyncio.sleep(0.2)
    await e.edit("**CROOTTTT AAAHHH.....**")
    await asyncio.sleep(0.2)
    await e.edit("AHHH ENAKKKKK SAYANGGGG🥵🥵**")


@CMD.UBOT("dino")
async def adadino(client, message):
    typew = await message.edit("`DIN DINNN.....`")
    await asyncio.sleep(1)
    await typew.edit("`DINOOOOSAURUSSSSS!!`")
    await asyncio.sleep(1)
    await typew.edit("`🏃                        🦖`")
    await typew.edit("`🏃                       🦖`")
    await typew.edit("`🏃                      🦖`")
    await typew.edit("`🏃                     🦖`")
    await typew.edit("`🏃   `LARII`          🦖`")
    await typew.edit("`🏃                   🦖`")
    await typew.edit("`🏃                  🦖`")
    await typew.edit("`🏃                 🦖`")
    await typew.edit("`🏃                🦖`")
    await typew.edit("`🏃               🦖`")
    await typew.edit("`🏃              🦖`")
    await typew.edit("`🏃             🦖`")
    await typew.edit("`🏃            🦖`")
    await typew.edit("`🏃           🦖`")
    await typew.edit("`🏃WOARGH!   🦖`")
    await typew.edit("`🏃           🦖`")
    await typew.edit("`🏃            🦖`")
    await typew.edit("`🏃             🦖`")
    await typew.edit("`🏃              🦖`")
    await typew.edit("`🏃               🦖`")
    await typew.edit("`🏃                🦖`")
    await typew.edit("`🏃                 🦖`")
    await typew.edit("`🏃                  🦖`")
    await typew.edit("`🏃                   🦖`")
    await typew.edit("`🏃                    🦖`")
    await typew.edit("`🏃                     🦖`")
    await typew.edit("`🏃  Huh-Huh           🦖`")
    await typew.edit("`🏃                   🦖`")
    await typew.edit("`🏃                  🦖`")
    await typew.edit("`🏃                 🦖`")
    await typew.edit("`🏃                🦖`")
    await typew.edit("`🏃               🦖`")
    await typew.edit("`🏃              🦖`")
    await typew.edit("`🏃             🦖`")
    await typew.edit("`🏃            🦖`")
    await typew.edit("`🏃           🦖`")
    await typew.edit("`🏃          🦖`")
    await typew.edit("`🏃         🦖`")
    await typew.edit("`DIA SEMAKIN MENDEKAT!!!`")
    await asyncio.sleep(1)
    await typew.edit("`🏃       🦖`")
    await typew.edit("`🏃      🦖`")
    await typew.edit("`🏃     🦖`")
    await typew.edit("`🏃    🦖`")
    await typew.edit("`Dahlah Pasrah Aja`")
    await asyncio.sleep(1)
    await typew.edit("`🧎🦖`")
    await asyncio.sleep(2)
    await typew.edit("`-TAMAT-`")


@CMD.UBOT("ajg")
async def anjg(client, message):
    await message.reply(
        "╥━━━━━━━━╭━━╮━━┳\n" "╢╭╮╭━━━━━┫┃▋▋━▅┣\n" "╢┃╰┫┈┈┈┈┈┃┃┈┈╰┫┣\n" "╢╰━┫┈┈┈┈┈╰╯╰┳━╯┣\n" "╢┊┊┃┏┳┳━━┓┏┳┫┊┊┣\n" "╨━━┗┛┗┛━━┗┛┗┛━━┻\n",
    )


@CMD.UBOT("nah")
async def nahlove(client, message):
    typew = await message.reply("`\n(\\_/)`" "`\n(●_●)`" "`\n />💖 *Ini Buat Kamu`")
    await asyncio.sleep(2)
    await typew.edit("`\n(\\_/)`" "`\n(●_●)`" "`\n💖<\\  *Tapi Bo'ong`")


@CMD.UBOT("tq")
async def _(client, message):
    await message.reply("╔══╦╗────╔╗─╔╗╔╗\n" "╚╗╔╣╚╦═╦═╣╚╗║╚╝╠═╦╦╗\n" "─║║║║║╬║║║╩║╚╗╔╣║║║║\n" "─╚╝╚╩╩╩╩╩╩╩╝─╚╝╚═╩═╝\n")


@CMD.UBOT("rumah")
async def _(client, message):
    await message.reply("╱◥◣\n" "│∩ │◥███◣ ╱◥███◣\n" "╱◥◣ ◥████◣▓∩▓│∩ ║\n" "│╱◥█◣║∩∩∩ ║◥█▓ ▓█◣\n" "││∩│ ▓ ║∩田│║▓ ▓ ▓∩ ║\n" "๑۩๑๑۩๑๑ ۩๑๑۩๑▓๑۩๑๑۩๑")


@CMD.UBOT("syg")
async def _(client, message):
    await message.edit("sayang..")
    await asyncio.sleep(3)
    await message.edit("❤️ I")
    await asyncio.sleep(0.5)
    await message.edit("❤️ I Love")
    await asyncio.sleep(0.5)
    await message.edit("❤️ I Love You")
    await asyncio.sleep(3)
    await message.edit("❤️ I Love You <3")


@CMD.UBOT("hack")
async def hack(client, message):
    await message.edit("hack akun aktif...")
    await asyncio.sleep(2)
    await message.edit(" User online: True\nTelegram access: True\nRead Storage: True ")
    await asyncio.sleep(2)
    await message.edit("Hacking... 0%\n[░░░░░░░░░░░░░░░░░░░░]\n`Looking for Telegram...`\nETA: 0m, 20s")
    await asyncio.sleep(2)
    await message.edit("Hacking... 11.07%\n[██░░░░░░░░░░░░░░░░░░]\n`Looking for Telegram...`\nETA: 0m, 18s")
    await asyncio.sleep(2)
    await message.edit("Hacking... 20.63%\n[███░░░░░░░░░░░░░░░░░]\n`Found folder C:/Telegram`\nETA: 0m, 16s")
    await asyncio.sleep(2)
    await message.edit("Hacking... 34.42%\n[█████░░░░░░░░░░░░░░░]\n`Found folder C:/Telegram`\nETA: 0m, 14s")
    await asyncio.sleep(2)
    await message.edit("Hacking... 42.17%\n[███████░░░░░░░░░░░░░]\n`Searching for databases`\nETA: 0m, 12s")
    await asyncio.sleep(2)
    await message.edit("Hacking... 55.30%\n[█████████░░░░░░░░░░░]\n`Found msgstore.db.crypt12`\nETA: 0m, 10s")
    await asyncio.sleep(2)
    await message.edit("Hacking... 64.86%\n[███████████░░░░░░░░░]\n`Found msgstore.db.crypt12`\nETA: 0m, 08s")
    await asyncio.sleep(2)
    await message.edit("Hacking... 74.02%\n[█████████████░░░░░░░]\n`Trying to Decrypt...`\nETA: 0m, 06s")
    await asyncio.sleep(2)
    await message.edit("Hacking... 86.21%\n[███████████████░░░░░]\n`Trying to Decrypt...`\nETA: 0m, 04s")
    await asyncio.sleep(2)
    await message.edit("Hacking... 93.50%\n[█████████████████░░░]\n`Decryption successful!`\nETA: 0m, 02s")
    await asyncio.sleep(2)
    await message.edit("Hacking... 100%\n[████████████████████]\n`Scanning file...`\nETA: 0m, 00s")
    await asyncio.sleep(2)
    await message.edit("Hacking complete!\nUploading file...")
    await asyncio.sleep(2)
    await message.edit("Targeted Account Hacked...!\n\n ✅ File has been successfully uploaded to my server.\nTelegram Database:\n`./DOWNLOADS/msgstore.db.crypt12`")
