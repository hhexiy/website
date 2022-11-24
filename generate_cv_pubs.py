import sys
from pub_data import *
from people import *
from venue import *

venue_format = '\\textit{{{name} ({abr})}}, {year}'

def gen_title(pub):
    return '{}'.format(pub['title'])

def gen_author(pub):
    s = []
    for author in pub['author']:
        symbol = ''
        if author in pub.get('equal', []):
            symbol = '*'
        name, _ = people.get(author, (author, None))
        if author == 'me':
            name = '\\textbf{{{name}}}'.format(name=name)
        name = name.replace('&eacute', "\\'e")
        if symbol:
            name = '{}$^{}$'.format(name, symbol)
        s.append(name)
    return '{} and {}'.format(', '.join(s[:-1]), s[-1])

def gen_venue(pub):
    name, abr = venue.get(pub['venue'], (pub['venue'], pub['venue']))
    if pub['type'] == 'arxiv':
        return '\\textit{{{name}:{index} preprint}}, {year}'.format(name=name, index=pub['index'], year=pub['year'])
    elif pub['type'] == 'workshop':
        name, link = venue.get(pub['ws'], (pub['ws'], ''))
        return '\\textit{{{venue} Workshop on {name}}}, {year}'.format(venue=abr, name=name, year=pub['year'])
    elif pub['type'] == 'demo':
        return '\\textit{{{name} ({abr}) demo, {year}}}'.format(name=name, abr=abr, year=pub['year'])
    elif pub['type'] == 'journal':
        return '\\textit{{{name} ({abr}) {vol}:{page}, {year}}}'.format(name=name, abr=abr, year=pub['year'], vol=pub['vol'], page=pub['page'])
    elif abr:
        return venue_format.format(name=name, abr=abr, year=pub['year'])
    else:
        return '\\textit{{{name}}}, {year}'.format(name=name, year=pub['year'])

pubs = sorted(pubs, key=lambda p: p['year'], reverse=True)
with open('conference.tex', 'w') as fconf, open('workshop.tex', 'w') as fwork, open('arxiv.tex', 'w') as farxiv, open('journal.tex', 'w') as fjournal:
    fouts = {
            'conference': fconf,
            'workshop': fwork,
            'arxiv': farxiv,
            'journal': fjournal,
            }
    for i, pub in enumerate(pubs):
        if pub['type'] in fouts:
            if 'notes' in pub:
                format_str = '{author}. {title}. {venue}. ({notes})\n\n'
            else:
                format_str = '{author}. {title}. {venue}.\n\n'
            pub_str = format_str.format(
                            title=gen_title(pub),
                            author=gen_author(pub),
                            venue=gen_venue(pub),
                            notes=pub.get('notes'))
            pub_str = pub_str.replace('&', '\\&')
            fouts[pub['type']].write(pub_str)
