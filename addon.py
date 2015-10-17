from xbmcswift2 import Plugin, xbmcgui
from resources.lib.api import SiteApi
import urllib


plugin = Plugin()
api = SiteApi()


@plugin.cached_route('/')
def index():
    '''
    Get movie categories
    '''
    plugin.log.debug('Get category menu')

    c = api.get_menu_category()

    items = [{
        'label': item['label'],
        'path': plugin.url_for(
            'browse_category', menuid=item.get('pk', '0'),
            page=1, url=item['url'])
    } for item in c]

    # search
    items.insert(0, {
        'label': "[B]** Search **[/B]",
        'path': plugin.url_for('search')
    })

    return items


@plugin.route('/search/')
def search():
    query = get_args('input') or plugin.keyboard(
        heading='Search'
    )
    if query:
        enc = urllib.quote_plus(query)
        movies = api.search(enc)

        items = [{
            'label': item['label'],
            'thumbnail': item['thumb'],
            'icon': item['thumb'],
            'info': {
                'plot': item['info']
            },
            'path': plugin.url_for(
                'browse_movie', menuid=0, page=1,
                movieid=item.get('pk', '0'), url=item['url'])
        } for item in movies]

        return items

    else:
        msg = ['No search terms provided']
        plugin.log.error(msg[0])
        dialog = xbmcgui.Dialog()
        dialog.ok(api.LONG_NAME, *msg)


@plugin.cached_route('/<menuid>/page/<page>')
def browse_category(menuid, page='1'):
    '''
    Get list of movies from category
    '''
    plugin.log.debug('Get movies menu')

    url = plugin.request.args['url'][0]
    movies = api.get_menu_movies(url)

    items = [{
        'label': item['label'],
        'thumbnail': item['thumb'],
        'icon': item['thumb'],
        'info': {
            'plot': item['info']
        },
        'path': plugin.url_for(
            'browse_movie', menuid=menuid, page=page,
            movieid=item.get('pk', '0'), url=item['url'])
    } for item in movies]

    if len(items) > 1:
        # build next link
        next_link = api.get_next_link(url)
        if next_link:
            items.append({
                'label': next_link['label'],
                'path': plugin.url_for(
                    'browse_category', menuid=item.get('pk', '0'),
                    page=next_link['pk'], url=next_link['url'])
            })

    return items


@plugin.route('/<menuid>/page/<page>/movie/<movieid>/')
def browse_movie(menuid, page, movieid):
    '''
    Get links for movie
    '''
    plugin.log.debug('Get movie links')

    page_url = plugin.request.args['url'][0]
    links = api.get_movie_links(page_url)

    items = [{
        'label': item['label'],
        'is_playable': item['is_playable'],
        'path': plugin.url_for(
            'resolve_movie', menuid=menuid, page=page,
            movieid=movieid, linkid=item.get('pk', '0'),
            url=item['url'])
    } for item in links]

    return items


@plugin.route('/<menuid>/page/<page>/movie/<movieid>/<linkid>')
def resolve_movie(menuid, page, movieid, linkid):
    '''
    Play movie
    '''
    page_url = plugin.request.args['url'][0]
    url = api.resolve_redirect(page_url)

    print 'resolve video: {url}'.format(url=url)
    plugin.log.debug('resolve video: {url}'.format(url=url))

    if url:
        media = __resolve_item(url, movieid)
        print 'resolved to: {url}'.format(url=media)

        if __is_resolved(media):
            plugin.set_resolved_url(media)
        else:
            if media is False:
                msg = 'Unresolvable link'
            else:
                msg = str(media.msg)
            raise Exception(msg)

    else:
        msg = 'video url not found'
        raise Exception(msg)


def __is_resolved(url):
    return (url and isinstance(url, basestring))


def __resolve_item(url, title):
    import urlresolver

    media = urlresolver.HostedMediaFile(
        url=url, title=title)
    return media.resolve()


###############################################


def get_args(arg_name, default=None):
    return plugin.request.args.get(arg_name, [default])[0]


if __name__ == '__main__':
    try:
        plugin.run()
    except Exception, e:
        print e
        plugin.log.error(e)
        plugin.notify(msg=e, delay=8000)
