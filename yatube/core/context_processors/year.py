from datetime import datetime


def year(request):
    dt = datetime.now().strftime('%Y')
    return {
        'year': int(dt),
    }
