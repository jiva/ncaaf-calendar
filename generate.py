#!/usr/bin/env python

import requests
import bs4

def get_soup(html):
    return bs4.BeautifulSoup(html, 'html.parser')

def get_networks(network_tags):
    networks = []
    for network_tag in network_tags:
        if isinstance(network_tag, bs4.element.NavigableString):
            networks.append(network_tag)
        else:
            imgs = network_tag.find_all('img')
            if imgs:
                assert(len(imgs) == 1)
                networks.append(imgs[0].get('class')[0])
    return networks

def parse_location(location_tag):
    if isinstance(location_tag, bs4.element.NavigableString):
        return location_tag
    else:
        return list(location.children)[0]

#ESPN_URL = 'http://www.espn.com/college-football/schedule/_/week/%d' # Current year assumed
#ESPN_URL = 'http://www.espn.com/college-football/schedule/_/year/%d/week/%d'
ESPN_URL = 'http://www.espn.com/college-football/schedule/_/year/%d/week/%d/group/%d'

year = 2016

weeks = xrange(1,16)
weeks = xrange(1,2)

conferences = dict()
conferences['fbs_i-a'] = 80
conferences['acc'] = 1
conferences['american'] = 151
conferences['big_12'] = 4
conferences['big_ten'] = 5
conferences['c-usa'] = 12
conferences['fbs_indep'] = 18
conferences['mac'] = 15
conferences['mw'] = 17
conferences['pac-12'] = 9
conferences['sec'] = 8
conferences['sun_belt'] = 37
conferences['fcs_i-aa'] = 81
conferences['big_sky'] = 20
conferences['big_south'] = 40
conferences['caa'] = 48
conferences['fcs_indep'] = 32
conferences['ivy'] = 22
conferences['meac'] = 24
conferences['mvfc'] = 21
conferences['nec'] = 25
conferences['ovc'] = 26
conferences['patriot'] = 27
conferences['pioneer'] = 28
conferences['swac'] = 31
conferences['southern'] = 29
conferences['southland'] = 30
conferences['div_ii-iii'] = 35


for week in weeks:
    req = requests.get(ESPN_URL % (year,week,conferences['fbs_i-a']))
    
    soup = get_soup(req.text)

    days = soup.find_all('h2', class_='table-caption')
    schedules = soup.find_all('div', class_='responsive-table-wrap')
    assert(len(days) == len(schedules))

    for day,schedule in zip(days,schedules):
        print 'DAY:', day.contents[0]
        tbody = schedule.find_all('tbody')
        for tr in tbody[0].find_all('tr'):
            tds = tr.find_all('td')
            away_team = tds[0].find_all('abbr')
            at_or_vs = tds[1].get('data-home-text')
            home_team = tds[1].find_all('abbr')
            espn_game_id = tds[2].find_all('a')[0].get('href').replace('/college-football/game?gameId=','')
            iso8601_time = tds[2].get('data-date')
            networks = get_networks(tds[3])
            location = tds[4].contents[0]
            print away_team[0].get('title'), at_or_vs, home_team[0].get('title'), 'PLAYING AT', parse_location(location)
        print


















