#!/usr/bin/python3

"""
markdown2html.py
Convert Markdown files to HTML files.
Usage:
    python3 markdown2html.py input.md output.html
"""

import sys
import os.path
import re
import hashlib

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html",
              file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(sys.argv[1]):
        print('Missing {}'.format(sys.argv[1]), file=sys.stderr)
        exit(1)

    with open(sys.argv[1]) as read:
        with open(sys.argv[2], 'w') as html:
            unordered_start, ordered_start, paragraph = False, False, False

            for line in read:
                # Process special markdown syntax
                # Bold and emphasis
                line = line.replace('**', '<b>', 1)
                line = line.replace('**', '</b>', 1)
                line = line.replace('__', '<em>', 1)
                line = line.replace('__', '</em>', 1)

                # MD5 hash - Fix: Properly extract content and apply MD5
                md5_matches = re.findall(r'\[\[(.+?)\]\]', line)
                for match in md5_matches:
                    md5_hash = hashlib.md5(match.encode()).hexdigest()
                    line = line.replace(f"[[{match}]]", md5_hash)

                # Remove letter C - Fix: Properly handle capture groups
                remove_c_matches = re.findall(r'\(\((.+?)\)\)', line)
                for match in remove_c_matches:
                    cleaned_text = ''.join(c for c in match if c not in 'Cc')
                    line = line.replace(f"(({match}))", cleaned_text)

                # Process line structure
                length = len(line)
                headings = line.lstrip('#')
                heading_num = length - len(headings)
                unordered = line.lstrip('-')
                unordered_num = length - len(unordered)
                ordered = line.lstrip('*')
                ordered_num = length - len(ordered)

                # Process headings
                if 1 <= heading_num <= 6:
                    line = '<h{}>'.format(
                        heading_num) + headings.strip() + '</h{}>\n'.format(
                        heading_num)

                # Process unordered lists
                if unordered_num:
                    if not unordered_start:
                        html.write('<ul>\n')
                        unordered_start = True
                    line = '<li>' + unordered.strip() + '</li>\n'
                elif unordered_start:
                    html.write('</ul>\n')
                    unordered_start = False

                # Process ordered lists
                if ordered_num:
                    if not ordered_start:
                        html.write('<ol>\n')
                        ordered_start = True
                    line = '<li>' + ordered.strip() + '</li>\n'
                elif ordered_start:
                    html.write('</ol>\n')
                    ordered_start = False

                # Process paragraphs
                if not (heading_num or unordered_start or ordered_start):
                    if not paragraph and length > 1:
                        html.write('<p>\n')
                        paragraph = True
                    elif length > 1:
                        html.write('<br/>\n')
                    elif paragraph:
                        html.write('</p>\n')
                        paragraph = False

                if length > 1:
                    html.write(line)

            # Clean up any unclosed tags
            if unordered_start:
                html.write('</ul>\n')
            if ordered_start:
                html.write('</ol>\n')
            if paragraph:
                html.write('</p>\n')
    exit(0)
