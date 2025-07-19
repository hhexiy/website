import sys
import re
import argparse
import arxiv
from scholarly import scholarly
from pub_data import pubs

def normalize_title(title):
    # Remove curly braces and non-alphanumeric characters
    title = re.sub(r'[{}]', '', title)
    return re.sub(r'[^a-z0-9]', '', title.lower())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, default=2023, help='Start year for publications to check')
    args = parser.parse_args()

    author_id = 'K-isjagAAAAJ'
    start_year = args.year

    # Fetch author details
    author = scholarly.search_author_id(author_id)
    author = scholarly.fill(author, sections=['publications'])

    # Get existing titles
    existing_titles = {normalize_title(pub['title']) for pub in pubs}

    new_pubs = []
    for pub in author['publications']:
        if 'pub_year' not in pub['bib'] or int(pub['bib']['pub_year']) < start_year:
            continue

        normalized_title = normalize_title(pub['bib']['title'])
        if normalized_title not in existing_titles:
            print(f"New publication found: {pub['bib']['title']}")
            confirm = input("Add this publication? (y/n): ")
            if confirm.lower() == 'y':
                authors = None
                bib_key = None
                pdf_link = pub.get('eprint_url')
                if not (pdf_link and 'arxiv' in pdf_link):
                    pdf_link = input("No arXiv link found. Please enter one, or press Enter to skip: ")

                if pdf_link and 'arxiv' in pdf_link:
                    try:
                        arxiv_id = re.search(r'/abs/(\d+\.\d+)', pdf_link).group(1)
                        search = arxiv.Search(id_list=[arxiv_id])
                        client = arxiv.Client()
                        paper = next(client.results(search))
                        authors = tuple([author.name for author in paper.authors])

                        first_author_last_name = authors[0].split()[-1].lower()
                        pub_year = pub['bib']['pub_year']
                        first_word_of_title = re.sub(r'[^a-z0-9]', '', pub['bib']['title'].split()[0].lower())
                        bib_key = f"{first_author_last_name}{pub_year}{first_word_of_title}"
                        print(f"Generated bib key: {bib_key}")

                    except Exception as e:
                        print(f"Could not fetch from arXiv: {e}")

                if not bib_key:
                    bib_key = input("Could not generate bib key. Please enter one manually: ")

                venue = input("Enter venue: ")
                pub_type = input("Enter publication type (e.g., conference, journal, arxiv): ")

                new_pubs.append({
                    'bib': bib_key,
                    'title': pub['bib']['title'],
                    'author': authors if authors else tuple(pub['bib'].get('author', '').split(' and ')),
                    'year': pub['bib']['pub_year'],
                    'venue': venue,
                    'type': pub_type,
                    'pdf': pdf_link if pdf_link else pub.get('pub_url', '')
                })
                print(new_pubs[-1])

    if new_pubs:
        with open('pub_data.py', 'a') as f:
            f.write('\n')
            for pub in new_pubs:
                f.write('pubs.append({\n')
                for key, value in pub.items():
                    if isinstance(value, str):
                        f.write(f"    '{key}': '{value}',\n")
                    else:
                        f.write(f"    '{key}': {value},\n")
                f.write('})\n\n')
        print(f"Added {len(new_pubs)} new publications to pub_data.py")
    else:
        print("No new publications found.")

if __name__ == '__main__':
    main()
