import os
import requests
import urllib
import Read_config
import helper

get_details = {"buildNumber": "",
               "url": "",
               "downloadItem": "",
               "download": False,
               "downloadLocation": "",
               "downloadUrl": "",
               "invokeQAT": False,
               "batchFilePath": "",
               "qatConfigfilePath": "",
               "authors": [],
               "authorsJenkins": [],
               "fileName": "",
               "schedularTaskName": "",
               "relativePath": ""}


# reads config.ini and load details in get_details dictionary
def read_configuration():
    try:
        load_config = Read_config.read_config()
        head_url = 'http://' + load_config['APPSettings']['server']
        job = '/job/' + load_config['APPSettings']['job']
        api = '/' + load_config['APPSettings']['api']
        get_details["url"] = head_url + job + api
        get_details["download"] = (load_config['APPSettings']['download']).upper()
        get_details["downloadItem"] = load_config['APPSettings']['downloadItem']
        get_details["downloadLocation"] = load_config['APPSettings']['downloadLocation']
        get_details["invokeQAT"] = load_config['APPSettings']['invokeQAT']
        get_details["batchFilePath"] = load_config['APPSettings']['batchFilePath']
        get_details["qatConfigfilePath"] = load_config['APPSettings']['qatConfigfilePath']
        get_details["schedularTaskName"] = load_config['APPSettings']['schedularTaskName']
        get_details["authors"] = (load_config['APPSettings']['authors']).split(',')
        print(get_details)
        return True
    except Exception as e:
        print(str(e))
        return False


# Fetches details from jenkins API "result,build number,author names,filename,relative path"
def get_url_details(url):
    try:
        response = requests.get(url)
        # response = requests.get('http://localhost:8080/job/test%20job/lastBuild/api/json', auth=('guru', 'jenkins'))
        if response.status_code == 200:
            json_data = response.json()
            if json_data['result'] == 'SUCCESS':
                get_details["buildNumber"] = json_data['number']
                get_author_names(json_data)
                artifact_details(json_data, get_details["downloadItem"])
                return True

            else:
                print('build result is fail')
                return False
        else:
            print('Http response is not success')
            return False

    except Exception as e:
        print(str(e))
        return False


# Fetches author names from json response
def get_author_names(json_data):
    try:
        if 'changeSets' in json_data:
            if len(json_data['changeSets']) > 0:
                change_set = json_data['changeSets']
                if len(change_set[0]['items']) > 0:
                    for b in (change_set[0]['items']):
                        get_details["authorsJenkins"].append(b['author']['fullName'])
                    return True
                else:
                    print('No items in change sets data')
                    return False
            else:
                print('No change sets data')
                return False
        else:
            print('No change sets')
            return False
    except Exception as e:
        print(str(e))
        return False


# Fetches filename,relative path and construct download url from json response
def artifact_details(json_data, file):
    try:
        if len(json_data['artifacts']) > 0:
            get_details["fileName"], get_details["relativePath"] = search(
                json_data['artifacts'], file)
            get_details["downloadUrl"] = json_data['url'] + 'artifact/' + urllib.parse.quote(
                get_details["relativePath"])
            return True
        else:
            print('No artifacts found')
            return False
    except Exception as e:
        print(str(e))
        return False


# sub function of artifacts_details: Matches filename with the input argument and
# returns filename and relative path from json response
def search(json_data, searchFor="Designer"):
    try:
        for B in json_data:
            if searchFor in (B['fileName']):
                return B['fileName'], B['relativePath']
        return None
    except Exception as e:
        print(str(e))
        return False


def main():
    try:
        if read_configuration():
            result = get_url_details(get_details["url"])
            if result:
                # if config download is true and authors matches from config
                if (get_details["download"] == 'TRUE') & (any(item in get_details["authorsJenkins"] for item
                                                              in get_details['authors'])):
                    if helper.download_file(get_details["downloadUrl"], get_details["downloadLocation"],
                                            get_details["fileName"]):
                        # subprocess.call([r'C:\Users\guru.tn\Desktop\QAT_invoke.bat'])
                        if get_details["invokeQAT"]:
                            os.system('schtasks /run /tn "QAT_invoke"')
                    else:
                        print('unable to download: ' + get_details['fileName'])
                else:
                    print('Download Failed --> download option in config set to : ' + get_details["download"] +
                          ' and build authors names are', get_details["authorsJenkins"])
            else:
                print('Failed to retrieve details from JENKINS')
        else:
            print('Read from config file failed')

    except Exception as e:
        print(str(e))
        return False


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
