This program lets you send pop-up notifications from remote servers to your
workstation.  You start this program then connect to a remote server using SSH,
having port 8111 forwarded back to you, this way:

    ssh -R 8111:localhost:8111

Or you can add this to your ~/.ssh/config:

    Host example.com
    RemoteForward 8111 localhost:8111

To send a message from the remote server, send "subject\nbody" to port 8111,
like this:

    echo "irssi\nYou have a message from XYZ." | netcat localhost 8111

Examples of using this script are in files nameed example-*.txt.
