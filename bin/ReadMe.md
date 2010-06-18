This are the script that I use every day and that others might find useful.
I have the following lines in my ~/.profile:

    if [ -d "$HOME/src/umonkey-tools/bin" ]; then
        PATH="$HOME/src/umonkey-tools/bin:$PATH"
    fi
