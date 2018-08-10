SUCCESS=0
FAIL=1

echo "Linting code..."
pylint rplugin/python3/nvim_diary_template 

echo "Checking code syntax with Black..."
black rplugin/python3/deoplete --check

if [ $? -ne 0 ]; then
    echo "Deoplete failed black check..."
    exit ${FAIL}
fi

black rplugin/python3/nvim_diary_template --check

if [ $? -ne 0 ]; then
    echo "Main code failed black check..."
    exit ${FAIL}
fi

echo "Running mypy on code base..."
if [ "${FULL_TYPING:-0}" -eq 1 ]; then
    mypy rplugin/python3/nvim_diary_template --strict
    false # Should return 0 every time, meaning the CI doesn't stop
else
    mypy rplugin/python3/nvim_diary_template --strict --allow-untyped-calls --allow-untyped-decorators
fi

if [ $? -ne 0 ]; then
    echo "Failed typing checks..."
    exit ${FAIL}
fi

echo "Script finished!"
exit ${SUCCESS}