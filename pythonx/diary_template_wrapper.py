from nvim_diary_template import DiaryTemplatePlugin as _DiaryTemplate
import vim

_obj: _DiaryTemplate = _DiaryTemplate(vim)


def init_diary() -> None:
    return _obj.init_diary()


def check_options() -> None:
    return _obj.check_options()


def make_diary_command() -> None:
    return _obj.make_diary_command()


def upload_to_calendar() -> None:
    return _obj.upload_to_calendar()


def grab_from_calendar() -> None:
    return _obj.grab_from_calendar()


def update_calendar() -> None:
    return _obj.update_calendar()


def sort_calendar() -> None:
    return _obj.sort_calendar()


def get_issues() -> None:
    return _obj.get_issues()


def sort_issues() -> None:
    return _obj.sort_issues()


def insert_issue() -> None:
    return _obj.insert_issue()


def insert_comment() -> None:
    return _obj.insert_comment()


def edit_comment() -> None:
    return _obj.edit_comment()


def edit_issue() -> None:
    return _obj.edit_issue()


def upload_new_issues() -> None:
    return _obj.upload_new_issues()


def upload_edited_issues() -> None:
    return _obj.upload_edited_issues()


def toggle_completion() -> None:
    return _obj.toggle_completion()


def upload_issue_completions() -> None:
    return _obj.upload_issue_completions()


def upload_all_issues() -> None:
    return _obj.upload_all_issues()


def swap_group_sorting() -> None:
    return _obj.swap_group_sorting()
