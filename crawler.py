import requests
import json
import os
import re
from lxml import html
from itertools import groupby

BASE_URL = 'https://studien.rj.ost.ch/'
OUTPUT_DIRECTORY = 'data'
MODULE_PATTERN = re.compile('(.*) \(M_(.*) \/.*')
CATEGORY_PATTERN = re.compile('(.*) \(.*[_-](.*)\)')

EXCLUDED_MODULES = ['SecSW', 'WSLS', 'WIoT']

content = requests.get(f'{BASE_URL}allStudies/10191_I.html').content
tree = html.fromstring(content)

modules = {}
categories = {}
focuses = []

for category in tree.xpath('//h3[contains(text(),"Zugeordnete Module")]/following-sibling::div'):
    category_fullname = category.xpath('.//h5/text()')[0][:-1]

    module_fullnames = category.xpath('.//a/text()')
    module_urls = [BASE_URL + url for url in category.xpath('.//a/@href')]

    (category_name, category_id) = CATEGORY_PATTERN.search(category_fullname).groups() if category_fullname != 'ohne Kategorie' else (None, None)

    if category_name is not None:
        (required_ects, _, total_ects) = category.xpath('.//p/text()')[0].partition('/')
        categories[category_name] = {
            'id': category_id,
            'name': category_name,
            'modules': [],
            'required_ects': required_ects,
            'total_ects': total_ects,
        }

    for (fullname, url) in zip(module_fullnames, module_urls):
        (module_name, module_id) = MODULE_PATTERN.search(fullname).groups()

        if fullname not in modules and not module_id in EXCLUDED_MODULES:
            modules[module_id] = {
                'id': module_id,
                'name': module_name,
                'url': url,
                'categories': [],
                'ects': None,
                'focuses': [],
            }

        if category_name in categories and module_id in modules:
            modules[module_id]['categories'].append(category_id)
            categories[category_name]['modules'].append(module_id)


for module_id,module in modules.items():
    print('Fetching details for module', module['name'])

    details_page = requests.get(module['url']).content
    module_tree = html.fromstring(details_page)

    modules[module_id]['ects'] = int(module_tree.xpath('//h5[contains(text(),"ECTS-Punkte")]/../following-sibling::div/div/text()')[0])


for focus in tree.xpath('//h5[contains(text(),"Vertiefungen")]/../following-sibling::div//a'):
    focuses.append({
        'name': focus.xpath('./text()')[0].replace(' STD_21 (Profil)', ''),
        'url': BASE_URL + focus.xpath('./@href')[0],
        'modules': [],
    })


for focus in focuses:
    print('Fetching details for focus', focus['name'])

    details_page = requests.get(focus['url']).content
    focus_tree = html.fromstring(details_page)

    module_fullnames = focus_tree.xpath('//h3[contains(text(),"Zugeordnete Module")]/following-sibling::div//a/text()')
    module_name_and_id = [MODULE_PATTERN.search(module_fullname).groups() for module_fullname in module_fullnames]

    for module_name, module_id in module_name_and_id:
        if module_id in EXCLUDED_MODULES:
            continue

        focus['modules'].append(module_id)
        modules[module_id]['focuses'].append(focus['name'])


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
