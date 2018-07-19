" Initalise some options

let g:nvim_diary_template#active = get(g:, 'nvim_diary_template#active', v:true)
let g:nvim_diary_template#notes_path = get(g:, 'nvim_diary_template#notes_path', '') 
let g:nvim_diary_template#config_path = get(g:, 'nvim_diary_template#config_path', g:nvim_diary_template#notes_path . '/config')

augroup nvim_diary_template_keybinds
    autocmd!
    autocmd FileType vimwiki nnoremap <buffer> <leader>wie :DiaryIssueEdit<CR>
    autocmd FileType vimwiki nnoremap <buffer> <leader>wic :DiaryIssueComment<CR>
    autocmd FileType vimwiki nnoremap <buffer> <leader>wii :DiaryIssue<CR>
augroup END

setlocal foldtext=DiaryFoldText()

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
