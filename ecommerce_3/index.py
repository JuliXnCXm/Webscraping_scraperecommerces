import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
import numpy as np
import bs4
import requests
import json
import os
from dotenv import load_dotenv

def generate_request(page,categoryId):
    url =os.getenv("URL_BACKEND_ECOMMERCE_3").format( categoryId , page)

    headers = CaseInsensitiveDict()
    headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"
    headers["Accept"] = "application/json, text/plain, */*"
    headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"

    headers["Accept-Encoding"] = "gzip, deflate, br"
    headers["Referer"] = os.getenv("BASE_LINK_ECOMMERCE_3")
    headers["Content-Type"] = "application/json"
    headers["country"] = "COL"
    headers["source"] = "WEB"
    headers["finalCountry"] = "Colombia"
    headers["Origin"] = os.getenv("BASE_LINK_ECOMMERCE_3")
    headers["Sec-Fetch-Dest"] = "empty"
    headers["Sec-Fetch-Mode"] = "cors"
    headers["Sec-Fetch-Site"] = "cross-site"
    headers["Connection"] = "keep-alive"
    resp = requests.get(url, headers=headers)
    return resp

def run():
    load_dotenv()
    LINK = os.getenv("URL_ECOMMERCE_3")
    categories = requests.get(os.getenv("URL_CATEGORIES_ECOMMERCE_3")).json()
    main_categories = [x["nameUrl"] for x in categories]
    subcategorie = []
    main_categorie = []
    fullUrl = []
    subcategorie_name= []
    subcategoryId = []
    for i in categories:
        for j in i["children"]:
            if "categoryPhoto"not in j.keys():
                subcategoryId.append(j["id"])
                subcategorie_name.append(j["name"])
                main_categorie.append(i["nameUrl"])
                subcategorie.append(j["nameUrl"])
                url = "{}/categorias/{}/{}".format(LINK, i["nameUrl"],j["nameUrl"])
                fullUrl.append(url)

    data_categories = pd.DataFrame(fullUrl)
    data_categories["main_categories"] = main_categorie
    data_categories["subcategorie"] = subcategorie
    data_categories["subcategorieName"] = subcategorie_name
    data_categories["subcategorieId"] = subcategoryId

    data_categories.columns =["CATEGORIE_URL", "MAIN_CATEGORIE", "SUBCATEGORIE", "SUBCATEGORIE_NAME", "SUBCATEGORIE_ID"]

    for particion, indice in zip(data_categories, range(len(data_categories))):
        nombres_productos = []
        imagenes_productos = []
        precios_productos = []
        url_categorias = []
        categorias = []
        skus = []
        def param_searcher(categorieUrl , categoryId, category_name):
            print(categoryId)
            resp = generate_request(0, categoryId)
            print(resp)
            respJson = resp.json()
            for x in range(int(respJson["pages"])+1):
                response = generate_request(x,categoryId)
                responseJson = response.json()
                if response.status_code == 200:
                    print("page: ", x)
                    try:
                        for j in responseJson["items"]:
                            precios_productos.append(j["fullPrice"])
                            imagenes_productos.append(j["mediaImageUrl"])
                            nombres_productos.append(j["mediaDescription"])
                            skus.append(j["seo"]["sku"])
                            url_categorias.append(categorieUrl)
                            categorias.append(category_name)
                    except Exception as e:
                        print(e)
        for idx in range(len(particion)):
            param_searcher(particion.iloc[idx]["CATEGORIE_URL"],particion.iloc[idx]["SUBCATEGORIE_ID"] , particion.iloc[idx]["SUBCATEGORIE_NAME"])
            print(particion.iloc[idx]["SUBCATEGORIE_NAME"])
            print(particion.iloc[idx]["CATEGORIE_URL"])
            print(nombres_productos[-1])
        data = pd.DataFrame(url_categorias)
        data["nombres_productos"] = nombres_productos
        data["precios"] = precios_productos
        data["categoria"] = categorias
        data["imagenes"] = imagenes_productos
        data["skus"] = skus

        data.to_csv("ecommerce_3.csv", index=False)
        data.to_json("ecommerce_3.json", orient ="records")
if __name__ == "__main__":
    run()
    