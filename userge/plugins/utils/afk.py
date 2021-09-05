""" Setup AFK Mode """

import asyncio
import time
from random import choice, randint

from userge import Config, Message, filters, get_collection, userge
from userge.utils import time_formatter

CHANNEL = userge.getCLogger(__name__)
SAVED_SETTINGS = get_collection("CONFIGS")
AFK_COLLECTION = get_collection("AFK")

IS_AFK = False
IS_AFK_FILTER = filters.create(lambda _, __, ___: bool(IS_AFK))
REASON = ""
TIME = 0.0
USERS = {}


async def _init() -> None:
    global IS_AFK, REASON, TIME  # pylint: disable=global-statement
    data = await SAVED_SETTINGS.find_one({"_id": "AFK"})
    if data:
        IS_AFK = data["on"]
        REASON = data["data"]
        TIME = data["time"] if "time" in data else 0
    async for _user in AFK_COLLECTION.find():
        USERS.update({_user["_id"]: [_user["pcount"], _user["gcount"], _user["men"]]})


@userge.on_cmd(
    "afk",
    about={
        "Header": "Set To AFK Mode",
        "Description": "Sets Your Status As Fuckin AFK. Responds To Anyone Who Fucking Tags/PM's.\n"
        "You Telling You Are Fuckin AFK. Switches Off AFK When You Fuckin Type Back Anything.",
        "Usage": "{tr}afk Or {tr}afk [Reason]",
    },
    allow_channels=False,
)
async def active_afk(message: Message) -> None:
    """Turn On Or Off The Fuckin AFK Mode"""
    global REASON, IS_AFK, TIME  # pylint: disable=global-statement
    IS_AFK = True
    TIME = time.time()
    REASON = message.input_str
    await asyncio.gather(
        CHANNEL.log(f"You Fuckin Went AFK! : `{REASON}`"),
        message.edit("`You Fuckin Went AFK!`", del_in=1),
        AFK_COLLECTION.drop(),
        SAVED_SETTINGS.update_one(
            {"_id": "AFK"},
            {"$set": {"on": True, "data": REASON, "time": TIME}},
            upsert=True,
        ),
    )


@userge.on_filters(
    IS_AFK_FILTER
    & ~filters.me
    & ~filters.bot
    & ~filters.user(Config.TG_IDS)
    & ~filters.edited
    & (
        filters.mentioned
        | (
            filters.private
            & ~filters.service
            & (
                filters.create(lambda _, __, ___: Config.ALLOW_ALL_PMS)
                | Config.ALLOWED_CHATS
            )
        )
    ),
    allow_via_bot=False,
)
async def handle_afk_incomming(message: Message) -> None:
    """Handle Incomming Messages When You Fuckin AFK!"""
    if not message.from_user:
        return
    user_id = message.from_user.id
    chat = message.chat
    user_dict = await message.client.get_user_dict(user_id)
    afk_time = time_formatter(round(time.time() - TIME))
    coro_list = []
    if user_id in USERS:
        if not (USERS[user_id][0] + USERS[user_id][1]) % randint(2, 4):
            if REASON:
                out_str = (
                    f"I'm Still Fuckin **AFK**.\nReason: <code>{REASON}</code>\n"
                    f"Last Fuckin Seen: `{afk_time} Ago`"
                )
            else:
                out_str = choice(AFK_REASONS)
            coro_list.append(message.reply(out_str))
        if chat.type == "private":
            USERS[user_id][0] += 1
        else:
            USERS[user_id][1] += 1
    else:
        if REASON:
            out_str = (
                f"I'm Fucking **AFK** Right Now.\nReason: <code>{REASON}</code>\n"
                f"Last Fuckin Seen: `{afk_time} Ago`"
            )
        else:
            out_str = choice(AFK_REASONS)
        coro_list.append(message.reply(out_str))
        if chat.type == "private":
            USERS[user_id] = [1, 0, user_dict["mention"]]
        else:
            USERS[user_id] = [0, 1, user_dict["mention"]]
    if chat.type == "private":
        coro_list.append(
            CHANNEL.log(
                f"#PRIVATE\n{user_dict['mention']} Fuckin Send You\n\n"
                f"{message.text}"
            )
        )
    else:
        coro_list.append(
            CHANNEL.log(
                "#GROUP\n"
                f"{user_dict['mention']} Fuckin Tagged You In Fuckin [{chat.title}](http://t.me/{chat.username})\n\n"
                f"{message.text}\n\n"
                f"[Goto_Msg](https://t.me/c/{str(chat.id)[4:]}/{message.message_id})"
            )
        )
    coro_list.append(
        AFK_COLLECTION.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "pcount": USERS[user_id][0],
                    "gcount": USERS[user_id][1],
                    "men": USERS[user_id][2],
                }
            },
            upsert=True,
        )
    )
    await asyncio.gather(*coro_list)


@userge.on_filters(IS_AFK_FILTER & filters.outgoing, group=-1, allow_via_bot=False)
async def handle_afk_outgoing(message: Message) -> None:
    """Handle Outgoing Messages When You Fuckin AFK!"""
    global IS_AFK  # pylint: disable=global-statement
    IS_AFK = False
    afk_time = time_formatter(round(time.time() - TIME))
    replied: Message = await message.reply("`I'm No Fuckin Longer AFK!`", log=__name__)
    coro_list = []
    if USERS:
        p_msg = ""
        g_msg = ""
        p_count = 0
        g_count = 0
        for pcount, gcount, men in USERS.values():
            if pcount:
                p_msg += f"👤 {men} ✉️ **{pcount}**\n"
                p_count += pcount
            if gcount:
                g_msg += f"👥 {men} ✉️ **{gcount}**\n"
                g_count += gcount
        coro_list.append(
            replied.edit(
                f"`You Recieved Fuckin {p_count + g_count} Messages While You Were Fuckin Away. "
                f"Check Log For More Fucking Details.`\n\n**AFK Time** : __{afk_time}__",
                del_in=3,
            )
        )
        out_str = (
            f"You've Recieved Fuckin **{p_count + g_count}** Messages "
            + f"From **{len(USERS)}** User's While You Were Fuckin Away!\n\n**AFK Time** : __{afk_time}__\n"
        )
        if p_count:
            out_str += f"\n**{p_count} Private Messages:**\n\n{p_msg}"
        if g_count:
            out_str += f"\n**{g_count} Group Messages:**\n\n{g_msg}"
        coro_list.append(CHANNEL.log(out_str))
        USERS.clear()
    else:
        await asyncio.sleep(3)
        coro_list.append(replied.delete())
    coro_list.append(
        asyncio.gather(
            AFK_COLLECTION.drop(),
            SAVED_SETTINGS.update_one(
                {"_id": "AFK"}, {"$set": {"on": False}}, upsert=True
            ),
        )
    )
    await asyncio.gather(*coro_list)


AFK_REASONS = (
    "I'm Fuckin Busy Right Now. Please Talk In A Fuckin Bag And When I Come Back You Can Just Fuckin Give Me The Bag!",
    "I'm Away Right Now. If You Fuckin Need Anything, leave Me A Fuckin Message After The Fucking BEEP!: \
`BeeeeeFuckeeeeeeFuckeeeeeFuckeeeFuckeeeeeeeFuckeeeeeeep!`",
    "You Missed Me, Next Time Aim Better!.",
    "I'll Be Back In A Few Fuckin 696969Hrs & If I'M Not...,\nWait Fucking Longer Unill You Die!.",
    "I'm Not Here Fucking Right Now, So I'm Probably Somewhere Fuckin Else In Other Universe Or Dimensions Or Maibi In Matrix Hell!.",
    "Roses Are Red,\nViolets Are Blue,\nLeave Me A Message,\nAnd I'll Fuck Back To You.",
    "Sometimes The Best Fuckin Things In Life Are Worth Waiting For…\nI'll Be Fuckin Right Back.",
    "I'll Be Fuckin Right Back,\nBut If I'm Not Fuckin Right Back,\nI'll Be Back After 696969Hrs Or Yrs Later Maibi Depends xD!.",
    "If You Haven't Figured It Out Already,\nI'm Not Fucking Here.",
    "I'm Fucking Away Over 7 Seas & 7 Countries,\n7 Waters & 7 Continents,\n7 Mountains & 7 Hills,\
7 Plains & 7 Mounds,\n7 Pools & 7 Lakes,\n7 Springs & 7 Meadows,\
7 Cities & 7 Neighborhoods,\n7 Blocks & 7 Houses...\
    Where Not Even Your Fuckin Messages Can Reach Me!",
    "I'm Fucking Away From The Fucking Keyboard At The Fucking Moment, But If You'll Fuckin Scream Loud Enough At Your Fuckin Screen,\
    I Might Just Fuckin Hear You Maibi!.",
    "I Went That Fuckin Way!,\n>>>>>",
    "I Went This Fuckin Way!,\n<<<<<",
    "Please Leave A Fuckin Message And Make Me Feel Even More Important Than I Already Am.",
    "If I Were Fuckin Here,\nI'd Tell You Where The Fuck I Am!.\n\nBut I'm Not,\nSoo Ask Me When I Fuckin Return!...",
    "I'm Fuckin Away!\nI Don't Fuckin Know When I'll Be Fuckin Back!\nHopefully A Few 696969Hrs/Yrs From Now!!",
    "I'm Not Fuckin Available Right Now Soo Please Leave Your Fuckin Name, & Fuckin Number, \
    & Fuckin Address & I Will Fuckin Stalk You Untill You Fuckin Die!. :P",
    "Sorry, I'm Not Here Fuckin Right Now.\nFeel Free To Talk To My @HyperUsergeX_Bot As Long As You Fucking Like.\
I'll Get Fuckin Back To You Later.",
    "I Bet You Were Fuckin Expecting An Away Auto-Message Huh! ^You Kiddo Beru Die^!",
    "Life Is So Fuckin Short, There Are So Many Fuckin Things To Do...\nI'm Away Doing One Oof Them..",
    "I Am Not Here Fuckin Right Now...\nBut If I Was...\n\nWouldn't That Be Fucking Awesome?",
)
