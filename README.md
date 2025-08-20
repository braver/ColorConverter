# ColorConverter for Sublime Text

Convert colors (e.g. in CSS) from one format to another. 
The following formats are supported as both input and output.
Any alpha value (opacity) present in the input color is retained in the output.

- [name](https://developer.mozilla.org/en-US/docs/Web/CSS/named-color)
- [hexadecimal](https://developer.mozilla.org/en-US/docs/Web/CSS/hex-color)
- [`rgb()`](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/rgb)
- [`hsl()`](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/hsl)
- [`lab()`](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/lab)
- [`color()`](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/color)

The `rgba()` and `hsla()` color functions are considered legacy:
the `rgb()` and `hsl()` functions both also take an alpha channel. This package will convert from, but not _to_, these legacy formats.

Note that relative value syntax (e.g. `color(from green ...`) is not supported.

## How to use

- Via the command palette (look for "ColorConverter: Convert to ...").
- Via the context menu.
- You can set up a keyboard shortcut.

Select or put your cursor on a color, then select the format to convert to.

It's also possible to convert all colors in a document.
If you run "convert all" with an active selection, only the colors in that selection are converted (this requires a ST build of 4181 or newer).

### Copy as...

A "Copy as hex" command is available in both the context menu and command palette. This converts the selected color to uppercase hexadecimal, with 6 characters (or 8 if there is opacity). This is an "portable" format that allows easy copying of colors across different applications.  
The "HEX6" format is not one of the default targets, but you can use it in your own  commands or keyboard shortcuts. All the other supported formats can also be used in the `color_convert_copy` command.

## How to customize

### Output formats

By default the output is minimalist:
no commas or optional units, lowercase and short hexadecimals.
Please refer to the preferences to fine-tune the output to your liking.

### Key bindings

To set up a keyboard shortcut, open the ColorConverter Key Bindings preferences,
either via the Packages Settings menu or the command palette.
Copy the example to your personal key bindings file. You can customize the keyboard combination that triggers the command. 

The `value` specified here is the target format, which is one of the following:

- `name`
- `hex`
- `rgb`
- `hsl`
- `lab`
- `color`

For more information on key bindings see the [community documentation](https://docs.sublimetext.io/reference/key_bindings.html).

### Context menu

To disable or customize the context menu:

- Create a `ColorConverter` directory in the `Packages` directory (which you can find via the Settings > Browse Packages menu item).
- In that directory place a `Context.sublime-menu` file.
  For its contents you can use this package's [original menu](https://github.com/braver/ColorConverter/blob/main/Context.sublime-menu).

This copy of the context menu now overrides the original one. You can for instance remove the formats you don't use. Or remove everything, leaving just `[]`, to remove and disable the menu completely.

See also the [official documentation](https://www.sublimetext.com/docs/packages.html#overriding-files-from-a-zipped-package) on this topic.

## Credits

This package is built on the [coloraide](https://facelessuser.github.io/coloraide/) library by [Isaac Muse](https://github.com/facelessuser).

It's inspired by the work of [@zhouyuexie](https://github.com/zhouyuexie/ColorConvert), [@TheDutchCoder](https://github.com/TheDutchCoder/ColorConvert), [@atadams](https://github.com/atadams/Hex-to-HSL-Color), [@vitorleal](https://github.com/vitorleal/hex-2-rgb), and [@aroscoe](https://github.com/aroscoe/Hex-to-RGBA), whose color converter packages preceded this one.

## Buy me a coffee 

☕️👌🏻

If you enjoy this package, feel free to make a little [donation via PayPal](https://paypal.me/koenlageveen) towards the coffee that keeps this project running. It's much appreciated!
