# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)

from pyrogram.errors import YouBlockedUser

from userge import Message, userge


@userge.on_cmd(
    "fstat",
    about={
        "header": "Fstat of user",
        "description": "fetch fstat of user using @missrose_bot",
        "usage": "{tr}fstat [UserID/username] or [reply to user]",
    },
)
async def f_stat(message: Message):
    """Fstat Of User"""
    reply = message.reply_to_message
    user_ = message.input_str if not reply else reply.from_user.id
    if not user_:
        user_ = message.from_user.id
    try:
        get_u = await userge.get_users(user_)
        user_name = " ".join([get_u.first_name, get_u.last_name or ""])
        user_id = get_u.id
    except BaseException:
        await message.edit(
            f"Fetching Fstat Of User <b>{user_}</b>...\nWARNING: User Not Found In Your Database, Checking Rose's Fucking Database."
        )
        user_name = user_
        user_id = user_
    await message.edit(
        f"Fetching Fstat Of User <a href='tg://user?id={user_id}'><b>{user_name}</b></a>..."
    )
    bot_ = "MissRose_Bot"
    async with userge.conversation(bot_, timeout=1000) as conv:
        try:
            await conv.send_message(f"/fstat {user_id}")
        except YouBlockedUser:
            await message.err("Unblock Bish @missrose_bot First...", del_in=5)
            return
        response = await conv.get_response(mark_read=True)
    fail = "Could Not Find A User"
    resp = response.text
    if fail in resp:
        await message.edit(
            f"User <code>{user_name}</code> Could Not Be Found In @MissRose_bot's Fucking Database."
        )
    else:
        await message.edit(resp.html, parse_mode="html")
