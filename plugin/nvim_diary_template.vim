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

