from googleapiclient.discovery import build
import local_settings
import random

def grabImage(query):
    """
    Searches Google Image Search for Query
    Using Custom Search API
    """

    google = build('customsearch','v1',developerKey=local_settings.GOOGLE_API)

    results = google.cse().list(q=query,
                                cx=local_settings.GOOGLE_CSE,
                                fileType = 'png gif jpg',
                                searchType ='image',
                                filter='1',
                                safe = 'off'
                                ).execute()

    output = random.choice(results['items'])['link']

    return output

def searchCleanup(searchterm):
    #Apart from first word which will be capitalised anyway, hoik out anything
    #that's capitalised to use for searching
    srcterm = filter(unicode.istitle,searchterm.split(' '))
    output = ""

    if len(srcterm) > 1:
        for s in srcterm:
            output += s + ' '
    else:
        output = searchterm

    return output
