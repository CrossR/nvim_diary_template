" Vim wrappers via nvim-yarp.

if has('nvim')
  finish
endif

let s:diary_plugin = yarp#py3('diary_template_wrapper')

function! DiaryInit()
    return s:diary_plugin.call('init_diary')
endfunc

function! DiaryOptionsInit()
    return s:diary_plugin.call('check_options')
endfunc

function! DiaryMake()
    return s:diary_plugin.call('make_diary_command')
endfunc

function! DiaryUploadCalendar()
    return s:diary_plugin.call('upload_to_calendar')
endfunc

function! DiaryGetCalendar()
    return s:diary_plugin.call('grab_from_calendar')
endfunc

function! DiaryUploadCalendar()
    return s:diary_plugin.call('update_calendar')
endfunc

function! DiarySortCalendar()
    return s:diary_plugin.call('sort_calendar')
endfunc

function! DiaryGetIssues()
    return s:diary_plugin.call('get_issues')
endfunc

function! DiarySortIssues()
    return s:diary_plugin.call('sort_issues')
endfunc

function! DiaryInsertIssue()
    return s:diary_plugin.call('insert_issue')
endfunc

function! DiaryInsertComment()
    return s:diary_plugin.call('insert_comment')
endfunc

function! DiaryEditComment()
    return s:diary_plugin.call('edit_comment')
endfunc

function! DiaryEditIssue()
    return s:diary_plugin.call('edit_issue')
endfunc

function! DiaryUploadNew()
    return s:diary_plugin.call('upload_new_issues')
endfunc

function! DiaryUploadEdits()
    return s:diary_plugin.call('upload_edited_issues')
endfunc

function! DiaryCompleteIssue()
    return s:diary_plugin.call('toggle_completion')
endfunc

function! DiaryUploadCompletion()
    return s:diary_plugin.call('upload_issue_completions')
endfunc

function! DiaryUploadIssues()
    return s:diary_plugin.call('upload_all_issues')
endfunc

function! DiarySwapGroupSorting()
    return s:diary_plugin.call('swap_group_sorting')
endfunc
