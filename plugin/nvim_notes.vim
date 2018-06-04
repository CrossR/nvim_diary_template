" Initalise some options

let g:nvim_notes#active = get(g:, 'nvim_notes#active', v:true)
let g:nvim_notes#config_path = get(g:, 'nvim_notes#config_path', '')

" Keybinds

augroup nvim_notes_keybinds
    autocmd!
    autocmd FileType markdown nnoremap <buffer> gs :ToggleLine<CR>
augroup END
