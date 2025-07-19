import os
from pub_data import pubs

def generate_bibtex_entry(pub):
    # Generate a BibTeX key, e.g., "Author2023Title"
    first_author_lastname = pub["author"][0].split()[-1]
    first_word_title = pub["title"].split()[0]
    bibtex_key = f"{first_author_lastname}{pub['year']}{first_word_title}"

    entry_type = pub.get("type", "misc")
    if entry_type == "conference":
        bib_type = "inproceedings"
    elif entry_type == "journal":
        bib_type = "article"
    else:
        bib_type = "misc"

    entry = f"@{bib_type}{{{bibtex_key},\n"
    entry += f"  title = {{{pub['title']}}},\n"
    
    authors = []
    for author in pub['author']:
        if author == 'me':
            authors.append('He, He')
        else:
            authors.append(author.title())
    entry += f"  author = {{{' and '.join(authors)}}},\n"
    
    entry += f"  year = {{{pub['year']}}},\n"

    if "venue" in pub:
        if bib_type == "inproceedings":
            entry += f"  booktitle = {{{pub['venue']}}},\n"
        elif bib_type == "article":
            entry += f"  journal = {{{pub['venue']}}},\n"

    if "vol" in pub:
        entry += f"  volume = {{{pub['vol']}}},\n"
    if "page" in pub:
        entry += f"  pages = {{{pub['page']}}},\n"
    if "url" in pub:
        entry += f"  url = {{{pub['url']}}},\n"
    if "pdf" in pub:
        entry += f"  url = {{{pub['pdf']}}},\n"
    if "abstract" in pub:
        entry += f"  abstract = {{{pub['abstract']}}},\n"
    entry += "}\n"
    return entry

def main():
    with open("pubs.bib", "w") as f:
        for pub in pubs:
            f.write(generate_bibtex_entry(pub))

if __name__ == "__main__":
    main()
