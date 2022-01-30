import requests
import json
import os
import re
from lxml import html
from itertools import groupby

BASE_URL = 'https://studien.rj.ost.ch/'
OUTPUT_DIRECTORY = 'data'
ID_PATTERN = re.compile('\(M_(\w*)')


content = requests.get(f'{BASE_URL}allStudies/10191_I.html').content
tree = html.fromstring(content)

modules = {}
categories = {}
focuses = []

for category in tree.xpath('//h3[contains(text(),"Zugeordnete Module")]/following-sibling::div'):
    category_name = category.xpath('.//h5/text()')[0][:-1]

    module_names = category.xpath('.//a/text()')
    module_urls = [BASE_URL + url for url in category.xpath('.//a/@href')]

    if category_name != 'ohne Kategorie':
        (required_ects, _, total_ects) = category.xpath('.//p/text()')[0].partition('/')
        categories[category_name] = {
            'name': category_name,
            'modules': [],
            'required_ects': required_ects,
            'total_ects': total_ects,
        }

    for (name, url) in zip(module_names, module_urls):
        if name not in modules and not 'Lern-Support' in name:
            modules[name] = {
                'id': ID_PATTERN.search(name).group(1),
                'name': name,
                'url': url,
                'categories': [],
                'ects': None,
                'focuses': [],
            }
        
        if category_name in categories:
            modules[name]['categories'].append(category_name)
            categories[category_name]['modules'].append(name)


for module_name,module in modules.items():
    print('Fetching details for module', module['name'])

    details_page = requests.get(module['url']).content
    module_tree = html.fromstring(details_page)

    modules[module_name]['ects'] = int(module_tree.xpath('//h5[contains(text(),"ECTS-Punkte")]/../following-sibling::div/div/text()')[0])


for focus in tree.xpath('//h5[contains(text(),"Vertiefungen")]/../following-sibling::div//a'):
    focuses.append({
    'name': focus.xpath('./text()')[0],
    'url': BASE_URL + focus.xpath('./@href')[0],
})


for focus in focuses:
    print('Fetching details for focus', focus['name'])

    details_page = requests.get(focus['url']).content
    focus_tree = html.fromstring(details_page)

    focus['modules'] = focus_tree.xpath('//h3[contains(text(),"Zugeordnete Module")]/following-sibling::div//a/text()')
    for module in focus['modules']:
        modules[module]['focuses'].append(focus['name'])


modules = list(modules.values())
categories = list(categories.values())


if not os.path.exists(OUTPUT_DIRECTORY):
    os.mkdir(OUTPUT_DIRECTORY)

with open(f'{OUTPUT_DIRECTORY}/categories.json', 'w') as output:
    json.dump(categories, output, indent=2)

with open(f'{OUTPUT_DIRECTORY}/modules.json', 'w') as output:
    json.dump(modules, output, indent=2)

with open(f'{OUTPUT_DIRECTORY}/focuses.json', 'w') as output:
    json.dump(focuses, output, indent=2)
