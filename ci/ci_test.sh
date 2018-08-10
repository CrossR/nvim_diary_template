SUCCESS=0
FAIL=1

echo "Linting code..."
pylint rplugin/python3/nvim_diary_template 

echo "Checking code syntax with Black..."
black rplugin/python3/deoplete --check

if [ $? -ne 0 ]; then
    echo "Deoplete failed black check."
    exit ${FAIL}
fi

black rplugin/python3/nvim_diary_template --check

if [ $? -ne 0 ]; then
    echo "Main code failed black check."
    exit ${FAIL}
fi

echo "Running mypy on code base..."
echo "TODO: Once fully updated, check the error code here."
mypy rplugin/python3/nvim_diary_template

echo "Script finished!"
exit ${SUCCESS}