import requests


# allows us to get mobile version
user_agent_mobile = 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25'

user_agent_desktop = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'

addon_id = 'plugin.video.india4movie'


def get_image_path(image):
    ''' get image path '''
    image = 'special://home/addons/{id}/resources/images/{image}'.format(
        id=addon_id, image=image)
    return image


def encode(string):
    ''' encode to utf-8 '''
    return string.encode('utf-8', 'ignore')


def get_remote_data(url, ismobile=True, referer=None):
    ''' fetch website data as mobile or desktop browser'''
    user_agent = user_agent_mobile if ismobile else user_agent_desktop

    headers = {'User-Agent': user_agent}
    if referer:
        headers['Referer'] = referer

    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    return r.content


def is_site_available(url):
    ''' ping site to see if it is up '''
    print 'Checking url: {url}'.format(url=url)

    try:
        r = requests.head(url)
        return r.status_code < 400

    except:
        return False
