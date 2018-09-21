import sys, os
sys.path.insert(0, '/Users/pairing/nick/rally-webhooks')
from webhook_adapter import WebhookRequest

yeti_id = '4c3f7050-3d68-4f5d-8b6b-e9ef0b21d69a'
wr    = WebhookRequest('configs/config.yml')

def test_getAll():
    result_count, results = wr.getPage()
    print(result_count)
    for item in results:
        print(item)
    if len(results) <= 200:
        assert result_count == len(results)

def test_getYetiWebhooks():
    result_count, results = wr.getPage()
    my_webhooks = [{item['ObjectUUID'] : item} for item in results if item['OwnerID'] == yeti_id]
    print(len(my_webhooks))
    for wh in my_webhooks:
        print (wh)

def test_getWebhookByID():
    webhook_uuid = '8aabeab3-cedb-46a7-b7da-edecb29af493'
    webhook = wr.get(webhook_uuid)
    assert webhook['OwnerID']   == yeti_id
    assert webhook['TargetUrl'] == 'http://alligator.proxy.beeceptor.com'
    assert webhook['Security']  == 'abc123'
    assert webhook['Expressions'][0]['AttributeName'] == 'ScheduleState'
    assert webhook['Expressions'][0]['Value'] == 'In-Progress'
    assert 'HierarchicalRequirement' in webhook['ObjectTypes']

def test_getNonExistingWebhook():
    webhook_uuid = 'ceaff839-c80d-49c9-ab3e-7dca59eb5c7e'
    response = wr.get(webhook_uuid)
    assert response.status_code == 404

def test_deleteNonExistingWebhook():
    webhook_uuid = 'ceaff839-c80d-49c9-ab3e-7dca59eb5c7e'
    result = wr.delete(webhook_uuid)
    assert result['Errors'][0]['message'] == 'Webhook not found'

def test_deleteWebhook():
    webhook_uuid = '9023eaf8-4e53-46c7-adf1-f393a8956401'
    response = wr.get(webhook_uuid)
    if isinstance(response, dict):
        result = wr.delete(webhook_uuid)
        assert result == {}

def test_postAndPatch():
    payload = {
        "AppName"    : "jakaloof-foo",
        "AppUrl"     : "foobar.com",
        "Name"       : "completed stories and defects",
        "TargetUrl"  : "http://alligator.proxy.beeceptor.com",
        "Security"   : "#1234!$#^&",
        "ObjectTypes": ["HierarchicalRequirement","Defect"],
        "Expressions": [{"Operator" : "=", "AttributeName" : "ScheduleState", "Value" : "Completed"}],

    }
    new_wh = wr.post(payload)
    print(new_wh)
    assert new_wh['SubscriptionID'] == 209
    assert new_wh['OwnerID']        == yeti_id

    webhook_uuid = new_wh['ObjectUUID']
    workspace_uuid = '7d1bc994-cb0a-4d2d-b172-62f81912ad34'
    payload = {
        "Expressions": [{"AttributeName": "ScheduleState", "Operator": "=", "Value": "Completed"},
                        {"AttributeName": "Workspace", "Operator": "=", "Value": workspace_uuid}]
    }
    updated_wh = wr.patch(webhook_uuid, payload)
    print(updated_wh)
    expressions = updated_wh['Expressions']
    expression = [exp for exp in expressions if exp['AttributeName'] == 'Workspace'][0]
    assert expression['Value'] == workspace_uuid


def test_postWebhook4Feature():
    payload = {
        "AppName"    : "jakaloof-foo",
        "AppUrl"     : "foobar.com",
        "Name"       : "completed stories and defects",
        "TargetUrl"  : "http://alligator.proxy.beeceptor.com",
        "Security"   : "#1234!$#^&",
        "ObjectTypes": ["Feature"],  #use Feature instead of PortfolioItem/Feature
        "Expressions": [{"Operator" : "=", "AttributeName" : "FormattedID", "Value" : "F2"},
                        {"Operator" : "=", "AttributeName" : "Workspace", "Value" : "7d1bc994-cb0a-4d2d-b172-62f81912ad34"}],
    }
    new_wh = wr.post(payload)
    print(new_wh)
    assert new_wh['SubscriptionID'] == 209
    assert new_wh['ObjectTypes']    == ['Feature']

def test_sub100():
    wr100 = WebhookRequest('configs/configkip100.yml')
    workspace_uuid = '3497d043-3ea7-4c8a-bf78-069847936c13' #Rally
    project_uuid   = '87b9a219-7bb9-40e9-8afe-96430e11d6f1' #AT
    payload = {
        "AppName"    : "alligator-tiers",
        "AppUrl"     : "foobar.com",
        "Name"       : "defects in AT",
        "TargetUrl"  : "http://alligator.proxy.beeceptor.com",
        "Security"   : "#1234!$#^&",
        "ObjectTypes": ["Defect"],
        "Expressions": [{"AttributeName" : "State",     "Operator" : "!=", "Value" : "Fixed"},
                        {"AttributeName" : "Workspace", "Operator" : "=",  "Value" : workspace_uuid},
                        {"AttributeName" : "Project",   "Operator" : "=",  "Value" : project_uuid}]
    }
    new_wh = wr100.post(payload)
    print(new_wh)
    assert new_wh['SubscriptionID'] == 100
    expressions = new_wh['Expressions']
    expression = [exp for exp in expressions if exp['AttributeName'] == 'Project'][0]
    assert expression['Value'] == project_uuid

def test_getNMWebhooks():
    nm_id = 'dd160a48-4dab-4c3f-a0ea-c94d77ac5735'
    kip_id = '8cbe0a5a-8f10-4aa3-8be3-6366096676ef'
    wr100 = WebhookRequest('configs/configkip100.yml')
    result_count, results = wr100.getPage()
    #my_webhooks = [{item['ObjectUUID'] : item} for item in results if item['OwnerID'] == nm_id]
    my_webhooks = [{item['ObjectUUID'] : item} for item in results if item['OwnerID'] == kip_id]
    print(len(my_webhooks))
    for wh in my_webhooks:
        print (wh)

def test_fawltyServer():
    payload = {
        "AppName": "jakaloof-foo",
        "AppUrl": "foobar.com",
        "Name": "completed stories and defects",
        #"TargetUrl": "http://wombat.f4tech.com:8885",
        "TargetUrl": "http://dae835ff.ngrok.io",
        "Security": "#1234!$#^&",
        "ObjectTypes": ["Feature"],  # use Feature instead of PortfolioItem/Feature
        "Expressions": [{"Operator": "=", "AttributeName": "FormattedID", "Value": "F2"},
                        {"Operator": "=", "AttributeName": "Workspace",
                         "Value": "7d1bc994-cb0a-4d2d-b172-62f81912ad34"}],
    }
    new_wh = wr.post(payload)
    print(new_wh)
    assert new_wh['SubscriptionID'] == 209
    assert new_wh['ObjectTypes'] == ['Feature']