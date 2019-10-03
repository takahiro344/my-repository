" Setting character code utf-8.
set encoding=utf-8
scriptencoding=utf-8

" Display title.
set title

" Display line number.
set number

" Inhibit creating backup file and swap file.
set nobackup
set noswapfile

" Set smart indent.
set smartindent

" Expand tab to half-wide spaces.
set expandtab

" Set tab width.
set tabstop=2

" Set tab width of the beginning of line.
set shiftwidth=2

" Enable incremental search.
set incsearch

" Set highlight.
set hlsearch

" Complementation of command mode.
set wildmenu

" Enable backspace.
set backspace=indent,eol,start

syntax on
colorscheme ron

filetype on

" Setting key maps.
" inoremap: Key mapping of insert mode.
" nnoremap: Key mapping of normal mode.
" <ESC>   : Escape
" <ENTER> : Enter
" <CR>    : Carriage return
" <DEL>   : Delete
" <BS>    : Backspace
" <UP>    : Up-key
" <LEFT>  : Left-key
" <C-?>   : Ctrl-key + ?
" <S-?>   : Shift-key + ?
nnoremap <F3> :noh<CR>

nnoremap + <C-a>
nnoremap - <C-x>

inoremap { {}<LEFT>
inoremap {<ENTER> {}<LEFT><CR><CR><BS><BS><ESC><UP><S-a>
inoremap ( ()<LEFT>
inoremap (<ENTER> ()<LEFT><CR><CR><BS><BS><ESC><UP><S-a>
inoremap [ []<LEFT>
inoremap " ""<LEFT>
inoremap ' ''<LEFT>

inoremap <C-a> <ESC><S-i>
nnoremap <C-a> <ESC><S-i>
inoremap <C-e> <ESC><S-a>
nnoremap <C-e> <ESC><S-a>

" Set paste mode automatically.
if &term =~ "xterm"
  let &t_ti .= "\e[?2004h"
  let &t_te .= "\e[?2004l"
  let &pastetoggle = "\e[201~"

  function XTermPasteBegin(ret)
    set paste
    return a:ret
  endfunction
  
  noremap <special> <expr> <Esc>[200~ XTermPasteBegin("0i")
  inoremap <special> <expr> <Esc>[200~ XTermPasteBegin("")
  cnoremap <special> <Esc>[200~ <nop>
  cnoremap <special> <Esc>[201~ <nop>
endif

" Ref: https://qiita.com/yahihi/items/4112ab38b2cc80c91b16
augroup vimrcEx
  au BufRead * if line("'\"") > 0 && line("'\"") <= line("$") |
  \ exe "normal g`\"" | endif
augroup END

