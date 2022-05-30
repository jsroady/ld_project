#!/usr/bin/env python3
# *-* coding: UTF-8 *-*
# Authors: Jessica Roady & Kyra Goud

import argparse
import requests
from nel import *


def create_arg_parser():
    parser = argparse.ArgumentParser(
        'Named Entity Recogniser and Linker',
        description='A command line tool for NER/NEL and calculating WordNet connectedness.')

    # TODO: Default to bible.txt if the user doesn't want to provide their own file.
    parser.add_argument('--file', type=argparse.FileType(encoding='utf-8'), nargs=1,
                        help=".txt file to analyse. Specify if the file is from Project Gutenberg and needs "
                             "headers/footers stripped and/or artificial line breaks fixed with the flags "
                             "'-headers_footers' and '-artifical_line_breaks'.")

    # TODO: Add args '-headers_footers' and '-artifical_line_breaks'.
    # TODO: Add arg '-entities' for the user to choose if they want to write the .tsv outfile with all NEs.

    return parser


def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    lines = read_file('bible.txt')
    stripped_lines = strip_headers_footers(lines)
    paragraphs = para_tokenise(stripped_lines)

    # TODO: change this to = stripped_lines if user says their text does not have artificial line breaks
    # params1['text'] = paragraphs
    # ...but for now, I'll work with 10 paragraphs to minimise runtime and avoid maxing out my Babelfy requests:
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


if __name__ == '__main__':
    main()
