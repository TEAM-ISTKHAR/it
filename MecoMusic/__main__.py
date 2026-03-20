import asyncio
import importlib
import logging

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from MecoMusic import LOGGER, app, userbot
from MecoMusic.core.call import Siddu
from MecoMusic.misc import sudo
from MecoMusic.plugins import ALL_MODULES
from MecoMusic.utils.database import get_banned_users, get_gbanned
from MecoMusic.utils.retry import async_retry
from config import BANNED_USERS

loop = asyncio.get_event_loop()

@async_retry(retries=3, delay=2.0, exceptions=(Exception,))
async def load_banned_users():
    users = await get_gbanned()
    for user_id in users:
        BANNED_USERS.add(user_id)
    users = await get_banned_users()
    for user_id in users:
        BANNED_USERS.add(user_id)

@async_retry(retries=3, delay=2.0, exceptions=(Exception,))
async def start_stream():
    await Siddu.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
    
    try:
        await sudo()
        await load_banned_users()
    except Exception as e:
        LOGGER(__name__).error(f"Error loading banned users: {e}")
        
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("MecoMusic.plugins" + all_module)
    LOGGER("MecoMusic.plugins").info("Successfully Imported Modules...")
    
    await userbot.start()
    await Siddu.start()
    
    try:
        await start_stream()
    except NoActiveGroupCall:
        LOGGER("MecoMusic").error(
            "Please turn on the videochat of your log group channel.\n\nStopping Bot..."
        )
        exit()
    except Exception as e:
        LOGGER("MecoMusic").error(f"Error in stream call: {e}")
        
    await Siddu.decorators()
    await idle()
    await app.stop()
    LOGGER("MecoMusic").info("Stopping MecoMusic...")

if __name__ == "__main__":
    loop.run_until_complete(init())
