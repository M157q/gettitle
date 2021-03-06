import traceback


def handle_error(e, debug=False, url=None):
    def handle_unexpected_error():
        if not debug:
            traceback.print_exc()

        print('')
        print('=' * 20)
        print("Unexpected Error Happened.")
        bug_report_url = "https://github.com/M157q/gettitle/issues"
        t = "Please report the error message above to {}"
        print(t.format(bug_report_url))
        print('=' * 20)

    def handle_connection_error(url):
        t = 'Check your network connection or the URL "{}" is invalid.'
        print(t.format(url))

    if debug:
        traceback.print_exc()
    else:
        handle_unexpected_error()

    exit()
