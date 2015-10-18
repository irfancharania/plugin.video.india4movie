from xbmcswift2 import Plugin, xbmcgui
import resources.lib.util as util
from resources.lib.abc_base import BaseI4M
from resources.lib.sites import *
import urllib


plugin = Plugin()


STRINGS = {
    'url_resolver_settings': 30100,
    'try_again': 30050,
    'site_unavailable': 30051,
    'is_unavailable': 30052,
    'try_again_later': 30053,
    'no_valid_links': 30057,
    'cannot_play': 30058,
    'no_search_terms': 30060,
    'video_url_not_found': 30061,
    'unresolvable_link': 30062
}


def _(string_id):
    if string_id in STRINGS:
        return plugin.get_string(STRINGS[string_id])
    else:
        plugin.log.warning('String is missing: %s' % string_id)
        return string_id


def get_cached(func, *args, **kwargs):
    '''Return the result of func with the given args and kwargs
    from cache or execute it if needed'''
    @plugin.cached(kwargs.pop('TTL', 1440))
    def wrap(func_name, *args, **kwargs):
        return func(*args, **kwargs)
    return wrap(func.__name__, *args, **kwargs)


###############################################


@plugin.route('/')
def index():
    '''
    Display sites
    '''
    plugin.log.debug('Get sites')

    items = [{
        'label': sc.LONG_NAME,
        'path': plugin.url_for(
            'get_category_menu', siteid=index,
            cls=sc.__name__),
        'thumbnail': util.get_image_path(sc.LOCAL_THUMB),
        'icon': util.get_image_path(sc.LOCAL_THUMB),
        } for index, sc in enumerate(BaseI4M.__subclasses__())]

    thumb = util.get_image_path('settings.png')
    items.append({
        'label': '[COLOR white]{txt}[/COLOR]'.format(
            txt=_('url_resolver_settings')),
        'path': plugin.url_for('get_urlresolver_settings'),
        'thumbnail': thumb,
        'icon': thumb
        })

    return items


@plugin.route('/urlresolver/')
def get_urlresolver_settings():
    import urlresolver
    urlresolver.display_settings()
    return


@plugin.route('/sites/<siteid>-<cls>/')
def get_category_menu(siteid, cls):
    '''
    Get movie categories
    '''
    siteid = int(siteid)
    api = BaseI4M.__subclasses__()[siteid]()

    plugin.log.debug('browse site: {site}'.format(site=cls))

    # check if site is available
    if api.BASE_URL:
        available = util.is_site_available(api.BASE_URL)

        if available:

            # search
            items = [{
                'label': "[B]** Search **[/B]",
                'path': plugin.url_for('search', siteid=siteid, cls=cls)
            }]

            # get categories
            plugin.log.debug('Get category menu')
            c = get_cached(api.get_menu_category, cls)
            if c:
                items.extend([{
                    'label': item['label'],
                    'path': plugin.url_for(
                        'browse_category', siteid=siteid, cls=cls,
                        menuid=item.get('pk', '0'), page=1, url=item['url'])
                } for item in c])

            return items

        else:
            msg = [
                '[B][COLOR red]{txt}[/COLOR][/B]'.format(
                    txt=_('site_unavailable')),
                '{site} {txt}'.format(
                    site=api.long_name, txt=_('is_unavailable')),
                _('try_again_later')]
            plugin.log.error(msg[1])

            dialog = xbmcgui.Dialog()
            dialog.ok(api.long_name, *msg)
    else:
        msg = 'Base url not implemented'
        plugin.log.error(msg)
        raise Exception(msg)


@plugin.route('/sites/<siteid>-<cls>/search/')
def search(siteid, cls):
    '''
    Search movies
    '''
    siteid = int(siteid)
    api = BaseI4M.__subclasses__()[siteid]()
    plugin.log.debug('Search')

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
                'browse_movie', siteid=siteid, cls=cls,
                menuid=0, page=1,
                movieid=item.get('pk', '0'), url=item['url'])
        } for item in movies]

        return items

    else:
        msg = [_('no_search_terms')]
        plugin.log.error(msg[0])
        dialog = xbmcgui.Dialog()
        dialog.ok(api.LONG_NAME, *msg)


@plugin.route('/sites/<siteid>-<cls>/<menuid>/page/<page>')
def browse_category(siteid, cls, menuid, page='1'):
    '''
    Get list of movies from category
    '''
    siteid = int(siteid)
    api = BaseI4M.__subclasses__()[siteid]()
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
            'browse_movie', siteid=siteid, cls=cls,
            menuid=menuid, page=page,
            movieid=item.get('pk', '0'), url=item['url'])
    } for item in movies]

    if len(items) > 1:
        # build next link
        next_link = api.get_next_link(url)
        if next_link:
            items.append({
                'label': next_link['label'],
                'path': plugin.url_for(
                    'browse_category', siteid=siteid, cls=cls,
                    menuid=item.get('pk', '0'),
                    page=next_link['pk'], url=next_link['url'])
            })

    return items


@plugin.route('/sites/<siteid>-<cls>/<menuid>/page/<page>/movie/<movieid>/')
def browse_movie(siteid, cls, menuid, page, movieid):
    '''
    Get links for movie
    '''
    siteid = int(siteid)
    api = BaseI4M.__subclasses__()[siteid]()
    plugin.log.debug('Get movie links')

    page_url = plugin.request.args['url'][0]
    links = api.get_movie_links(page_url)

    items = [{
        'label': item['label'],
        'is_playable': item['is_playable'],
        'path': plugin.url_for(
            'resolve_movie', siteid=siteid, cls=cls,
            movieid=movieid, linkid=item.get('pk', '0'),
            url=item['url'])
    } for item in links]

    return items


@plugin.route('/sites/<siteid>-<cls>/movie/<movieid>/<linkid>')
def resolve_movie(siteid, cls, movieid, linkid):
    '''
    Play movie
    '''
    siteid = int(siteid)
    api = BaseI4M.__subclasses__()[siteid]()
    plugin.log.debug('Play movie')

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
                msg = _('unresolvable_link')
            else:
                msg = str(media.msg)
            raise Exception(msg)

    else:
        msg = _('video_url_not_found')
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
