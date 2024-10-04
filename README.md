# Keystroke Visualizer for Specific Applications

With this app you can see the pressed keys when using specific applications (windows only). So for example you can put photoshop's path and whenever you're using photoshop, the visualizer will appear. I made this because my pen-tablet doesn't show which button is pressed. You can use it too if you want.

## Installation

Download the [latest release](releases/latest). It's portable, so just unzip it and double click the exe to run.

#### build via source

If you want to use the source code instead, just download this repo and type `python app.py`.
you can also turn this into a pyw file and add a startup task in `task schedular`

## Usage

When you start the application the first time, you'll see a warning telling you to to specify at least one application. Right click on the tray icon and click `Settings` then make your changes and `Apply Settings`. That's all, enjoy

#### example path

Example path: `C:/Program Files/.../Photoshop.exe` (tip: you can shit click the file and choose `copy as path`. remove the double quotations as well)

#### Notes

- The position would by default be top middle. Remove everything (except for excutable's path) and you'll get the default values
- `X`, `Y`, `Width` and `Height` are for the bounding box where the visualizer is
- `Hide After` is the amount of time (in seconds) that the visualizer shows each key (by default shows for 1 second and disappears)
- Change the [icon.ico](icon.ico) file if you don't like the thumbnail in system tray
- Some parts were made by ChatGPT. If you encounter anything weird, that's why

## Copyright

Free for personal usage. Credit for Commercial and Non-personal usage

### Buy Me A Coffee

Since I'm making this project free and public, any donation is appreciated :3
- USDT (BEP20): `0xF11206c2234306c55794169C3991f9e8a09063Eb`
- USDT (ERC20): `0xF11206c2234306c55794169C3991f9e8a09063Eb`
