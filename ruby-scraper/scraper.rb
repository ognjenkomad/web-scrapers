require 'nokogiri'
require 'httparty'
require 'byebug'
require "json"

BASE_URL = 'https://www.1-light.eu'.freeze
CATEGORY_URL = BASE_URL + '/_processScripts/loadCategories.php'

def scraper
  unparsed_page = HTTParty.get(CATEGORY_URL)
  parsed_page = Nokogiri::HTML(unparsed_page)
  categories = parsed_page.css('div.categoryBlock')

  json = {
    categories: []
  }

  categories.each do |category|
    url = category.css('.categoryBlock__image a').attribute('href').text
    image_url = category.css('.categoryBlock__image a img').attribute('src').text
    category_name = category.css('.categoryBlock__image a img').attribute('alt').text

    
  end

  # json[:categories].each do |category|
  category = json[:categories].first
  category_number = category[:category_url].match(/([^\/]+$)/)[0]
  url = BASE_URL + '/_processScripts/loadProducts2.php'
  response = HTTParty.post(url, body: { categories: category_number.to_i, selectedView: 1, pageNumber: 1, limitNumber: 48 })
  parsed_response = Nokogiri::HTML(response)

  subcategory = ''
  subcategory_hash = {}
  parsed_response.css('.familyBlock .row div').each do |item|
    if item.attribute('class').text.include?('familyBlock__title')
      if subcategory != item.text
        subcategory = item.text
        subcategory_name = subcategory.match(/([^\>]+$)/)[0].strip
        subcategory_hash = { subcategory_name: subcategory_name,  products: [] } 
        category[:subcategories] << subcategory_hash
      end
    else
      product_url = item.css('.familyBlock__product .familyBlock__product__image a').attribute('href')
      product_image = item.css('.familyBlock__product .familyBlock__product__image a img').attribute('src')
      product_image_title = item.css('.familyBlock__product__image__title')

      next unless product_url && product_image && product_image_title

      subcategory_hash[:products] << {
        product_url: BASE_URL + '/' + product_url.text,
        product_image_url: BASE_URL + product_image.text,
        product_image_title: product_image_title.text
      }
    end
  end
  # end
  parsed_json = json.to_json
  File.open('lights.json', 'w') { |file| file.puts JSON.pretty_generate(parsed_json) }
  
  # csv_data = CSV.generate do |csv|
  #   JSON.parse(File.open('lights.json').read).each do |hash|
  #     csv << hash.values
  #   end
  # end

  # File.open('lights.csv', 'w') { |f| f.puts csv_data }  

end

scraper


json[:categories] << {
  category_name: 'indoor',
  category_url: BASE_URL + '/' + url,
  category_image: BASE_URL + image_url,
  subcategories: [
    {
      category_name: 'suspension',
      category_url: BASE_URL + '/' + url,
      category_image: BASE_URL + image_url,
      products: [
        {
          id: 'sdas',
          product_name: '',
          product_url: BASE_URL + '/' + product_url.text,
          product_image_url: BASE_URL + product_image.text,
          artworks: {
            primary_artwork: 'ime_artikla/id',
            descritpion_artworks: ['ime_artikla/descriptions/id1'],
            alternate_artworks: ['ime_artikla/artworks/id1']
          }
          descritpion: ''
          dimensions: {
            text: '',
            image: 
          }
        }
      ]
    }
  ]
}