#!/usr/bin/env python3

from os import walk
from os.path import join, relpath
from utils import get_template
from re import sub, search
from urllib.parse import quote

from utils import get_root_of_vault

# These are directories and files to exclude
# By adding a dir/file, this script will ignore them and never change them!
DIRECTORIES_TO_EXCLUDE = ['.git', '.github', '.idea', 'venv', '01 Templates', 'DO NOT COMMIT']
FILES_TO_EXCLUDE = ['.DS_Store', '.gitignore']


def add_footer(top_directory: str, debug: bool = True):
    """
    Walks through the filetree rooted at `root`.
    For each markdown file that it finds, it replaces a particular comment line with the corresponding template.

    Parameters:
        top_directory: path from which this method should run. Generally: root of the hub.
        debug: boolean that indicates wether or not to print logging statements
    """
    # Grab the template
    template = get_template("footer")

    # This is the regex to search for
    # Note that we select the comment itself, and then ANYTHING afterwards
    # This requires the "DOTALL" (?s) and "MULTILINE" (?m) flags to be set
    comment = r"(?sm)%% Hub footer: Please don't edit anything below this line %%.*"

    # Loop through the files
    for root, dirs, files in walk(top_directory, topdown=True):
        # Exclude directories and files
        dirs[:] = [d for d in dirs if d not in DIRECTORIES_TO_EXCLUDE]
        files[:] = [f for f in files if f not in FILES_TO_EXCLUDE]

        # Loop through the files
        for file in files:
            # We only care about markdown files
            # Note: Alternative implementation is to use os.splitext;
            # both work for this usecase
            if file.endswith(".md"):

                # Get the ABSOLUTE filepath
                absolute_path = join(root, file)

                relative_path = relpath(absolute_path, top_directory)
                # Open the (ABSOLUTE) file in read/write mode
                with open(absolute_path, "r+") as f:
                    if debug:
                        print(f"Processing '{relative_path}'...")

                    # Read the file contents
                    contents = f.read()

                    replacement = add_footer_to_markdown(relative_path, contents, comment, template, debug)

                    # Actually write
                    # This is done by seeking to the beginning of the file
                    f.seek(0)
                    # Then writing the replacement string
                    f.write(replacement)
                    # And finally truncating the file to close it
                    f.truncate()


def add_footer_to_markdown(relative_path, contents, comment, template, debug):
    # Get the rendered template (file => relative path => html encoded)
    render = template.render(
        file_path=quote(relative_path))

    # Check if our particular comment is present
    if search(comment, contents):
        replacement = sub(comment, render, contents)
        if debug:
            print(
                f"\t=> Replacing everything below the line with the template for '{relative_path}'.")
    # If it's not there: Add it
    else:
        replacement = contents + "\n" + render

        if debug:
            print(f"\t=> Adding the template for '{relative_path}'.")

    return replacement


def main():
    # Grab the root folder to run in.
    # Uses the utility method to get root of the vault.
    root = get_root_of_vault()

    # Set debug to whichever you'd like; true by default
    add_footer(root)


if __name__ == "__main__":
    main()
