#!/bin/bash

LogMessage() {
    echo `date +%d"/"%m"/"%Y" "%X` : "$*"
}

# Setup some global variables
SUCCESS=0
FAIL=1

LogMessage "Starting testing script..."

# Printing relevant versions of libraries
poetry run python --version

if [ "${LINT_CODE:-0}" -eq 1 ]; then

    poetry run pylint --version
    poetry run black --version

    LogMessage "Running full lint of code..."
    poetry run pylint rplugin/python3/nvim_diary_template -j 0
    LogMessage "Finished running full lint of code..."

    LogMessage "Linting code ignoring TODO warnings..."
    poetry run pylint rplugin/python3/nvim_diary_template -j 0 -d W0511
    LogMessage "Finished running second lint of code..."

    RETURN_CODE=$?

    LogMessage "Pylint returned ${RETURN_CODE}..."

    if [ $RETURN_CODE -ne 0 ]; then
        LogMessage "pylint failed check..."
        exit ${FAIL}
    fi

    LogMessage "Running black source code syntax with Black..."
    poetry run black rplugin/python3/deoplete --check
    LogMessage "Finished running black on deopletet source..."

    RETURN_CODE=$?

    LogMessage "black returned ${RETURN_CODE}..."

    if [ $RETURN_CODE -ne 0 ]; then
        LogMessage "Deoplete failed black check..."
        exit ${FAIL}
    fi

    LogMessage "Running black on main source..."
    poetry run black rplugin/python3/nvim_diary_template --check
    LogMessage "Finished running black on main source..."

    RETURN_CODE=$?

    LogMessage "black returned ${RETURN_CODE}..."

    if [ $RETURN_CODE -ne 0 ]; then
        LogMessage "Main code failed black check..."
        exit ${FAIL}
    fi
fi

if [ "${FULL_TYPING:-0}" -eq 1 ]; then

    poetry run mypy --version

    LogMessage "Running full mypy on code base..."
    poetry run mypy rplugin/python3/nvim_diary_template --strict
    LogMessage "Finished running full mypy on code base..."

    RETURN_CODE=$?

    LogMessage "mypy returned ${RETURN_CODE}..."

    if [ $RETURN_CODE -ne 0 ]; then
        LogMessage "Full typing check failed..."
        exit ${FAIL}
    else
        LogMessage "Full typing check passed!"
    fi
fi

if [ "${BASIC_TYPING-0}" -eq 1 ]; then

    poetry run mypy --version

    LogMessage "Running basic mypy on code base..."
    poetry run mypy --config-file mypy.ini rplugin/python3/nvim_diary_template
    LogMessage "Finished running basic mypy on code base..."

    RETURN_CODE=$?

    LogMessage "mypy returned ${RETURN_CODE}..."

    if [ $RETURN_CODE -ne 0 ]; then
        LogMessage "Basic typing check failed..."
        exit ${FAIL}
    else
        LogMessage "Basic typing check passed!"
    fi
fi

LogMessage "Script finished!"
exit ${SUCCESS}
