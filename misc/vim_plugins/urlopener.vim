" Lets you open URLs by pressing \w on a line with URLs.
"
" FIXME: after the browser is open, the screen has trash on it, ^L needs to be
" pressed.

function! Browser ()
  let line = matchstr(getline("."), "http[^ ]*")
  :if line==""
    let line = "http://" . matchstr(getline("."), "www\.[^ ]*")
  :endif
  :if line != ""
    silent exec "!xdg-open " . line
  :endif
endfunction
map <Leader>w :call Browser ()<CR>
