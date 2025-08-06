from coloraide import Color
import sublime
import sublime_plugin


class ColorConvert(sublime_plugin.TextCommand):

    def run(self, edit, format='rgb'):
        settings = sublime.load_settings('ColorConvertor.sublime-settings')
        c = Color("rebeccapurple")

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
