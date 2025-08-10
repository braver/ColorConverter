from coloraide import Color
from decimal import Decimal
import re
import sublime
import sublime_plugin


# hex color, but without the first #
HEX_COLOR_RE = re.compile(r'([a-f0-9]{6}|[a-f0-9]{3})', re.IGNORECASE)
# relatively naive color function search
# coloraide doesn't understand the more complex "from gree" notations anyway
RGB_COLOR_RE = re.compile(r'(rgba?|color)\([^)]+\)', re.IGNORECASE)
HLS_RE = re.compile(r'hsla?\(((?P<angle>[0-9.]+)(?:deg)?|(?P<none>none)),?\s*(?P<sat>[0-9.]+)%?,?\s*(?P<light>[0-9.]+)%?\s*(\/\s*(?P<opperc>[0-9.]+)%?|,?\s*(?P<opdec>[0-9.]+))?\)', re.IGNORECASE)  # noqa: E501


def find_point(view, event):
    if not view:
        return None

    if event is not None:
        return event['text_point']
    else:
        selections = view.sel()
        for selection in selections:
            return selection.a

    return None


def get_search_region(view, region):
    """ From the cursor widen 50 points in both directions
        to search for a color.
    """
    point = region.begin()
    visible = view.visible_region()
    start = point - 50
    end = point + 50
    if start < visible.begin():
        start = visible.begin()
    if end > visible.end():
        end = visible.end()

    return sublime.Region(start, end)


def parse_hsl(match):
    """ With the regex split out the parts of the h, s, l, a. """
    hue = 0
    if not match.group('none'):
        hue = Decimal(match.group('angle'))
    sat = Decimal(match.group('sat') or 0) / 100
    light = Decimal(match.group('light') or 0) / 100

    opacity = 1
    if match.group('opdec'):
        opacity = Decimal(match.group('opdec'))
    elif match.group('opperc'):
        opacity = Decimal(match.group('opperc')) / 100

    # create the color object and convert to srgb
    return Color('hsl', [hue, sat, light], opacity).convert('srgb')


def find_color_func_at_region(view, region):
    search_region = get_search_region(view, region)
    content = view.substr(search_region)

    relative_cursor_pos = region.a - search_region.a

    for m in RGB_COLOR_RE.finditer(content):
        match_start, match_end = m.span()
        if match_start <= relative_cursor_pos <= match_end:
            match_region = sublime.Region(search_region.a + m.start(0), search_region.a + m.end(0))
            return (match_region, Color(extract_word(view, match_region)))

    for m in HLS_RE.finditer(content):
        match_start, match_end = m.span()
        if match_start <= relative_cursor_pos <= match_end:
            match_region = sublime.Region(search_region.a + m.start(0), search_region.a + m.end(0))
            return (match_region, parse_hsl(m))

    return None


def extract_word(view, region):
    return view.substr(region).lower()


def get_cursor_color(view, region):
    """ Find the color string around the given region,
        then return the exact region of that string, and the string itself
    """

    # first try to find rgb() like color function colors
    rgb = find_color_func_at_region(view, region)
    if rgb is not None:
        return rgb

    # otherwise try to use the word at the point
    word_region = view.word(region)

    word = extract_word(view, word_region)
    # If the word looks like a hex and is preceded by a #, include it in the word
    if HEX_COLOR_RE.match(word):
        if region.a > 0 and view.substr(sublime.Region(word_region.a - 1, word_region.a)) == '#':
            word_region = sublime.Region(word_region.a - 1, word_region.b)

    return (word_region, Color(extract_word(view, word_region)))


def convert(color, value):
    """ Convert a Color to a target format value """
    settings = sublime.load_settings('ColorConvertor.sublime-settings')

    if value == 'name':
        # caveat: if the color has no name, it will fall back to rgb() probably
        return color.to_string(names=True)

    if value == 'color':
        return color.to_string(
            color=True,
            comma=settings.get('commas')
        )

    if value == 'rgb':
        return color.to_string(
            comma=settings.get('commas'),
        )

    if value == 'hex':
        return color.to_string(
            hex=True,
            upper=settings.get('hex_case') == 'upper',
            compress=settings.get('hex_short'),
        )

    if value == 'hsl':
        color.convert('hsl', in_place=True)
        args = dict(
            percent=True,
            comma=settings.get('commas'))
        if settings.get('hsl_round'):
            args['precision'] = [0, 0, 0, 3]
        return color.to_string(**args)

    if value == 'lab':
        color.convert('lab', in_place=True)
        return color.to_string(
            comma=settings.get('commas'),
            percent=settings.get('%')
        )


class ColorConvert(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.view = view

    def run(self, edit, value='rgb'):
        sels = self.view.sel()
        for sel in sels:
            try:
                source = get_cursor_color(self.view, sel)
                color = source[1]
                result = convert(color, value)
                self.view.replace(edit, source[0], result)
            except Exception:
                sublime.status_message('That does not seem to be a color')


class ContextConvert(sublime_plugin.TextCommand):
    def want_event(self):
        return True

    def is_visible(self, event=None):
        view = self.view
        pnt = find_point(view, event)
        if not pnt:
            return False

        return True

    def run(self, edit, value, event=None):
        view = self.view
        pnt = find_point(view, event)

        if not pnt:
            view.window().status_message('No selection')
            return

        try:
            source = get_cursor_color(self.view, sublime.Region(pnt, pnt))
            color = source[1]
            result = convert(color, value)
            if value == 'name' and result.startswith('rgb'):
                # coloraide converts to rgb() if there is no name
                sublime.status_message('This color does not have a name')
                return
            self.view.replace(edit, source[0], result)
        except Exception:
            sublime.status_message('That does not seem to be a color')
