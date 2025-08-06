from coloraide import Color
import sublime
import sublime_plugin


def get_cursor_color(view, region):
    point = region.begin()
    visible = view.visible_region()
    start = point - 50
    end = point + 50
    if start < visible.begin():
        start = visible.begin()
    if end > visible.end():
        end = visible.end()
    bfr = view.substr(sublime.Region(start, end))
    ref = point - start
    print(ref, bfr)
    # for m in util.COLOR_RE.finditer(bfr):
    #     if ref >= m.start(0) and ref < m.end(0):
    #         color, alpha, alpha_dec = util.translate_color(m, argb)
    #         break
    # return color, alpha, alpha_dec


class ColorConvert(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.view = view

    def run(self, edit, format='rgb'):
        settings = sublime.load_settings('ColorConvertor.sublime-settings')
        c = Color("rebeccapurple")

        sels = self.view.sel()
        for sel in sels:
            get_cursor_color(self.view, sel)

        print('---------')
        print('output:')
        if format == 'name':
            print(c.to_string(names=True))
            return

        if format == 'rgb':
            print(c.to_string(
                comma=settings.get('commas'),
                color=settings.get('color()')
            ))
            return

        if format == 'rgba':
            print(c.to_string(
                alpha=True,
                comma=settings.get('commas'),
                color=settings.get('color()')
            ))
            return

        if format == 'hex':
            print(c.to_string(
                hex=True,
                upper=settings.get('hex_case') == 'upper',
                compress=settings.get('hex_short'),
            ))
            return

        if format == 'hexa':
            print(c.to_string(
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
            c.convert('hsl', in_place=True)
            print(c.to_string(**common_args))
            return

        if format == 'hsla':
            c.convert('hsl', in_place=True)
            print(c.to_string(alpha=True, **common_args))
            return

        if format == 'lab':
            c.convert('lab', in_place=True)
            print(c.to_string(**common_args))
            return

        if format == 'laba':
            c.convert('lab', in_place=True)
            print(c.to_string(alpha=True, **common_args))
            return
