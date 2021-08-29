#!/usr/bin/env python3

"""scrapes posts metadata from hans bacher’s wordpress blog and saves it to
../data/posts.json

wordpress post data is incredibly verbose.
therefore i am cutting each post down to:
* its url
* its date
* its title
* its title slug
* its tag list
hans doesn’t use categories, so they don’t need to get saved
"""

import json
import logging
import os
import requests


def is_content(response):
    """determine whether a JSON response has content.

    for posts: a page with no more posts has data/status with code 400."""
    try:
        assert response['data']['status'] == 400
        return False
    except (TypeError, AssertionError):
        return True


def parse_post(post):
    return {
        'url': post['link'],
        'date': post['date'],
        'title': post['title']['rendered'],
        'slug': post['slug'],
        'tags': post['tags']
    }


url = 'https://public-api.wordpress.com/wp/v2/sites/4826996/posts?page={page}'
out_fpath = '../data/posts.json'


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('starting')
    page = 1
    data = []

    while True:
        logging.info('requesting page %s', page)
        req = requests.get(url.format(page=page))
        response = json.loads(req.content.decode())
        if is_content(response):
            for post in response:
                data.append(parse_post(post))
        else:
            logging.info('page %s did not contain more posts', page)
            break
        page += 1
    logging.info('writing to posts.json')
    with open(os.path.join(os.path.dirname(__file__), out_fpath), 'w') as f:
        json.dump(data, f, indent=1)
    logging.info('done')
