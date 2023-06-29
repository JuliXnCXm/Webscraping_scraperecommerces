import requests
from requests.structures import CaseInsensitiveDict
import json
import os
from dotenv import load_dotenv

def requestGenerator():
    url = os.getenv("URL_BACKEND_ECOMMERCE_1")
    headers = CaseInsensitiveDict()
    headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0"
    headers["Accept"] = "*/*"
    headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
    headers["Accept-Encoding"] = "gzip, deflate, br"
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Referer"] = os.getenv("BASE_LINK_BRAND_ECOMMERCE_1")
    headers["Origin"] =  os.getenv("BASE_LINK_BRAND_ECOMMERCE_1")
    headers["Sec-Fetch-Dest"] = "empty"
    headers["Sec-Fetch-Mode"] = "cors"
    headers["Sec-Fetch-Site"] = "cross-site"
    headers["Connection"] = "keep-alive"

    data = os.getenv("FORM_DATA_ECOMMERCE_1")
    resp = requests.post(url, headers=headers, data=data)
    return resp.json()["results"][0]["hits"]

def data_builder():
    BASE_IMAGE_LINK = os.getenv("BASE_IMAGE_LINK_ECOMMERCE_1")
    results = requestGenerator()
    DataResultsObject = []
    for item in results:
        DataResultsObject.append({
            "0": os.getenv("BASE_LINK_ECOMMERCE_1"),
            "categoria": item.get("main_category_id"),
            "precios": item.get("price_neto"),
            "imagenes": BASE_IMAGE_LINK+ item.get("objectID"),
            "skus": item.get("id_item"),
            "nombres_productos": item.get("title"),
        })
    json_object = json.dumps(DataResultsObject, indent=4)
    with open("./ecommerce_1/ecommerce_1.json", "w") as outfile:
        outfile.write(json_object)

if __name__ == "__main__":
    load_dotenv()
    data_builder()