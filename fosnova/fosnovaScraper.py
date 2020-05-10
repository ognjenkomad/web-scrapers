import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path

with open('meta_data.json') as meta_data:
    scraper_meta_data = json.load(meta_data)
with open('data.json') as data:
    scraper_data = json.load(data)

def scrape_product(soup, category, url):
    print('-' * 20)
    if soup.find('h1', 'prod-title text-left'):
        product_title = soup.find('h1', 'prod-title text-left').get_text(strip=True)    # title
        url.split('/')[-1].split('?')[0]
        product_id = url.split('/')[-1].split('?')[0]
    else:
        print('\t{} product not scraped!'.format(url))
        category['skip_scraping'].extend([url])
        return
    if soup.find('div', 'prod__txt'):
        product_desc = soup.find('div', 'prod__txt').get_text('\n', strip=True)   # description
    else:
        print('\t{} product does not have description!'.format(product_title))
        product_desc = ""
    for div_tag in soup.find_all('div', 'col-sm-3 text-right'):
        if div_tag.find('a'):
            product_pdf_url = scraper_meta_data['base_url'] + div_tag.find('a')['href']     # pdf url
            break
        else:
            print('\t{} product does not have pdf!'.format(product_title))
            product_pdf_url = ""
    if soup.find(id='zoom-prod'):
        product_image_url = scraper_meta_data['base_url'] + soup.find(id='zoom-prod')['href']   # image url
    else:
        print('\t{} product does not have image!'.format(product_title))
        product_image_url = ""
    if soup.find(id='item-pitto'):
        product_image_dim_url = scraper_meta_data['base_url'] + soup.find(id='item-pitto')['href']   # dimensions image url
    else:
        print('\t{} product does not have dimension image!'.format(product_title))
        product_image_dim_url = ""
    if soup.find(id='pitto'):
        product_art_image_urls = []                                                                 # descArt image urls
        for a_tag in soup.find(id='pitto').find_all('a', 'pittogramma'):            
            if a_tag.find('img'):
                url_to_add = scraper_meta_data['base_url'] + a_tag.find('img')['src']
                product_art_image_urls.append(url_to_add)
    else:
        print('\t{} product does not have descArt images!'.format(product_title))
        product_art_image_urls = []
    if soup.find('div', 'table-responsive'):
        product_table = []
        table_tag = soup.find('div', 'table-responsive').find('table', 'table table-striped table__art')    # table items
        if table_tag:
            dict_keys = []            
            for header_title in table_tag.find('thead').find('tr').find_all('th'):
                if header_title.get_text(strip=True) != "":
                    dict_keys.append(header_title.get_text(strip=True))
            if dict_keys:
                dict_keys.append('Colour')
                for tbody_tag in soup.find_all('tbody', recursive = False):
                    dict_values = []
                    for idx, td_tag in enumerate(tbody_tag.find('tr').find_all('td')):
                        if idx > 5:
                            break
                        if td_tag.get_text(strip=True) != "":
                            dict_values.append(td_tag.get_text(strip=True))
                    product_table_item = dict(zip(dict_keys, dict_values))
                    product_table.append(product_table_item)
    else:
        print('\t{} product does not have table data!'.format(product_title))
        product_table = []


    try:
        os.mkdir('products/' + product_id)                          # make folder for product and download images and pdf
        os.mkdir('products/' + product_id + '/altArt')        
    except OSError:
        print('\t{} product folder already exists!'.format(product_title))
    
    alt_artworks = []
    for image_url in [product_image_url, product_image_dim_url]:
        prim_img = requests.get(image_url)            
        with open('products/' + product_id + "/altArt/" + image_url.split('/')[-1], "wb") as prim_img_file:
            prim_img_file.write(prim_img.content)             
        alt_artworks.append('products/' + product_id + "/altArt/" + image_url.split('/')[-1])
    
    desc_artworks = []
    for small_image_url in product_art_image_urls:
        image_name = small_image_url.split('/')[-1]
        image_file = Path('descArt/' + image_name)                
        if image_file.is_file():
            desc_artworks.append(image_file.as_posix())
            continue
        img_contents = requests.get(small_image_url)
        with open(image_file, "wb") as img_file:
            img_file.write(img_contents.content)
        desc_artworks.append(image_file.as_posix())
    
    pdf_content = requests.get(product_pdf_url)
    with open('products/' + product_id + "/" + product_pdf_url.split('/')[-1], "wb") as pdf_file:
        pdf_file.write(pdf_content.content)
    product_pdf_loc = 'products/' + product_id + "/" + product_pdf_url.split('/')[-1]
    
    product_dict = {
        "product_id" : product_id,
        "product_title" : product_title,
        "product_url" : url,
        "product_description" : product_desc,
        "product_artworks" : {
            "description_artworks" : desc_artworks,
            "alternate_artworks" : alt_artworks
        },
        "product_pdf" : product_pdf_loc,
        "product_table" : product_table
    }

    cat_inx = None
    for idx, cat in enumerate(scraper_data['category']):
        if category['category_name'] == cat['category_name']:
            cat_inx = idx
    scraper_data['category'][cat_inx]['products'].append(product_dict)
    print('\tSCRAPED {} PRODUCT!'.format(product_title.upper()))
    print('-' * 20)
    category['skip_scraping'].extend([url])

def visit_product(category, product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, "html.parser")
    products_on_page = soup.find(id='mainContent_noapp')
    if products_on_page:
        products_on_page = products_on_page.find(id='product_container').find_all('div', 'col-sm-3 col-lg-2 col-xs-6')        
        for product in products_on_page:
            url = scraper_meta_data['base_url'] + product.find('a')['href'] + scraper_meta_data['language_param']
            product_name = product.find('div', 'news-box__title vert-middle hor-center').get_text(strip=True)
            if url  not in category['skip_scraping']:
                if scraper_meta_data['interactive']:                    
                    do_scrape_product = input('Scrape {} product?(y/n/q)'.format(product_name))
                    if str(do_scrape_product).lower() == 'n':
                        continue
                    elif str(do_scrape_product).lower() == 'q':
                        return
                visit_product(category, url)
            else:
                print('\tPRODUCT {} ALREADY SCRAPED!'.format(product_name.upper()))
    else:
        scrape_product(soup, category, product_url)

for category in scraper_meta_data['categories']:
    do_scrape_category = input('Scrape {} category?(y/n)'.format(category['category_name']))
    if str(do_scrape_category).lower() != 'y':
        continue
    print('Category: {}'.format(category['category_name']))
    visit_product(category, category['category_url'] + scraper_meta_data['language_param'])
    

do_save = input('Save meta data?(y/n)')
if str(do_save).lower() == 'y':
    with open('meta_data.json', 'w') as meta_data_out:
        json.dump(scraper_meta_data, meta_data_out, indent=4)

do_save = input('Save data?(y/n)')
if str(do_save).lower() == 'y':
    with open('data.json', 'w') as data_out:
        json.dump(scraper_data, data_out, indent=4)
