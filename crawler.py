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
    category_title = category.xpath('.//h5/text()')[0][:-1]
    module_names = category.xpath('.//a/text()')
    module_urls = [BASE_URL + url for url in category.xpath('.//a/@href')]

    categories.append(category_title)

    modules.extend([{
        "name": name,
        "url": url,
        "category": category_title,
    } for (name, url) in zip(module_names, module_urls)])


for module in modules:
    try:
        print('Fetching details for module', module['name'])

        details_page = requests.get(module['url']).content
        module_tree = html.fromstring(details_page)

        module['ects'] = int(module_tree.xpath('//h5[contains(text(),"ECTS-Punkte")]/../following-sibling::div/div/text()')[0])
    except:
        pass


focuses = [{
    'name': focus.xpath('./text()')[0],
    'url': BASE_URL + focus.xpath('./@href')[0]
} for focus in tree.xpath('//h5[contains(text(),"Vertiefungen")]/../following-sibling::div//a')]


for focus in focuses:
    print('Fetching details for focus', focus['name'])

    details_page = requests.get(focus['url']).content
    focus_tree = html.fromstring(details_page)

    focus['modules'] = focus_tree.xpath('//h3[contains(text(),"Zugeordnete Module")]/following-sibling::div//a/text()')


if not os.path.exists(OUTPUT_DIRECTORY):
    os.mkdir(OUTPUT_DIRECTORY)

with open(f'{OUTPUT_DIRECTORY}/categories.json', 'w') as output:
    json.dump(categories, output, indent=2)

with open(f'{OUTPUT_DIRECTORY}/modules.json', 'w') as output:
    json.dump(modules, output, indent=2)

with open(f'{OUTPUT_DIRECTORY}/focuses.json', 'w') as output:
    json.dump(focuses, output, indent=2)
