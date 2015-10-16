import resources.lib.util as util
import re
from bs4 import BeautifulSoup
from bs4 import SoupStrainer


class SiteApi():

    MAIN_URL = 'http://www.india4movie.co/'
    LONG_NAME = 'India 4 Movie'

    def search(self, query):
        print 'Searching: ' + query

        items = []

        if query:
            url = '{base}?s={query}'.format(base=self.MAIN_URL, query=query)
            items = self.get_menu_movies(url)

        return items

    def get_menu_category(self):
        '''
        Get main list of categories
        '''
        print 'Get list categories'

        url = self.MAIN_URL
        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, 'html.parser',
                             parse_only=SoupStrainer('div', {'class': 'menu-secondary-container'})
                             )

        items = []

        for item in soup.findAll('li'):
            link = item.a['href'].encode('utf-8', 'ignore')
            pk = item['id']

            # ignore invalid links
            if 'category/' not in link:
                continue

            items.append({
                'label': item.a.text,
                'url': link,
                'pk': pk,
            })

        return items

    def get_menu_movies(self, url):
        '''
        Get movie titles for category
        '''
        print 'Get list movies: {url}'.format(url=url)

        data = util.get_remote_data(url)

        # Get list of movie titles
        soup = BeautifulSoup(data, 'html.parser',
                             parse_only=SoupStrainer('div', {'class': 'entry clearfix'})
                             )
        items = []

        pk_regex = re.compile('\/([\w\-]+)\/')

        for item in soup:
            img = item.a.img
            thumb = img['src'].encode('utf-8', 'ignore')

            link = item.a['href'].encode('utf-8', 'ignore')
            info = item.h4.text.strip()
            label = info
            pk = pk_regex.search(item.a['href']).group(1)

            items.append({
                'label': label,
                'url': link,
                'thumb': thumb,
                'info': info,
                'pk': pk,
                'is_playable': False
            })

        return items

    def get_next_link(self, url):
        '''
        Get next page link
        '''
        print 'Get next page link: {url}'.format(url=url)

        data = util.get_remote_data(url)

        # Get list of movie titles
        soup = BeautifulSoup(data, 'html.parser',
                             parse_only=SoupStrainer('a', rel='next')
                             )

        if soup:
            link = soup.a['href']
            page = link.rstrip('/').rsplit('/', 1)[1]
            
            item = {
                'label': '[B]Next >> [/B]',
                'url': link,
                'pk': page
            }
            return item

        return None

    def get_movie_links(self, url):
        print 'Get movie links: {url}'.format(url=url)

        data = util.get_remote_data(url)

        soup = BeautifulSoup(data, 'html.parser',
                             parse_only=SoupStrainer('a', rel='nofollow')
                             )
        items = []

        pk_regex = re.compile('http://([\w\.]+)\/(?:([\w-]+)\/|)')

        for a in soup:
            if 'Full' in a.text and 'Online' in a.text:
                link = a['href'].encode('utf-8', 'ignore')

                match = pk_regex.search(link)
                if match:
                    group1 = match.group(1)
                    group2 = match.group(2)
                    label = group2 if group2 else group1
                    pk = label

                    items.append({
                        'label': label,
                        'url': link,
                        'pk': pk,
                        'is_playable': True
                    })

        return items

    def resolve_redirect(self, url):
        print 'Resolving redirect: {url}'.format(url=url)

        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, 'html.parser',
                             parse_only=SoupStrainer('div', id='content')
                             )
        link = None

        iframe = soup.find('iframe')
        if iframe:
            link = iframe['src']
        else:
            direct = soup.find('a', rel='nofollow')
            if direct:
                link = direct['href']


        return link
