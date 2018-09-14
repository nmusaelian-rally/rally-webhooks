import sys, os
import json
import yaml
import requests

class WebhookRequest:
    def __init__(self, config_path):
        self.config = self.read_config(config_path)
        self.protocol  = self.config.get('Protocol', 'https')
        self.server    = self.config.get('Server',   'rally1.rallydev.com/apps/pigeon/api/v2/webhook')
        self.apikey    = self.config.get('ApiKey',    None)
        self.pagesize  = self.config.get('Pagesize', 200)
        self.base_url = "%s://%s" %(self.protocol, self.server)
        self.headers   = {"content-type": "appication/json"}
        if self.apikey:
            self.headers['cookie'] = "ZSESSIONID=%s" % self.apikey

    def read_config(self, config_path):
        with open(config_path, 'r') as cf:
            content = cf.read()
            conf = yaml.load(content)
        return conf

    def getPage(self):
        try:
            response = requests.get(self.base_url, headers=self.headers, params={"pagesize":self.pagesize})
            response = response.json()
            result_count = response['TotalResultCount']
            results      = response['Results']
        except requests.exceptions.RequestException as e:
            print (e)
            sys.exit(1)
        return result_count, results

    def get(self, uuid):
        url = "%s/%s" % (self.base_url, uuid)
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                response = response.json()
        except requests.exceptions.RequestException as e:
            print (e)
            sys.exit(1)
        return response

    def post(self, payload):
        try:
            response = requests.post(self.base_url, headers=self.headers, data=json.dumps(payload))
            response = response.json()
        except requests.exceptions.RequestException as e:
            print (e)
            sys.exit(1)
        return response

    def patch(self, uuid, payload):
        url = "%s/%s" % (self.base_url, uuid)
        try:
            response = requests.patch(url, headers=self.headers, data=json.dumps(payload))
            response = response.json()
        except requests.exceptions.RequestException as e:
            print (e)
            sys.exit(1)
        return response

    def delete(self, uuid):
        url = "%s/%s" % (self.base_url, uuid)
        try:
            response = requests.delete(url, headers=self.headers)
            result = response.json()
        except requests.exceptions.RequestException as e:
            print (e)
            sys.exit(1)
        return result

# def main():
#     wr  = WebhookRequest('configs/config.yml')
#     result_count, results = wr.getPage()
#     print(result_count)
#     for item in results:
#         print(item)
#
#
# if __name__ == '__main__':
#     main()