# ColorConvertor for Sublime Text

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

- Via the command palette (look for "ColorConvertor: Convert to ...").
- Via the context menu.
- You can set up a keyboard shortcut.

Select or put your cursor on a color, then select the format to convert to.

## How to customize

### Key bindings

To set up a keyboard shortcut, open the ColorConvertor Key Bindings preferences,
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

- Create a `ColorConvertor` directory in the `Packages` directory (which you can find via the Settings > Browse Packages menu item).
- In that directory place a `Context.sublime-menu` file.
  For its contents you can use this package's [original menu](https://github.com/braver/ColorConvertor/blob/main/Context.sublime-menu).

This copy of the context menu now overrides the original one. You can for instance remove the formats you don't use. Or remove everything, leaving just `[]`, to remove and disable the menu completely.

See also the [official documentation](https://www.sublimetext.com/docs/packages.html#overriding-files-from-a-zipped-package) on this topic.

## Credits

This package is built on the [coloraide](https://facelessuser.github.io/coloraide/) library by [Isaac Muse](https://github.com/facelessuser).


## Replace all the colors!

This is probably a common feature request.
I haven't found a reliable way of iterating over larger ranges of a buffer.
As soon as you start making changes the positions of each color in the document start to shift.
You need to find a color, convert it, move to the end of the new color's region, find the next color, rinse repeat. So a single command for this is not currently planned.

However, depending on your situation, you can use Sublime's Find > Quick Find All menu item, or the Find All option in the Find panel. This way you can easily select all colors you want to convert, and then use the command palette to convert to your format of choice.
