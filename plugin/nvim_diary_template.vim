" Initalise some options

let g:nvim_diary_template#active = get(g:, 'nvim_diary_template#active', v:true)
let g:nvim_diary_template#notes_path = get(g:, 'nvim_diary_template#notes_path', '')
let g:nvim_diary_template#config_path = get(g:, 'nvim_diary_template#config_path', g:nvim_diary_template#notes_path . '/config')

augroup nvim_diary_template_keybinds
    autocmd!
    " Edit existing issue/comments binds
    autocmd FileType vimwiki nnoremap <buffer> <leader>wec :DiaryEditComment<CR>
    autocmd FileType vimwiki nnoremap <buffer> <leader>wei :DiaryEditIssue<CR>
    autocmd FileType vimwiki nnoremap <buffer> <leader>wci :DiaryCompleteIssue<CR>

    " Insert new issue/comments binds
    autocmd FileType vimwiki nnoremap <buffer> <leader>wic :DiaryInsertComment<CR>
    autocmd FileType vimwiki nnoremap <buffer> <leader>wii :DiaryInsertIssue<CR>

    " Upload edited/new issues and comments
    autocmd FileType vimwiki nnoremap <buffer> <leader>wun :DiaryUploadNew<CR>
    autocmd FileType vimwiki nnoremap <buffer> <leader>wue :DiaryUploadEdits<CR>
    autocmd FileType vimwiki nnoremap <buffer> <leader>wuc :DiaryUploadCompletion<CR>

    autocmd FileType vimwiki setlocal foldtext=DiaryFoldText()
    autocmd FileType vimwiki setlocal foldmethod=expr
    autocmd FileType vimwiki setlocal foldexpr=GetDiaryFold(v:lnum)
augroup END

let s:issue_start = '^### \[[ X]\] Issue {\d\{1,}}:'
let s:comment_start = '^#### Comment {\d\{1,}} - '
let s:date_time_regex = '\d\{4}-\d\{2}-\d\{2} \d\{2}:\d\{2}'
let s:label = '+label:\a\{1,}'

function! DiaryFoldText()

  let l:start_line = getline(v:foldstart)

  " If we are folding the top of an issue, include the title for context.
  " If we are folding a comment, instead include the first line and
  if l:start_line =~? s:issue_start
    let l:issue_topic_line = getline(v:foldstart + 2)
    let l:issue_title_regex = '^#### Title: '
    let l:issue_topic = substitute(l:issue_topic_line, l:issue_title_regex, '', "")

    let l:labels = filter(map(split(l:start_line), 'matchstr(v:val, s:label)'), {idx, val -> val != ''})

    let l:issue_number = matchstr(l:start_line, '\d\{1,}')
    let l:issue_status = matchstr(l:start_line, '\[X\]')

    let l:completed_status = '[ ]'

    if l:issue_status != ""
      let l:completed_status = '[X]'
    endif

    " Add the completion status, then the issue number, then title.
    " Finally append each label
    let l:issue_fold_text = "### " . l:completed_status
    let l:issue_fold_text = l:issue_fold_text . " Issue {" . l:issue_number . "} - Title: "
    let l:issue_fold_text = l:issue_fold_text . l:issue_topic . "."

    if len(l:labels) != 0
      for label in l:labels
        let l:issue_fold_text = l:issue_fold_text . " " . label
      endfor
    endif

    return l:issue_fold_text

  elseif l:start_line =~? s:comment_start
    let l:start_of_comment = getline(v:foldstart + 1)
    let l:padding = '        '
    let l:comment_brief = substitute(l:start_of_comment, l:padding, '', "")

    let l:comment_number = matchstr(l:start_line, '\d\{1,}')
    let l:comment_date_time = matchstr(l:start_line, s:date_time_regex)

    return '#### Comment {' . l:comment_number . "} - " . l:comment_date_time . ": " . l:comment_brief . "."
  else
    return l:start_line

endfunction

function! GetDiaryFold(lnum)
  let l:line = getline(a:lnum)
  let l:indent_level = IndentLevel(a:lnum)

  let l:heading = '^## '

  " If its a top level heading, it shouldn't be folded.
  if l:line =~? l:heading
    return '0'
  endif

  " If its next to a top level heading, it shouldn't be folded to maintain the new line.
  if getline(a:lnum + 1) =~? l:heading
    return '0'
  endif

  " If its the start of an issue, fold to level 1.
  if l:line =~? s:issue_start
    return '>1'
  endif

  " If its the start of a comment, fold to level 2.
  " This means it will be folded into the issue fold.
  if l:line =~? s:comment_start
    return '>2'
  endif

  " If we are between two comments, we should set the fold level to 1 to
  " close the previous comment fold.
  if getline(a:lnum + 1) =~? s:comment_start && indent_level == 0 && foldlevel(a:lnum - 1) != 1
    return '1'
  endif

  " If its between issues, close the current issue fold so the issues are seperate.
  if getline(a:lnum + 1) =~? s:issue_start && indent_level == 0 && foldlevel(a:lnum - 2) == 2
    return '0'
  endif

  " If we've gotten here.... return the existing level.
  return '='
endfunction

function! IndentLevel(lnum)
    return indent(a:lnum) / &shiftwidth
endfunction
