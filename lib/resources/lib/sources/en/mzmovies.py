# -*- coding: utf-8 -*-

'''
    Covenant Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib, urlparse, re

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser
from resources.lib.modules import directstream
from resources.lib.modules import debrid



class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['mehlizmovies.com']
        self.base_link = 'http://mehlizmovies.com/'
        self.search_link = '?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(
                aliases),year)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search(
                [tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = urlparse.urljoin(self.base_link, url)
            query = client.request(url)
            data = client.parseDOM(query, 'ul', attrs={'class': 'episodios'})
            links  = client.parseDOM(data, 'div', attrs={'class': 'episodiotitle'})
            sp = zip(client.parseDOM(data, 'div', attrs={'class': 'numerando'}), client.parseDOM(links, 'a', ret='href'))

            Sea_Epi = '%d-%d'% (int(season), int(episode))
            for i in sp:
                sep = i[0].replace(' ','')
                if sep == Sea_Epi:
                    url = source_utils.strip_domain(i[1])

            return url
        except:
            return

    def __search(self, titles, year):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.getsearch(titles[0])))

            query = urlparse.urljoin(self.base_link, query)

            t = cleantitle.get(titles[0])

            data = client.request(query)
            data = client.parseDOM(data, 'div', attrs={'class': 'result-item'})
            r = dom_parser.parse_dom(data, 'div', attrs={'class': 'title'})
            r = zip(dom_parser.parse_dom(r, 'a'), dom_parser.parse_dom(data, 'span', attrs={'class': 'year'}))
            url = []
            for i in range(len(r)):

                title = cleantitle.get(r[i][0][1])
                title = re.sub('(\d+p|4k|3d|hd)','',title)
                y = r[i][1][1]
                link = r[i][0][0]['href']
                if 'season' in title: continue
                if t == title and y == year:
                    if 'tvshow' in link:
                        url.append(source_utils.strip_domain(link))
                        return url[0]
                    else: url.append(source_utils.strip_domain(link))

            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources
            if debrid.status() == False: raise Exception()
            links = self.links_found(url)

            hostdict = hostDict + hostprDict
            for url in links:
                try:
                    valid, host = source_utils.is_host_valid(url, hostdict)
                    if 'mehliz' in url:
                        host = 'MZ'; direct = True; urls = (self.mz_server(url))

                    elif 'ok.ru' in url:
                        host = 'vk'; direct = True; urls = (directstream.odnoklassniki(url))

                    else:
                        direct = False; urls = [{'quality': 'SD', 'url': url}]

                    for x in urls:
                        sources.append({'source': host, 'quality': x['quality'], 'language': 'en',
                                        'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def links_found(self,urls):
        try:
            links = []
            if type(urls) is list:
                for item in urls:
                    query = urlparse.urljoin(self.base_link, item)
                    r = client.request(query)
                    data = client.parseDOM(r, 'div', attrs={'id': 'playex'})
                    data = client.parseDOM(data, 'div', attrs={'id': 'option-\d+'})
                    links += client.parseDOM(data, 'iframe', ret='src')


            else:
                query = urlparse.urljoin(self.base_link, urls)
                r = client.request(query)
                data = client.parseDOM(r, 'div', attrs={'id': 'playex'})
                data = client.parseDOM(data, 'div', attrs={'id': 'option-\d+'})
                links += client.parseDOM(data, 'iframe', ret='src')

            return links
        except:
            return urls

    def mz_server(self,url):
        try:
            urls = []
            url = url.replace('https', 'http')
            data = client.request(url)
            data = re.findall('''file:\s*["']([^"']+)",label:\s*"(\d{3,}p)"''', data, re.DOTALL)
            for url, label in data:
                label = source_utils.label_to_quality(label)
                if label == 'SD': continue
                urls.append({'url': url, 'quality': label})
            return urls
        except:
            return url

    def resolve(self, url):
        return url
