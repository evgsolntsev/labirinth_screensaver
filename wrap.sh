#!/bin/bash

cd ${0%/*}

export SDL_WINDOWID="$XSCREENSAVER_WINDOW"

child=0

function ex {
  kill -s 9 $child > /tmp/child
  exit 0
}
trap ex SIGINT SIGTERM

/usr/bin/python3 ./run.py &

child=$!

wait $child
