from coloraide import Color
import re
import sublime
import sublime_plugin


# hex color, but without the first #
HEX_COLOR_RE = re.compile(r'([a-f0-9]{6}|[a-f0-9]{3})', re.IGNORECASE)
# relatively naive color function search
# coloraide doesn't understand the more complex "from gree" notations anyway
RGB_COLOR_RE = re.compile(r'(rgba?|hsla?|color)\([^)]+\)', re.IGNORECASE)


def find_rgb_color_at_region(view, region):
    # from the cursor widen 50 points in both directions to search for a color
    point = region.begin()
    visible = view.visible_region()
    start = point - 50
    end = point + 50
    if start < visible.begin():
        start = visible.begin()
    if end > visible.end():
        end = visible.end()

    search_region = sublime.Region(start, end)
    content = view.substr(search_region)

    relative_cursor_pos = region.a - search_region.a

    for m in RGB_COLOR_RE.finditer(content):
        match_start, match_end = m.span()
        if match_start <= relative_cursor_pos <= match_end:
            rgb_region = sublime.Region(search_region.a + m.start(0), search_region.a + m.end(0))
            return (rgb_region, extract_word(view, rgb_region))
    return None


def extract_word(view, region):
    return view.substr(region).lower()


def get_cursor_color(view, region):
    """ Find the color string around the given region,
        then return the exact region of that string, and the string itself
    """

    # first try to find rgb() like color function colors
    rgb = find_rgb_color_at_region(view, region)
    if rgb is not None:
        print(rgb)
        return rgb

    # otherwise try to use the word at the point
    print('word mode')
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

    if format == 'color':
        return color.to_string(
            color=True,
            comma=settings.get('commas')
        )

    if format == 'colora':
        return color.to_string(
            alpha=True,
            color=True,
            comma=settings.get('commas')
        )

    if format == 'rgb':
        return color.to_string(
            comma=settings.get('commas'),
        )

    if format == 'rgba':
        return color.to_string(
            alpha=True,
            comma=settings.get('commas')
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
        percent=settings.get('%')
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
                # if result starts with hsl/hsla we need to post-process
                # the percentages need to be converted to floats
                print(result)
                self.view.replace(edit, source[0], result)
            except Exception:
                sublime.status_message('That does not seem to be a color')
