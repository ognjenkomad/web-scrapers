import requests
import urllib.request
from bs4 import BeautifulSoup
import json
import os

base_url = 'https://www.ideal-lux.com/en/products'
category = 'indoor'

def get_product_collection(main_product):    
    response = requests.get(main_product)
    soup = BeautifulSoup(response.text, "html.parser")
    visited_a = [main_product]
    product_list = []
    for a_tag in soup.find(id='product-collection').find_all('a'):        
        if a_tag['href'] not in visited_a:
            visited_a.append(a_tag['href'])
            response_article = requests.get(a_tag['href'])
            soup_article = BeautifulSoup(response_article.text, "html.parser")
            article_id = a_tag['href'].split('/', 7)[6] # id
            article_url = a_tag['href'] # url
            article_category = 'indoor' # category
            product_info = soup_article.find('div', 'product-info')
            slider_div = soup_article.find(id='ctl51_ctl01_productPanel_Images').find_all('img', 'imgsliderimg')
            article_name = 'IDEAL LUX ' + product_info.find('strong').get_text(strip=True).upper() # name
            article_subcategory = product_info.find(id='ctl51_ctl01_lblFunzioneNome').get_text(strip=True) # subcategory
            article_desc = 'code ' + product_info.find(id='lblCode').get_text(strip=True) + ' ' + product_info.find(id='ctl51_ctl01_DescrizioneArt').get_text(strip=True) # desc
            article_dim = product_info.find(id='ctl51_ctl01_BoxDes').find_all('span', 'valori')
            dim_text = "";
            for span_tag in article_dim:
                dim_text += span_tag.get_text(strip=True) + ' '
            
            desc_art = product_info.find('div', 'descrittoriboolean')
            
            os.mkdir(article_id)
            os.mkdir(article_id + '/descArt')
            os.mkdir(article_id + '/altArt')
            i=0
            j=0
            desc_artworks = []
            alt_artworks = []
            for img_tag in slider_div:
                src_img = img_tag['data-zoom-image']
                prim_img = requests.get(src_img)            
                with open(article_id + "/altArt/" + article_id + "_" + "alternate" + str(j) + src_img[-4:], "wb") as prim_img_file:
                    prim_img_file.write(prim_img.content)             
                alt_artworks.append(article_id + "/altArt/" + article_id + "_" + "alternate" + str(j) + src_img[-4:])
                j+=1
            for img_tag in desc_art.find_all('img'):
                img_contents = requests.get(img_tag['src']);
                with open(article_id + "/descArt/" + article_id + "_" + "artwork" + str(i) + ".png", "wb") as img_file:
                    img_file.write(img_contents.content)
                desc_artworks.append(article_id + "/descArt/" + article_id + "_" + "artwork" + str(i) + ".png")
                i+=1
            product_dict = {
                "product_id" : article_id,
                "product_name" : article_name,
                "product_url" : article_url,
                "product_subcategory" : article_subcategory,
                "product_description" : article_desc,
                "product_dimension" : {
                    "text" : dim_text,
                    "image" : None
                },
                "product_artworks" : {                
                    "description_artworks" : desc_artworks,
                    "alternate_artworks" : alt_artworks
                }
            }
            product_list.append(product_dict)
    return product_list
    

def get_product(product_url):
    response_article = requests.get(product_url)
    soup_article = BeautifulSoup(response_article.text, "html.parser")
    article_id = product_url.split('/', 7)[6] # id
    article_url = product_url # url
    article_category = 'indoor' # category
    product_info = soup_article.find('div', 'product-info')
    slider_div = soup_article.find(id='ctl51_ctl01_productPanel_Images').find_all('img', 'imgsliderimg')
    article_name = 'IDEAL LUX ' + product_info.find('strong').get_text(strip=True).upper() # name
    article_subcategory = product_info.find(id='ctl51_ctl01_lblFunzioneNome').get_text(strip=True) # subcategory
    article_desc = 'code ' + product_info.find(id='lblCode').get_text(strip=True) + ' ' + product_info.find(id='ctl51_ctl01_DescrizioneArt').get_text(strip=True) # desc
    article_dim = product_info.find(id='ctl51_ctl01_BoxDes').find_all('span', 'valori')
    dim_text = "";
    for span_tag in article_dim:
        dim_text += span_tag.get_text(strip=True) + ' '
    
    desc_art = product_info.find('div', 'descrittoriboolean')
    
    os.mkdir(article_id)
    os.mkdir(article_id + '/descArt')
    os.mkdir(article_id + '/altArt')
    i=0
    j=0
    desc_artworks = []
    alt_artworks = []
    for img_tag in slider_div:
        src_img = img_tag['data-zoom-image']
        prim_img = requests.get(src_img)            
        with open(article_id + "/altArt/" + article_id + "_" + "alternate" + str(j) + src_img[-4:], "wb") as prim_img_file:
            prim_img_file.write(prim_img.content)             
        alt_artworks.append(article_id + "/altArt/" + article_id + "_" + "alternate" + str(j) + src_img[-4:])
        j+=1
    for img_tag in desc_art.find_all('img'):
        img_contents = requests.get(img_tag['src']);
        with open(article_id + "/descArt/" + article_id + "_" + "artwork" + str(i) + ".png", "wb") as img_file:
            img_file.write(img_contents.content)
        desc_artworks.append(article_id + "/descArt/" + article_id + "_" + "artwork" + str(i) + ".png")
        i+=1

    product_collection = get_product_collection(article_url)
    product_dict = {
        "product_id" : article_id,
        "product_name" : article_name,
        "product_url" : article_url,
        "product_subcategory" : article_subcategory,
        "product_description" : article_desc,
        "product_dimension" : {
            "text" : dim_text,
            "image" : None
        },
        "product_artworks" : {                
            "description_artworks" : desc_artworks,
            "alternate_artworks" : alt_artworks
        }
    }
    return product_dict, product_collection

product_list = []
for page_no in range(1):
    response = requests.get(base_url + '/' + category + '/?page_no=' + str(page_no))
    soup = BeautifulSoup(response.text, "html.parser")
    k=0
    for a_tag in soup.find_all('a', 'nk-portfolio-item-link'):
        product, product_collection = get_product(a_tag['href'])
        product_list.append(product)
        for p in product_collection:
            product_list.append(p)             
        
    
hanging_list = []
ceiling_list = []
wall_list = []
recessed_list = []
table_list = []
floor_list = []

for p in product_list:
    if p['product_subcategory'] == 'Hanging':
        hanging_list.append(p)
    elif p['product_subcategory'] == 'Ceiling':
        ceiling_list.append(p)
    elif p['product_subcategory'] == 'Applique':
        wall_list.append(p)
    elif p['product_subcategory'] == 'Recessed':
        recessed_list.append(p)
    elif p['product_subcategory'] == 'Table':
        table_list.append(p)
    elif p['product_subcategory'] == 'Floor':
        floor_list.append(p)
idealLux = {            
            "category" : [
                {
                    "category_name" : category,
                    "category_url" : base_url + '/' + category,
                    "subcategories" : [
                        {
                            "category_name" : "Hanging",
                            "products" : hanging_list
                        },
                        {
                            "category_name" : "Ceiling",
                            "products" : ceiling_list
                        },
                        {
                            "category_name" : "Wall",
                            "products" : wall_list
                        },
                        {
                            "category_name" : "Recessed",
                            "products" : recessed_list
                        },
                        {
                            "category_name" : "Table",
                            "products" : table_list
                        },
                        {
                            "category_name" : "Floor",
                            "products" : floor_list
                        }
                    ]
                }
            ]          
        }
with open('indoorFirstPage.json', 'w') as file:
    json.dump(idealLux, file, indent=4)

