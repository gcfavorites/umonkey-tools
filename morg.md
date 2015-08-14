> _**This project is closed: I'm using [Taskwarrior](http://taskwarrior.org/projects/taskwarrior/wiki/FAQ) now.**_

**Morg** is a command line (for now) file system based organizer which has a wiki and an issue tracker build in.  Everyhing is a text file with support for [Markdown](http://daringfireball.net/projects/markdown/syntax) formatting.  Morg can send all changes to Git or Mercurial transparently, if you want that.  The name stands for <strong>m</strong>inimalistic <strong>org</strong>anizer.



# Issue file format #

Issues are text files that look like this:

```
title: New issue description...
labels: private
created: 2010-10-28
---
Issue description goes here...
```

Everything above the first line with 3 dashes is the header, everything below is the body (a text block of whatever you want).  The header consists of lines with "key: value" pairs.  There are no restrictions on keys nor values, the following keys are supported:

  * title: issue title, used by `morg issue list`.
  * labels: a comma or space separated list of arbitraty values.  The only special value is "closed", which hides the issue from the default list.  Values "feature" and "bug" change the issue marker in lists from "T" to "E" and "D", respectively (see the `morg issue list` command description below).
  * created: the day when the issue was created.  Not used anywhere.
  * priority: an integer from 1 to 9, defaults to 3.  Lower values mean higher priority.  Issue lists are sorted according to this value.

Issues are stored in files with names like `issues/123/README.markdown`, where "123" is the issue id.  It is assigned automatically and iccementally when you create an issue.

> _Issue file format is inspired by [Poole](http://bitbucket.org/obensonne/poole/src), a static web site generator written in Python.  I use it for [my web site](http://umonkey.net/)._


# Usage #

Morg stores all data in folders `issues` and `wiki` in the current directory.  It uses your default editor to edit files, that is: whatever you have in the `EDITOR` environment variable, or if there's no such variable, the `editor` binary (the Ubuntu way).

Everything is done with the `morg` command.  Examples:

**`morg`**

Runs the default command, which usually "help", but can be overriden in the configuration file (see below).


**`morg config`**

Opens your main configuration file for editing (see below).


**`morg help`**

Shows a brief command introduction.


**`morg patch`**

Opens itself for editing.  Useful when you know Python and patch morg often.


**`morg push`**

Push local commits to a remote Git or Mercurial repository, if there is a `.git` or an `.hg` folder.


**`morg show`**

Shows all existing files in the curent project.


**`morg issue [list [args]]`**

Shows the list of issues.  By default shows only issues without the "closed" label (see below).  You can specify a particular label to show (e.g.: `morg issue list closed`).

Example output:

```
$ morg
T1    1: Написать нормальную систему для самоорганизации
T3    8: Описать работу со статусами заказов  [work]
T3    9: Написать gnome-radio  [tmradio]
T3   11: Использование volman для определения имён дисков  [gpoder]
T3   12: Добавить gpodder в индикатор сообщений  [gpodder]
||    |
||    +- issue id (use: morg issue edit id)
||
|+------ priority (lower = higher)
+------- type (enhancement, defect, task)
```

Labels, if the issue has some, are listed in square brackets.  When you get used to listing issues, you can disable the hints in your configuration file (see below).


**`morg issue create`**

Creates a new issue.  It first creates a temporary file (`~/new-morg-issue.markdown`), writes some sensible defaults to it, opens the file for editing, then moves it to the permanent location.

The default template looks like this:

```
title: New issue description...
labels: private
created: 2010-10-28
---
Issue description goes here...
```

The only way to cancel creating an issue is to kill the editor.  You can do so by first pressing `^Z` to minimize it, then issuing the `kill %` command.

After the changes are made, a `morg issue list` command is automatically executed to reflect them.


**`morg issue edit ...`**

Opens the specified issues for editing.  After the changes are made, a `morg issue list` command is automatically executed to reflect them.


## Tips and tricks ##

I've been using [DevTodo](http://swapoff.org/DevTodo) for a while and got used to its short commands: `todo`, `tda` and `tde` to list, add and edit tasks.  So I found it useful to create these bash aliases in `~/.bashrc`:

```
alias todo='morg issue list todo'
alias tda='morg issue create'
alias tde='morg issue edit'
```


# Configuration #

Configuration options are read (and combined) from the following files:

  * `~/.morg` (your main config file)
  * `./.morg` (in your current project)

Local configuration updates (i.e. extends) the main one.  These files are like issue headers: lines with "key: value" pairs, comments start with a hash sign.  Example:

```
default-command: issue list
#less-hints: yes
auto-commit: yes
default-path: ~/workspace
```

You can edit `~/.morg` with `morg config`.  The local `.morg` file you will have to edit manually.

Supported configuration options:

**`default-command`**

This is what's really executed when you run `morg` without arguments.  If not specified, defaults to "help".  So, when you run `morg` without arguments, you actually run `morg help`.  If most of the time you work with issues labelled "private", you can set this parameter to "issue list private" to save yourself some time.


**`less-hints`**

Set to a non-empty string (e.g., "yes") to disable hints (column descriptions) for `morg issue list`.


**`auto-commit`**

Commit changes to your Git or Mercurial repository after editing or adding issues.


**`auto-push`**

Push changes to your Git or Mercurial repository after editing or adding issues.


**`default-path`**

Specify the default project.  That's a folder where your data is.  It's only used when you run `morg` from a directory which doesn't have a `.morg` file (or from your home dir).  Set this to something and run `morg` to see the list of open issues wherever you are.


**`editor`**

Your preferred editor.  Use this if you want to use a particular editor with particular command line options.  For example, if you often edit more than one issue, use vim and want to open all of them in a horizontal split, set this to "vim -o".


**`alias-xyz`**

This is not a single parameter, but a group.  The "alias-" prefix lets you create short aliases for long commands.  For example:

```
alias-todo: issue list todo
```

With this options you can type `morg todo` instead of `morg issue list todo`.


# Source code #

  * [Read or download](http://umonkey-tools.googlecode.com/hg/bin/morg)
  * [See changes](http://code.google.com/p/umonkey-tools/source/list?path=bin/morg)


# Other similar software #

  * [Fossil](http://fossil-scm.org/): is local with support for distributed sync, has a wiki and an issue tracker, a built-in simple to use web server, but uses an SQLite backend.
  * [Ikiwiki](http://ikiwiki.info/): a local wiki, support for Subversion and Git is built in, has full-text search and a lot of plugins.  No issue tracker, no stand-alone server.
  * [Taskwarrior](http://taskwarrior.org/projects/taskwarrior/wiki/FAQ), a CLI task manager.


# Support and future plans #

  * [Bug reports and feature requests](http://code.google.com/p/umonkey-tools/issues/list?q=Component%3Dmorg)