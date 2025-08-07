from coloraide import Color
import re
import sublime
import sublime_plugin


# without the first #
HEX_COLOR_RE = re.compile(r'([a-f0-9]{6}|[a-f0-9]{3})')


def extract_word(view, region):
    return view.substr(region).lower()


def get_cursor_color(view, region):
    # get_cursor_color from ColorHints takes a large region (+/- 50) around the cursor
    # then applies a complex regex that will actually look for all kinds of patterns
    # ... let's try for something more elegant

    # First handle colors that are words: names and hex
    # Get the word under the cursor
    word_region = view.word(region)

    word = extract_word(view, word_region)
    # If the word looks like a hex and is preceded by a #, include it in the word
    if HEX_COLOR_RE.match(word):
        if region.a > 0 and view.substr(sublime.Region(word_region.a - 1, word_region.a)) == '#':
            word_region = sublime.Region(word_region.a - 1, word_region.b)

    return extract_word(view, word_region)


def convert(color, format):
    """ Convert a Color to a target format """
    settings = sublime.load_settings('ColorConvertor.sublime-settings')
    print('---------')
    print('output:')
    if format == 'name':
        print(color.to_string(names=True))
        return

    if format == 'rgb':
        print(color.to_string(
            comma=settings.get('commas'),
            color=settings.get('color()')
        ))
        return

    if format == 'rgba':
        print(color.to_string(
            alpha=True,
            comma=settings.get('commas'),
            color=settings.get('color()')
        ))
        return

    if format == 'hex':
        print(color.to_string(
            hex=True,
            upper=settings.get('hex_case') == 'upper',
            compress=settings.get('hex_short'),
        ))
        return

    if format == 'hexa':
        print(color.to_string(
            alpha=True,
            hex=True,
            upper=settings.get('hex_case') == 'upper',
            compress=settings.get('hex_short'),
        ))
        return

    common_args = dict(
        comma=settings.get('commas'),
        percent=settings.get('%'),
        color=settings.get('color()')
    )

    if format == 'hsl':
        color.convert('hsl', in_place=True)
        print(color.to_string(**common_args))
        return

    if format == 'hsla':
        color.convert('hsl', in_place=True)
        print(color.to_string(alpha=True, **common_args))
        return

    if format == 'lab':
        color.convert('lab', in_place=True)
        print(color.to_string(**common_args))
        return

    if format == 'laba':
        color.convert('lab', in_place=True)
        print(color.to_string(alpha=True, **common_args))
        return


class ColorConvert(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.view = view

    def run(self, edit, format='rgb'):
        sels = self.view.sel()
        for sel in sels:
            source = get_cursor_color(self.view, sel)
            print('source:', source)
            try:
                color = Color(source)
                convert(color, format)
            except Exception:
                sublime.status_message('This is not a color')
