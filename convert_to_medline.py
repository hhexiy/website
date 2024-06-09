import sys
from pub_data import *
from people import *
from venue import *

def convert_to_medline(pub):
    """
    Converts a publication dictionary to a MEDLINE format string.

    Args:
    pub (dict): A dictionary containing publication information.

    Returns:
    str: A string formatted in the MEDLINE style.
    """
    # Format author names
    authors = []
    for author in pub['author']:
        first, last = people.get(author, (author, None))[0].rsplit(' ', 1)
        authors.append(last + ',' + ''.join([f[0].upper() for f in first.split(' ')]))
    authors = '\n'.join(f'AU - {author}' for author in authors)

    # Format title
    title = pub['title']
    journal = venue[pub["venue"]][1]
    year = pub['year']

    # Combine all parts
    medline_format = f'{authors}\nTI - {title}\nJT - {journal}\nDP - {year}'
    return medline_format

# Convert to MEDLINE format
medline_formatted_publications = [convert_to_medline(pub) for pub in pubs]
with open('pubs_medline.txt', 'w') as fout:
    for pub in medline_formatted_publications:
        fout.write(pub + '\n\n')

