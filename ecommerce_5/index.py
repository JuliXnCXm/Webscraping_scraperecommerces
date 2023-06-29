import pandas as pd
import json
import os
import bs4
import requests
from dotenv import load_dotenv
import re

def request_data():
    LINK = os.getenv("URL_ECOMMERCE_5")
    response = requests.get(LINK)
    response.raise_for_status()
    try:
        store = bs4.BeautifulSoup(response.text, "lxml").find_all('script')
    except Exception as e:
        print(e)
    data_home = json.loads([store[x].text for x in range(len(store)) if store[x].text.startswith('{"store.home":')][0])
    categories = [x["text"] for x in data_home['store.home/$before_header.full/header-layout.desktop/sticky-layout#main-header/flex-layout.row#4-desktop/flex-layout.col#hamburger-desktop/MegaMenuTrigger/megamenu']["props"]["links"] ]
    submenus = [x["subMenu"] for  x  in data_home['store.home/$before_header.full/header-layout.desktop/sticky-layout#main-header/flex-layout.row#4-desktop/flex-layout.col#hamburger-desktop/MegaMenuTrigger/megamenu']["props"]["links"]]
    enrutamiento_submenus = [x["top"]["links"] for x in range(len(submenus)) for x in submenus[x]]
    enrutamiento_subcategories = [x["top"]["page"] for x in range(len(submenus)) for x in submenus[x] if x["top"]["page"] != ""]
    enrutamiento_subcategories_cleaned = [x for x in enrutamiento_subcategories if x != '/categoría']
    names_subcategories = [x["top"]["titleSubMenu"] for x in range(len(submenus)) for x in submenus[x]]
    names_subcategories_cleaned = [x for x in names_subcategories if x != "Ver todo"]
    enrutamiento_cleaned = [enrutamiento_submenus[x][:-1] for x in range(len(enrutamiento_submenus))]
    data_categorias = pd.DataFrame(enrutamiento_subcategories_cleaned)
    data_categorias["NAME"] = names_subcategories_cleaned
    data_categorias.columns= ["CATEGORIE_URL", "CATEGORIE NAME"]
    data_categorias["CATEGORIE_URL"] = data_categorias["CATEGORIE_URL"].apply(lambda x : os.getenv("URL_CATEGORIES_ECOMMERCE_5").format(x))
    return data_categorias

def builder_data():
    data_categorias = request_data()
    categorias = []
    nombres_productos = []
    imagenes_productos = []
    skus = []
    precios_productos = []
    url_categorias = []
    def param_searcher(url,category_name , initial_param):
        global max_param
        max_param = initial_param
        sub_response = requests.get(url + "&page={}".format(max_param))
        sub_response.raise_for_status()
        try:
            sub_categorie = bs4.BeautifulSoup(sub_response.text, "lxml").find_all('script')
        except Exception as e:
            print(e)
        try:
            global sub_categorie_raw
            sub_categorie_raw = json.loads([sub_categorie[x].text for x in range(len(sub_categorie)) if sub_categorie[x].text.startswith('{"Product:sp')][0])
            max_param += 1
            print(max_param)
            raw = [x for x in sub_categorie_raw.keys()]
            global products_detail
            products_detail = [x for x in raw if x.endswith("""items({"filter":"FIRST_AVAILABLE"}).0""")]
            products_prices = [x for x in raw if x.endswith("""items({"filter":"FIRST_AVAILABLE"}).0.sellers.0""")]

            for j in range(len(products_detail)):
                try:
                    nombre = sub_categorie_raw[products_detail[j]]["nameComplete"]
                    imagen = sub_categorie_raw[sub_categorie_raw[products_detail[j]]["images"][0]["id"]]["imageUrl"]
                    sku = sub_categorie_raw[products_detail[j]]["name"]
                    precio = sub_categorie_raw[sub_categorie_raw[products_prices[j]]["commertialOffer"]["id"]]["Price"]
                    if nombre and nombre != "" and imagen  and imagen != "" and sku and sku != "" and precio and precio != "":
                        nombres_productos.append(nombre)
                        skus.append(sku)
                        imagenes_productos.append(imagen)
                        precios_productos.append(precio)
                        url_categorias.append(url)
                        categorias.append(category_name)
                except Exception as e:
                    print(e)
            param_searcher(url,category_name , max_param)
        except Exception as e:
            print(e)
            max_param -= 1
    for idx in range(len(data_categorias)):
        param_searcher(data_categorias.iloc[idx]["CATEGORIE_URL"],data_categorias.iloc[idx]["CATEGORIE NAME"] , 1 )
    data = pd.DataFrame(url_categorias)
    data["categoria"] = categorias
    data["precios"] = precios_productos
    data["imagenes"] = imagenes_productos
    data["skus"]= skus
    data["nombres_productos"] = nombres_productos
    data.to_json("ecommerce_5.json", orient="records")

if __name__ == "__main__":
    load_dotenv()
    builder_data()