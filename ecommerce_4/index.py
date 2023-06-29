import pandas as pd
import json
import os
import bs4
import requests
from dotenv import load_dotenv
import re

def request_data():
    links_to_avoid = ["productos-importados---gourmet", "promociones", "mariscos"]
    LINK = os.getenv("URL_ECOMMERCE_4")
    response = requests.get(LINK)
    categories_links_tags = bs4.BeautifulSoup(response.text, "lxml").find("div", {'id': "productos-menu"}).find_all("a", href=True)
    categories_links = [x["href"] for x in categories_links_tags if x["href"].split("/")[-1] not in links_to_avoid]
    return categories_links


def data_builder():
    categories_links = request_data()
    nombres_productos = []
    nombres_categorias = []
    cantidades = []
    precios = []
    imagenes = []
    url_categoria = []

    for j in categories_links:
        response_categorie = requests.get(j)
        products_names_data = bs4.BeautifulSoup(response_categorie.text, "lxml").find_all("span", {'class': "product-card-name"})
        [nombres_productos.append(x.get_text()) for x in products_names_data]
        categorie_name_data = bs4.BeautifulSoup(response_categorie.text, 'lxml').find('h5', {'class' : 'label-productos'})
        [nombres_categorias.append(categorie_name_data.get_text()) for x in range(len(products_names_data))]
        [url_categoria.append(j) for c in range(len(products_names_data))]
        cantidad_data = bs4.BeautifulSoup(response_categorie.text, "lxml").find_all("span", {'class': "product-card-quantity"})
        [cantidades.append(x.get_text()) for x in cantidad_data]
        precios_data = bs4.BeautifulSoup(response_categorie.text, "lxml").find_all("span", {'class': "product-card-price"})
        [precios.append(x.get_text()) for x in precios_data]
        imagenes_data = bs4.BeautifulSoup(response_categorie.text, "lxml").find_all("div", {'class': "image-product-card"})
        [imagenes.append( x["data-src"]) for x in imagenes_data]
    data = pd.DataFrame(nombres_productos)
    data["categorias"] = nombres_categorias
    data["precios"] = precios
    data["cantidad"] = cantidades
    data["imagenes"] = imagenes
    data["url"] = url_categoria
    data["cantidad"] = data["cantidad"].apply(lambda x: re.sub(r'\n[0-9]?(spoilers)?', '', x))
    data.drop(columns=["cantidad"], inplace=True)
    data["nombres_productos"] = data["nombres_productos"] + " X" + data["cantidad"]
    data.to_csv("ecommerce_4.csv", index=False)



if __name__ == "__main__" :
    load_dotenv()
    data_builder()