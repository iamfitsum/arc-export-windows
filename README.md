# Arc Pinned Tabs to HTML Bookmarks Converter

## Overview

This project provides a script for converting pinned tabs in the **Arc Browser** to a standard HTML bookmarks file. These bookmarks can then be imported into any web browser.

This addresses the lack of a pinned tabs export feature in Arc Browser.

## Requirements

- Python 3.x
- Arc Browser installed

## Installation

1. Clone the repository: `git clone https://github.com/iamfitsum/arc-export-windows.git`
2. Navigate to the project folder: `cd arc-export-windows`

or download using `curl`:

```sh
curl -o main.py https://raw.githubusercontent.com/iamfitsum/arc-export-windows/main/main.py
```

## Usage

### Finding `StorableSidebar.json` in Windows

1. Enable "Show hidden files" by clicking **View** on the top navigation bar of the File Explorer, then clicking on **Show** and checking the **Hidden items**.
2. Navigate to `C:\Users\{UserName}\AppData\Local\Packages\TheBrowserCompany.Arc_ttt1ap7aakyb4\LocalCache\Local\Arc`.
3. Copy the `StorableSidebar.json` file to the directory where you placed `main.py` (i.e., the cloned project folder or the folder where you downloaded `main.py`).

Then, run the `main.py` script from the command line:

```sh
python3 main.py

# or if there is an error:
python main.py
```

## How It Works

1. **Read JSON**: Reads the `StorableSidebar.json` file from the current directory.
2. **Convert Data**: Converts the JSON data into a hierarchical bookmarks dictionary.
3. **Generate HTML**: Transforms the bookmarks dictionary into an HTML file.
4. **Write HTML**: Saves the HTML file with a timestamp, allowing it to be imported into any web browser.

## Acknowledgments

This project is based on the [arc-export](https://github.com/ivnvxd/arc-export) project by [ivnvxd](https://github.com/ivnvxd). Thank you for the original work!

## Contributions

Contributions are very welcome. Please submit a pull request or create an issue.

And do not forget to give the project a star if you like it! :star:

## License

This project is licensed under the MIT License.
