def strikeout_line(line):
    line_content = line.strip().split()[1:]
    return f"~~{' '.join(line_content)}~~"

