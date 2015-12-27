from resources.lib.abc_base import BaseI4M
import resources.lib.util as util
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import re


class FullNewMovieApi(BaseI4M):

    BASE_URL = 'http://www.fullnewmovie.net/'
    SHORT_NAME = 'fnm'
    LONG_NAME = 'Full New Movie'
    LOCAL_THUMB = ''

    SoupStrainer_Category = SoupStrainer('div', {'id': 'menu'})
    SoupStrainer_Movies = SoupStrainer('div', {'class': 'post-text'})
    SoupStrainer_Next_Link = SoupStrainer('a', rel='next')
    SoupStrainer_Movie_Link = SoupStrainer('p')

###############################################

    def get_menu_category(self, api):
        '''
        Get main list of categories
        '''
        print 'Get list categories'

        url = self.BASE_URL
        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, 'html.parser',
                             parse_only=self.SoupStrainer_Category
                             )

        items = []

        pk_regex = re.compile('\/([\w\-]+)\/')
        
        for item in soup.findAll('li'):
            if item.a.has_attr('href'):
                link = util.encode(item.a['href'])
                # ignore invalid links
                if 'category/' not in link:
                    continue

                pk = pk_regex.search(item.a['href']).group(1)

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

        data = util.get_remote_data(url, False)

        # Get list of movie titles
        soup = BeautifulSoup(data, 'html.parser',
                             parse_only=self.SoupStrainer_Movies
                             )
        items = []

        pk_regex = re.compile('\/([\w\-]+)\/')

        for item in soup:
            img = item.a.img
            thumb = util.encode(img['src']) if img else ''

            link = util.encode(item.a['href'])

            txt = item.text.strip() or item.a.get('title', None)
            info = util.encode(txt.strip())
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

        data = util.get_remote_data(url, False)

        # Get list of movie titles
        soup = BeautifulSoup(data, 'html.parser',
                             parse_only=self.SoupStrainer_Next_Link
                             )

        if soup and soup.a:
            link = soup.a['href']
            page = link.rstrip('/').rsplit('/', 1)[1]

            item = {
                'label': '[B]Next >> [/B]',
                'thumb': '',
                'info': '',
                'url': link,
                'pk': page,
                'is_playable': False
            }
            return item

        return None

    def get_movie_links(self, url):
        print 'Get movie links: {url}'.format(url=url)

        data = util.get_remote_data(url)

        soup = BeautifulSoup(data, 'html.parser',
                             parse_only=self.SoupStrainer_Movie_Link
                             )
        items = []

        for item in soup.findAll('a', href=True):
            lower = item.text.lower()

            if 'in' in lower and 'now' in lower:
                label = util.encode(item.text)
                link = util.encode(item['href'])
                pk = label

                items.append({
                    'label': label,
                    'url': link,
                    'pk': pk,
                    'is_playable': True
                })

        return items
