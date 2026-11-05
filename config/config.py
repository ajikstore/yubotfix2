import json
import os
import sys
from base64 import b64decode

import requests
from dotenv import load_dotenv


def get_blacklist():
    try:
        aa = "aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL05hcnV0b3Jhd3IvZGV2cy9tYWluL2JsYWNrbGlzdC5qc29u="
        bb = b64decode(aa).decode("utf-8")
        res = requests.get(bb)
        if res.status_code == 200:
            return json.loads(res.text)
    except Exception as e:
        return f"An error occurred: {str(e)}"
        sys.exit(1)


load_dotenv()

HELPABLE = {}

DICT_BUTTON = {}

COPY_ID = {}

API_ID = int(os.environ.get("API_ID", 16336404))
MAX_BOT = int(os.environ.get("MAX_BOT", 500))

API_HASH = os.environ.get("API_HASH", "e0a3b47bd2784584465ab52546dc8506") 

BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot token lu")

BOT_ID = int(BOT_TOKEN.split(":")[0])

API_GEMINI = os.environ.get("API_GEMINI", "apigeminilu")

API_BOTCHAX = os.environ.get("API_BOTCHAX", "awas_ada_maling")

API_BETABOTZ = os.environ.get("API_BETABOTZ", "rahasia20")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

API_GROQ = os.environ.get("GROQ_API_KEY", "rahasia20")
API_GROQ = os.environ.get("API_GROQ", "Gsk_vCA7P0s6wy1jY27afDlO9xO6")

API_MAELYN = os.environ.get("API_MAELYN", "sk_ms_b=93e580f3=15")
U_COOKIES = os.getenv(
    "U_COOKIES",
    "177z8dNGn_x75gJwLaZNfmDg7EXLeYNle8QrBt2_6BZUDNsRjebnIrEsPjYi1pUpN85Cgas8lg19W1Kziq_QcZwb1fRKCaD636EZ5eAhdY6CXyxhie3t2o8bOAiUbdDor6rhwbh7LzlAgdUG4GTWIXGA8yHeg8aq6tNA_TyToXF77uVrRF2lAhnqBpVEsVBEW-sOd9baq5zbp0EFbXeg2oQ",
)
SRCHHPGUSR_COOKIES = os.getenv(
    "SRCHHPGUSR_COOKIES",
    "SRCHLANG=id&IG=67D2396333774399B050E814BA037A45&PREFCOL=1&CW=361&CH=612&SCW=361&SCH=612&BRW=MM&BRH=MM&DPR=1.9&UTC=420&PV=11.0.0&HV=1753217653&HVE=CfDJ8Inh5QCoSQBNls38F2rbEpQFDSnN4y8y4FTUaqL8JEbN6LbDH__2yqaT_Ahd9R4xDtijC0QCUX5sQ9MCkM1EfWlIWGRGxDgIAAx8w6FZYclifiICQkJOtE7Ab7TAVWUsDkKOKiNdYfhLeLi59_JXTQxYlHbDeFdEMACtOei9T9C5NWqGe1eR3W6QIJUq-45F1w&HBOPEN=2&DM=1&PRVCW=361&PRVCH=612",
)
COOKIE_BING = os.environ.get(
    "COOKIE_BING",
    "SRCHLANG=id&IG=67D2396333774399B050E814BA037A45&PREFCOL=1&CW=361&CH=612&SCW=361&SCH=612&BRW=MM&BRH=MM&DPR=1.9&UTC=420&PV=11.0.0&HV=1753217653&HVE=CfDJ8Inh5QCoSQBNls38F2rbEpQFDSnN4y8y4FTUaqL8JEbN6LbDH__2yqaT_Ahd9R4xDtijC0QCUX5sQ9MCkM1EfWlIWGRGxDgIAAx8w6FZYclifiICQkJOtE7Ab7TAVWUsDkKOKiNdYfhLeLi59_JXTQxYlHbDeFdEMACtOei9T9C5NWqGe1eR3W6QIJUq-45F1w&HBOPEN=2&DM=1&PRVCW=361&PRVCH=612",
)

# NAME BOR
BOT_NAME = os.environ.get("BOT_NAME", "vio ᴜʙᴏᴛ")

# NAMA DATABASE BOT 
DB_NAME = os.environ.get("DB_NAME", "vio")

# BUAT FOTO LOG
URL_LOGO = os.environ.get("URL_LOGO", "https://telegram.org/img/t_logo.png")

WAJIB_JOIN = os.environ.get("WAJIB_JOIN", "storegarf")

STORE_NAME = "storegarf"

BLACKLIST_GCAST = get_blacklist()

SUDO_OWNERS = list(
    map(
        int,
        os.environ.get(
            "SUDO_OWNERS",
            "6866643730",
        ).split(),
    )
)
DEVS = list(
    map(
        int,
        os.environ.get(
            "DEVS",
            "6866643730",
        ).split(),
    )
)

# AKSES BIKIN UBOT
AKSES_DEPLOY = list(map(int, os.environ.get("AKSES_DEPLOY", "6866643730").split()))

# ID OWNER 
OWNER_ID = int(os.environ.get("OWNER_ID", "6866643730"))

# BUAT GRUPLOG SELLER
LOG_SELLER = int(os.environ.get("LOG_SELLER", "-1004350065765"))

# BUAT GRUPLOG ERROR
LOG_ERROR = int(os.environ.get("LOG_ERROR", "-1004350065765"))

# BUAT START BOR
SUPPORT = int(os.environ.get("SUPPORT", "-1004350065765"))

# BUAT DATABASE BOT
DATABASE = int(os.environ.get("PEER", "6866643730"))

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "b4cc1b82532245b5b05a331e355068e4")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "fb110a1fddae4c659c7db16cc9f15abc")
SAWERIA_EMAIL = os.environ.get("SAWERIA_EMAIL", "")
SAWERIA_NAME = os.environ.get("SAWERIA_NAME", "")
SAWERIA_USERID = os.environ.get("SAWERIA_USERID", "")
FAKE_DEVS = list(map(int, os.environ.get("FAKE_DEVS", "6866643730").split()))

# BUAT DEVELOPER 
KELRA = list(map(int, os.environ.get("KELRA", "6866643730").split()))
if OWNER_ID not in SUDO_OWNERS:
    SUDO_OWNERS.append(OWNER_ID)
if OWNER_ID not in DEVS:
    DEVS.append(OWNER_ID)
if OWNER_ID not in FAKE_DEVS:
    FAKE_DEVS.append(OWNER_ID)
for P in FAKE_DEVS:
    if P not in DEVS:
        DEVS.append(P)
    if P not in SUDO_OWNERS:
        SUDO_OWNERS.append(P)
