from resources.lib.abc_base import BaseI4M
import resources.lib.util as util
from bs4 import BeautifulSoup
from bs4 import SoupStrainer


class FullNewMovieApi(BaseI4M):

    BASE_URL = 'http://www.fullnewmovie.net/'
    SHORT_NAME = 'fnm'
    LONG_NAME = 'Full New Movie'
    LOCAL_THUMB = ''

    SoupStrainer_Category = SoupStrainer('div', {'class': 'menu-menu-container'})
    SoupStrainer_Movies = SoupStrainer('div', {'class': 'post-text'})
    SoupStrainer_Next_Link = SoupStrainer('div', {'class': 'nextpostslink'})
    SoupStrainer_Movie_Link = SoupStrainer('div', {'class': 'post-text'})

###############################################

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
