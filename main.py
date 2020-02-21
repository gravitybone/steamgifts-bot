import sys
import requests
import json
from bs4 import BeautifulSoup
from requests import RequestException
from random import randint
from time import sleep

xsrf_token = 0
points = 0


def get_cookie():
    try:
        file = open('cookie.txt', 'r')
        cook = file.readline()
        if len(cook) == 0:
            print('There is no cookie in cookie.txt file')
            sys.exit(0)
        cookies = {'PHPSESSID': cook}
        return cookies
    except FileNotFoundError:
        print('Cant find cookie.txt file')
        sys.exit(0)


def get_soup_from_page(url, cookie):
    r = requests.get(url, cookies=cookie)
    return BeautifulSoup(r.text, 'html.parser')


# enter all games on one site
def enter_games(page, cookies):
    global points
    soup = get_soup_from_page(page, cookies)

    try:
        gifts_list = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['giveaway__row-inner-wrap'])

        for item in gifts_list:
            game_cost = item.find_all('span', {'class': 'giveaway__heading__thin'})

            last_div = None
            for last_div in game_cost:
                pass
            if last_div:
                game_cost = last_div.getText().replace('(', '').replace(')', '').replace('P', '')

            game_name = item.find('a', {'class': 'giveaway__heading__name'}).text.encode('utf-8')

            if points - int(game_cost) < 0:
                print('Not enough points to enter: ' + game_name.decode("utf-8"))
                continue
            elif points - int(game_cost) > 0:
                enter_giveaway(item.find('a', {'class': 'giveaway__heading__name'})['href'].split('/')[2], game_name,
                               cookies)
                points -= int(game_cost)
    except AttributeError as e:
        return


# get codes of the games
def get_games(cookie):
    print("Proccessing games from wishlist.")
    get_page(cookie)
    enter_games("https://www.steamgifts.com/giveaways/search?type=wishlist", cookie)
    print(points)
    if points > 5:
        print("Proccessing all games.")
        get_page(cookie)
        enter_games("https://www.steamgifts.com", cookie)
        n = 2
        while points > 5 and n < 5:
            get_page(cookie)
            enter_games("https://www.steamgifts.com/giveaways/search?page=" + str(n), cookie)
            print(n)
            print(points)
            sleep_time = randint(10, 30)
            n += 1
    print('Finished')


def get_page(cookie):
    global xsrf_token, points
    try:
        soup = get_soup_from_page('https://www.steamgifts.com', cookie)
        xsrf_token = soup.find('input', {'name': 'xsrf_token'})['value']
        points = int(soup.find('span', {'class': 'nav__points'}).text)  # storage points
    except RequestException:
        print('Cant connect to the site')
        print('Waiting 2 minutes and reconnect...')
        sleep(120)
        get_page()
    except TypeError:
        print('Cant recognize your cookie value.')
        sys.exit(0)


def enter_giveaway(code, game_name, cookies):
    payload = {'xsrf_token': xsrf_token, 'do': 'entry_insert', 'code': code}
    entry = requests.post('https://www.steamgifts.com/ajax.php', data=payload, cookies=cookies)
    json_data = json.loads(entry.text)

    # updating points after entered a giveaway
    if json_data['type'] == 'success':
        print('> Bot has entered giveaway: ' + game_name.decode("utf-8"))
        sleep_time = randint(10, 30)
        print("> Sleeping " + str(sleep_time) + " Seconds")
        sleep(sleep_time)


def main():
    cookie = get_cookie()
    get_games(cookie)


if __name__ == '__main__':
    main()
