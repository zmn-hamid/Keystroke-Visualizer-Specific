# Keystroke Visualizer for Specific Applications

With this app you can see the pressed keys when using specific applications (windows only). So for example you can put photoshop's path and whenever you're using photoshop, the visualizer will appear. I made this because my pen-tablet doesn't show which button is pressed. You can use it too if you want.

## Installation

1. Install python 3 and add it to path
2. Download this repository.
3. Double click on [install-reqs.cmd](install-reqs.cmd) file and wait for it to install everything
5. Now you can just start the [app.pyw](app.pyw) file by double clicking on it

**Note**: You have to specify the path to your executable file. After running the app,
right click on the tray app's icon and choose "settings" from the menu, make your changes and save,
then restart the app from the same menu

### Auto-Start

To automatically start your app on windows startup, you can use the built-in "Task Schedular".

**When adding action**:
- Use `pythonw` in the `Program/Script` field. for example: `C:\Users\username\AppData\Local\Programs\Python\Python312\pythonw.exe`
- Type `app.pyw` in the `add argument` field
- Type the path to the repository's folder in the `start in` field: `c:/path/to/repository`

**When adding trigger**:
- Use "at log on", not "at startup"

## Usage

- Right Click on the tray app and choose `change settings`. Now enter the path to your executable file. for example: `C:/Program Files/.../Photoshop.exe` (tip: you can shit click, `copy as path` and remove the double quotations from the copied text)
- You can change the position and font of the text as well
- After making any changes to settings, restart the app and now you'll see visualizer of your keystrokes in the desired application.

#### Notes

- The position would by default be top middle. remove everything (except for excutable's path) and you'll get the default values
- Change the [icon.ico](icon.ico) file if you don't like it
- Some parts were used by ChatGPT. If you encounter anything weird, that's why

## Copyright

Free for personal usage. Credit for Commercial and Non-personal usage

### Buy Me A Coffee

Would Appreciate any donation :3
- USDT (BEP20): `0xF11206c2234306c55794169C3991f9e8a09063Eb`
- USDT (ERC20): `0xF11206c2234306c55794169C3991f9e8a09063Eb`
