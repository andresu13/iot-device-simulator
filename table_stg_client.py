from azure.data.tables import TableClient
my_filter = "PartitionKey eq 'device_id'"
table_client = TableClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=andresu13storage;AccountKey=8cAytC4rtq6JfCgonlAZZft8xRhBmwNDwMSYgErfUiKYZ6TTsYqSKOf+3aD9gElSu1g0lIdyGx/AjNdHxR2Sgg==;EndpointSuffix=core.windows.net", table_name="iottablestg1")
entities = table_client.query_entities(my_filter)
#entities = table_client.query_entities()
for entity in entities:
    for key in entity.keys():
        print("Key: {}, Value: {}".format(key, entity[key]))