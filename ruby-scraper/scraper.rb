require 'nokogiri'
require 'httparty'
require 'byebug'
require "json"
require "down"
require "fileutils"

BASE_URL = 'https://www.1-light.eu'.freeze
CATEGORIES_URL = BASE_URL + '/_processScripts/loadCategories.php'
PRODUCTS_URL = 
UNNECESSARY_CATEGORIES = ['Accessories', 'Advertising & Marketing'].freeze

def scraper
  json = {
    categories: []
  }

  unparsed_page = HTTParty.get(CATEGORIES_URL)
  parsed_page = Nokogiri::HTML(unparsed_page)

  categories = get_categories(parsed_page).compact
  json[:categories] = categories
  # # categories.each do |category|

  # # end

  category = json[:categories].first
  products = get_products(category)
  json[:categories].first[:products] = products

  parsed_json = json.to_json
  File.open('one-light.json', 'w') do |f|
    f.write(parsed_json)
  end
end

def get_categories(page)
  categories = page.css('div.categoryBlock')

  categories = categories.map do |category|
    url = category.css('.categoryBlock__image a').attribute('href').text
    image_url = category.css('.categoryBlock__image a img').attribute('src').text
    category_name = category.css('.categoryBlock__image a img').attribute('alt').text
    category_name = category_name.gsub(/^(\d* )/, '')

    next if UNNECESSARY_CATEGORIES.include?(category_name)

    path_to_the_artwork = download_artwork(image_url)
    {
      category_name: category_name,
      category_url: BASE_URL + url,
      category_artwork: path_to_the_artwork,
      products: []
    }
  end

  categories
end

def get_products(category, page_number = 1)
  products = []
  url = BASE_URL + '/_processScripts/loadProducts2.php'
  puts ">>>>>>>>>> page_number #{page_number}"
  category_number = category[:category_url].match(/([^\/]+$)/)[0]
  products_response = HTTParty.post(url, body: { categories: category_number.to_i, selectedView: 1, pageNumber: page_number, limitNumber: 48 })
  parsed_response = Nokogiri::HTML(products_response)
  pagination_items = parsed_response.css('.pagination li').reject { |li| li.attribute('class') && li.attribute('class').text == 'active' }

  parsed_response.css('.familyBlock .row div').each do |item|
    product_url = item.css('.familyBlock__product .familyBlock__product__image a').attribute('href')
    product_image = item.css('.familyBlock__product .familyBlock__product__image a img').attribute('src')
    product_name = item.css('.familyBlock__product__image__title').text

    next unless product_url && product_image && product_name

    products = products.concat(get_product(product_url.text))
    puts ">>>>>>>>>>>>>>>>>> #{product_name} DONE!"
  end

  if page_number == 1
    pagination_items.each do |pagination_item|
      page_number = pagination_item.css('a').text
      products.concat(get_products(category, page_number))
    end
  end
  products
end


def get_product(url, is_variant = false)
  complete_url = url.match(/^\//).nil? ? BASE_URL + '/' + url : BASE_URL + url
  product_response = HTTParty.get(complete_url)
  parsed_response = Nokogiri::HTML(product_response)

  product_id                  = url.match(/\/([^\/]*)$/)[1]
  product_name                = parsed_response.css('.productGreyCell .productSummaryTitle').text.gsub('/', '-')
  product_url                 = complete_url
  product_description         = parsed_response.css('.productGreyCell .row')[2].text.strip.gsub(/\r\n?/, '')
  product_description_images  = parsed_response.css('.productGreyCell .row')[4].css('img')
  dimensions_div              = parsed_response.css('.productHeader').detect { |div| div.text == 'Dimensions'}
  pdf_div                     = parsed_response.css('.productDownloads').detect { |div| div.attribute('title').text == 'Product Pdf'}

  main_artwork                = parsed_response.css('.productPhotoSummary img')
  alternate_artworks_imgs     = parsed_response.css('.colorboxPhoto img')
  artworks                    = [main_artwork, alternate_artworks_imgs].flatten 

  alternate_artworks = []
  artworks.each do |alternate_artwork|
    alternate_artwork_url = alternate_artwork.attribute('src').text
    alternate_artworks << download_artwork(alternate_artwork_url, "#{product_name}/altArt")
  end

  description_artworks = []
  product_description_images.each do |image|
    image_url = image.attribute('src').text
    description_artworks << download_artwork(image_url, 'description_artworks')
  end

  unless dimensions_div.nil?
    dimension_artwork_url = dimensions_div.parent.parent.next_element.css('img').attribute('src').text
    dimension_artwork = download_artwork(dimension_artwork_url, "#{product_name}/dimArt")
  end

  unless pdf_div.nil?
    url = pdf_div.attribute('href').text
    pdf_path = download_pdf(url, "#{product_name}/pdf")
  end

  unless is_variant
    color_variants = parsed_response.css('.product__color').reject { |item| item.attribute('class').text.include?('active') }

    related_products = []
    color_variants.each do |color_variant|
      url = color_variant.css('a').attribute('href').text
      related_products << get_product(url, true)
    end
  end

  product = {
    product_id: product_id,
    product_name: product_name,
    product_url: product_url,
    product_description: product_description,
    product_artworks: {
      description_artworks: description_artworks,
      alternate_artworks: alternate_artworks,
      dimension_artwork: dimension_artwork
    },
    pdf_file: pdf_path
  }

  if is_variant
    return product
  else
    return related_products.unshift(product)
  end
end

def download_artwork(image_url, folder_name = 'categories')
  begin
    complete_url = image_url.match(/^\//).nil? ? BASE_URL + '/' + image_url : BASE_URL + image_url
    tempfile = Down.download(complete_url)
    path = "#{folder_name}/#{tempfile.original_filename}"
    FileUtils.mkdir_p folder_name
    FileUtils.mv(tempfile.path, "./#{path}")
    path
  rescue Exception => ex
    puts ">>>>>>>>>>> EXCEPTION #{ex.to_s}"
    nil
  end
end

def download_pdf(url, folder_name)
  begin
    complete_url = url.match(/^\//).nil? ? BASE_URL + '/' + url : BASE_URL + url 
    tempfile = Down.download(complete_url)
    path = "#{folder_name}/#{tempfile.original_filename}"
    FileUtils.mkdir_p folder_name
    FileUtils.mv(tempfile.path, "./#{path}")
    path
  rescue Exception => ex
    puts ">>>>>>>>>>> EXCEPTION #{ex.to_s}"
    nil
  end
end

scraper
