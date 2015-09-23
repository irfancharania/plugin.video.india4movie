import resources.lib.util as util
import re
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import SoupStrainer


class SiteApi():

    MAIN_URL = 'http://www.india4movie.co/'
    LONG_NAME = 'India 4 Movie'

    def get_menu_category(self):
        '''
        Get main list of categories
        '''
        print 'Get list categories'

        url = self.MAIN_URL
        data = util.get_remote_data(url)
        product = SoupStrainer('div', {'class': 'menu-secondary-container'})

        soup = BeautifulStoneSoup(data, parseOnlyThese=product,
                                  convertEntities=BeautifulSoup.XML_ENTITIES)

        items = []

        for item in soup.findAll('li'):
            link = item.a['href'].encode('utf-8', 'ignore')
            pk = item['id']

            # ignore invalid links
            if 'category/' not in link:
                continue

            items.append({
                'label': item.text,
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
        product = SoupStrainer('div', {'class': 'entry clearfix'})

        soup = BeautifulStoneSoup(data, parseOnlyThese=product,
                                  convertEntities=BeautifulSoup.XML_ENTITIES)
        items = []

        pk_regex = re.compile('\/([\w\-]+)\/')

        for item in soup:
            link = item.a['href'].encode('utf-8', 'ignore')
            img = item.a.img
            thumb = item.a.img['src'].encode('utf-8', 'ignore') if img else ''
            info = item.p.text
            pk = pk_regex.search(item.a['href']).group(1)

            items.append({
                'label': item.text,
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
        product = SoupStrainer('div', {'class': 'wp-pagenavi'})

        soup = BeautifulStoneSoup(data, parseOnlyThese=product,
                                  convertEntities=BeautifulSoup.XML_ENTITIES)
        current_item = soup.find('span', {'class': 'current'})
        if current_item:
            next_item = current_item.findNextSibling()

            if next_item:
                item = {
                    'label': '[B]Next >> [/B]',
                    'url': next_item['href'],
                    'pk': next_item.text
                }
                return item

        return None

    def get_movie_links(self, url):
        print 'Get movie links: {url}'.format(url=url)

        data = util.get_remote_data(url)
        product = SoupStrainer('a', rel="nofollow")

        soup = BeautifulStoneSoup(data, parseOnlyThese=product,
                                  convertEntities=BeautifulSoup.XML_ENTITIES)
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
        product = SoupStrainer('iframe')

        soup = BeautifulStoneSoup(data, parseOnlyThese=product,
                                  convertEntities=BeautifulSoup.XML_ENTITIES)

        if soup.iframe:
            return soup.iframe['src']

        return None
