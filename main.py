import datetime
import json
from pathlib import Path


def main() -> None:
    data: dict = read_json()
    html: str = convert_json_to_html(data)
    write_html(html)

    print("Done!")


def read_json() -> dict:
    print("Reading JSON...")

    # Use the current working directory for the JSON file
    filename: Path = Path("StorableSidebar.json")
    data: dict = {}

    if filename.exists():
        with filename.open("r", encoding="utf-8") as f:
            print(f"> Found {filename} in the current directory.")
            data = json.load(f)
    else:
        print('> File not found. Look for the "StorableSidebar.json" file in the current directory.')
        raise FileNotFoundError

    return data


def convert_json_to_html(json_data: dict) -> str:
    containers: list = json_data["sidebar"]["containers"]
    target: int = sum([1 for i in containers if "global" in i])

    spaces: dict = get_spaces(json_data["sidebar"]["containers"][target]["spaces"])
    items: list = json_data["sidebar"]["containers"][target]["items"]

    bookmarks: dict = convert_to_bookmarks(spaces, items)
    html_content: str = convert_bookmarks_to_html(bookmarks)

    return html_content


def get_spaces(spaces: list) -> dict:
    print("Getting spaces...")

    spaces_names: dict = {"pinned": {}, "unpinned": {}}
    spaces_count: int = 0
    n: int = 1

    for space in spaces:
        if "title" in space:
            title: str = space["title"]
        else:
            title: str = "Space " + str(n)
            n += 1

        if isinstance(space, dict):
            containers: list = space["newContainerIDs"]

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
    print("Converting to bookmarks...")

    bookmarks: dict = {"bookmarks": []}
    bookmarks_count: int = 0
    item_dict: dict = {item["id"]: item for item in items if isinstance(item, dict)}

    def recurse_into_children(parent_id: str) -> list:
        nonlocal bookmarks_count
        children: list = []
        for item_id, item in item_dict.items():
            if item.get("parentID") == parent_id:
                if "data" in item and "tab" in item["data"]:
                    children.append(
                        {
                            "title": item.get("title", None)
                            or item["data"]["tab"].get("savedTitle", ""),
                            "type": "bookmark",
                            "url": item["data"]["tab"].get("savedURL", ""),
                        }
                    )
                    bookmarks_count += 1
                elif "title" in item:
                    child_folder: dict = {
                        "title": item["title"],
                        "type": "folder",
                        "children": recurse_into_children(item_id),
                    }
                    children.append(child_folder)
        return children

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
    print("Converting bookmarks to HTML...")

    html_str: str = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>"""

    def traverse_dict(d: dict, html_str: str, level: int) -> str:
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
    print("Writing HTML...")

    current_date: str = datetime.datetime.now().strftime("%Y_%m_%d")
    output_file: Path = Path("arc_bookmarks_" + current_date).with_suffix(".html")

    with output_file.open("w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"> HTML written to {output_file}.")


if __name__ == "__main__":
    main()
