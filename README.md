# Backslash Testbed
This repository is intended to test the Backslash test reporting server. It emulates clients running
test suites against the server, and is aimed at stress testing and generating large data sets.

## Usage

```
$ ./run.py --backslash-url http://your-backslash-url
```

**NOTE** this tool requires your backslash to be configured with the TESTING configuration set,
since it attempts to create users on the fly.

## License

MIT
