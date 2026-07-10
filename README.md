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
    - [Unified Settings Rows & Change Tracking](#unified-settings-rows--change-tracking)
    - [Search Functionality](#search-functionality)
    - [Tooltips](#tooltips)
    - [Log Window](#log-window)
    - [Import/Export & Sharing Settings](#importexport--sharing-settings)
    - [Settings Library](#settings-library)
    - [Advanced Viewers](#advanced-viewers)
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
3. Build the executable — double-click `build.bat` (or run `python build.py`)
4. The executable will be created in the `dist` folder


## Getting Started

1. Double-click the .exe file to launch the application.
2. On first launch, you'll see a warning message about the application's advanced nature. Read it carefully and click "OK" to proceed.
3. You'll be prompted to select the game you want to modify settings for:
   - Modern Warfare 2 2022
   - Modern Warfare 3/Warzone 2023
   - Black Ops 6/Warzone 2024
   - Black Ops 7/Warzone 2025

## Main Interface

The main interface consists of:
- A menu bar at the top
- A tabbed interface displaying different categories of settings
- A log window (can be toggled on/off)

### Menu Bar
- **File**: Contains options for loading, saving, reloading options, exporting/importing settings, the Settings Library, changing games, and exiting.
- **View**: Allows you to show/hide the log window.
- **Options**: Includes options to save settings as read-only and clear all settings and even change the visual theme of the application.
- **Advanced**: Opens the Controller Settings and Advanced Console Settings viewers.
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
   - For MW3 2023: options.4.cod23.cst and gamerprofile.0.BASE.cst (or gamerprofile.pc.0.BASE.cst)
   - For BO6 2024: s.1.0.cod24.txt and g.1.0.l.txt
   - For BO7 2025: s.1.0.cod25.txt and g.p.cod25.1.0.l.txt

Note: BO6/BO7 keep two copies of the settings file. The editor loads the current one and updates
**both** when you save, so the game always sees your change.

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


### Unified settings rows & change tracking
Every setting is now one consistent row — `[dot] [name] [control] [revert] [range]` — where the
control (toggle / dropdown / slider+number / read-only field) shares one height/radius/colour
language keyed to the **active theme accent**, so all themes look native.
- **Changed-since-load state**: when a value differs from what's on disk the row shows an **amber
  dot**, tints its control amber, and reveals a per-row **↺ revert** button. The status bar shows a
  live count and the window title gains a `•`.
- **Revert**: click a row's ↺ to restore just that value, or **Options → Revert All Changes** (also
  the "Revert all" chip in the top-right corner) to restore everything to disk.
- **Save-as-read-only** is a single control now (the corner toggle and `Options` menu item share one
  state); the old duplicate checkbox is gone.
- Read-only rows (hardware fields / `DO NOT MODIFY`) render as a muted dashed field and never count
  as changed.

### Search Functionality
- Use the search bar to find specific settings; a live **result count** ("N results" / "No results")
  appears next to it
- Matching rows highlight in the **theme accent**; non-matching tabs disable and the view auto-jumps
  when there are only a few matches
- Filter by category using the dropdown menu
- Search works across setting names, help text, and current values

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

### Import/Export & sharing Settings
- **Export**: `File > Export Settings...` prompts for a **title / author / description**, then
  writes your current (edited) values to a portable `.codsettings` file (JSON) tagged with the
  source game. This is a **shareable** file — send it to a friend, post it, etc., and they can
  load it or add it to their library.
- **Import**: `File > Import Settings...` opens an interactive **preview** of a `.codsettings`
  file against the currently loaded game. Settings are matched **by name**, so it works across
  profiles *and* across games (e.g. player 1 exports from MW2, player 2 imports into MW3).

### Settings Library
Open via `File > Settings Library...`. A browsable collection of presets, so you can pick
**recommended** settings, use **someone else's** shared preset, or keep **your own** — and decide
for yourself which to apply.
- Two shelves: **Recommended** (bundled with the app, in `presets/`) and **My Presets** (yours,
  under `%LOCALAPPDATA%\CODOptionsEditor\presets`). Filter to just the loaded game if you like.
- Select a preset to see its author/description, then **Preview && Apply** (runs the same by-name,
  cross-game preview as Import). **Save current as preset...** adds your live settings to the
  library; **Import file to library...** drops a shared `.codsettings` in; **Delete** removes your
  own; **Open folder** reveals the presets folder.
- The `.codsettings` format carries `title / author / description / game` so shared presets are
  self-describing; older files without those fields still load (title falls back to the filename).
- The preview is a tick-list showing **current → new** with a colour-coded status:
  - **Changed** (green, checked by default) — valid and different; applied on confirm.
  - **Unchanged** (grey, locked) — matched but already equal.
  - **Invalid** (red, locked) — out of range / not a valid option for the target game.
  - **Not present** — settings the target game/profile doesn't have (counted, not listed).
  Use *Select all changeable* / *Deselect all*, then **Apply Selected** (or Cancel).
- Applied changes are marked unsaved; use `File > Save Options` to write them.

### Advanced viewers
The **Advanced** menu exposes settings that aren't shown in the main config tabs:

- **Controller Settings** — the controller settings the game keeps in its saved-settings file:
  stick deadzones, stick sensitivity, ADS sensitivity multipliers, Tac-Stance sensitivity, and
  button/stick layout. Hover any setting to see what it does.
  - Sensitivity and deadzone values are **editable** and use the **same unified row** as the main
    editor — a slider + number box that turns **amber with a ↺ revert** when you change it.
    **Save Changes to Game File** writes them back safely: a **timestamped backup** is made
    automatically first, and **Restore from Backup…** rolls back to any earlier backup. Close the
    game before saving.
  - Layout and behavior settings (button layout, stick layout, sprint, interact/reload) are shown
    for reference — change those in the game's own Controller settings.

- **Advanced Console Settings** — the advanced console settings stored in the game's config files,
  shown read-only for reference. Change these in-game.

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
- **File Detection**: The editor now searches all known launcher/platform locations automatically:
  - Steam/Battle.net: `~\Documents\Call of Duty\players\` and `~\Documents\Call of Duty\[Steam/Battle.net ID]\`
  - Per-title: `~\Documents\Call of Duty MWII\`, `Call of Duty MWIII\`, `Call of Duty Modern Warfare\`
  - Microsoft Store / Game Pass: `%LOCALAPPDATA%\Activision\Call of Duty\players\[XUID]\` (and per-title variants)
  - It also looks one folder deep for account (Steam/Battle.net/Xbox XUID) subfolders.
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