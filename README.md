# Call of Duty Options Editor User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Main Interface](#main-interface)
5. [Loading and Saving Options](#loading-and-saving-options)
6. [Editing Options](#editing-options)
7. [Additional Features](#additional-features)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Introduction

The Call of Duty Options Editor is a tool designed to help you customize your Call of Duty game settings. It supports multiple Call of Duty titles and provides an intuitive interface for modifying various game options.

**Warning**: This is an advanced application. Incorrect modifications may affect your game performance or stability. Always backup your settings files before making changes.

## Installation

1. Locate the downloaded .rar file containing the application.
2. Extract the contents of the .rar file to a location of your choice.
3. You should find a single .exe file after extraction. This is the Call of Duty Options Editor application.

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
- **Options**: Includes options to save settings as read-only and clear all settings.
- **Help**: Provides access to the "About" information and the first-time warning.

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

- If files aren't detected automatically, ensure you're looking in the correct directory:
  - Default: `~\Documents\Call of Duty\players\`
  - Steam: `~\Documents\Call of Duty\[Steam ID]\`
  - Battle.net: `~\Documents\Call of Duty\[Battle.net ID]\`
- For BO6 2024, make sure you're selecting .txt files instead of .cst files
- Check application_log.txt for detailed error information

## FAQ

Q: Can using this tool get me banned?
A: This tool only modifies official game settings files in supported ways. However, use at your own risk as game policies may change.

Q: Why are some options grayed out?
A: Some options are read-only to prevent potential issues or because they're automatically determined by the game.

Q: What's the difference between GameSpecific and GameAgnostic settings?
A: GameSpecific settings are unique to each game, while GameAgnostic settings apply across different Call of Duty titles.

Q: Will my settings persist after game updates?
A: Yes, if you've saved them as read-only. Otherwise, game updates might reset them to defaults.

Q: The application crashed. What should I do?
A: Check the log file (application_log.txt) for error details, ensure you have the latest Windows updates and Visual C++ Redistributables installed.
