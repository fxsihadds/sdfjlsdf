from CaptchaGenerator.CaptchaGenerator import Captcha


async def user_captcha(bot, cmd):
    CaptchaEquation, CaptchaCorrect = Captcha.CaptchaGeneratorMath()
    CaptchaMath = await cmd.reply_text(f"<b>🔢 Solve The Equation : {CaptchaEquation} </b>")
    GetSolve = await cmd.chat.ask("<b>📝 Solve Insert The Equation : </b>")
    if int(GetSolve.text) == CaptchaCorrect:
        await bot.delete_messages(chat_id=cmd.chat.id, message_ids=[CaptchaMath.id, GetSolve.id, cmd.id], revoke=True)
        return True
        # data_user.append(message.from_user.id)
    else:
        await cmd.reply_text("Captcha is Wrong!! ❌")
        await bot.delete_messages(chat_id=cmd.chat.id, message_ids=[CaptchaMath.id, GetSolve.id, cmd.id], revoke=True)
        return False
