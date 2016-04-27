import abc
import re
import resources.lib.util as util
from xbmcswift2 import xbmcgui
from bs4 import BeautifulSoup
from bs4 import SoupStrainer


class BaseI4M(object):
    __metaclass__ = abc.ABCMeta

    BASE_URL = ''
    SHORT_NAME = 'base'
    LONG_NAME = 'Base'
    LOCAL_THUMB = ''

    SoupStrainer_Category = SoupStrainer('div', {'class': 'menu-secondary-container'})
    SoupStrainer_Movies = SoupStrainer('div', {'class': 'entry clearfix'})
    SoupStrainer_Next_Link = SoupStrainer('a', rel='next')
    SoupStrainer_Movie_Link = SoupStrainer('a', rel='nofollow')

###############################################

    def search(self, query):
        print 'Searching: ' + query

        items = []

        if query:
            url = '{base}?s={query}'.format(base=self.BASE_URL, query=query)
            items = self.get_menu_movies(url)

        return items

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

        for item in soup.findAll('li'):
            if item.a.has_attr('href'):
                link = util.encode(item.a['href'])
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

        data = util.get_remote_data(url)

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

        pk_regex = re.compile('http://([\w\.]+)\/(?:([\w-]+)\/|)')

        for a in soup:
            if ('Full' in a.text or \
                'Play' in a.text) and \
                'Online' in a.text:

                link = util.encode(a['href'])

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
        soup = BeautifulSoup(data, 'html.parser')
        link = None

        iframe = soup.find('iframe')
        if iframe:
            link = iframe.get('data-lazy-src', None) or \
                iframe.get('src', None)
        else:
            direct = soup.find('a', src=re.compile(r'embed')) or \
                soup.find('a', {'class': 'aio-orange-medium'}) or \
                soup.find('a', {'class': 'main-button dlbutton'}) or \
                soup.find('a', rel='nofollow')

            if direct:
                link = direct.get('href', None)

        print 'Resolving link: {link}'.format(link=link)
        return link
