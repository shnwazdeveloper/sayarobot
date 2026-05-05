import requests
from aiohttp import ClientSession

# Aiohttp Async Client
aiohttpsession = ClientSession()

async def post(url: str, *args, **kwargs):
    async with aiohttpsession.post(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data

async def batbin(text: str):
    url = "https://batbin.me/api/v2/paste"
    req = await post(url, data=text)
    if req['success']:
        return url.split('api')[0] + req['message']
    return False    

async def spacebin(text: str):
    url = "https://spaceb.in/api/v1/documents/"
    response = requests.post(url, data={"content": text, "extension": "txt"})
    id = response.json().get('payload').get('id')
    res = requests.get(f"https://spaceb.in/api/v1/documents/{id}").json()
    created_at = res.get("payload").get("created_at")
    link = f"https://spaceb.in/{id}"
    raw = f"https://spaceb.in/api/v1/documents/{id}/raw"
    result = {"result": {"link": link, "raw": raw, "datetime": created_at}}
    return result
