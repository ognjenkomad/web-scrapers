import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path

def get_product(product_url, get_colletion=True):
    response_article = requests.get(product_url)
    soup_article = BeautifulSoup(response_article.text, "html.parser")
    if len(product_url.split('/', 7)) == 8:
        article_id = product_url.split('/', 7)[6] # id
    else:
        return None,[]    
    article_url = product_url # url    
    product_info = soup_article.find('div', 'product-info')
    if not product_info:
        return None, []
    slider_div = soup_article.find(id='ctl51_ctl01_productPanel_Images').find_all('img', 'imgsliderimg')
    if product_info.find('strong'):
        article_name = 'IDEAL LUX ' + product_info.find('strong').get_text(strip=True).upper() # name
    else:
        article_name = 'IDEAL LUX ' + product_url.split('/', 7)[6].upper()
    if product_info.find(id='ctl51_ctl01_lblFunzioneNome'):
        article_subcategory = product_info.find(id='ctl51_ctl01_lblFunzioneNome').get_text(strip=True) # subcategory
    else:
        return None,[]
    if product_info.find(id='lblCode'):
        if product_info.find(id='ctl51_ctl01_DescrizioneArt'):
            article_desc = 'code ' + product_info.find(id='lblCode').get_text(strip=True) + ' ' + product_info.find(id='ctl51_ctl01_DescrizioneArt').get_text(strip=True) # desc
        else:
            article_desc = 'code ' + product_info.find(id='lblCode').get_text(strip=True)
    else:
        return None, []
    if product_info.find(id='ctl51_ctl01_BoxDes'):
        article_dim = product_info.find(id='ctl51_ctl01_BoxDes').find_all('span', 'valori')
    else:
        article_dim = []
    dim_text = ""
    for span_tag in article_dim:
        dim_text += span_tag.get_text(strip=True) + ' '
    
    desc_art = product_info.find('div', 'descrittoriboolean')
    try:
        os.mkdir('products/' + article_id)        
        os.mkdir('products/' + article_id + '/altArt')        
    except OSError:
        raise
    
    desc_artworks = []
    alt_artworks = []
    if slider_div:
        for img_tag in slider_div:
            src_img = img_tag['data-zoom-image']
            prim_img = requests.get(src_img)            
            with open('products/' + article_id + "/altArt/" + src_img.split('/')[-1], "wb") as prim_img_file:
                prim_img_file.write(prim_img.content)             
            alt_artworks.append('products/' + article_id + "/altArt/" + src_img.split('/')[-1])
        
    for img_tag in desc_art.find_all('img'):
        image_name = img_tag['src'].split('/')[-1]
        image_file = Path('descArt/' + image_name)                
        if image_file.is_file():
            desc_artworks.append(image_file.as_posix())
            continue
        img_contents = requests.get(img_tag['src'])
        with open(image_file, "wb") as img_file:
            img_file.write(img_contents.content)
        desc_artworks.append(image_file.as_posix())

    product_collection = []
    if get_colletion:
        visited_a = [product_url]        
        for a_tag in soup_article.find(id='product-collection').find_all('a'):        
            if a_tag['href'] not in visited_a:
                visited_a.append(a_tag['href'])
                try:
                    sub_product = get_product(a_tag['href'], False)
                except OSError as e:
                    print(e)
                else:
                    product_collection.append(sub_product)
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

with open('scraper_data_test.json') as data_file:
    scraper_data = json.load(data_file)
with open('scraper_meta_data.json') as meta_data_in:
    scraper_meta_data = json.load(meta_data_in)

for category in scraper_data['category']:
    if category['category_name'] in scraper_meta_data['skip_categories']:
        continue
    do_scrape_category = input('Scrape {} category?(y/n)'.format(category['category_name']))
    if str(do_scrape_category).lower() != 'y':
        continue
    print('Category: {}'.format(category['category_name']))
    product_list = []
    while True:
        do_scrape_page = input('Scrape {} page?(y/n)'.format(scraper_meta_data[category['category_name']]['page_no']))
        if str(do_scrape_page).lower() != 'y':
            break
        print('\tPage: {}'.format(scraper_meta_data[category['category_name']]['page_no']))
        response = requests.get(category['category_url'] + '?page_no=' + str(scraper_meta_data[category['category_name']]['page_no']))
        soup = BeautifulSoup(response.text, "html.parser")
        products_on_page = soup.find_all('a', 'nk-portfolio-item-link')
        
        if not products_on_page:
            scraper_meta_data['skip_categories'].append(category['category_name'])
            break

        for a_tag in products_on_page:
            try:
                product, product_collection = get_product(a_tag['href'])
            except OSError as e:
                print("Already exists")
                continue
            else:
                if product is not None:
                    print('\t\tScraped main product: {}'.format(product['product_id']))                
                    product_list.append(product)
                    for p, x in product_collection:
                        if p is not None:
                            print('\t\t\tScraped sub product: {}'.format(p['product_id']))
                            product_list.append(p) 
            
        
        suspension_list = []
        ceiling_list = []
        wall_list = []
        recessed_list = []
        table_list = []
        floor_list = []

        if category['category_name'] == 'Indoor' or category['category_name'] == 'Outdoor' or category['category_name'] == 'Technical':
            for p in product_list:
                if p['product_subcategory'] == 'Hanging':
                    suspension_list.append(p)
                elif p['product_subcategory'] == 'Ceiling':
                    ceiling_list.append(p)
                elif p['product_subcategory'] == 'Applique':
                    wall_list.append(p)
                elif p['product_subcategory'] == 'Recessed':
                    recessed_list.append(p)
                elif p['product_subcategory'] == 'Table' or p['product_subcategory'] == 'Tracklight':
                    table_list.append(p)
                elif p['product_subcategory'] == 'Floor' or p['product_subcategory'] == 'Linear System':
                    floor_list.append(p)  
            category['subcategories'][0]['products'].extend(suspension_list)
            category['subcategories'][1]['products'].extend(ceiling_list)
            category['subcategories'][2]['products'].extend(wall_list)
            category['subcategories'][3]['products'].extend(recessed_list)
            category['subcategories'][4]['products'].extend(table_list)
            category['subcategories'][5]['products'].extend(floor_list)    
        elif category['category_name'] == 'Bulbs':
            category['subcategories'][0]['products'].extend(product_list)

        scraper_meta_data[category['category_name']]['page_no'] += 1                   
    
    
with open('scraper_meta_data.json', 'w') as meta_data_out:
    json.dump(scraper_meta_data, meta_data_out, indent=4)
with open('scraper_data_test.json', 'w') as fout:
    json.dump(scraper_data, fout, indent=4)    
    