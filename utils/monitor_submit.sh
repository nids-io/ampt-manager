#!/bin/sh
#
# Simulate event monitor log submissions to AMPT manager. Needs work.
# Currently need to modify the curl(1) calls below to set required address/port
# options.

set -e

PATH=/bin:/usr/bin:/usr/local/bin

# Output random-ish source port
rand_port()
{
    echo $(((RANDOM + RANDOM) % 65535))
}

err()
{
    echo "USAGE: $(basename $0) <ADDRESS>:<PORT>" 2>&1
}

if [ -n "$1" ]; then
    REMOTE_SVC="$1"
    if ! echo "$REMOTE_SVC" |egrep -q ':[0-9]{1,5}$'; then
        err; exit 1
    fi
else
    err; exit 1
fi

URL="https://${REMOTE_SVC}/log/receivedlog/"

curl --insecure --include --request POST \
    -d monitor=1 \
    -d src_addr=10.8.42.3 \
    -d src_port=$(rand_port) \
    -d dest_addr=10.0.1.1 \
    -d dest_port=80 \
    -d protocol=tcp \
    -d alert_time="$(date -u -v "-5M" "+%F %T")" \
    "$URL"

#curl --insecure --include --request POST \
#    -d monitor=1 \
#    -d src_addr=172.24.199.7 \
#    -d src_port=$(rand_port) \
#    -d dest_addr=192.0.2.20 \
#    -d dest_port=80 \
#    -d protocol=tcp \
#    -d alert_time="$(date -u -v "-5M" "+%F %T")" \
#    "$URL"
