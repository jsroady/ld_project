#!/usr/bin/env python3
# *-* coding: UTF-8 *-*
# Authors: Jessica Roady & Kyra Goud

import requests
import re
import csv
import json
import spacy
# You will have to run the following in the command line. Alternatively, try en_core_web_trf for a bigger model:
# python3 -m spacy download en_core_web_sm

# If spaCy creates problems with the above, try uncommenting the following:
# from spacy.cli.download import download
# download(model='en_core_web_sm')

# Variables for URL-API information retrieval (1000 requests per day and per key):
# Jessica's key: ac0e292a-80e6-4040-8f33-64105a016803
# Jessica's key 2: 1a12a465-41cd-4109-b4f3-5e84529bfaac
# Jessica's key 3: 642b0a6e-678b-4e0f-9997-2aac099430e2
# Simon's key: f18a3a58-5499-4e50-ad27-a9512055f56b
# Kyra's key: 90f56d8f-b050-4366-a9f8-e183cec01edc
key = '642b0a6e-678b-4e0f-9997-2aac099430e2'
lang = 'EN'
headers = {'Accept-Encoding': 'gzip'}
text = ''
lemma = ''

# Parameters of API-urls:
params1 = {
    'text':text,  # list of strings from read_file()
    'lang':lang,
    'key': key,
}
params2 = {
    'lemma':lemma,
    'lang':lang,
    'key':key
}

#  URLs for information retrieval of API:
service_url_disambiguate = 'https://babelfy.io/v1/disambiguate'
service_url_retrievesynset = 'https://babelnet.io/v6/getSynsetIds'
url_retrievesynsets = f'https://babelnet.io/v6/getSynsetIds?lemma{lemma}&searchLang={lang}&key={key}'.format(
    lemma=params2['lemma'], searchLang=params2['lang'], key=params2['key'])
url_babelfyversion = f'https://babelnet.io/v6/getVersion?key={key}'.format(key=params1['key'])
url_disambiguate = f'https://babelfy.io/v1/disambiguate?text={text}&lang={lang}&key={key}'.format(
    text=params1['text'],lang=params1['lang'],key=params1['key'])


def get_response(url, params):
    """ Returns the API-response (json format)"""
    response = requests.get(url, params=params, headers=headers)
    return response.json()


# TODO: Implement a CLI
def parse_cli():
    pass


def read_file(file):
    with open(file, 'r') as f:
        lines = [line.rstrip() for line in f]
    return lines


def strip_headers_footers(lines):
    """Strip Project Gutenberg headers/footers"""
    r_header = re.compile(r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*")
    header_line = list(filter(r_header.match, lines))[0]
    r_footer = re.compile(r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK .*")
    footer_line = list(filter(r_footer.match, lines))[0]

    header_index = lines.index(header_line)
    footer_index = lines.index(footer_line)

    return lines[header_index+5:footer_index-4]  # +5 and -4 to get rid of trailing newlines


# TODO: Once CLI is implemented, make this part run only if the user says their text has artificial line breaks
def para_tokenise(stripped_lines):
    """Fix artificial line breaks"""
    paragraph = ''
    paragraphs = []

    for line in stripped_lines:  # If the line is a newline, we will know the paragraph has ended.
        if line == '':  # It will be '' and not '\n' because we did line.strip() when reading in the file.
            paragraphs.append(paragraph)  # We can add it to our list of paragraphs...
            paragraph = ''  # ...and reset the paragraph string to start at the next paragraph.
        else:  # Otherwise, we keep on appending lines, making sure to add a whitespace at the end of each one.
            paragraph += line + ' '

    return paragraphs


def get_link(babelsynsetID):
    """ Returns the link of the NE according to its babelsynsetID """
    url = f'https://babelnet.org/synset?word={babelsynsetID}&lang=EN&langTrans=DE'
    return url


def get_entity(text, cfStart, cfEnd):
    """ Returns the entity according to the character span """
    return text[cfStart:cfEnd+1]


def generate_data(lines):
    """ Tokenization, lemmatization, POS-tagging, NE linking """
    nlp = spacy.load("en_core_web_sm")
    json_content = read_json('json_response.json')

    entities = []
    ent_on_off = []
    tok_index = []
    tokens = []
    lemmas = []
    pos = []
    links = []
    synsetIds = []

    for i, texts in enumerate(json_content, start=0):
        doc = nlp(lines[i])
        for o, token in enumerate(doc):
            tokens.append(token.text)
            tok_index.append((token.i, token.i))
            lemmas.append(token.lemma_)
            pos.append(token.pos_)

        results_per_text = json_content[texts]
        for result in results_per_text:
            # token from fragment retrieval
            tokenFragment = result.get('tokenFragment')
            tfStart = tokenFragment.get('start')
            tfEnd = tokenFragment.get('end')
            ent_on_off.append((tfStart, tfEnd))

            # Babelsynset ID retrieval
            synsetId = result.get('babelSynsetID')
            synsetIds.append(synsetId)
            links.append(get_link(synsetId))

            # char from fragment retrieval, needed for entity linking
            charFragment = result.get('charFragment')
            cfStart = charFragment.get('start')
            cfEnd = charFragment.get('end')

            entity = get_entity(lines[i], cfStart, cfEnd)
            entities.append(entity)

    return tokens, lemmas, pos, tok_index, entities, ent_on_off, synsetIds, links


def remove_duplicate_ents(entities, ent_on_off, synsetIds, links):
    """ Removes shortest-span entities """
    ent_info = list(zip(entities, ent_on_off, synsetIds, links))

    for i, item in enumerate(ent_info):
        if i > 0:
            e1_on = ent_info[i - 1][1][0]
            e1_off = ent_info[i - 1][1][1]
            e2_on = item[1][0]
            e2_off = item[1][1]

            # Using the type as a flag for later removal, because if I just remove it the indices will get messed up
            if e1_on >= e2_on and e1_off <= e2_off:
                ent_info[i - 1] = list(ent_info[i - 1])
            if e1_on <= e2_on and e1_off >= e2_off:
                ent_info[i] = list(ent_info[i])

    for i in ent_info:
        if isinstance(i, list):
            ent_info.remove(i)

    return ent_info


def align_toks_to_ents(tokens, lemmas, pos, tok_index, ent_info):
    """ Aligns tokens with entities """
    data = []
    token_info = list(zip(tokens, lemmas, pos, tok_index))

    for t in token_info:
        row = list(t)

        for e in ent_info:
            entity = e[0]
            ent_index = e[1]
            ent_id = e[2]
            ent_link = e[3]

            # Single-token entities:
            if t[0] == entity and t[3] == ent_index:  # OK because no two identical tokens also have the same indices
                row.extend([entity, 'B-' + ent_id, ent_link])

            # Multi-token entities:
            #   if the onset is the same:
            elif t[0] + ' ' in entity and t[3][0] == ent_index[0]:
                if not len(row) == 7:  # needed to avoid appending the entity multiple times
                    row.extend([entity, 'B-' + ent_id, ent_link])
            #   if the offset is the same:
            elif ' ' + t[0] in entity and t[3][1] == ent_index[1]:
                if not len(row) == 7:
                    row.extend([entity, 'I-' + ent_id, ent_link])

            # TODO: this is a problem because there are ents longer than 3 tokens now

            #   if the onsets are within 1 of each other (this is enough because there are no entities longer than 3):
            elif ' ' + t[0] + ' ' in entity and t[3][0] - 1 == ent_index[0]:
                if not len(row) == 7:
                    row.extend([entity, 'I-' + ent_id, ent_link])
            #   if the offsets are within 1 of each other:
            elif ' ' + t[0] + ' ' in entity and t[3][1] + 1 == ent_index[1]:
                if not len(row) == 7:
                    row.extend([entity, 'I-' + ent_id, ent_link])

        data.append(row)

    return data


def read_json(file):
    """ Reads a json file and returns its content """
    with open(file, 'r') as j:
        json_content = json.loads(j.read())
    return json_content


def create_json_file(data_disambiguate):
    """ Creates a json file """
    with open('json_response.json', 'w') as f:
        json.dump(data_disambiguate, f, indent=4)


def write_tsv(data):
    """ Creates a .tsv file of data """
    with open('data.tsv', 'w', encoding='UTF8', newline='\n') as f:
        header = ['token', 'lemma', 'pos', '(onset, offset)', 'entity', 'babelfy_id(iob)', 'link', 'TP', 'FP', 'FN']
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)
        writer.writerows(data)


def main():
    lines = read_file('bible.txt')  # TODO: make this take command-line input
    stripped_lines = strip_headers_footers(lines)
    paragraphs = para_tokenise(stripped_lines)

    # TODO: change this to = stripped_lines if user says their text does not have artificial line breaks
    # params1['text'] = paragraphs

    # For dev purposes, I'll work with just 10 paragraphs:
    extract = paragraphs[10:21]
    params1['text'] = extract

    # Getting API-response from request and creating a .json file out of it
    datadis = {}
    for i, text in enumerate(params1['text'], start=1):
        params1['text'] = text
        response_dis = requests.get(service_url_disambiguate, params=params1, headers=headers)
        json_data_dis = response_dis.json()
        datadis['text ' + str(i)] = json_data_dis

    create_json_file(datadis)

    tokens, lemmas, pos, tok_index, entities, ent_on_off, synsetIds, links = generate_data(extract)
    ent_info = remove_duplicate_ents(entities, ent_on_off, synsetIds, links)

    data = align_toks_to_ents(tokens, lemmas, pos, tok_index, ent_info)
    write_tsv(data)


if __name__ == "__main__":
    main()
