"""issue_helpers

Simple helpers to deal with Github issues.
"""

def convert_issues(github_service, issue_list):
    """convert_issues

    Given a basic list of issues, grab the associated comments for printing.
    """

    formatted_issues = []

    for issue in issue_list:
        comments = github_service.get_comments_for_issue(issue['number'])
        formatted_issues.append({
            'number': issue['number'],
            'title': issue['title'],
            'comments': comments,
        })

    return formatted_issues
