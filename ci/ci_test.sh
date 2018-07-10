SUCCESS=0
FAIL=1

pyflakes .
pylint rplugin/python3/nvim_diary_template 

exit ${SUCCESS}