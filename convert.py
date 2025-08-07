from coloraide import Color
import re
import sublime
import sublime_plugin


# hex color, but without the first #
HEX_COLOR_RE = re.compile(r'([a-f0-9]{6}|[a-f0-9]{3})', re.IGNORECASE)

RGB_COLOR_RE = re.compile(
    r'rgb\s*\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\)',
    re.IGNORECASE
)

# maybe? (rgba?|hsla?)\([^)]+\)
""" test set:
rgb(255 255 255)
rgb(255 255 255 / 50%)
rgba(0 255 255)
rgb(0, 255, 255)
rgb(0, 255, 255, 50%)
hsl(120deg 75% 25%)
hsl(120 75 25)
hsl(120deg 75% 25% / 60%)
hsl(none 75% 25%)
hsl(from green h s l / 0.5)
hsl(from #0000FF h s calc(l + 20))
hsl(from rgb(200 0 0) calc(h + 30) s calc(l + 30))
hsla(120deg 75% 25% / 60%)
hsl(120, 75%, 25%)
hsl(120deg, 75%, 25%, 0.8)
"""


def find_rgb_color_at_region(view, region):
    # Expand to a reasonable range around the cursor (e.g., line, or +/–30 chars)
    line_region = view.line(region)
    line_text = view.substr(line_region)

    # Adjust the region's offset relative to the line
    offset = region.a - line_region.a

    # Search all rgb() in the line, and see if the cursor is inside one
    for match in RGB_COLOR_RE.finditer(line_text):
        match_start, match_end = match.span()
        if match_start <= offset <= match_end:
            # Found the rgb() the cursor is inside
            rgb_region = sublime.Region(line_region.a + match_start, line_region.a + match_end)
            rgb_string = view.substr(rgb_region)
            return rgb_region, rgb_string
    return None, None


def extract_word(view, region):
    return view.substr(region).lower()


def get_cursor_color(view, region):
    """ Find the color string around the given region,
        then return the exact region of that string, and the string itself
    """

    # get_cursor_color from ColorHints takes a large region (+/- 50) around the cursor
    # then applies a complex regex that will actually look for all kinds of patterns
    # ... let's try for something more elegant, like handling one pattern at a time

    # First handle colors that are words: names and hex
    # Get the word under the cursor
    word_region = view.word(region)

    word = extract_word(view, word_region)
    # If the word looks like a hex and is preceded by a #, include it in the word
    if HEX_COLOR_RE.match(word):
        if region.a > 0 and view.substr(sublime.Region(word_region.a - 1, word_region.a)) == '#':
            word_region = sublime.Region(word_region.a - 1, word_region.b)

    return (word_region, extract_word(view, word_region))


def convert(color, format):
    """ Convert a Color to a target format """
    settings = sublime.load_settings('ColorConvertor.sublime-settings')

    if format == 'name':
        # caveat: if the color has no name, it will fall back to rgb() probably
        return color.to_string(names=True)

    if format == 'rgb':
        return color.to_string(
            comma=settings.get('commas'),
            color=settings.get('color()')
        )

    if format == 'rgba':
        return color.to_string(
            alpha=True,
            comma=settings.get('commas'),
            color=settings.get('color()')
        )

    if format == 'hex':
        return color.to_string(
            hex=True,
            upper=settings.get('hex_case') == 'upper',
            compress=settings.get('hex_short'),
        )

    if format == 'hexa':
        return color.to_string(
            alpha=True,
            hex=True,
            upper=settings.get('hex_case') == 'upper',
            compress=settings.get('hex_short'),
        )

    common_args = dict(
        comma=settings.get('commas'),
        percent=settings.get('%'),
        color=settings.get('color()')
    )

    if format == 'hsl':
        color.convert('hsl', in_place=True)
        return color.to_string(**common_args)

    if format == 'hsla':
        color.convert('hsl', in_place=True)
        return color.to_string(alpha=True, **common_args)

    if format == 'lab':
        color.convert('lab', in_place=True)
        return color.to_string(**common_args)

    if format == 'laba':
        color.convert('lab', in_place=True)
        return color.to_string(alpha=True, **common_args)


class ColorConvert(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.view = view

    def run(self, edit, format='rgb'):
        sels = self.view.sel()
        for sel in sels:
            source = get_cursor_color(self.view, sel)

            try:
                color = Color(source[1])
                result = convert(color, format)
                self.view.replace(edit, source[0], result)
            except Exception:
                sublime.status_message('That does not seem to be a color')
