import sys, re, argparse
from pub_data import pubs
from people import *
from venue import *

fout = sys.stdout

title_format = '<a href="{link}">{name}</a>'
author_format = '<a href="{link}" class="author">{name}</a>{symbol}'
author_no_link_format = '{name}{symbol}'
venue_format = '<i>{name} ({abr})</i>, {year}.'

def gen_title(pub):
    if 'pdf' in pub:
        title = title_format.format(link=pub['pdf'], name=pub['title'])
    else:
        title = '%s' % pub['title']
    return '%s.' % (title,)

def gen_author(pub):
    s = []
    for author in pub['author']:
        symbol = ''
        if author in pub.get('equal', []):
            symbol = '*'
        name, link = people.get(author, (author, None))
        #if not link:
        s.append(author_no_link_format.format(name=name, symbol=symbol))
        #else:
        #    s.append(author_format.format(link=link, name=name, symbol=symbol))
    return r'%s and %s.' % (', '.join(s[:-1]), s[-1])

def gen_venue(pub):
    name, abr = venue[pub['venue']]
    if pub['type'] == 'arxiv':
        return '<i>{name}:{index} preprint</i>, {year}.'.format(name=name, index=pub['index'], year=pub['year'])
    elif pub['type'] == 'workshop':
        name, link = venue.get(pub['ws'], (pub['ws'], None))
        return '<i>{venue} Workshop on {name}</i>, {year}.'.format(venue=abr, link=link, name=name, year=pub['year'])
    elif pub['type'] == 'demo':
        return '<i>{name} ({abr}) demo</i>, {year}.'.format(name=name, abr=abr, year=pub['year'])
    elif abr:
        return venue_format.format(name=name, abr=abr, year=pub['year'])
    else:
        return '<i>{name}</i>, {year}.'.format(name=name, year=pub['year'])

def gen_award(pub):
    if 'award' in pub:
        name, link = pub['award']
        award = ' <font color="red">{name}</font>'.format(name=name, link=link)
    else:
        award = ''
    return award

def gen_bib(pub):
    s = []
    for author in pub['author']:
        if author == 'hal':
            s.append("Hal {Daum\\'{e} III}")
        elif author == 'alvin':
            s.append('Alvin {Grissom II}')
        else:
            s.append(people.get(author, (author, None))[0])
    author = ' and '.join(s)

    type_ = pub['type']
    conf, abr = venue[pub['venue']]

    title = pub['title'].replace('{', '\{')
    title = title.replace('}', '\}')
    if type_ == 'conference':
        bib = """@inproceedings{{{name},
        author={{{author}}},
        title={{{title}}},
        booktitle={{{conference} ({abr})}},
        year={{{year}}}\n}}""".\
                    format(name=pub['bib'], \
                    author=author, \
                    title=title, \
                    conference=conf, abr=abr, year=pub['year'])
    elif type_ == 'arxiv':
        bib = """@article{{{name},
        author={{{author}}},
        title={{{title}}},
        journal={{arXiv:{index}}},
        year={{{year}}}\n}}""".\
                    format(name=pub['bib'], \
                    author=author, \
                    title=pub['title'], \
                    index=pub['index'], year=pub['year'])
    elif type_ == 'workshop':
        ws, link = venue.get(pub['ws'], (pub['ws'], None))
        bib = """@inproceedings{{{name},
        author={{{author}}},
        title={{{title}}},
        booktitle={{{venue} Workshop on {ws}}},
        year={{{year}}}\n}}""".\
                    format(name=pub['bib'], \
                    author=author, \
                    title=pub['title'], \
                    venue=abr, \
                    ws=ws, year=pub['year'])
    elif type_ == 'journal':
        bib = """@article{{{name},
        author={{{author}}},
        title={{{title}}},
        journal={{{venue}}},
        volume={{{volume}}},
        pages={{{page}}},
        year={{{year}}}\n}}""".\
                    format(name=pub['bib'], \
                    author=author, \
                    title=pub['title'], \
                    venue=abr, \
                    volume=pub['vol'],
                    page=pub['page'],
                    year=pub['year'])

    return bib

def gen_resource(i, pub):
    s = []
    bib_div = None
    if 'bib' in pub:
        s.append('[<a href="javascript:copy(div{idx}, bib{idx})">bib</a>]'.format(idx=i))
        bib_div = '<div id="div{idx}"></div><div id="bib{idx}" style="display:none">\n<div class="bib">\n<pre>\n{bibtex}\n</pre>\n</div>\n</div>'.format(idx=i, bibtex=gen_bib(pub))

    for key in ['code', 'data', 'slides', 'poster', 'screencast', 'talk', 'project', 'codalab']:
        if key in pub:
            if not pub[key].startswith('http'):
                s.append('[<a href="{{% link /{link} %}}">{name}</a>]'.format(link=pub[key], name=key))
            else:
                s.append('[<a href="{link}">{name}</a>]'.format(link=pub[key], name=key))

    return '%s<br>\n%s' % ('\n'.join(s), bib_div if bib_div else '')

def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(description='Generate HTML files for publications.')
    parser.add_argument('--selected', type=int, help='Only process selected publications and output to -selected files')
    parser.add_argument('--no-year', action='store_true', help='Do not print year')
    args = parser.parse_args()

    curr_year = None
    sorted_pubs = sorted(pubs, key=lambda x: x['year'], reverse=True)
    for i, pub in enumerate(sorted_pubs):
        if args.selected is not None and (pub.get('selected') is None or int(pub.get('selected')) > args.selected):
            continue

        if pub['type'] == 'arxiv':
            pub['index'] = re.search(r'(\d+\.\d+)', pub['pdf']).group(1)

        if args.no_year:
            if curr_year is None:
                fout.write('<ul>\n')
                curr_year = 1
            fout.write('<li>{title}<br>{author} {venue} {award} {resource} </li>\n'.format(title=gen_title(pub), author=gen_author(pub), venue=gen_venue(pub), award=gen_award(pub), resource=gen_resource(i, pub)))
        else:
            if pub['year'] != curr_year:
                if curr_year != None:
                    fout.write('</ul>\n')
                fout.write('<h2>%s</h2>\n' % pub['year'])
                fout.write('<ul>\n')
                curr_year = pub['year']
            fout.write('<li>{title}<br>{author} {venue} {award} {resource} </li>\n'.format(title=gen_title(pub), author=gen_author(pub), venue=gen_venue(pub), award=gen_award(pub), resource=gen_resource(i, pub)))

    # end
    fout.write('</ul>\n')

if __name__ == '__main__':
    main()

