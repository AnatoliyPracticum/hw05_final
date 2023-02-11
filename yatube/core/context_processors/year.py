from datetime import datetime


def year(request):
    year = datetime.now()
    return {'year': year.year}
