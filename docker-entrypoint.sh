#!/bin/bash

export LOG_LEVEL=${LOG_LEVEL:-"INFO"}

do_gosu(){
    user="$1"
    shift 1

    is_exec="false"
    if [ "$1" = "exec" ]; then
        is_exec="true"
        shift 1
    fi

    if [ "$(id -u)" = "0" ]; then
        if [ "${is_exec}" = "true" ]; then
            exec gosu "${user}" "$@"
        else
            gosu "${user}" "$@"
            return "$?"
        fi
    else
        if [ "${is_exec}" = "true" ]; then
            exec "$@"
        else
            eval '"$@"'
            return "$?"
        fi
    fi
}


if [[ "start" == "$1" ]]; then
    echo "Starting python worker"
    do_gosu "${PROJECT_USER}:${PROJECT_GROUP}" python run.py
elif [[ "start-webhook" == "$1" ]]; then
    echo "Starting webhook server"
    do_gosu "${PROJECT_USER}:${PROJECT_GROUP}" exec python -m shared.webhook
fi


exec "$@"
