import psutil
import platform
from pyrogram import Client, filters


@Client.on_message(filters.command("sysinfo", ["/", "."]))
async def system_info(client, message):
    uname = platform.uname()
    svmem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    response = f"""
**System Information:**
**System:** `{uname.system}`
**Node Name:** `{uname.node}`
**Release:** `{uname.release}`
**Version:** `{uname.version}`
**Machine:** `{uname.machine}`
**Processor:** `{uname.processor}`

**Memory Information:**
**Total:** `{get_size(svmem.total)}`
**Available:** `{get_size(svmem.available)}`
**Used:** `{get_size(svmem.used)}`
**Percentage:** `{svmem.percent}%`

**Disk Information:**
**Total:** `{get_size(disk.total)}`
**Used:** `{get_size(disk.used)}`
**Free:** `{get_size(disk.free)}`
**Percentage:** `{disk.percent}%`
    """

    await message.reply(response)


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor
