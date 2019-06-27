from nvim_diary_template import DiaryTemplatePlugin as _DiaryTemplate
import vim

_obj: _DiaryTemplate = _DiaryTemplate(vim)


def diary_echo(*args):
    return _obj.diary_echo(args)

def diary_make(*args):
    return _obj.make_diary_command()