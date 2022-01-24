import requests
import json
import os
from lxml import html

BASE_URL = 'https://studien.rj.ost.ch/'
OUTPUT_DIRECTORY = 'data'


content = requests.get(f'{BASE_URL}allStudies/10191_I.html').content
tree = html.fromstring(content)

categories = []
modules = []

for category in tree.xpath('//h3[contains(text(),"Zugeordnete Module")]/following-sibling::div'):
    category_title = category.xpath('.//h5/text()')[0]
    module_names = category.xpath('.//a/text()')
    module_urls = [BASE_URL + url for url in category.xpath('.//a/@href')]

    categories.append(category_title)
    modules.extend([{
        "name": name,
        "url": url,
        "category": category_title,
    } for (name, url) in zip(module_names, module_urls)])


if not os.path.exists(OUTPUT_DIRECTORY):
    os.mkdir(OUTPUT_DIRECTORY)

with open(f'{OUTPUT_DIRECTORY}/categories.json', 'w') as output:
    json.dump(categories, output, indent=2)

with open(f'{OUTPUT_DIRECTORY}/modules.json', 'w') as output:
    json.dump(modules, output, indent=2)
