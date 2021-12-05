import os

import requests
from bs4 import BeautifulSoup


class ArticlesExtraction:
    "Class for articles extraction from https://as-botanicalstudies.springeropen.com website"

    def __init__(self, number=20, verbose=True, save_txt=True, save_pdf=True):
        self.number = number
        if self.number >= 50:
            raise ValueError(f'Maximum number of articles supported is 50, {self.number} was chosen')
        self.verbose = verbose
        self.save_txt = save_txt
        self.save_pdf = save_pdf

    def _get_links(self):
        if self.verbose:
            print(f'Getting the links for {self.number} articles...')
        mainpage = requests.get('https://as-botanicalstudies.springeropen.com/articles')
        mainsoup = BeautifulSoup(mainpage.text, features='lxml')
        links = ['https://as-botanicalstudies.springeropen.com' + x['href'] for x in
                 sum([x.findAll('a') for x in mainsoup.findAll('h3', class_="c-listing__title")], [])]
        return links[:self.number]

    def extract(self):
        extra = ['Availability of data and materials', 'Abbreviations', 'References', 'Acknowledgements',
                 'Funding', 'Author information', 'Ethics declarations', 'Additional information',
                 'Rights and permissions', 'About this article']
        links = self._get_links()
        pdf_links = []
        if self.verbose:
            print('Getting the texts...')
        texts = dict()
        for num, link in enumerate(links):
            if self.verbose:
                print(f'{num + 1}/{len(links)} links', end="\r")
            page = requests.get(link)
            pagecontent = BeautifulSoup(page.text, features='lxml')
            name = pagecontent.findAll('h1', class_="c-article-title")[0].text
            text = "\n".join(sum([list(map(lambda y: y.text, x.findAll('p'))) for x in pagecontent.findAll('section') if
                                  x.has_attr('data-title') and x['data-title'] not in extra], []))
            texts[name] = text
            pdf_link = [x.findAll('a') for x in pagecontent.findAll('div', class_="c-pdf-download u-clear-both")][0][0][
                'href']
            pdf_links.append(pdf_link)
        if self.save_txt:
            if self.verbose:
                print('Saving the articles in txt...')
            if not os.path.exists('articles'):
                os.mkdir('articles')
            for key, value in texts.items():
                with open(f"articles/{key.replace('/', '|')}.txt", 'w', encoding='utf-8') as file:
                    file.write(value)
        if self.save_pdf:
            if self.verbose:
                print('Saving the articles in pdf...')
            if not os.path.exists('articles_pdf'):
                os.mkdir('articles_pdf')
            for (key, value), link in zip(texts.items(), pdf_links):
                pdf = requests.get('https:' + link, allow_redirects=True)
                open(f"articles_pdf/{key.replace('/', '|')}.pdf", 'wb').write(pdf.content)
        return texts
