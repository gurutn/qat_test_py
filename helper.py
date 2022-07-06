import os
import requests


def download_file(url, destination, filename):
    if os.path.exists(destination):
        for f in os.listdir(destination):
            os.remove(os.path.join(destination, f))

    print(filename)
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(destination + filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunked:
                    f.write(chunk)
        return True
    except Exception as e:
        print(str(e))
        return False