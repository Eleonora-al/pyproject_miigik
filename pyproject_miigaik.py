from bs4 import BeautifulSoup
import requests
import json
import xlsxwriter
import time
start_time = time.time()

def dump_to_json(filename, data, **kwargs):
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('indent', 1)
    with open (filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent = 1)

def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup

#парсим одну гонку
def parse(data, link):
    url = 'https://www.motorsport.com' + link
    a = get_soup(url).find_all('span', class_='name')  # Racer's name
    b = get_soup(url).find_all('td', class_='ms-table_cell ms-table_field--time')  # time
    c = get_soup(url).find_all('td', class_='ms-table_cell ms-table_field--pits')  # pits
    d = get_soup(url).find_all('td', class_='ms-table_cell ms-table_field--avg_speed')  # average speed
    yr = link[12:(link[:-1].rfind('/'))]  # year
    gp = link[17:(link.find('-gp'))]  # country

    for i in range(min(len(a), len(b), len(c), len(d))):
        item = {
            'Name': a[i].text.strip(),
            'Time': b[i].text.strip(),
            'Pits': c[i].text.strip(),
            'AVG speed': d[i].text.strip(),
            'yearr': yr,
            'Grand Prix': gp
        }
        data.append(item)
        item = {}

def dump_tp_xlsx(filename, data):
    with xlsxwriter.Workbook(filename) as workbook:
        ws = workbook.add_worksheet()

        headers = ['Racer', 'Time', 'Pits', 'AVG speed', 'Year', 'Grand Prix']
        for a, b in enumerate(headers):
            ws.write_string(0, a, b)

        for row, item in enumerate(data, start = 1):
            ws.write_string(row, 0, item['Name'])
            ws.write_string(row, 1, item['Time'])
            ws.write_string(row, 2, item['Pits'])
            ws.write_string(row, 3, item['AVG speed'])
            ws.write_string(row, 4, item['yearr'])
            ws.write_string(row, 3, item['Grand Prix'])

def get_links(url, links):
    a = get_soup(url).find_all('a', class_='ms-results-subnav_item')
    for i in a:
        links.append((i.get('href')))  # get href to every race in a year
    """for link in links:
        parse(data, link)"""

def get_years(url, years):
    a = get_soup(url).find_all('a', class_='ms-link ms-filter-option ms-filter-option--sort-by')
    for i in a:
        years.append(i.get('href'))
    years.append(get_soup(url).find('a', class_='ms-link ms-filter-option ms-filter-option--sort-by active').get('href'))
    years = sorted(years)

    """for year in years:
        url = 'https://www.motorsport.com' + year
        get_links(url, links)"""

out_json_filename = 'qout.json'
out_xlsx_filename = 'out.xlsx'
links =[]
years = []
data =[]
url = 'https://www.motorsport.com/f1/results/2015/australian-gp-26/'

get_years(url, years)
for year in years:
    url = 'https://www.motorsport.com' + year
    get_links(url, links)
for link in links:
    parse(data, link)
dump_tp_xlsx(out_xlsx_filename, data)
dump_to_json(out_json_filename, data)
print("--- %s seconds ---" % (time.time() - start_time))

