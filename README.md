Bad Apple
=========
What is this?
-------------
Imagine you have an application that takes a file as input and does something
with each line in the file (for example, `xargs`). One line makes your
application fail, but you don't know which.

Let's say that the application is really slow to start (for example, `java`),
then executing your application serially across every line isn't viable. That's
when `bad-apple.py` comes in! It does a binary search across all lines and
tries too find which lines are failing while testing as many lines as possible
in each run.

The application can also be used to make sure to execute something for all
lines if you application fails on first line.

Usage
-----
```sh
$ ./bad-apple.py --arg-file myfile ./my-slow-application
failing-line#1
failing-line#2
...
```
or
```sh
$ cat myfile | ./bad-apple.py ./my-slow-application
failing-line#1
failing-line#2
...
```
. If your application takes flags you can add `--` for `bad-apple.py` to not
thing it's a parameter to itself. Ie., you can doo
```sh
$ ./bad-apple.py --arg-file myfile -- xargs -n 1 -- ./my-slow-application -v -t echo
failing-line#1
failing-line#2
...
```

Try it
------
You can find all lines in this readme containing the string "Develop" by executing
```sh
$ cat README.md | ./bad-apple.py -- /bin/sh -c '! grep -q Develop $1' --
Develop
```
If you want to follow along in the binary search you can do
```sh
$ cat README.md | ./bad-apple.py --verbose -- /bin/sh -c '! grep -q Develop $1' --
...
Develop
...
```
.
