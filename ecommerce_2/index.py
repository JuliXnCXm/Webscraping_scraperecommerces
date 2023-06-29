import pandas as pd
import numpy as np
import bs4
import requests
import json
import os
from dotenv import load_dotenv

def run():
    load_dotenv()
    LINK = os.getenv("BASE_LINK_BRAND_ECOMMERCE_1") 
    response = requests.get(LINK)
    response.raise_for_status()
    try:
        store = bs4.BeautifulSoup(response.text, "lxml")
    except Exception as e:
        print(e)
    routes =os.getenv("ROUTES_ECOMMERCE_2")
    categories_routes = [x["href"] for x in routes if x["href"] != '' if x["href"] != '/escuela-de-cocina' if x["href"] != '/vida-sana/portafolio' if x["href"] != '/hogar-y-decoracion' ]
    categories_routes.append("/mascotas")
    categories_routes.append("/vehiculos-y-ferreteria")
    categories_routes.append("/bebes-y-jugueteria")
    categories_routes.append("/hogar-y-decoracion/muebles-de-oficina-y-estudio")
    categories_routes.append("/hogar-y-decoracion/muebles-de-alcoba")
    categories_routes.append("/hogar-y-decoracion/muebles-de-sala")
    categories_routes.append("/hogar-y-decoracion/muebles-de-comedor")
    categories_routes.append("/hogar-y-decoracion/mesa")
    categories_routes.append("/hogar-y-decoracion/colchones")
    categories_routes.append("/m/mesa")
    categories_routes.append("/hogar-y-decoracion/ropa-hogar")
    names_subcategories_cleaned = [x["name"] for x in routes if x["name"] != 'Otras Categorias ' if x["name"] != "Escuela de Cocina" if x["name"] != "Green Market" if x["name"] != "Green Market" if x["name"] != "Hogar y decoración"]
    names_subcategories_cleaned.append("Mascotas")
    names_subcategories_cleaned.append("Vehiculos y ferreteria")
    names_subcategories_cleaned.append("Bebes y juegureteria")
    names_subcategories_cleaned.append("Muebles de oficina y estudio")
    names_subcategories_cleaned.append("Muebles de alcoba")
    names_subcategories_cleaned.append("Muebles de sala")
    names_subcategories_cleaned.append("Muebles de comedor")
    names_subcategories_cleaned.append("Muebles de Mesa")
    names_subcategories_cleaned.append("Colchones")
    names_subcategories_cleaned.append("Mesa")
    names_subcategories_cleaned.append("Ropa Hogar")
    data_categorias = pd.DataFrame(categories_routes)
    data_categorias["NAME"] = names_subcategories_cleaned
    data_categorias.columns= ["CATEGORIE_URL", "CATEGORIE NAME"]
    data_categorias["CATEGORIE_URL"] = data_categorias["CATEGORIE_URL"].apply(lambda x : os.getenv("BASE_LINK_ECOMMERCE_2").format(x))

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
        if last_page == False and retries < 50 and max_param < 80:
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
                            nombre = sub_categorie_raw[j]["item"]["name"]
                            imagen = sub_categorie_raw[j]["item"]["image"]
                            sku = sub_categorie_raw[j]["item"]["sku"]
                            precio = sub_categorie_raw[j]["item"]["offers"]["offers"][0]["price"]
                            if nombre and nombre != "" and imagen  and imagen != "" and sku and sku != "" and precio and precio != "":
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
    for idx in range(len(data_categorias)):
        param_searcher(data_categorias.iloc[idx]["CATEGORIE_URL"],data_categorias.iloc[idx]["CATEGORIE NAME"] , 1 , False, 0)
        print(data_categorias.iloc[idx]["CATEGORIE NAME"])
        print(data_categorias.iloc[idx]["CATEGORIE_URL"])
        print(nombres_productos[-1])

    data = pd.DataFrame(url_categorias)
    data["NOMBRES"] = nombres_productos
    data["PRECIOS"] = precios_productos
    data["IAMGENES"] = imagenes_productos
    data["CATEGORIA"] = categorias
    data["SKUS"] = skus
    data.to_csv("ecommerce_2.csv", index=False)

if __name__ == "__main__":
    run()