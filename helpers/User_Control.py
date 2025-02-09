from datetime import datetime, timedelta
from database.connects import connect_db
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

subscriptions = connect_db()  # MongoDB Connection Setup


class Subscription:
    def __init__(self, user_id):
        self.user_id = user_id

    def has_used_free_trial(self):
        return (
            subscriptions.find_one({"user_id": self.user_id, "plan": "free_trial"})
            is not None
        )

    def start_subscription(self, plan):
        plans = {"free_trial": timedelta(hours=1), "weekly": timedelta(days=7)}

        if plan == "free_trial" and self.has_used_free_trial():
            return {
                "status": "error",
                "message": "You have already used the free trial!",
            }

        start_date = datetime.now()
        end_date = start_date + plans.get(plan, timedelta(days=0))

        subscription_data = {
            "user_id": self.user_id,
            "plan": plan,
            "start_date": start_date,
            "end_date": end_date,
            "status": "Active",
        }
        subscriptions.insert_one(subscription_data)
        return {
            "status": "success",
            "message": f"Subscription {plan} activated until {end_date}",
        }

    def is_active(self):
        sub = subscriptions.find_one({"user_id": self.user_id, "status": "Active"})
        #print(sub['end_date'])
        #print(sub['user_id'])
        if sub and datetime.now() < sub["end_date"]:
            return True
        else:
            subscriptions.update_one(
                {"user_id": self.user_id}, {"$set": {"status": "Expired"}}
            )
            return False

    def renew_subscription(self, plan):
        plans = {"weekly": timedelta(days=7)}

        if plan not in plans:
            return {"status": "error", "message": "Invalid Plan!"}

        new_start_date = datetime.now()
        new_end_date = new_start_date + plans[plan]

        subscriptions.update_one(
            {"user_id": self.user_id},
            {
                "$set": {
                    "plan": plan,
                    "start_date": new_start_date,
                    "end_date": new_end_date,
                    "status": "Active",
                }
            },
            upsert=True,
        )
        return {
            "status": "success",
            "message": f"Subscription renewed until {new_end_date}",
        }

    def get_subscription_info(self):
        sub = subscriptions.find_one({"user_id": self.user_id})

        if sub:
            return sub
        return sub

    def can_use_free_command(self):
        user_data = subscriptions.find_one({"user_id": self.user_id})
        now = datetime.now()

        if user_data:
            last_used = user_data["last_used"]
            if now - last_used < timedelta(minutes=5):
                remaining_time = timedelta(minutes=5) - (now - last_used)
                return {
                    "status": "error",
                    "message": f"Please wait {remaining_time.seconds // 60} min {remaining_time.seconds % 60} sec!",
                }

        # ৫ মিনিট পার হলে নতুন সময় আপডেট করো
        subscriptions.update_one(
            {"user_id": self.user_id}, {"$set": {"last_used": now}}, upsert=True
        )
        return {"status": "success", "message": "You can use the command!"}


subs_button = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="BUY", callback_data="buy_subs"),
            InlineKeyboardButton(text="INFO", callback_data="infoo"),
            InlineKeyboardButton(text="FREE TRAIL", callback_data="freetrails"),
        ],
        [
            InlineKeyboardButton(text="🤖", url="https://t.me/Fxsihad"),
            InlineKeyboardButton(text="🚫", callback_data="closed"),
        ],
    ]
)


async def user_check(bot: Client, cmd: Message) -> bool:
    user_id = cmd.from_user.id
    sub = Subscription(user_id)
    sub_act = sub.is_active()
    print(sub_act)

    if not sub_act:
        await cmd.reply_text(
            "<b>You don't have an active subscription!</b>", reply_markup=subs_button
        )
        return False

    plan = sub.get_subscription_info()["plan"]
    card_number = {
        "free_trial": 5000,
        "weekly": 5000,
    }
    return card_number.get(plan, 0)
