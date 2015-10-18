from resources.lib.abc_base import BaseI4M
import resources.lib.util as util
from bs4 import BeautifulSoup
from bs4 import SoupStrainer


class MovieRulzApi(BaseI4M):

    BASE_URL = 'http://www.movierulz.to/'
    SHORT_NAME = 'mr'
    LONG_NAME = 'Movie Rulz'
    LOCAL_THUMB = 'thumb_movierulz.png'

    SoupStrainer_Category = SoupStrainer('nav', {'id': 'menu'})
    SoupStrainer_Movies = SoupStrainer('div', {'class': 'boxed film'})
    SoupStrainer_Next_Link = SoupStrainer('div', {'class': 'nav-older'})
    SoupStrainer_Movie_Link = SoupStrainer('div', {'class': 'entry-content'})

###############################################

    def get_movie_links(self, url):
        print 'Get movie links: {url}'.format(url=url)

        data = util.get_remote_data(url)

        soup = BeautifulSoup(data, 'html.parser',
                             parse_only=self.SoupStrainer_Movie_Link
                             )
        items = []

        for item in soup.findAll('p'):
            if item.strong and item.a:

                href = item.a.get('href', None)
                if href:

                    label = util.encode(item.strong.text)
                    link = util.encode(href)
                    pk = label

                    items.append({
                        'label': label,
                        'url': link,
                        'pk': pk,
                        'is_playable': True
                    })

        return items
