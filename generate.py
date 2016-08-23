#!/usr/bin/env python

import requests
import bs4
from icalendar import Calendar, Event
import datetime
from dateutil import parser
import pytz

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
        return str(location_tag)
    else:
        return str(list(location.children)[0])

def format_day(raw_day, year):
    '''Returns a datetime object from a day string, kinda ghetto.
       Need this for to handle TBD events'''

    days = ['Monday, ','Tuesday, ','Wednesday, ','Thursday, ','Friday, ','Saturday, ','Sunday, ']
    months = {'August ':8, 'September ':9, 'October ':10, 'November ':11, 'December ':12, 'January ':1}
    
    for day in days:
        if day in raw_day:
            raw_day = raw_day.replace(day,'')

    month = None
    for month_name in months:
        if month_name in raw_day:
            raw_day = raw_day.replace(month_name, '')
            month = months[month_name]

    return datetime.datetime(year, month, int(raw_day), 16, 0)

#ESPN_URL = 'http://www.espn.com/college-football/schedule/_/week/%d' # Current year assumed
#ESPN_URL = 'http://www.espn.com/college-football/schedule/_/year/%d/week/%d'
ESPN_URL = 'http://www.espn.com/college-football/schedule/_/year/%d/week/%d/group/%d'

year = 2016

weeks = xrange(1,16)

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

cal = Calendar()
cal.add('dtstart', datetime.datetime.now())
cal.add('summary', '%d NCAAF Schedule' % year)
cal.add('prodid', '-//ncaaf-calendar//jiva//')
cal.add('version', '2.0')

for week in weeks:
    req = requests.get(ESPN_URL % (year,week,conferences['fbs_i-a']))
    #req = requests.get(ESPN_URL % (year,week,conferences['sec']))

    soup = get_soup(req.text)

    days = soup.find_all('h2', class_='table-caption')
    schedules = soup.find_all('div', class_='responsive-table-wrap')
    assert(len(days) == len(schedules))

    for day,schedule in zip(days,schedules):
        tbody = schedule.find_all('tbody')
        for tr in tbody[0].find_all('tr'):
            tds = tr.find_all('td')
            
            # team info
            away_team = tds[0].find_all('abbr')[0].get('title')
            at_or_vs = tds[1].get('data-home-text')
            home_team = tds[1].find_all('abbr')[0].get('title')
            
            # espn game id
            espn_game_id = tds[2].find_all('a')[0].get('href').replace('/college-football/game?gameId=','')
            
            # start time in iso8601 format
            timetbd = ''
            iso8601_time = tds[2].get('data-date')
            if not iso8601_time: # time is TBD, but dtstart is required. Setting time to 12:00pm.
                 timetbd = ' (TIME TBD)'
                 dtstart = format_day(day.contents[0], year)
            else:
                dtstart = parser.parse(iso8601_time)

            # tv networks broadcasting came, this field will likely change often depending on week
            networks = get_networks(tds[3])
            
            # location of game
            location = tds[4].contents[0]
            location = parse_location(location)
            
            # create event 
            event = Event()
            event.add('uid', espn_game_id)
            event.add('dtstart', dtstart)
            event.add('dtend', dtstart + datetime.timedelta(hours=3, minutes=30))
            event.add('dtstamp', datetime.datetime.now())
            event.add('summary', '%s %s %s%s' % (away_team, at_or_vs, home_team, timetbd))
            event.add('url', 'http://www.espn.com/college-football/game?gameId=%s' % espn_game_id)
            event.add('description', 'URL: http://www.espn.com/college-football/game?gameId=%s\nNetworks: %s' % (espn_game_id, ','.join(networks)))
            event.add('location', location)
            cal.add_component(event)

print cal.to_ical()
