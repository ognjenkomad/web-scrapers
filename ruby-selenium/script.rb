
require 'selenium-webdriver'
require 'pry'

username = 'petar'
password = 'smart1207home12'
category_link = 'edit-tags.php?taxonomy=product_cat&post_type=product'
category_name = 'New 2020 Edition 2'
category_slug = 'new-2020-edition-2'

driver = Selenium::WebDriver.for(:firefox)

driver.get('http://ledrasvjeta.ba/wp-login.php')

# Login
driver.find_element(id: 'user_login').send_keys(username)
driver.find_element(xpath: "//*[@type='password']").send_keys(password)
driver.find_element(id: 'wp-submit').click

# Go to category page
# prozivodi = driver.find_elements(class: 'wp-menu-name').detect { |el| el.text == 'Proizvodi' }
# driver.move_to(prozivodi).perform

category_url = driver.find_element(xpath: "//*[@href='#{category_link}']")['href']
driver.get(category_url)

# create category
driver.find_element(id: 'tag-name').send_keys(category_name)
driver.find_element(id: 'tag-slug').send_keys(category_slug)
select_type = driver.find_element(id: 'display_type')
option = Selenium::WebDriver::Support::Select.new(select_type)
option.select_by(:text, 'Proizvodi')
binding.pry
# upload image
driver.find_element(class: 'upload_image_button').click
driver.find_element(class: 'upload-ui').find_element(tag_name: 'button').click
sleep(3)
driver.find_element(:css, 'input[type=file]').send_keys('/Users/administrator/Documents/ruby-selenium/NEW_ITEMS_2020_EDITION_2.jpg')
sleep(3)
driver.find_elements(tag_name: 'button').detect { |el| el.text == 'Koristi sliku'}.click
sleep(3)
driver.find_elements(tag_name: 'input').detect { |el| el['value'] == 'Dodaj novu kategoriju'}.click
