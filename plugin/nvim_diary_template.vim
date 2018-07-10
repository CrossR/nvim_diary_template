" Initalise some options

let g:nvim_notes#active = get(g:, 'nvim_notes#active', v:true)
let g:nvim_notes#notes_path = get(g:, 'nvim_notes#notes_path', '') 
let g:nvim_notes#config_path = get(g:, 'nvim_notes#config_path', g:nvim_notes#notes_path . '/config')
