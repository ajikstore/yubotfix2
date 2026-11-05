from kelra.helpers import CMD, Emoji, Tools
from kelra.database import dB
import datetime

__MODULES__ = "Bola"
__HELP__ = """<blockquote>Command Help **Bola**</blockquote>
<blockquote expandable>
• <code>{0}bola</code>: Menampilkan jadwal bola hari ini.
</blockquote>"""

__CATEGORY__ = "search <emoji id=5017088445353296841>🔍</emoji>"

@CMD.UBOT("bola")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await message.reply(f"{emo.proses} **Mengambil data bola (Personal API)...**")
    
    # API Key Pribadi Lu
    api_key = "52d99a7ffb8b0505069a20865734e3e2"
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://apiv3.apifootball.com/?action=get_events&from={today}&to={today}&APIkey={api_key}"
    
    try:
        res = await Tools.fetch.get(url)
        data = res.json()
        
        # Validasi jika API tidak mengembalikan error
        if data and not isinstance(data, dict) or "error" not in data:
            # Simpan ke cache jika data valid
            if data:
                await dB.set_var(client.me.id, "CACHE_BOLA", data)
            
            teks = "<blockquote><b>⚽ JADWAL BOLA HARI INI</b></blockquote>\n\n"
            if not data:
                teks += "<i>Tidak ada pertandingan hari ini.</i>"
            else:
                for match in data[:6]: 
                    teks += f"<blockquote expandable><b>{match['match_hometeam_name']} vs {match['match_awayteam_name']}</b>\n"
                    teks += f"🕒 <b>Jam:</b> {match['match_time']}\n"
                    teks += f"🏟 <b>Liga:</b> {match['league_name']}</blockquote>\n"
            
            await pros.edit(teks, disable_web_page_preview=True)
            
        else:
            # Mode Offline jika API error
            cached_data = await dB.get_var(client.me.id, "CACHE_BOLA")
            if cached_data:
                teks = "<blockquote><b>⚽ DATA CACHE (OFFLINE MODE)</b></blockquote>\n\n"
                for match in cached_data[:6]:
                    teks += f"<blockquote expandable><b>{match['match_hometeam_name']} vs {match['match_awayteam_name']}</b>\n"
                    teks += f"🕒 <b>Jam:</b> {match['match_time']} (Data Terakhir)</blockquote>\n"
                await pros.edit(teks)
            else:
                await pros.edit(f"{emo.gagal} **Data bola tidak tersedia.**")
                
    except Exception as e:
        await pros.edit(f"{emo.gagal} **Error:** `Server sedang sibuk.`")
