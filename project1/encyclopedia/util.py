import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None
    

def markdown_to_html(markdown):
    # Convert headings (e.g., # Heading 1, ## Heading 2, etc.)
    markdown = re.sub(r"^(#)(.*)", r"<h1>\2</h1>", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^(##)(.*)", r"<h2>\2</h2>", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^(###)(.*)", r"<h3>\2</h3>", markdown, flags=re.MULTILINE)

    # Convert bold text (e.g., **bold** to <b>bold</b>)
    markdown = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", markdown)

    # Convert unordered lists (e.g., * Item to <ul><li>Item</li></ul>)
    markdown = re.sub(r"^\* (.*)", r"<ul><li>\1</li></ul>", markdown, flags=re.MULTILINE)

    # Convert links (e.g., [link](URL) to <a href="URL">link</a>)
    markdown = re.sub(r"\[(.*?)\]\((.*?)\)", r"<a href='\2'>\1</a>", markdown)

    # Wrap paragraphs (separate by blank lines, wrap in <p> tags)
    markdown = re.sub(r"([^\n]+)", r"<p>\1</p>", markdown)

    return markdown
