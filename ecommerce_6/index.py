import pandas as pd
import numpy as np
import bs4
import requests
import json
import os
from dotenv import load_dotenv


def run():

    LINK = os.getenv("URL_ECOMMERCE_6")

    f = open('data.json')
    data = json.load(f)

    sub_categories_name = []
    sub_categories_url = []
    for x in data:
        for j in x["children"]:
            sub_categories_name.append(j["name"])
            sub_categories_url.append(j["url"])

    data_categorias = pd.DataFrame(sub_categories_url)
    data_categorias["NAME"] = sub_categories_name
    data_categorias.columns= ["CATEGORIE_URL", "CATEGORIE NAME"]
    data_categorias["CATEGORIE_URL"] = data_categorias["CATEGORIE_URL"].apply(lambda x : os.getenv("URL_CATEGORIES_ECOMMERCE_6").format(LINK,x))

    for particion, indice in zip(data_categorias, range(len(data_categorias))):
        print(len(particion))
        categorias = []
        nombres_productos = []
        imagenes_productos = []
        precios_productos = []
        skus = []
        url_categorias = []
        def param_searcher(url , category_name , initial_param, last_page, retries):
            global max_param
            max_param = initial_param
            print(max_param)
            print(last_page)
            if last_page == False and retries < 100 and max_param < 80:
                try:
                    sub_response = requests.get(url + "&page={}".format(max_param))
                    sub_response.raise_for_status()
                    global sub_categorie
                    sub_categorie =  bs4.BeautifulSoup(sub_response.text, "lxml").find("div", {'class':"vtex-store__template"}).find("script")
                    try:
                        global sub_categorie_raw
                        sub_categorie_raw = json.loads(sub_categorie.text)["itemListElement"]
                        max_param += 1
                        for j in range(len(sub_categorie_raw)):
                            try:
                                nombres_productos.append(sub_categorie_raw[j]["item"]["name"])
                                imagenes_productos.append(sub_categorie_raw[j]["item"]["image"])
                                skus.append(sub_categorie_raw[j]["item"]["sku"])
                                precios_productos.append(sub_categorie_raw[j]["item"]["offers"]["offers"][0]["price"])
                                url_categorias.append(url)
                                categorias.append(category_name)
                            except Exception as e:
                                print(e)
                        param_searcher(url,category_name , max_param, False, retries)
                    except Exception as e:
                        print(e)
                        if str(e) == "'NoneType' object has no attribute 'text'":
                            param_searcher(url,category_name , max_param, True, retries)
                except Exception as e:
                    print(e)
                    if str(e) == "'NoneType' object has no attribute 'text'":
                        print("Last Page:", last_page)
                        param_searcher(url, category_name , max_param, True, retries)
                    elif str(e) == "'NoneType' object has no attribute 'find'":
                        retries += 1
                        print(e)
                        param_searcher(url,category_name , max_param, False, retries)
        for idx in range(len(particion)):
            param_searcher(particion.iloc[idx]["CATEGORIE_URL"],particion.iloc[idx]["CATEGORIE NAME"] , 1 , False, 0)
            print(particion.iloc[idx]["CATEGORIE NAME"])
            print(particion.iloc[idx]["CATEGORIE_URL"])
            print(nombres_productos[-1])

        data = pd.DataFrame(url_categorias)
        data["NOMBRES"] = nombres_productos
        data["PRECIOS"] = precios_productos
        data["IAMGENES"] = imagenes_productos
        data["CATEGORIA"] = categorias
        data["SKUS"] = skus
        data.to_csv("ecommerce_6.csv", index=False)

if __name__ == "__main__":
    load_dotenv()
    run()