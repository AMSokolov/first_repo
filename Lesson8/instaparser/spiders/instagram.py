import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']

    insta_login = 'vinatoly'
    insta_pwd = ''
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    parse_users = ['mdergachev', 'kuznetsovvictor']

    api_url = 'https://i.instagram.com/api/v1/friendships/'


    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        print('csrf=', csrf)
        yield scrapy.FormRequest(self.insta_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.insta_login,
                                           'enc_password': self.insta_pwd},
                                 headers={'X-CSRFToken': csrf})
    def login(self, response: HtmlResponse):
        j_data = response.json()
        print('j_data=', j_data)
        print()
        if j_data['authenticated']:
            for user in self.parse_users:
                print('user=', user)
                yield response.follow(
                    f'/{user}/',
                    callback=self.follow_parse,
                    cb_kwargs={'username': user})

    def follow_parse(self, response: HtmlResponse, username):
        print()
        user_id = self.fetch_user_id(response.text, username)
        variables = {'max_id': 12}
        api_followers = f'{self.api_url}{user_id}/followers/?count=12&{urlencode(variables)}&search_surface=follow_list_page'
        yield response.follow(
            api_followers,
            callback=self.user_follow_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'source': 'followers',
                       'variables': deepcopy(variables)},
                       headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        api_following = f'{self.api_url}{user_id}/following/?count=12&{urlencode(variables)}&search_surface=follow_list_page'
        yield response.follow(
            api_following,
            callback=self.user_follow_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'source': 'following',
                       'variables': deepcopy(variables)},
                       headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    def user_follow_parse(self, response: HtmlResponse, username, user_id, source, variables):
        j_data = response.json()
        if j_data.get('next_max_id'):
            variables['max_id'] += 12

            api_follow = f'{self.api_url}{user_id}/{source}/?count=12&{urlencode(variables)}&search_surface=follow_list_page'
            print()
            yield response.follow(
                api_follow,
                callback=self.user_follow_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'source': source,
                           'variables': deepcopy(variables)},
                           headers={'User-Agent': 'Instagram 155.0.0.37.107'})


        for follow in j_data['users']:
            item = InstaparserItem(
                username=username,
                source=source,
                user_id=follow.get('pk'),
                follow_name=follow.get('username'),
                follow_photo=follow.get('profile_pic_url'))
            yield item

    def fetch_csrf_token(self, text):
        # Получаем токен для авторизации
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
