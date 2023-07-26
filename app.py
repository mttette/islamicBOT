from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from modules.api import search_almerja,get_answer_almerja
from modules.db import set_key,get_key,delete_key
from pyrogram import Client, filters
from dotenv import load_dotenv
from io import BytesIO
import traceback
import logging
import uvloop
import os

uvloop.install()

logging.basicConfig(filename="error.log")

# ? init enviroment variables
load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_NAME = os.getenv('BOT_NAME')


app = Client(BOT_NAME, api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_callback_query()
async def handle_callback_query(client:Client, call):
    try:
        message = call.message
        data = call.data 
        await call.answer()
        if data == "cancel":
            delete_key(message.chat.id)
            await client.delete_messages(message.chat.id,message.id)
            return await client.send_message(message.chat.id,"تم الغاء الطلب ✅")
        elif data.startswith("id"):
            url = data.split(";")[0]
            topic = data.split(";")[-1]
            return await follow_up_almerja(client,message,url,topic)
        # elif data.startswith("SIS;"):
        #     answer_id = data.replace("SIS;","")
        #     return await follow_up_sistani(client,message,answer_id)
        else:
            if data == "aqaed":
                return await ask_almerja(client,message)
            # elif data == "sistani":
            #     return await ask_sistani(client,message,question)
    except Exception:
        logging.error(traceback.format_exc())


async def ask_almerja(client:Client,message):
    question = get_key(f"user:{message.chat.id}:state").split(":")[-1]
    wait_message = await client.send_message(message.chat.id,"⌛")
    data = await search_almerja(question)

    buttons = []
    try:
        if data:
            for obj in data:
                buttons.append([InlineKeyboardButton(obj["quz"],callback_data=f"id{obj['id']};{obj['quz'][:21]}..")])
            buttons.append([InlineKeyboardButton("الغاء", callback_data="cancel"),])
            keyboard = InlineKeyboardMarkup(buttons)
            await client.delete_messages(message.chat.id,wait_message.id)
            await client.send_message(message.chat.id,"نتائج البحث 🔍\n\n\n.",reply_markup=keyboard)
        else:
            await client.delete_messages(message.chat.id,wait_message.id)
            await client.send_message(message.chat.id,"لا توجد نتائج ... حاول أن تبحث باسم الموضوع")
            delete_key(message.chat.id)
    except Exception:
        logging.error(traceback.format_exc())
        await client.delete_messages(message.chat.id,wait_message.id)
        await client.send_message(message.chat.id,"⚠️ حدث خطأ الرجاء اعاده المحاولة❗")
        delete_key(message.chat.id)

async def split_text_and_send(bot, chat_id, text):
    max_message_size = 4096

    # Split the text into words
    words = text.split()

    # Initialize a list to hold the message chunks
    message_chunks = []
    current_chunk = ""

    for word in words:
        # Check if adding the current word would exceed the maximum size
        if len(current_chunk) + len(word) + 1 <= max_message_size:
            # Add the word and a space to the current chunk
            current_chunk += word + " "
        else:
            # Append the current chunk to the list and start a new one
            message_chunks.append(current_chunk)
            current_chunk = word + " "

    # Append the last chunk
    message_chunks.append(current_chunk)

    # Send each chunk as a separate message
    for chunk in message_chunks:
        await bot.send_message(chat_id=chat_id, text=chunk)


async def follow_up_almerja(client:Client,message,url,topic):
    await client.delete_messages(message.chat.id,message.id)
    wait_message = await client.send_message(message.chat.id,"⌛")
    results = await get_answer_almerja(url)
    try:
        if results:
            await client.send_message(message.chat.id,topic)
            await split_text_and_send(client,message.chat.id,results)
        else:
            await client.send_message(message.chat.id,"⚠️ حدث خطأ الرجاء اعاده المحاولة❗")
            
    except Exception:
        logging.error(traceback.format_exc())
        await client.send_message(message.chat.id,"⚠️ حدث خطأ الرجاء اعاده المحاولة❗")
    
    await client.delete_messages(message.chat.id,wait_message.id)
    delete_key(message.chat.id)
    


# async def ask_sistani(client:Client,message,question):
#     await client.delete_messages(message.chat.id,message.id)
#     wait_message = await client.send_message(message.chat.id,"⌛")
#     data = await search_sistani(question)

#     buttons = []
#     try:
#         if data:
#             for obj in data:
#                 buttons.append([InlineKeyboardButton(obj["quz"].replace("\n", ""),callback_data="SIS;"+obj["id"])])
#             buttons.append([InlineKeyboardButton("الغاء", callback_data="cancel"),])
#             keyboard = InlineKeyboardMarkup(buttons)
#             await client.delete_messages(message.chat.id,wait_message.id)
#             await client.send_message(message.chat.id,"نتائج البحث 🔍\n\n\n.",reply_markup=keyboard)
#         else:
#             await client.delete_messages(message.chat.id,wait_message.id)
#             await client.send_message(message.chat.id,"لا توجد نتائج")
#             delete_key(message.chat.id)
#     except Exception:
#         logging.error(traceback.format_exc())
#         await client.delete_messages(message.chat.id,wait_message.id)
#         await client.send_message(message.chat.id,"⚠️ حدث خطأ الرجاء اعاده المحاولة❗")
#         delete_key(message.chat.id)
    

# async def follow_up_sistani(client:Client,message,id):
#     await client.delete_messages(message.chat.id,message.id)
#     wait_message = await client.send_message(message.chat.id,"⌛")
#     results = await get_answer_sistani(id)
#     try:
#         if results:
#             question = results["quz"].replace("\n", "")
#             answer = results["answer"].replace("\n", "")
#             topic = results["topic"]
#             await client.send_message(message.chat.id,f"{topic}\n\nالسؤال {question}\n\nالجواب {answer}")
#             await client.delete_messages(message.chat.id,wait_message.id)
#         else:
#             await client.delete_messages(message.chat.id,wait_message.id)
#             await client.send_message(message.chat.id,"⚠️ حدث خطأ الرجاء اعاده المحاولة❗")
#     except Exception:
#         logging.error(traceback.format_exc())
    
#     delete_key(message.chat.id)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    reply_text =f"""
                 اهلا 👋 بك {message.from_user.first_name} في الموسوعة الدينية. 

                .للبدأ باستخدام البوت الرجاء إرسال سؤالك

                """
    key = f"user:{message.chat.id}:state"
    user_state = get_key(key)
    if user_state:
        user_state = user_state.split(":")[0]
        if user_state == "wait":
            await client.delete_messages(message.chat.id,message.id)
            reply_text="❗الرجاء أنظار الطلب السابق او إلغائه\n\n."
            set_key(key,f"spam:{message.text}",(5*60))
        else:
            return await client.delete_messages(message.chat.id,message.id)
    await message.reply_text(reply_text)

@app.on_message(filters.text)
async def handle_text(client:Client, message):
    try:
        reply_text = "."
        keyboard = None
        key = f"user:{message.chat.id}:state"
        user_state = get_key(key)
        if user_state:
            user_state = user_state.split(":")[0]
            if user_state == "wait":
                await client.delete_messages(message.chat.id,message.id)
                reply_text="❗الرجاء أنظار الطلب السابق او الغاءه\n\n."
                set_key(key,f"spam:{message.text}",(5*60))
            else:
                return await client.delete_messages(message.chat.id,message.id)
        else:
            set_key(key,f"wait:{message.text}",(5*60))
            return await ask_almerja(client,message)

        await client.send_message(message.chat.id,reply_text,reply_markup=keyboard)
    except Exception:
        logging.error(traceback.format_exc())

app.run()


