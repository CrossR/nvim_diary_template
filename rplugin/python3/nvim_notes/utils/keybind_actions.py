def strikeout_line(line):
    line_content = line.strip().split()[1:]
    first_non_space = len(line) - len(line.strip())

    return [f"{line[:first_non_space]}~~{' '.join(line_content)}~~"]

