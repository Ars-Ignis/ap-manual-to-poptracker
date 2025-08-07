# AP Manual to PopTracker
A utility for translating a Manual APWorld to a PopTracker pack

## References
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago): A cross-game multiworld randomizer framework
- [Manual for Archipelago](https://github.com/ManualForArchipelago/Manual): A framework to quickly build plug-ins for Archipelago
- [PopTracker](https://github.com/black-sliver/PopTracker): A tool for automatic graphical tracking of randomizers, especially Archipelago

## What is this tool?
This is a tool that parses the data files of a Manual APWorld and from those produces 90% of a PopTracker pack. All you 
need to do is run the script, replace the placeholder images, and position the location squares where you want them. The
script takes care of everything else, including:
- Item inputs
- Location sections
- Pack settings
- Automated Archipelago tracking
- Sending of APManual locations through PopTracker

## How do I use it?
1. [Install Python](https://www.python.org/downloads/)
2. Download the source code
3. In the directory where you downloaded the source code, open a command prompt.
4. In that command prompt, run `python convert.py <path_to_Manual_APWorld>`, where `<path_to_Manual_APWorld>` is the 
full filepath to the Manual APWorld you're trying to convert.

That's it!

There are additionally the following optional parameters:
- `--output_path`: the directory where you want your PopTracker pack to be created. The directory will be created if it 
does not already exist. If not provided, it defaults to a folder named `poptracker` adjacent to the APWorld.
- `--datapackage_URL`: The URL of an Archipelago datapackage that include your Manual APWorld. Most likely found by 
running your own copy of the WebHost from source. If you're not sure how to do that, don't worry about it; it is likely 
to work without it, and at worst you'll need to manually update the `item_mapping.lua` and `location_mapping.lua` files 
produced by the tool. Note: use of this feature requires the Python `requests` module. To install it, you will first 
need pip, which can be installed by running `python -m ensurepip --upgrade` from the command line prompt. After 
installing pip, run `pip install requests` to install the requests module.
- `--author`: The name by which you wish to be credited in the PopTracker pack's manifest. Can be manually added after
the fact.

It's also possible to pre-position the PopTracker squares on your map by providing X and Y coordinates in your 
`locations.json`. For example:
```json
	{
		"name": "Scenario 1 - Complete",
		"region": "Scenario 1",
		"category": ["Main Story Scenarios"],
		"requires": [],
		"x": 255,
		"y": 174
	}
```
This location (and any other locations in the same region and category) will get automatically placed in a square 255
pixels to the right and 174 pixels down from the top-left corner of the map image. If the coordinates are not provided, 
locations will just be placed in an evenly spaced grid.

## What are the tool's limitations?
As previously mentioned, this tool only produces placeholder images and arbitrary location coordinates. Additionally, it
only works with the raw json data in the APWorld; if your Manual APWorld makes extensive use of hooks, especially to 
define logic, items, or locations, this tool won't be able to detect that. It also struggles with slashes in location 
names, due to how PopTracker identifies sections. I haven't yet come up with a satisfactory solution to this problem,
but I am working on it.
