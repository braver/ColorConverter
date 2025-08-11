from coloraide import Color
from decimal import Decimal
import re
import sublime
import sublime_plugin


# hex color, but without the first #
HEX_COLOR_RE = r'([a-f0-9]{6}|[a-f0-9]{3})'
# relatively naive color function search
# coloraide doesn't understand the more complex "from green" notations anyway
RGB_COLOR_RE = r'(rgba?|hsla?|lab|color)\([^)]+\)'
HLS_RE = re.compile(r'hsla?\(((?P<angle>[0-9.]+)(?:deg)?|(?P<none>none)),?\s*(?P<sat>[0-9.]+)%?,?\s*(?P<light>[0-9.]+)%?\s*(\/\s*(?P<opperc>[0-9.]+)%?|,?\s*(?P<opdec>[0-9.]+))?\)', re.IGNORECASE)  # noqa: E501


def get_search_region(view, pnt):
    """ From the cursor widen 50 points in both directions
        to search for a color.
    """
    start = max(pnt - 50, 0)
    end = min(pnt + 50, view.size())
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


def find_color_func_at_point(view, pnt):
    search_region = get_search_region(view, pnt)
    content = view.substr(search_region)

    relative_cursor_pos = pnt - search_region.a

    for m in re.compile(RGB_COLOR_RE, re.IGNORECASE).finditer(content):
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


def get_cursor_color(view, pnt):
    """ Find the color string around the given point,
        then return the exact region of that string, and the string itself
    """

    # first try to find rgb() like color function colors
    rgb = find_color_func_at_point(view, pnt)
    if rgb is not None:
        return rgb

    # otherwise try to use the word at the point
    word_region = view.word(pnt)

    word = extract_word(view, word_region)

    # if all we have is #, move the selection to the next character
    # because in #abc # and abc are 2 separate words
    if word.strip() == '#':
        word_region = view.word(pnt + 1)
        word = extract_word(view, word_region)

    # if the word looks like a hex and is preceded by a #, include it in the word
    if re.compile(HEX_COLOR_RE, re.IGNORECASE).match(word):
        if pnt > 0 and view.substr(sublime.Region(word_region.begin() - 1, word_region.begin())) == '#':
            word_region = sublime.Region(word_region.begin() - 1, word_region.end())

    return (word_region, Color(extract_word(view, word_region)))


def convert(color, format):
    """ Convert a Color to a target format """
    settings = sublime.load_settings('ColorConvertor.sublime-settings')

    common_args = dict(
        comma=settings.get('commas'),
        percent=settings.get('%')
    )

    if settings.get('round'):
        common_args['precision'] = [0, 0, 0, 3]

    if format == 'name':
        # caveat: if the color has no name, it will fall back to rgb() probably
        return color.to_string(names=True)

    if format == 'hex':
        return color.to_string(
            hex=True,
            upper=settings.get('hex_case') == 'upper',
            compress=settings.get('hex_short'),
        )

    if format == 'color':
        if not settings.get('%'):
            del common_args['precision']
        return color.to_string(
            color=True,
            **common_args
        )

    if format == 'rgb':
        common_args['percent'] = settings.get('%_rgb')
        return color.to_string(**common_args)

    if format == 'hsl':
        color.convert('hsl', in_place=True)
        return color.to_string(**common_args)

    if format == 'lab':
        color.convert('lab', in_place=True)
        return color.to_string(**common_args)


class ColorConvert(sublime_plugin.TextCommand):
    def run(self, edit, format='rgb'):
        selections = self.view.sel()
        for sel in selections:
            try:
                source = get_cursor_color(self.view, sel.begin())
                color = source[1]
                result = convert(color, format)
                self.view.replace(edit, source[0], result)
            except Exception:
                sublime.status_message('That does not seem to be a color')


class ColorConvertAll(sublime_plugin.TextCommand):
    def convert_region(self, edit, region, format):
        try:
            source = get_cursor_color(self.view, region.begin())
            color = source[1]
            result = convert(color, format)
            self.view.replace(edit, source[0], result)
        except Exception:
            sublime.status_message('That does not seem to be a color')

    def run(self, edit, format='rgb'):
        find_args = dict(flags=sublime.FindFlags.IGNORECASE)

        selections = self.view.sel()
        if selections[0].size() >= 1:
            find_args['within'] = selections[0]

        hexes = self.view.find_all('#' + HEX_COLOR_RE, **find_args)
        for region in reversed(hexes):
            self.convert_region(edit, region, format)


        rgbs = self.view.find_all(RGB_COLOR_RE, **find_args)
        for region in reversed(rgbs):
            self.convert_region(edit, region, value)


class ContextConvert(sublime_plugin.TextCommand):
    def find_point(self, event):
        """ Find the clicked point for the context menu """
        if not self.view:
            return None

        if event is not None:
            return event['text_point']
        else:
            selections = self.view.sel()
            for selection in selections:
                return selection.a

        return None

    def want_event(self):
        return True

    def is_visible(self, event=None):
        pnt = self.find_point(event)
        if not pnt:
            return False

        return True

    def run(self, edit, format, event=None):
        pnt = self.find_point(event)
        if not pnt:
            self.view.window().status_message('No selection')
            return

        try:
            source = get_cursor_color(self.view, pnt)
            color = source[1]
            result = convert(color, format)
            if format == 'name' and result.startswith('rgb'):
                # coloraide converts to rgb() if there is no name
                sublime.status_message('This color does not have a name')
                return
            self.view.replace(edit, source[0], result)
        except Exception:
            sublime.status_message('That does not seem to be a color')
