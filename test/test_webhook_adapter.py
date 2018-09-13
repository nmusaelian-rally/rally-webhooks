from webhook_adapter import WebhookRequest

yeti_id = '4c3f7050-3d68-4f5d-8b6b-e9ef0b21d69a'
wr  = WebhookRequest('../configs/config.yml')

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
    webhook_uuid = 'c898d5e1-04e7-4f8c-95c7-28ac04f1f285'
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