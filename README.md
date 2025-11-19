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
3. In the directory where you downloaded the source code, open a command prompt. (On Windows, this can be done by 
opening the folder, clicking the address bar, typing `cmd`, and pressing Enter.)
4. In that command prompt, run `python convert.py <path_to_Manual_APWorld>`, where `<path_to_Manual_APWorld>` is the 
full filepath to the Manual APWorld you're trying to convert.

That's it!

There are additionally the following optional parameters:
- `--output_path`: the directory where you want your PopTracker pack to be created. The directory will be created if it 
does not already exist. If not provided, it defaults to a folder named `poptracker` adjacent to the APWorld.
- `--author`: The name by which you wish to be credited in the PopTracker pack's manifest. Can be manually added after
the fact.


## Additional Keys
By adding some additional optional keys to your Manual APWorld's JSON, this tool can provide a more customized 
experience for your specific use case. The following additional keys are available: 
### Location Position
It's possible to pre-position the PopTracker squares on your map by providing X and Y coordinates in your 
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

### Additional Maps
All locations are added to a map named `main_map` by default. To either rename the map in advance, or produce multiple 
map tabs, you can add the `map` key to any region to move all of that region's locations to that map. This will also 
produce additional tabs, one for each map. For example:
```json
	"Scenario 8": 	{
		"connects_to": ["Scenario 7","Scenario 13","Scenario 14"],
		"requires": "|City Adventuring Permit|",
		"map": "gloomhaven"
	},
```
This will place all the locations in the region named `Scenario 8` into the map named `gloomhaven`.

## What are the tool's limitations?
As previously mentioned, this tool only produces placeholder images and arbitrary location coordinates. Additionally, it
only works with the raw json data in the APWorld; if your Manual APWorld makes extensive use of hooks, especially to 
define logic, items, or locations, this tool won't be able to detect that. It also struggles with slashes in location 
names, due to how PopTracker identifies sections. Finally, it is unable to resolve the built-in logic functions OptOne 
and OptAll, due to not having any information about how many copies of each item were actually generated for a given world.
