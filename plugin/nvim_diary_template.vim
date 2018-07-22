" Initalise some options

let g:nvim_diary_template#active = get(g:, 'nvim_diary_template#active', v:true)
let g:nvim_diary_template#notes_path = get(g:, 'nvim_diary_template#notes_path', '') 
let g:nvim_diary_template#config_path = get(g:, 'nvim_diary_template#config_path', g:nvim_diary_template#notes_path . '/config')

augroup nvim_diary_template_keybinds
    autocmd!
    autocmd FileType vimwiki nnoremap <buffer> <leader>wie :DiaryIssueEdit<CR>
    autocmd FileType vimwiki nnoremap <buffer> <leader>wic :DiaryIssueComment<CR>
    autocmd FileType vimwiki nnoremap <buffer> <leader>wii :DiaryIssue<CR>
    autocmd FileType vimwiki setlocal foldtext=DiaryFoldText()
    autocmd FileType vimwiki setlocal foldmethod=expr
    autocmd FileType vimwiki setlocal foldexpr=GetDiaryFold(v:lnum)
augroup END

function! DiaryFoldText()

  let l:issue_start = '^- \[[ X]\] Issue {\d}:'
  let l:comment_start = '^    - Comment {\d}:'
  let l:start_line = getline(v:foldstart)

  if l:start_line =~? l:issue_start
    let l:issue_topic_line = getline(v:foldstart + 1)
    let l:issue_title_regex = '^    - Title: '
    let l:issue_topic = substitute(l:issue_topic_line, l:issue_title_regex, '', "")

    let l:issue_number = matchstr(l:start_line, '\d')

    return "-- Issue {" . l:issue_number . "} - Title: " . l:issue_topic . "."
  elseif l:start_line =~? l:comment_start
    let l:start_of_comment = getline(v:foldstart + 1)
    let l:padding = '        '
    let l:comment_brief = substitute(l:start_of_comment, l:padding, '', "")

    let l:comment_number = matchstr(l:start_line, '\d')

    return '    - Comment {' . l:comment_number . "}: " . l:comment_brief . "."
  else
    return l:start_line

endfunction

function! GetDiaryFold(lnum)
  let l:line = getline(a:lnum)
  let l:indent_level = IndentLevel(a:lnum)

  let l:issue_start = '^- \[[ X]\] Issue {\d}:'
  let l:comment_start = '^    - Comment {\d}:'
  let l:heading = '^# '

  " If its a heading, it shouldn't be folded.
  if l:line =~? l:heading
    return '0'
  endif

  " If its the start of an issue, fold to level 1.
  if l:line =~? l:issue_start
    return '>1'
  endif

  " If its the start of a comment, fold to level 2.
  " This means it will be folded into the issue fold.
  if l:line =~? l:comment_start
    return '>2'
  endif

  " If we are between two comments, we should set the fold level to 1 to
  " close the previous comment fold.
  if getline(a:lnum + 1) =~? l:comment_start && indent_level == 0 && foldlevel(a:lnum - 1) != 1
    return '1'
  endif

  " If its between issues, close the current issue fold so the issues are seperate.
  if getline(a:lnum + 1) =~? l:issue_start && indent_level == 0 && foldlevel(a:lnum - 2) == 2
    return '1'
  endif

  " If its the end of the issues section, close the issue fold.
  if getline(a:lnum + 1) =~? l:heading && indent_level == 0 && foldlevel(a:lnum - 2) == 2
    return '>1'
  endif

  " If we've gotten here.... return the existing level.
  return '='
endfunction

function! IndentLevel(lnum)
    return indent(a:lnum) / &shiftwidth
endfunction
