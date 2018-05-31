PADDING = '   '

def strikeout_line(line):
    line_content = line.strip().split()[1:]
    first_non_space = len(line) - len(line.strip())
    start_of_line = line[:first_non_space + 1]

    return [f"{start_of_line}{PADDING}~~{' '.join(line_content)}~~"]

