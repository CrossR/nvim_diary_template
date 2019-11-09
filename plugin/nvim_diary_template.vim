" Initialise some options

let g:nvim_diary_template#active = get(g:, 'nvim_diary_template#active', v:true)
let g:nvim_diary_template#notes_path = get(g:, 'nvim_diary_template#notes_path', '')
let g:nvim_diary_template#config_path = get(g:, 'nvim_diary_template#config_path', g:nvim_diary_template#notes_path . '/config')

" Wrap functions in commands
command DiaryInit call DiaryInit()
command DiaryOptionsInit call DiaryOptionsInit()

command DiaryEditComment call DiaryEditComment()
command DiaryEditIssue call DiaryEditIssue()
command DiaryCompleteIssue call DiaryCompleteIssue()

command DiaryInsertComment call DiaryInsertComment()
command DiaryInsertIssue call DiaryInsertIssue()

command DiaryUploadNew call DiaryUploadNew()
command DiaryUploadEdits call DiaryUploadEdits()
command DiaryUploadCompletion call DiaryUploadCompletion()
command DiaryUploadIssues call DiaryUploadIssues()

command DiaryGetIssues call DiaryGetIssues()
command DiarySortIssues call DiarySortIssues()
command DiarySwapGroupSorting call DiarySwapGroupSorting()

command DiaryGetCalendar call DiaryGetCalendar()
command DiaryUploadCalendar call DiaryUploadCalendar()

" Setup binds, and fold bits.
augroup nvim_diary_template_keybinds
    autocmd!
    " Edit existing issue/comments binds
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wec :DiaryEditComment<CR>
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wei :DiaryEditIssue<CR>
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wci :DiaryCompleteIssue<CR>

    " Insert new issue/comments binds
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wic :DiaryInsertComment<CR>
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wii :DiaryInsertIssue<CR>

    " Upload edited/new issues and comments
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wun :DiaryUploadNew<CR>
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wue :DiaryUploadEdits<CR>
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wuc :DiaryUploadCompletion<CR>
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wua :DiaryUploadIssues<CR>

    " Grab/Sort Issues
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wgi :DiaryGetIssues<CR>
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wsi :DiarySortIssues<CR>
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wsg :DiarySwapGroupSorting<CR>

    " Calendar Binds
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wgc :DiaryGetCalendar<CR>
    autocmd FileType markdown nnoremap <silent><buffer> <leader>wug :DiaryUploadCalendar<CR>

    autocmd FileType markdown setlocal foldtext=DiaryFoldText()
    autocmd FileType markdown setlocal foldmethod=expr
    autocmd FileType markdown setlocal foldexpr=GetDiaryFold(v:lnum)

    autocmd BufEnter *.md call SetupDiaryPlug()
augroup END

" Function to be called on startup.
" Either just init the options, or make the diary too.
function! SetupDiaryPlug()

  if expand("%:p") !~ "diary"
    return
  endif

  if line('$') == 0
    call DiaryOptionsInit()
    return
  endif

  " Otherwise, we should also populate the file.
  call DiaryInit()

endfunction
