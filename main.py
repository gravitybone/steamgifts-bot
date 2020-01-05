import sys
import requests
from bs4 import BeautifulSoup
import json
import threading
from requests import RequestException
from random import randint
from time import sleep

try:
    file = open('cookie.txt', 'r')
    cook = file.readline()
    if len(cook) == 0:
        print('There is no cookie in cookie.txt file')
        sleep(30)
        sys.exit(0)
except FileNotFoundError:
    print('Cant find cookie.txt file')
    sleep(30)
    sys.exit(0)

pages = 1
cookies = {}
xsrf_token = 0
points = 0


def get_soup_from_page(url):
    global cookies

    cookies = {'PHPSESSID': cook}
    r = requests.get(url, cookies=cookies)
    return BeautifulSoup(r.text, 'html.parser')


def get_page():
    global xsrf_token, points

    try:
        soup = get_soup_from_page('https://www.steamgifts.com')

        xsrf_token = soup.find('input', {'name': 'xsrf_token'})['value']
        points = soup.find('span', {'class': 'nav__points'}).text  # storage points
    except RequestException:
        print('Cant connect to the site')
        print('Waiting 2 minutes and reconnect...')
        sleep(120)
        get_page()
    except TypeError:
        print('Cant recognize your cookie value.')
        sleep(30)
        sys.exit(0)


# get codes of the games
def get_games():
    global pages

    n = 1
    while n <= pages:
        print('Proccessing games from %d page.' % n)

        soup = get_soup_from_page('https://www.steamgifts.com/giveaways/search?page=' + str(n) + "&type=wishlist")

        try:
            gifts_list = soup.find_all(
                lambda tag: tag.name == 'div' and tag.get('class') == ['giveaway__row-inner-wrap'])

            for item in gifts_list:
                if int(points) == 0:
                    print('> Sleeping to get 6 points')
                    sleep(900)
                    get_games()
                    break

                game_cost = item.find_all('span', {'class': 'giveaway__heading__thin'})

                last_div = None
                for last_div in game_cost:
                    pass
                if last_div:
                    game_cost = last_div.getText().replace('(', '').replace(')', '').replace('P', '')

                game_name = item.find('a', {'class': 'giveaway__heading__name'}).text.encode('utf-8')

                if int(points) - int(game_cost) < 0:
                    print('Not enough points to enter: ' + game_name.decode("utf-8"))
                    continue
                elif int(points) - int(game_cost) > 0:
                    entry_gift(item.find('a', {'class': 'giveaway__heading__name'})['href'].split('/')[2], game_name)

            n = n + 1
        except AttributeError as e:
            break

    print('List of games ended. Exiting')


def entry_gift(code, game_name):
    payload = {'xsrf_token': xsrf_token, 'do': 'entry_insert', 'code': code}
    entry = requests.post('https://www.steamgifts.com/ajax.php', data=payload, cookies=cookies)
    json_data = json.loads(entry.text)

    get_page()

    # updating points after entered a giveaway
    if json_data['type'] == 'success':
        print('> Bot has entered giveaway: ' + game_name.decode("utf-8"))
        sleep_time = randint(10, 30)
        print("> Sleeping " + str(sleep_time) + " Seconds")
        sleep(sleep_time)


if __name__ == '__main__':
    get_page()
    get_games()
