# An example of implementing D-Bus server and client using DBussy

Please refer to the files `src/dbussyexample/server.py` and `src/dbussyexample/client.py` for the implementation details.

## Demo

### Server

```
$ pipenv run dbussy-example-server
INFO:root:starts serving...
INFO:root:add(52, 6)
INFO:root:subtract(52, 6)
```

### Client

```
$ pipenv run dbussy-example-client
[client] a = 52, b = 6
[server] a + b = 58
[server] a - b = 46
```

## Installation

```
git clone https://github.com/changyuheng/a-simple-python-dbussy-server-client-example.git
cd a-simple-python-dbussy-server-client-example
pipenv sync
```

## Usage

### With pip

To start the server:
```
pipenv run dbussy-example-server
```

To run the client:
```
pipenv run dbussy-example-client
```
