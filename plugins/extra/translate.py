from pyrogram import filters, Client
from pyrogram.types import Message
from easygoogletranslate import EasyGoogleTranslate
from asyncio import create_task


@Client.on_message(filters.command('tr'))
async def translator(bot: Client, cmd: Message):
    sing = cmd.text.split('/tr', 1)[1].strip()
    if sing.lower() == "code":
        await cmd.reply_text("`Here is Language Code`: https://cloud.google.com/translate/docs/languages")
    elif sing.lower() == "help":
        await cmd.reply_text('`Command Like <code>/tr en </code> Reply With Any Language Texts`')
    elif len(sing) > 2:
        await cmd.reply_text('<b>`This is Not A Language Code!`</b>')
    else:
        if cmd.reply_to_message:
            if cmd.reply_to_message.text and sing:
                status = await cmd.reply_text('`Translating...`')
                create_task(translate(bot, cmd, sing, status, input=cmd.reply_to_message.text))
        else:
            await cmd.reply_text('<b>`Please Reply With Text With Language Code!`</b>')


# This is Translator Functions!
async def translate(bot, cmd, sing, status, input) -> str:
    translator = EasyGoogleTranslate(
        target_language=sing,
        timeout=10
    )
    result = translator.translate(input)
    await status.edit_text(f"""<b>
```
{result}  
```</b>""")
