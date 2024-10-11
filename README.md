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
   - MW2/Warzone 2023
   - MW3/Warzone 2024
   - BO6 (currently disabled)

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
1. Go to File > Load Options
2. You'll be prompted to select two files:
   - A game-specific file (e.g., options.4.cod23.cst for MW3/Warzone 2024)
   - A game-agnostic file (gamerprofile.0.BASE.cst)
3. These files are typically located in `~\Documents\Call of Duty\players\`

### Saving Options
1. After making changes, go to File > Save Options
2. The changes will be saved to the originally loaded files
3. If "Save as Read-only" is checked, the files will be set as read-only after saving

## Editing Options

1. Navigate through the tabs to find the option you want to modify.
2. Each option has a label, an input field (which may be a text box, checkbox, or dropdown), and a comment describing valid values.
3. Hover over an option to see a tooltip with more information.
4. Make your desired changes.

## Additional Features

### Log Window
- Toggle the log window visibility via View > Show Log
- The log window displays information about actions performed in the application

### Read-only Mode
- Enable "Save as Read-only" in the Options menu to prevent the game from overwriting your custom settings

### Changing Games
- Use File > Change Game to switch between supported Call of Duty titles

### Clearing Settings
- Use Options > Clear All Settings to reset the application to its initial state

## Troubleshooting

- If the application fails to start, ensure you have the latest version of Windows and all necessary Visual C++ Redistributables installed.
- If you encounter errors while loading or saving files, check that you have the necessary permissions to read/write in the game's directory.
- If changes don't appear in-game, verify that the correct files were modified.

## FAQ

Q: Can using this tool get me banned?
A: This tool only modifies settings that are normally accessible to users. However, use it at your own risk, as game policies may change.

Q: Why are some options grayed out?
A: Some options are not editable to prevent potential issues or because they're automatically determined by the game.

Q: The application crashed. What should I do?
A: Check the log file (application_log.txt) for error details.

