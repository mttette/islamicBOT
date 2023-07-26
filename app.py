from modules.api import search,get_answer,search_sistani,get_answer_sistani
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
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
        elif data.startswith("https://www.aqaed.com"):
            return await search_aqaed(client,message,data)
        elif data.startswith("SIS;"):
            id = data.replace("SIS;","")
            return await sistani_search(client,message,id)
        question = get_key(f"user:{message.chat.id}:state").split(":")[-1]
        if data == "aqaed":
            return await ask_aqaed(client,message,question)
        elif data == "sistani":
            return await ask_sistani(client,message,question)
    except Exception:
        logging.error(traceback.format_exc())


async def ask_aqaed(client,message,question):
    await client.delete_messages(message.chat.id,message.id)
    wait_message = await client.send_message(message.chat.id,"⌛")
    data = await search(question)

    buttons = []
    try:
        if data:
            for obj in data:
                buttons.append([InlineKeyboardButton(obj["quz"],callback_data=obj["url"])])
            buttons.append([InlineKeyboardButton("الغاء", callback_data="cancel"),])
            keyboard = InlineKeyboardMarkup(buttons)
            await client.delete_messages(message.chat.id,wait_message.id)
            await client.send_message(message.chat.id,"""نتائج البحث 🔍

.
""",reply_markup=keyboard)
        else:
            await client.delete_messages(message.chat.id,wait_message.id)
            await client.send_message(message.chat.id,"لا توجد نتائج")
            delete_key(message.chat.id)
    except Exception:
        logging.error(traceback.format_exc())
        await client.delete_messages(message.chat.id,wait_message.id)
        await client.send_message(message.chat.id,"⚠️ حدث خطأ الرجاء اعاده المحاولة❗")
        delete_key(message.chat.id)


async def search_aqaed(client:Client,message,url):
    await client.delete_messages(message.chat.id,message.id)
    wait_message = await client.send_message(message.chat.id,"⌛")
    bot_user = await client.get_users("me")
    bot_username = bot_user.username
    results = await get_answer(url,bot_username)
    try:
        if results:
            await client.send_document(message.chat.id,BytesIO(results["pdf_bytes"]),file_name="results.pdf",caption=f"""✅ جواب السؤال حول موضوع :
                                      {results["quz"]}
""") 
            await client.delete_messages(message.chat.id,wait_message.id)
        else:
            await client.delete_messages(message.chat.id,wait_message.id)
            await client.send_message(message.chat.id,"⚠️ حدث خطأ الرجاء اعاده المحاولة❗")
            
    except Exception:
        logging.error(traceback.format_exc())
    
    delete_key(message.chat.id)
    


async def ask_sistani(client:Client,message,question):
    await client.delete_messages(message.chat.id,message.id)
    wait_message = await client.send_message(message.chat.id,"⌛")
    data = await search_sistani(question)

    buttons = []
    try:
        if data:
            for obj in data:
                buttons.append([InlineKeyboardButton(obj["quz"].replace("\n", ""),callback_data="SIS;"+obj["id"])])
            buttons.append([InlineKeyboardButton("الغاء", callback_data="cancel"),])
            keyboard = InlineKeyboardMarkup(buttons)
            await client.delete_messages(message.chat.id,wait_message.id)
            await client.send_message(message.chat.id,"""نتائج البحث 🔍
                                      

.                                        
""",reply_markup=keyboard)
        else:
            await client.delete_messages(message.chat.id,wait_message.id)
            await client.send_message(message.chat.id,"لا توجد نتائج")
            delete_key(message.chat.id)
    except Exception:
        logging.error(traceback.format_exc())
        await client.delete_messages(message.chat.id,wait_message.id)
        await client.send_message(message.chat.id,"⚠️ حدث خطأ الرجاء اعاده المحاولة❗")
        delete_key(message.chat.id)
    

async def sistani_search(client:Client,message,id):
    await client.delete_messages(message.chat.id,message.id)
    wait_message = await client.send_message(message.chat.id,"⌛")
    results = await get_answer_sistani(id)
    try:
        if results:
            question = results["quz"].replace("\n", "")
            answer = results["answer"].replace("\n", "")
            topic = results["topic"]
            await client.send_message(message.chat.id,f"""{topic}
                                      
السؤال {question}


الجواب {answer}
""")
            await client.delete_messages(message.chat.id,wait_message.id)
        else:
            await client.delete_messages(message.chat.id,wait_message.id)
            await client.send_message(message.chat.id,"⚠️ حدث خطأ الرجاء اعاده المحاولة❗")
    except Exception:
        logging.error(traceback.format_exc())
    
    delete_key(message.chat.id)

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
            reply_text="""❗الرجاء أنظار الطلب السابق او إلغائه

.
"""
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
                reply_text="""❗الرجاء أنظار الطلب السابق او إلغائه

.
"""
                set_key(key,f"spam:{message.text}",(5*60))
            else:
                return await client.delete_messages(message.chat.id,message.id)
        else:
            set_key(key,f"wait:{message.text}",(5*60))
            reply_text = """⭕ أختر مصدر المعلومات:

.
"""
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("مركز أبحاث العقائدية", callback_data="aqaed"),
                ],
                [
                    InlineKeyboardButton("سيد السيستاني", callback_data="sistani"),
                ],
                [
                    InlineKeyboardButton("الغاء", callback_data="cancel"),
                ],
            ])

        await client.send_message(message.chat.id,reply_text,reply_markup=keyboard)
    except Exception:
        logging.error(traceback.format_exc())

app.run()


