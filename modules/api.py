import aiohttp
from bs4 import BeautifulSoup
import logging
import traceback
from weasyprint import HTML,CSS

with open("styles.css","r")as f:
    css = f.read()

def html_to_pdf(html_code,Bot_username):
    global css
    css +="""
        body {
            text-align: right;
            background-image: url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="600"%3E%3Ctext x="50%" y="50%" font-size="50" fill="rgba(135, 206, 250, 0.5)" transform="rotate(-45 400 300)" text-anchor="middle"%3E@"""+Bot_username+"""%3C/text%3E%3C/svg%3E');
            background-repeat: no-repeat;
            background-position: center;
        }
        """
    bytes_html = b''
    bytes_html = HTML(string=html_code).write_pdf(target=None,stylesheets=[CSS(string=css)])
    return bytes_html

async def search(question,topic="جميع المواضيع"):
    results = None
    url = f"https://www.aqaed.com/faq/search/?q={question}&sid={topic}"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.aqaed.com/faq/1665/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Te": "trailers"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers)as response:
                if response.ok:
                    result_html = await response.text()
                    soup = BeautifulSoup(result_html,"html.parser")
                    results_divs = soup.find_all('div',class_='faqList')
                    results = []
                    for div in results_divs:
                        results_questions = div.find_all('a')
                        for question in results_questions:
                            results.append({"quz":question.text,"url":"https://www.aqaed.com"+question["href"]})
    except Exception:
        logging.error(traceback.format_exc())
    
    return results

async def get_answer(url,bot_username="mtte"):
    result = None

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Te": "trailers"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers) as response:
                result_html = await response.text()
                soup = BeautifulSoup(result_html,"html.parser")
                html = soup.find('div',class_='border border-info p-3 my-1')
                if html:
                    result = {}
                    result["quz"]=html.find("h1").text
                    result["pdf_bytes"]=html_to_pdf(html.prettify(),bot_username)
    except Exception:
        logging.error(traceback.format_exc())

    return result




if __name__=="__main__":
    import asyncio

    question = "كلب رقيه"

    async def main():
        results = await search(question)

        if results:
            r = await get_answer(results[-1]["url"])
            if r:
                with open("test.pdf","wb") as f:
                    f.write(r)



    asyncio.run(main())