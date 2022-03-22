import requests
from bs4 import BeautifulSoup
import requests_cache

requests_cache.install_cache('demo_cache')

class ImdbScraper(object):

    def __init__(self, url):
        self. url = url
        self.data = {}
        self.data_references = {}

    def get_request(self):
        return requests.get(self.url).text

    def get_soup(self):
        return BeautifulSoup(self.get_request(), 'html.parser')

    def get_page(self):
        return self.get_soup().find('main', class_='page__main')
    
    def get_content(self):
        page = self.get_page()
        return page.find('div', class_='mw-parser-output')

    def get_text(self):
        url = 'https://leagueoflegends.fandom.com/'
        page = self.get_page()
        content = self.get_content()     
         
        title = page.find('h1', class_='page-header__title').get_text().strip()
        skinCataLink = content.div
        link = url + skinCataLink.a['href']
        description = content.p.get_text().strip()
        availableChamps = content.find('span', class_='mw-headline').get_text().strip()
        costReductions = content.select('#Upcoming_Cost_Reductions')[0].get_text().strip()
        costReductionsMain = content.dl.dd.i.div.get_text()
        costReductionsMainLink = url + content.dl.dd.i.div.a['href']
        costReductionsList = content.find_all('ul', limit=3)[2].get_text().strip().split('\n')
        scrappedChamps = content.select('#List_of_Scrapped_Champions')[0].get_text().strip()
        scrappedChampsList = content.find('div', class_='columntemplate').ul
        # Beautify the list
        save = []
        columns = scrappedChampsList.find_all('li')
        for column in columns:
            text = column.find_all('a', limit=2)[1].get_text()
            save.append(text)
        trivia = content.select('#Trivia')[0].get_text().strip()
        triviaList = content.select('a[href="/wiki/Urf"]')[1]
        triviaListLink = url + triviaList['href']

        return {
            'title': title, 
            'skinCataLink': skinCataLink.get_text().strip(),
            'link': link, 
            'description': description, 
            'availableChamps': availableChamps, 
            'costReductions': costReductions,
            'costReductionsMain': costReductionsMain, 
            'costReductionsMainLink': costReductionsMainLink, 
            'costReductionsList': costReductionsList, 
            'scrappedChamps': scrappedChamps, 
            'scrappedChampsList': save,
            'trivia': trivia,
            'triviaList': triviaList.get_text().strip(),
            'triviaListLink': triviaListLink,
        }

    def get_references(self):
        page = self.get_page()
        content = self.get_content()
        title = content.select('#References')[0].get_text().strip()

        box = content.find('div', class_='navbox-wrapper')
        header = box.find('div').get_text().strip()
        table = box.find('tbody')
        rows = table.find_all('tr')
        for row in rows:
            columns = row.find_all(['th', 'td'])
            save = []
            for cell in columns:
                datas = list(map(lambda data: data.get_text().strip(), cell))
                save.append(list(filter(lambda data: data, datas)))
            self.data_references[f'{" ".join(save[0])}'] = ''.join(map(str, save[1]))
        
        return {
            'title': title,
            'header': header,
            'save': self.data_references,
        }


    def get_top_imdb(self):
        page = self.get_page()
        content = self.get_content()

        table = content.find('table', class_='article-table')
        rows = table.find_all('tr')

        for row in rows:
            columns = row.find_all(['th', 'td'])
            save = []
            for cell in columns:
                datas = list(map(lambda data: data.get_text().strip(), cell))
                save.append(list(filter(lambda data: data, datas)))

            self.data[f'{" ".join(save[0])}'] = {
                'classes': save[1][0],
                'date': save[2][0],
                'lastChanged': save[3][0],
                'BE': save[4][0],
                'RP': save[5][0],
                }

        return self.data


if __name__ == "__main__":

    # Get texts
    text = ImdbScraper(r'https://leagueoflegends.fandom.com/wiki/List_of_champions').get_text()
    print(text['title']+ '\n \n')
    print(text['skinCataLink'])
    print(text['link'] + '\n')
    print(text['description']+ '\n \n')
    print(text['availableChamps']+ '\n')

    # Get champion's table
    table = ImdbScraper(r'https://leagueoflegends.fandom.com/wiki/List_of_champions').get_top_imdb()
    print('{:_^152}'.format('_'))
    for prop, value in table.items():
        print('|{:^50s} | {:^20s} | {:^20s} | {:^20s} | {:^15s} | {:^10s}|'.format(prop,value['classes'],value['date'],value['lastChanged'],value['BE'],value['RP']))
        print('|{:_^150}|'.format('_'))
    print('\n \n')
    print(text['costReductions']+ '\n')
    print(text['costReductionsMain'])
    print(text['costReductionsMainLink']+ '\n')
    print(text['costReductionsList'][0].strip())
    print(text['costReductionsList'][1].strip() + '\n \n')
    print(text['scrappedChamps']+ '\n')
    for prop in text['scrappedChampsList']:
        print(f"- {prop}")
    print('\n \n')
    print(text['trivia'] + '\n')
    print(text['triviaList'])
    print(text['triviaListLink'] + '\n \n')
    
    # Get refenrces table
    references = ImdbScraper(r'https://leagueoflegends.fandom.com/wiki/List_of_champions').get_references()
    print(references['title']+ '\n \n')
    print(references['header']+ '\n')
    for prop, value in references['save'].items():
        print(f"{prop}: {value}")

