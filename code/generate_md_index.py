#!/usr/bin/env python3

"""builds markdown indices to hans bacher blog posts archived on the wayback
machine from blog metadata.

1. index by date
    * one root file with links to single years: index-md/by-date/root.md
    * one file per year: index-md/by-date/year-YYYY.md
    * subheadings per month
    * one link per blog post
2. index by tag
    * one root file with links to single tags: index-md/by-tag/root.md
    * one file per tag: index-md/by-tag/tag-TAGSLUG.md
    * one link per blog post
3. index by title
    * one root file with links to starting character: index-md/by-title/root.md
    * one file per starting character: index_md/letter-CHAR.md
    * one link per blog post
"""

import json
import re
from html import unescape
from itertools import groupby
from pathlib import Path


def postlink(post):
    """write a markdown link to a wayback machine archive of a blog post."""
    return POST_LINK.format(date=post['date'][:10],
                            time=post['date'][11:16],
                            title=unescape(post['title']),
                            url=post['url'],
                            tags=', '.join([TAGS[i] for i in post['tags']]))


def year_page_lines(year, group):
    """build the lines for a given year’s markdown index.

    has the year mentioned in the level 1 heading, builds level 2 headings per
    month, and sets a list of links for individual posts underneath.

    args:
        year (str): the year the index is of.
        group (list(str)): the list of iso-dates for the posts in that year.

    returns:
        list(str): the text lines to be written to file.
    """
    lines = [
        H1.format(index_type=year),
        ''
        ]
    for month, monthgroup in groupby(group, lambda x: x[:7]):
        lines.append(H2.format(text=month))
        lines.append('')
        for date in monthgroup:
            lines.append(postlink(POSTS[date]))
        lines.append('')
    return lines


def tag_page_lines(tag, group):
    """build the lines for a given tag’s markdown index.

    has the tag mentioned in the level 1 heading and sets a list of links for
    individual posts underneath.

    args:
        tag (str): the tag the index is of.
        group (list(str)): the list of iso-dates for the posts in that year.

    returns:
        list(str): the text lines to be written to file.
    """
    lines = [
        H1.format(index_type=tag),
        ''
        ]
    for date in group:
        lines.append(postlink(POSTS[date]))
    return lines


def letter_page_lines(letter, group):
    """build the lines for a given title letter’s markdown index.

    has the letter mentioned in the level 1 heading and sets a list of links
    for individual posts underneath.

    args:
        letter (str): thetitle starting letter the index is of.
        group (list(str)): the list of iso-dates for the posts with titles
            starting with that letter.

    returns:
        list(str): the text lines to be written to file.
    """
    lines = [
        H1.format(index_type=letter.upper()),
        ''
        ]
    for date in group:
        lines.append(postlink(POSTS[date]))
    return lines


if __name__ == '__main__':
    root_path = (Path(__file__).parent / Path('..')).resolve()

    # POSTS: timestamps to their posts
    with (root_path / Path('data', 'posts.json')).open() as f:
        POSTS = json.load(f)
        POSTS = {d['date']: d for d in POSTS}

    # TAG_IDS: tag names to tag ids
    # TAG_SLUGS: tag names to tag slugs
    # TAGS: tag ids to tag names
    with (root_path / Path('data', 'tags.json')).open() as f:
        TAGS = json.load(f)
        TAG_IDS = {d['name']: d['id'] for d in TAGS}
        TAG_SLUGS = {d['name']: d['slug'] for d in TAGS}
        TAGS = {d['id']: d['name'] for d in TAGS}

    H1 = '# Hans Bacher Blog Wayback Index: {index_type}'
    H2 = '## {text}'
    POST_LINK = '* {date} ({time}): ' \
        '[{title}](https://web.archive.org/web/{url}) ' \
        '({tags})'
    YR_LINK = '* [{yr}](year-{yr}.md) ({n} posts)'
    TAG_LINK = '* [{tag}](tag-{slug}.md) ({n} posts)'
    LETTER_LINK = '* [{letter}](letter-{letter}.md) ({n} posts)'

    # =========================================================================
    # build by-date index
    # =========================================================================

    date_path = root_path / Path('index-md', 'by-date')
    date_path.mkdir(parents=True, exist_ok=True)

    # start collecting lines: a heading…
    lines = [
        H1.format(index_type='By Date'),
        ''
        ]

    # …and a list of links per year
    year_grouping = [(year, list(group))
                     for year, group
                     in groupby(sorted(POSTS), lambda x: x[:4])]
    for year, yeargroup in year_grouping:
        lines.append(YR_LINK.format(yr=year, n=len(yeargroup)))

        # also, write a year page per year
        with (date_path / Path('year-{yr}.md'.format(yr=year))).open('w') as f:
            f.write('\n'.join(year_page_lines(year, yeargroup)))

    # finally, write the collected index root lines to file
    with (date_path / Path('root.md')).open('w') as f:
        f.write('\n'.join(lines))

    # =========================================================================
    # build by-tag index
    # =========================================================================

    tag_path = root_path / Path('index-md', 'by-tag')
    tag_path.mkdir(parents=True, exist_ok=True)

    # start collecting lines: a heading…
    lines = [
        H1.format(index_type='By Tag'),
        ''
        ]

    # …a subheading per starting letter…
    letter_grouping = [(letter, list(group))
                       for letter, group
                       in groupby(sorted(TAGS.values(), key=str.casefold),
                                  lambda x: x[:1].upper())]
    for letter, lettergroup in letter_grouping:
        lines.append(H2.format(text=letter))
        lines.append('')

        # …and a link per tag
        for tag in lettergroup:
            slug = TAG_SLUGS[tag]
            tag_id = TAG_IDS[tag]
            tag_posts = [postdate
                         for postdate
                         in sorted(POSTS)
                         if tag_id in POSTS[postdate]['tags']]
            lines.append(TAG_LINK.format(tag=tag, slug=slug, n=len(tag_posts)))

            # also, write a tag page per tag
            with (tag_path / Path('tag-{slug}.md'.format(slug=slug))).open('w') as f:
                f.write('\n'.join(tag_page_lines(tag, tag_posts)))

        lines.append('')

    # finally, write the collected index root lines to file
    with (tag_path / Path('root.md')).open('w') as f:
        f.write('\n'.join(lines))

    # =========================================================================
    # build by-title index
    # =========================================================================

    title_path = root_path / Path('index-md', 'by-title')
    title_path.mkdir(parents=True, exist_ok=True)

    orderable_titles = {re.sub('^[ #…]+', '', unescape(d['title'].upper())): d['date']
                        for d in POSTS.values()}

    # start collecting lines: a heading…
    lines = [
        H1.format(index_type='By Title'),
        ''
        ]

    # …a subheading per starting letter…
    letter_grouping = [(letter, list(group))
                       for letter, group
                       in groupby(sorted(orderable_titles),
                                  lambda x: x[:1].upper())]
    for letter, lettergroup in letter_grouping:
        lines.append(LETTER_LINK.format(letter=letter, n=len(lettergroup)))

        # also, write a letter page per letter
        filtered_post_dates = [orderable_titles[title]
                               for title in lettergroup]
        with (title_path / Path('letter-{letter}.md'.format(letter=letter))).open('w') as f:
            f.write('\n'.join(letter_page_lines(letter, filtered_post_dates)))

    # finally, write the collected index root lines to file
    with (title_path / Path('root.md')).open('w') as f:
        f.write('\n'.join(lines))
