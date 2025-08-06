from coloraide import Color
import sublime
import sublime_plugin


class ColorConvert(sublime_plugin.TextCommand):

    def run(self, edit, format='rgb'):
        settings = sublime.load_settings('ColorConvertor.sublime-settings')
        c = Color("red")

        if format == 'name':
            print(c.to_string(names=True))
            return

        want_hex = format == 'hex'
        print(c.to_string(
            comma=settings.get('commas'),
            upper=settings.get('hex_case') == "upper" and want_hex,
            compress=settings.get('hex_short') and want_hex,
            hex=want_hex,
        ))
