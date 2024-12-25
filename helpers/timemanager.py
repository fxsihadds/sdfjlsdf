import time
import os
from helpers.s_captcha import user_captcha
import asyncio
from typing import Callable, Union
from functools import wraps
from pyrogram.types import Message, CallbackQuery
from pyrogram import enums
from helpers.pylimitars import Ratelimiter
from time import perf_counter


# Dictionary to store the last invocation time of each user
last_command_time = {}

# Ensure a Consistent event loop!
def get_or_create_event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


loop = get_or_create_event_loop()

# Define a threshold for the time difference (e.g., 15 seconds)
COMMAND_THRESHOLD = 15


async def time_limit(bot, cmd):
    try:
        user_id = cmd.from_user.id
        current_time = time.time()
        if user_id in last_command_time:
            time_diff = current_time - last_command_time[user_id]
            if time_diff < COMMAND_THRESHOLD:
                # Require captcha
                captcha = await user_captcha(bot, cmd)
                if not captcha:
                    return False
        last_command_time[user_id] = current_time
        print(last_command_time)
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        await cmd.reply_text('An error occurred while processing your request.')
        return False


def create_task_for_user(func: Callable) -> Callable:
    '''
    Decorator that runs the decorated function in a thread pool executor.
    '''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await loop.run_in_executor(None, func, *args, **kwargs)

    return wrapper


def run_sync_in_thread(func: Callable) -> Callable:
    """
        A decorator for running a synchronous long running function asynchronously in a separate thread,
        without blocking the main event loop which make bot unresponsive.

        To use this decorator, apply it to any synchronous function, then you can then call that function to anywhere
        in your program and can use it along with await keyword. This will allow the function to be run asynchronously,
        and avoid blocking of the main event loop.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await loop.run_in_executor(None, func, *args, **kwargs)

    return wrapper


def run_sync_in_thread_running_loop(func: Callable) -> Callable:
    """
    A decorator for running a synchronous long-running function asynchronously in a separate thread,
    without blocking the main event loop which makes the bot unresponsive.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()  # Get the current running event loop
        return await loop.run_in_executor(None, func, *args, **kwargs)

    return wrapper




def Admin_Check(func: Callable) -> bool:
    '''
    ->For Check ADMIN or Sudu Users 
    '''
    @wraps(func)
    async def wrapper(cmd):
        try:
            if not cmd.from_user: return False
            if cmd.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]: return False
            client = cmd._client
            chat_id = cmd.chat.id
            user_id = cmd.from_user.id
            check_status = await client.get_chat_member(chat_id=chat_id, user_id=user_id)
            admin_strings = [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
            if check_status.status not in admin_strings:return False
            else:
                return True
        except Exception as err:
            cmd.reply_text(f'Something went Wrongs: {err}')


    return wrapper


def error(func: Callable) -> Callable:
    '''
    This is not very much usefull but sometimes need it, 
    when you need to catch a error by decorator!
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"From Func {e}")

    return wrapper


# this func for any functions execute as a new thread its event loop Altranative
def to_thread_task(func):

    @wraps
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


def get_time(func: Callable) -> Callable:

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = perf_counter()
        await func(*args, **kwargs)
        end_time = perf_counter()
        print(f'Takes {end_time-start_time:.3f} Seconds')

    return wrapper


# Create an instance of Ratelimiter
rate_limiter = Ratelimiter()


def ratelimiters(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(bot, cmd: Union[Message, CallbackQuery]):  # type: ignore
        user_id = cmd.from_user.id
        # Corrected to await the instance method
        is_limited = await rate_limiter.acquire(user_id=user_id)
        if is_limited:
            if isinstance(cmd, Message):  # type: ignore
                await cmd.reply_text('Spam Detected!, Wait Few Minutes!')
            elif isinstance(cmd, CallbackQuery):  # type: ignore
                await cmd.answer('Spam Detected!, Wait Few Minutes!', show_alert=True)
        else:
            return await func(bot, cmd)

    return wrapper



def run_sync_in_thread_new_loop(func: Callable) -> Callable:
    """
    A decorator for running a synchronous long-running function asynchronously in a separate thread,
    without blocking the main event loop which makes the bot unresponsive.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loops = asyncio.new_event_loop()  # Get the current running event loop
        return await loops.run_in_executor(None, func, *args, **kwargs)

    return wrapper

