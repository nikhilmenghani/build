import time

import NikGapps.Git.GitConfig as Config
import json
import requests


class GitApi:
    @staticmethod
    def read_from_url(url, params=None, authenticate=False):
        if params is None:
            params = {"": ""}
        if authenticate:
            headers = {'Authorization': f'token {Config.git_token_admin}'}
        else:
            headers = {'Accept': 'application/vnd.github.v3+json'}
        r = requests.get(url, data=json.dumps(params), headers=headers)
        print("--------------------------------------------------------------------------------")
        print(f"Response {str(r.status_code)} while reading from {url}")
        if not r.status_code.__eq__(200):
            print(json.dumps(r.json(), indent=4, sort_keys=True))
        print("--------------------------------------------------------------------------------")
        return r

    @staticmethod
    def put_to_url(url, params=None, authenticate=False):
        if params is None:
            params = {"": ""}
        if authenticate:
            headers = {'Content-Type': 'application/json',
                       'Authorization': f'token {Config.git_token_admin}'}
        else:
            headers = {'Accept': 'application/vnd.github.v3+json'}
        r = requests.put(url, data=json.dumps(params), headers=headers)
        print("--------------------------------------------------------------------------------")
        print(f"Response {str(r.status_code)} while putting to {url}")
        if not r.status_code.__eq__(200):
            print(json.dumps(r.json(), indent=4, sort_keys=True))
        print("--------------------------------------------------------------------------------")
        return r

    @staticmethod
    def post_to_url(url, params=None, authenticate=False):
        if params is None:
            params = {"": ""}
        if authenticate:
            headers = {'Content-Type': 'application/json',
                       'Authorization': f'token {Config.git_token_admin}'}
        else:
            headers = {'Accept': 'application/vnd.github.v3+json'}
        r = requests.post(url, data=json.dumps(params), headers=headers)
        print("-------------------------------------------------------------------------------------")
        print(f"Response {str(r.status_code)} while posting to {url}")
        if not r.status_code.__eq__(201):
            print(json.dumps(r.json(), indent=4, sort_keys=True))
        print("-------------------------------------------------------------------------------------")
        return r

    @staticmethod
    def get_open_pull_requests(authenticate=False):
        query_url = f"https://api.github.com/repos/{Config.owner}/{Config.repo}/pulls"
        pull_requests = []
        data_json = GitApi.read_from_url(query_url, authenticate=authenticate).json()
        if len(data_json) > 0:
            for i in range(0, len(data_json)):
                pull_requests.append(data_json[i])
        return pull_requests

    @staticmethod
    def get_comments_from_pull_request(pull_number, authenticate=False):
        query_url = f"https://api.github.com/repos/{Config.owner}/{Config.repo}/issues/{pull_number}/comments"
        comments = []
        data_json = GitApi.read_from_url(query_url, authenticate=authenticate).json()
        if len(data_json) > 0:
            for i in range(0, len(data_json)):
                comments.append(data_json[i])
        return comments

    @staticmethod
    def comment_on_pull_request(pull_number, failure_reason):
        query_url = f"https://api.github.com/repos/{Config.owner}/{Config.repo}/issues/{pull_number}/comments"
        comment = "We cannot merge the pull request due to following reasons\n\n"
        for reason in failure_reason:
            comment += "- " + reason + "\n"
        comment += "\nKindly make the changes and send the pull request again!"
        print(comment)
        params = {
            "body": comment
        }
        execution_status = False
        try:
            r = GitApi.post_to_url(query_url, params=params, authenticate=True)
            if r.status_code.__eq__(201):
                print("Comment successfully made!")
                execution_status = True
        except Exception as e:
            print(str(e))
        return execution_status

    @staticmethod
    def merge_pull_request(pull_number):
        query_url = f"https://api.github.com/repos/{Config.owner}/{Config.repo}/pulls/{pull_number}/merge"
        params = {
            "commit_title": f"Squash Merge pull request #{pull_number}",
            "commit_message": "Merging automatically",
            "merge_method": "squash"
        }
        execution_status = False
        try:
            r = GitApi.put_to_url(query_url, params, authenticate=True)
            if r.status_code.__eq__(405):
                print("Base branch was modified. Trying the merge again")
                time.sleep(60)
                r = GitApi.put_to_url(query_url, params, authenticate=True)
            if r.status_code.__eq__(200):
                print(json.dumps(r.json(), indent=4, sort_keys=True))
                execution_status = True
        except Exception as e:
            print(str(e))
        return execution_status
