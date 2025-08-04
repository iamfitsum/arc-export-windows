import datetime
import json
import re
from pathlib import Path


def fix_malformed_urls(json_content: str) -> str:
    """
    Fix malformed URL escaping in JSON content.
    
    Arc browser exports sometimes have incorrectly escaped file paths and URLs
    that cause JSON parsing errors. This function corrects these issues.
    """
    # Fix malformed URL patterns
    json_content = re.sub(r'file:\\\/\\\/\\\/', 'file:///', json_content)
    json_content = re.sub(r'https:\\\/\\\/', 'https://', json_content)
    json_content = re.sub(r'http:\\\/\\\/', 'http://', json_content)
    
    # Fix Windows file paths with unescaped backslashes
    json_content = re.sub(r'C:\\', 'C:/', json_content)
    json_content = re.sub(r'D:\\', 'D:/', json_content)
    
    return json_content


def main() -> None:
    """Main function to convert Arc browser bookmarks to HTML format."""
    data: dict = read_json()
    html: str = convert_json_to_html(data)
    write_html(html)
    print("Done!")


def read_json() -> dict:
    """Read and parse the StorableSidebar.json file with error handling."""
    print("Reading JSON...")
    filename: Path = Path("StorableSidebar.json")
    
    if not filename.exists():
        print('> File not found. Look for the "StorableSidebar.json" file in the current directory.')
        raise FileNotFoundError
    
    with filename.open("r", encoding="utf-8") as f:
        print(f"> Found {filename} in the current directory.")
        content = f.read()
        # Fix malformed URLs before parsing
        content = fix_malformed_urls(content)
        return json.loads(content)


def convert_json_to_html(json_data: dict) -> str:
    """Convert Arc browser JSON data to HTML bookmark format."""
    containers: list = json_data["sidebar"]["containers"]
    
    # Find the container with the most items (likely the main container)
    target_container = None
    max_items = 0
    
    for container in containers:
        if "spaces" in container and "items" in container:
            item_count = len(container["items"])
            if item_count > max_items:
                max_items = item_count
                target_container = container
    
    if not target_container:
        print("No container with spaces and items found!")
        return ""
    
    print(f"> Using container with {max_items} items")
    
    spaces: dict = get_spaces(target_container["spaces"])
    items: list = target_container["items"]
    bookmarks: dict = convert_to_bookmarks(spaces, items)
    
    return convert_bookmarks_to_html(bookmarks)


def get_spaces(spaces: list) -> dict:
    """Extract space names and organize them by pinned/unpinned status."""
    print("Getting spaces...")
    
    spaces_names: dict = {"pinned": {}, "unpinned": {}}
    spaces_count: int = 0
    n: int = 1

    for space in spaces:
        # Get space title or generate default name
        if "title" in space:
            title: str = space["title"]
        else:
            title: str = "Space " + str(n)
            n += 1

        if isinstance(space, dict):
            containers: list = space["newContainerIDs"]

            # Map container IDs to space names
            for i in range(len(containers)):
                if isinstance(containers[i], dict):
                    if "pinned" in containers[i]:
                        spaces_names["pinned"][str(containers[i + 1])] = title
                    elif "unpinned" in containers[i]:
                        spaces_names["unpinned"][str(containers[i + 1])] = title

            spaces_count += 1

    print(f"> Found {spaces_count} spaces.")
    return spaces_names


def convert_to_bookmarks(spaces: dict, items: list) -> dict:
    """Convert Arc items to bookmark structure with proper hierarchy."""
    print("Converting to bookmarks...")

    bookmarks: dict = {"bookmarks": []}
    bookmarks_count: int = 0
    item_dict: dict = {item["id"]: item for item in items if isinstance(item, dict)}

    def recurse_into_children(parent_id: str) -> list:
        """Recursively build bookmark hierarchy from parent-child relationships."""
        nonlocal bookmarks_count
        children: list = []
        
        for item_id, item in item_dict.items():
            if item.get("parentID") == parent_id:
                if "data" in item and "tab" in item["data"]:
                    # This is a bookmark
                    children.append({
                        "title": item.get("title", None) or item["data"]["tab"].get("savedTitle", ""),
                        "type": "bookmark",
                        "url": item["data"]["tab"].get("savedURL", ""),
                    })
                    bookmarks_count += 1
                elif "title" in item:
                    # This is a folder
                    child_folder: dict = {
                        "title": item["title"],
                        "type": "folder",
                        "children": recurse_into_children(item_id),
                    }
                    children.append(child_folder)
        return children

    # Create bookmark folders for each space
    for space_id, space_name in spaces["pinned"].items():
        space_folder: dict = {
            "title": space_name,
            "type": "folder",
            "children": recurse_into_children(space_id),
        }
        bookmarks["bookmarks"].append(space_folder)

    print(f"> Found {bookmarks_count} bookmarks.")
    return bookmarks


def convert_bookmarks_to_html(bookmarks: dict) -> str:
    """Convert bookmark structure to Netscape bookmark HTML format."""
    print("Converting bookmarks to HTML...")

    html_str: str = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>"""

    def traverse_dict(d: dict, html_str: str, level: int) -> str:
        """Recursively traverse bookmark structure and generate HTML."""
        indent: str = "\t" * level
        for item in d:
            if item["type"] == "folder":
                html_str += f'\n{indent}<DT><H3>{item["title"]}</H3>'
                html_str += f"\n{indent}<DL><p>"
                html_str = traverse_dict(item["children"], html_str, level + 1)
                html_str += f"\n{indent}</DL><p>"
            elif item["type"] == "bookmark":
                html_str += f'\n{indent}<DT><A HREF="{item["url"]}">{item["title"]}</A>'
        return html_str

    html_str = traverse_dict(bookmarks["bookmarks"], html_str, 1)
    html_str += "\n</DL><p>"

    print("> HTML converted.")
    return html_str


def write_html(html_content: str) -> None:
    """Write HTML content to a timestamped file."""
    print("Writing HTML...")
    
    current_date: str = datetime.datetime.now().strftime("%Y_%m_%d")
    output_file: Path = Path("arc_bookmarks_" + current_date).with_suffix(".html")

    with output_file.open("w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"> HTML written to {output_file}.")


if __name__ == "__main__":
    main()
