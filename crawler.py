import requests
from bs4 import BeautifulSoup
from time import sleep
import json
from reppy.robots import Robots


def crawler(seed):
    frontier = set()
    frontier.add(seed)
    crawled = []
    articles = []
    robots = Robots.fetch(seed + '/robots.txt')
    agent = robots.agent('CVUT-FIT CRAWLER')
    print('sitemaps: ', list(robots.sitemaps))
    while frontier:
        sleep(agent.delay)
        page = frontier.pop()
        try:
            print('Crawled:' + page)
            source = requests.get(page, headers={'user-agent': 'CVUT-FIT CRAWLER'}).text
            soup = BeautifulSoup(source, "html5lib")
            if len(soup.select('.node-type-article')) > 0:
                #print('Found article')
                #print(soup.select('h1'))
                #print(soup.select('.field--name-perex .even'))
                #print(soup.select('.field--name-post-date'))
                #print(soup.select('.field--name-body-paged  p,.field--name-body-paged h2'))
                #print(soup.select('.authors .field--name-user-display-name-linked-to-profile a'))
                if len(soup.select('.field--name-perex .even')) == 0:
                    abstract = ''
                else:
                    abstract = soup.select('.field--name-perex .even')[0].text
                articles.append({'title': soup.select('h1')[0].text,
                                 'abstract': abstract,
                                 'published': soup.select('.field--name-post-date')[0].text,
                                 'article': '\n'.join([a.text for a in soup.select('.field--name-body-paged  p,.field--name-body-paged h2')]),
                                 'author': soup.select('.authors .field--name-user-display-name-linked-to-profile a')[0].text,
                                 })

            links = soup.findAll('a', href=True)
            for link in links:
                clean_link = link['href'].split('?')[0]
                if 'http' in clean_link or 'javascript:void' in clean_link or 'files' in clean_link:
                    continue
                if seed + clean_link not in crawled and \
                        agent.allowed(clean_link):
                    frontier.add(seed + clean_link)
            print('todo', len(frontier))
            print('articles', len(articles))
            if len(articles) > 1000:
                break
            crawled.append(seed + page)

        except Exception as e:
            print(e)
        finally:
            json.dump(articles, open('file.json', 'w+'), indent=2)
    return crawled

crawler('http://g.cz')
