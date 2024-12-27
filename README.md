# Call of Duty Options Editor User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Main Interface](#main-interface)
    - [Menu Bar](#menu-bar)
    - [Themes](#themes)
5. [Loading and Saving Options](#loading-and-saving-options)
    - [Loading Options](#loading-options)
    - [Saving Options](#saving-options)
6. [Editing Options](#editing-options)
7. [Additional Features](#additional-features)
    - [Search Functionality](#search-functionality)
    - [Tooltips](#tooltips)
    - [Log Window](#log-window)
    - [Read-only Mode](#read-only-mode)
    - [Changing Games](#changing-games)
    - [Clearing Settings](#clearing-settings)
8. [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Logs and Debugging](#logs-and-debugging)
9. [FAQ](#faq)


## Introduction

The Call of Duty Options Editor is a tool designed to help you customize your Call of Duty game settings. It supports multiple Call of Duty titles and provides an intuitive interface for modifying various game options.

**Warning**: This is an advanced application. Incorrect modifications may affect your game performance or stability. Always backup your settings files before making changes.


### Installation

#### Pre-built Release
1. Locate the downloaded .rar file containing the application.
2. Extract the contents of the .rar file to a location of your choice.
3. You should find a single .exe file after extraction. This is the Call of Duty Options Editor application.

#### Building from Source
1. Ensure Python 3.12 or higher is installed
2. Download or clone the source code
3. Run the appropriate build script:
   - Windows: Double-click `build.bat`
   - Unix/Linux: Run `./build.sh`
4. The executable will be created in the `dist` folder


## Getting Started

1. Double-click the .exe file to launch the application.
2. On first launch, you'll see a warning message about the application's advanced nature. Read it carefully and click "OK" to proceed.
3. You'll be prompted to select the game you want to modify settings for:
   - Modern Warfare 2 2022
   - Modern Warfare 3/Warzone 2023
   - Black Ops 6/Warzone* 2024 (*Once game fully transitions over)

## Main Interface

The main interface consists of:
- A menu bar at the top
- A tabbed interface displaying different categories of settings
- A log window (can be toggled on/off)

### Menu Bar
- **File**: Contains options for loading, saving, reloading options, changing games, and exiting.
- **View**: Allows you to show/hide the log window.
- **Options**: Includes options to save settings as read-only and clear all settings and even change the visual theme of the application.
- **Help**: Provides access to the "About" information and the first-time warning.

### Themes
The application supports multiple visual themes:
- Dark themes: Blue, Cyan, Light Green, Pink, Purple, Red, Teal, Yellow
- Light themes: Blue, Amber, Cyan, Light Green, Pink, Purple, Red, Teal, Yellow


## Loading and Saving Options

### Loading Options
1. The application will automatically attempt to locate your game files
2. If files aren't found automatically, you'll be prompted to select two files:
   - For MW2 2022: options.3.cod22.cst and settings.3.local.cod22.cst
   - For MW3 2023: options.4.cod23.cst and gamerprofile.0.BASE.cst
   - For BO6 2024: s.1.0.cod24.txt and g.1.0.l.txt

### Saving Options
1. After making changes, go to File > Save Options
2. The changes will be saved to the originally loaded files
3. Optional: Enable "Save as Read-only" to prevent the game from overwriting your settings

## Editing Options

1. Navigate through the tabs to find the option you want to modify.
2. Each option displays:
   - Setting name
   - Input field (slider, checkbox, dropdown, or text box)
   - Valid value range or options
   - File type (GameSpecific or GameAgnostic)
3. Hover over any option to see detailed help text
4. Changes are marked as unsaved until you save them

## Additional Features


### Search Functionality
- Use the search bar to find specific settings
- Filter by category using the dropdown menu
- Search works across setting names and descriptions

### Tooltips
Hover over any setting to see:
- Detailed description
- Valid value ranges
- Additional help text

### Log Window
- Toggle via View > Show Log
- Tracks all actions and changes
- Can be detached and positioned separately
- Save log contents for troubleshooting

### Read-only Mode
- Option to save files as read-only
- Prevents game from overwriting your settings
- Can be toggled before saving

### Changing Games
- Use File > Change Game to switch between supported Call of Duty titles

### Clearing Settings
- Use Options > Clear All Settings to reset the application to its initial state

## Troubleshooting

### Common Issues
- **File Detection**: If files aren't detected automatically, ensure you're looking in:
  - Default: `~\Documents\Call of Duty\players\`
  - Steam: `~\Documents\Call of Duty\[Steam ID]\`
  - Battle.net: `~\Documents\Call of Duty\[Battle.net ID]\`
- **BO6 2024 Files**: Make sure you're selecting .txt files instead of .cst files
- **Theme Issues**: If theme changes don't apply, try restarting the application
- **Search Not Working**: Clear the search bar and category filter to reset the view

### Logs and Debugging
- Check application_log.txt for detailed error information
- Use the Log Window to track real-time changes
- Save logs for troubleshooting via the Log Window's "Save Log" button


## FAQ

Q: `Can using this tool get me banned?`
- A: `This tool only modifies official game settings files in supported ways. However, use at your own risk as game policies may change.`

Q: `Why are some options grayed out?`
- A: `Some options are read-only to prevent potential issues or because they're automatically determined by the game.`

Q: `What's the difference between GameSpecific and GameAgnostic settings?`
- A: `GameSpecific settings are unique to each game, while GameAgnostic settings apply across different Call of Duty titles.`

Q: `Will my settings persist after game updates?`
- A: `Yes, if you've saved them as read-only. Otherwise, game updates might reset them to defaults.`

Q: `The application crashed. What should I do?`
- A: `Check the log file (application_log.txt) for error details, ensure you have the latest Windows updates and Visual C++ Redistributables installed.`

Q: `Can I have different settings for different games?`
- A: `Yes, the application manages settings separately for each supported game.`

Q: `Do I need specific software to build from source?`
- A: `Yes, you need Python 3.12 or higher. The build script will handle all other dependencies.`

Q: `Why does the application show different file types for BO6 2024?`
- A: `BO6 2024 uses .txt files instead of .cst files for settings storage.`

Q: `Can I revert to default settings?`
- A: `Yes, use Options > Clear All Settings to reset the application settings. For game settings, refer to the game's default options.`

Q: `Why do some sliders not respond to mouse wheel?`
- A: `This is intentional to prevent accidental changes when scrolling through settings.`