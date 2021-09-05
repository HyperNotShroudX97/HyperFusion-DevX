# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)
# v3.0.10

from asyncio import gather

from pyrogram import filters

from userge import Config, Message, userge
from userge.utils import capitaled


@userge.on_cmd(
    "dz",
    about={
        "header": "Deezer Music",
        "description": "Download Music From Deezer",
        "usage": "{tr}dz [Artist Name] [Song Name] [; Number](Optional)",
    },
)
async def deezing_(message: Message):
    """Download Music From Deezer"""
    query_ = message.input_str
    if ";" in query_:
        split_ = query_.split(";", 1)
        song_, num = split_[0], split_[1]
    else:
        song_ = query_
        num = "0"
    try:
        num = int(num)
    except BaseException:
        await message.edit("Please Enter A Proper Number After ';'...", del_in=5)
        return
    bot_ = "DeezerMusicBot"
    song_ = await capitaled(song_)
    await message.edit(f"Searching <b>{song_}</b> On Deezer...")
    results = await userge.get_inline_bot_results(bot_, song_)
    if not results.results:
        await message.edit(f"Song <code>{song_}</code> Not Found...", del_in=5)
        return
    try:
        log_send = await userge.send_inline_bot_result(
            chat_id=Config.LOG_CHANNEL_ID,
            query_id=results.query_id,
            result_id=results.results[int(num)].id,
        )
        await gather(
            userge.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.LOG_CHANNEL_ID,
                message_id=log_send.updates[0].id,
            ),
            message.delete(),
        )
    except BaseException:
        await message.err(
            "Something Unexpected Happend, Please Try Again Later...", del_in=5
        )


@userge.on_cmd(
    "dzlist",
    about={
        "header": "Deezer Music List",
        "description": "Get Music List From Deezer"
        "\nSudo Users Use DZ After Getting The List",
        "usage": "{tr}dzlist [Query]",
    },
)
async def dlist_(message: Message):
    """Get List And Number Corresponding To Song's"""
    bot_ = "deezermusicbot"
    query_ = message.input_str
    if not query_:
        await message.err("Input Not Found...", del_in=5)
        return
    query_ = await capitaled(query_)
    await message.edit(f"Searching For <b>{query_}</b>...")
    result = await userge.get_inline_bot_results(bot_, query_)
    if not result:
        await message.edit(
            f"Results Not Found For <code>{query_}</code>, Try Something Else...",
            del_in=5,
        )
        return
    list_ = []
    total_ = 0
    for one in range(0, 10):
        try:
            title_ = result.results[one].document.attributes[1].file_name
            dure_ = result.results[one].document.attributes[0].duration
            min_ = dure_ / 60
            sec_ = (min_ - int(min_)) * 60
            min_ = f"{int(min_):02}"
            sec_ = f"{int(sec_):02}"
            list_.append(f"• [<b>{one}</b>] {title_} <b>({min_}:{sec_})</b>")
            total_ += 1
        except BaseException:
            break
    if not list_:
        await message.edit(
            f"Couldn't Find Results For <code>{query_}</code>...", del_in=5
        )
        return
    list_ = "\n".join(list_)
    out_ = f"Results Found For <b>{query_}</b>: [<b>{total_}</b>]\n\n"
    out_ += list_
    out_ += "\n\nReply With Corresponding Number <b>Within 20 Seconds </b> To Get The Music."
    await message.edit(out_)
    me_ = await userge.get_me()
    try:
        async with userge.conversation(message.chat.id, timeout=20) as conv:
            response = await conv.get_response(
                mark_read=True, filters=(filters.user(me_.id))
            )
            resp = response.text
            try:
                reply_ = int(resp)
            except BaseException:
                out_ += f"\n\n### The Response <b>{resp}</b> Is Not A Number, <b>Please Retry</b>. ###"
                await response.delete()
                await message.edit(out_, del_in=15)
                return
            try:
                result_id = result.results[reply_].id
            except BaseException:
                out_ += f"\n\n### Response <b>{resp}</b> Gave Out Of Index Error, <b>Please Retry</b>. ###"
                await response.delete()
                await message.edit(out_, del_in=15)
                return
            await response.delete()
    except BaseException:
        out_ += "\n\n### <b>Response Time Expired.</b> ###"
        await message.edit(out_)
        return
    try:
        log_send = await userge.send_inline_bot_result(
            chat_id=Config.LOG_CHANNEL_ID,
            query_id=result.query_id,
            result_id=result_id,
        )
        await userge.copy_message(
            chat_id=message.chat.id,
            from_chat_id=Config.LOG_CHANNEL_ID,
            message_id=log_send.updates[0].id,
        )
        out_ += f"\n\n### <b>Responded With {reply_}.</b> ###"
        await message.edit(out_)
    except BaseException:
        await message.err(
            "Something Unexpected Happend, Please Try Again Later...", del_in=5
        )
