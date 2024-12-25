import logging
from pathlib import Path

class Config:
    BOT_TOKEN = "6747452073:AAHVyfYU67j_MSR5EsMgA4E054qwyE8EECw"
    USER_SESSION = True
    API_ID = 21374177
    API_HASH = "a84abea042ac55b4783f1c168e25a010"
    BOT_USERNAME= ''
    BOT_SESSION = 'Multibot'
    OWNER_ID = 7066157562
    SESSION = 'BQFGJOEAHN0YazxjPR5_6Je0d6C_TZZw3hB_5r2HyjQ7ciW4icHboxS0zh7pIXl4n-AIR7-tbC0YvhAXTS6diKYdbqtunEsXQCp_mrsZQ8qBIh-T9ZnkNaLVbx4eKvMZthw8Its2oUCp8gbXqQ7oGOZbQKbkp5OHxaDXgWK5z7qya_c_xWuHHGA_ypCfWru6nTlWCUmWS6ift102iPL9HL0L8Zou4Gfy_IsqXxxwh1C2F6SwAgz8lqm94r8HS3FXnFU45b6llydjx3mW8wa4nc2TcI5W0Snje3QIy6C_l-8xAP2F-la784lYglfrF_odJPdwxmeEpwTHI6u53fAuabBpiNPziwAAAAGlLQH6AA'
    IS_PREMIUM = False
    ARGET_CHATS = ["channel_username_1", "channel_username_2", 123456789]

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
