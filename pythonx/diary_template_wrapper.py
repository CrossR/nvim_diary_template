from nvim_diary_template import DiaryTemplatePlugin as _DiaryTemplate
import vim

_obj: _DiaryTemplate = _DiaryTemplate(vim)


def make_diary_command():
    return _obj.make_diary_command()

def upload_to_calendar():
    return _obj.upload_to_calendar()

def grab_from_calendar():
    return _obj.grab_from_calendar()

def update_calendar():
    return _obj.update_calendar()

def sort_calendar():
    return _obj.sort_calendar()

def get_issues():
    return _obj.get_issues()

def sort_issues():
    return _obj.sort_issues()

def insert_issue():
    return _obj.insert_issue()

def insert_comment():
    return _obj.insert_comment()

def edit_comment():
    return _obj.edit_comment()

def edit_issue():
    return _obj.edit_issue()

def upload_new_issues():
    return _obj.upload_new_issues()

def upload_edited_issues():
    return _obj.upload_edited_issues()

def toggle_completion():
    return _obj.toggle_completion()

def upload_issue_completions():
    return _obj.upload_issue_completions()

def upload_all_issues():
    return _obj.upload_all_issues()

def swap_group_sorting():
    return _obj.swap_group_sorting()
