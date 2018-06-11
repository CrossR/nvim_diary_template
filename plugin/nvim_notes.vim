" Initalise some options

let g:nvim_notes#active = get(g:, 'nvim_notes#active', v:true)
let g:nvim_notes#config_path = get(g:, 'nvim_notes#config_path', '')

" Keybinds

augroup nvim_notes_keybinds
    autocmd!
    autocmd FileType markdown nnoremap <buffer> <leader>s :ToggleLine<CR>
    autocmd FileType markdown nnoremap <buffer> <leader>w :OpenSchedule<CR>
    autocmd FileType markdown nnoremap <buffer> <leader>n :OpenNote<CR>
augroup END

" Buffer settings

" TODO: Make these into settings.
augroup nvim_notes_settings
    autocmd FileType markdown setlocal spell spelllang=en_gb
    autocmd FileType markdown setlocal textwidth=80
augroup END

