# ftp-client

Bare bones implementation of FTP command-line client with Python sockets.

## Usage

```
$ python main.py
```

If you'd like to activate debug output, you can use the `--debug` flag. This is
useful if you're interested in looking at the actual protocol messages sent back
and forth between the client and server.

## The client

Once you start up the FTP client you'll get this prompt:

```
FTP >
```

You can start typing `help` or `?` to see available commands. Also, typing `help
<command>` shows you the documentation for that specific command.

### Available commands

This FTP client does not exhaustively implement each of the commands available
in the FTP protocol, but it's enough for common usage. Here's the full list of
those available:

* `connect` - Connect to FTP server running on specified host.
* `login` - Prompts for user and password to authenticate with the FTP server.
* `logout` - Logout current logged in user.
* `disconnect` - Quits the connection to the FTP server.
* `list` - Show information about file or directory, defaults to info about
  current directory.
* `retrieve` - Download file.
* `store` - Upload file.
* `pwd` - Output current directory.
* `cwd` - Change working directory.
* `cdup` - Change working directory to parent of current working directory.
* `mkdir` - Create directory.
* `rm` - Remove file.
* `rmdir` - Remove directory.
* `rename` - Rename file or directory.

### Limitations

* Only ASCII transmission mode is supported.
* No support for secure connections over TLS/SSL.
