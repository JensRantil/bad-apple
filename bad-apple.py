#!/usr/bin/env python

import argparse
import itertools
import logging
import subprocess
import sys
import tempfile


def main():
    default_parser_args = {
        "formatter_class": argparse.ArgumentDefaultsHelpFormatter,
    }
    parser = argparse.ArgumentParser(
        description='Output a list of rows of a file that an application could not execute.',
        **default_parser_args
    )
    parser.add_argument('--verbose', '-v', help="Enable debug logging", action="count")
    parser.add_argument('--stdout-to-stdout', '-s', dest="stdout_to_stdout", help="Don't forward stdout to stderr.", action="store_true")
    parser.add_argument('--show-multi-row-output', '-m', dest="multi_row_output", help="Show the output of tests when the file contains multiple rows. Usually seeing the output only for the single failing line is enough.", action="store_true")
    parser.add_argument('--arg-file', '-a', dest="input", default="-", help="Read items from file instead of standard input.", type=argparse.FileType())

    args, leftovers = parser.parse_known_args()
    init_logging(args)

    toexec = leftovers[leftovers.index('--')+1:] if '--' in leftovers else leftovers
    if not toexec:
        parser.error("missing application to execute")
    return run(args, toexec)


def init_logging(args):
    if args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARN
    logging.basicConfig(level=level)


def run(args, toexec):
    haderrors = False

    nlines = 0
    with tempfile.NamedTemporaryFile() as alllines:
        nlines = copy(args.input, alllines)
        alllines.flush()

        backlog = [(0, nlines)]
        while backlog:
            rows = backlog.pop()

            alllines.seek(0)
            if not test(args, alllines, rows, toexec):
                haderrors = True
                if rows[1]-rows[0] > 1:
                    intermediate = rows[0] + (rows[1]-rows[0])/2
                    backlog += [(intermediate, rows[1]), (rows[0], intermediate)]

    return 1 if haderrors else 0


def test(args, infile, rows, toexec):
    logging.info("Testing lines [%s]...", rows)
    with tempfile.NamedTemporaryFile() as smallerfile:
        for line in itertools.islice(infile, *rows):
            smallerfile.write(line)
        smallerfile.flush()
        cmd = toexec + [smallerfile.name]
        logging.info("Executing %s...", cmd)
        out=stdout(args, rows)
        err=stderr(args, rows)
        logging.debug("stdout=%s stderr=%s", out, err)
        exitcode = subprocess.call(cmd, stdout=out, stderr=err)
        logging.info("Return code: %d", exitcode)
    if exitcode and rows[1]-rows[0]==1:
        print line.strip()
    return exitcode == 0


def stderr(args, rows):
    if rows[1]-rows[0] > 1 and not args.multi_row_output:
        return None
    return sys.stderr


def stdout(args, rows):
    if rows[1]-rows[0] > 1 and not args.multi_row_output:
        return None
    if args.stdout_to_stdout:
        sys.stdout
    return sys.stderr


def copy(source, dest):
    nlines = 0
    for line in source:
        dest.write(line)
        nlines += 1
    return nlines

if __name__=="__main__":
    sys.exit(main())
