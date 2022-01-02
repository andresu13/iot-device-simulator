# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
import uuid
import time
import json
import numpy as np
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
from azure.iot.device import MethodResponse

## remove these lines
import datetime
import csv

## Classes below simulate temperature and humidity sensors
class SensorTemp():
    def __init__(self, min_temp=0, max_temp=100):
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.current_temp = np.random.randint(self.min_temp, self.max_temp)
    def readSensorData(self):
        self.current_temp = np.random.normal(self.current_temp, 2)
        return self.current_temp
    def sensorName(self):
        return "Temperature"
    def sensorID(self):
        return "temp-01"

class SensorHumidity():
    def __init__(self, min_humidity=0, max_humidity=100):
        self.min_humidity = min_humidity
        self.max_humidity = max_humidity
        self.current_humidity = np.random.randint(self.min_humidity, self.max_humidity)
    def readSensorData(self):
        #self.current_temp = random.randrange(self.min_humidity, self.max_humidity)
        self.current_humidity = np.random.normal(self.current_humidity, 2)
        return self.current_humidity
    def sensorName(self):
        return "Humidity"
    def sensorID(self):
        return "humidity-01"

## This method will send Device-to-Cloud (C2D) messages/telemetry
async def send_recurring_telemetry(sensors):
    
    # Send recurring telemetry
    i = 25000
    while True:
        i += 1
        msg_dict  = {}
        for sensor in sensors:
            sensor_name = sensor.sensorName()
            sensor_id = sensor.sensorID()
            sensor_value = sensor.readSensorData()
            #msg_dict[sensor_name] = sensor_value
            msg_dict[sensor_name] = i
        
        #### Sample basic JSON message structure ####
        # json_msg = {"temperature":50, "humidity":{"sensor1": 50, "sensor2":80}}
        # msg = Message(json.dumps(json_msg))
        # msg.content_encoding = "utf-8"
        # msg.content_type = "application/json"

        #### Sample basic CSV message structure ####
        # csv_msg="id,temperature,humidity\n12345,50,80"
        # msg=Message(csv_msg)
        # msg.content_encoding = "utf-8"
        # msg.content_type = "text/csv"


        msg = Message(json.dumps(msg_dict))
        msg.message_id = uuid.uuid4()
        msg.correlation_id = uuid.uuid4()
        msg.content_encoding = "utf-8"
        msg.content_type = "application/json"
        msg.custom_properties["my-custom-property"] = "yes"
        
        print("sending message #" + str(i))
        print(msg)
        print(msg.message_id)
        if(device_client.connected):
            print("I am connected")
        else:
            print("Disconnected")
        try:
            await asyncio.gather(device_client.send_message(msg))
        except Exception as e:
            print(e)
        #    print("I am here")
            #device_client.send_message(msg)
        #except asyncio_tools.CompoundException as exception:
        #    print(exception)
        #except Exception as e:
            #return 'Error sendign IoT message', 500
            #print("Network Connection Issue")
            #raise
        time.sleep(device_properties["send_interval"])

## This method will handle Cloud-to-Device (C2D) messages
def message_received_handler(message):
        print("the data in the message received was ")
        print(message.data)
        print("custom properties are")
        print(message.custom_properties)
        print("content Type: {0}".format(message.content_type))
        print("")

## This method will handle direct method requests
async def method_request_handler(method_request):
        # Determine how to respond to the method request based on the method name
        if method_request.name == "method1":
            payload = {"result": True, "data": "some data"}  # set response payload
            status = 200  # set return status code
            print("executed method1")
        elif method_request.name == "method2":
            payload = {"result": True, "data": 1234}  # set response payload
            status = 200  # set return status code
            print("executed method2")
        else:
            payload = {"result": False, "data": "unknown method"}  # set response payload
            status = 400  # set return status code
            print("executed unknown method: " + method_request.name)

        # Send the response
        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        await device_client.send_method_response(method_response)

## This method will handle device twin update requests
async def twin_patch_handler(patch):
    prop_dict = {}
    print("the data in the desired properties patch was: {}".format(patch))
    ignore_keys = ["__t", "$version"]
    for prop_name, prop_value in patch.items():
        if prop_name not in ignore_keys:
            device_properties[prop_name] = prop_value
    print(device_properties)
    #    print(prop_name, prop_value)
    #    prop_dict[prop_name] = {"ac":200, "ad": "Successfully executed patch", "av": patch["$version"], "value": prop_value}
    #prop_dict["anotherproperty"] = {"ac":200, "ad": "Successfully executed patch", "av": 6, "value": 15}
    #prop_dict["version"] = 76
    #print(patch["$version"])
    await device_client.patch_twin_reported_properties(device_properties)

async def main():
    # The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
    #conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
    conn_str = "HostName=iot-demo-hub1.azure-devices.net;DeviceId=simulated-vm-device1;SharedAccessKey=dCDgVItTl0j+nrddy/MHXX/fTv/S9EVemLzTB4AGjdU="
    # The client object is used to interact with your Azure IoT hub.
    global device_client
    global device_properties
    
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the client.
    await device_client.connect()

    # Get desired properties from device twin (such as send interval)
    twin = await device_client.get_twin()
    device_properties = twin["desired"]
    device_properties.pop("$version")
    print(twin["desired"])

    # Set the method request handlers for receiving messages (D2C), receiving direct methods and device twin updates
    device_client.on_message_received = message_received_handler
    device_client.on_method_request_received = method_request_handler
    device_client.on_twin_desired_properties_patch_received = twin_patch_handler



    #print(asyncio.all_tasks())


    ##### DELETE THIS #################
    # # define behavior for halting the application
    # def stdin_listener():
    #     while True:
    #         selection = input("Press Q to quit\n")
    #         if selection == "Q" or selection == "q":
    #             print("Quitting...")
    #             break
    # loop = asyncio.get_running_loop()
    
    # user_finished = loop.run_in_executor(None, stdin_listener)

    # await user_finished
    
    # print("HELLO THERE!!!!")
    # # Finally, shut down the client
    # await device_client.shutdown()
    #####################################

    # Initialize sensors
    sensor_temp = SensorTemp()
    sensor_humidity = SensorHumidity()
    sensor_list = [sensor_temp, sensor_humidity]

    # Start sending telemetry
    print("IoTHub Device Client Recurring Telemetry Sample")
    print("Press Ctrl+C to exit")
    try:
        await send_recurring_telemetry(sensor_list)
        #await send_recurring_telemetry([sensor_temp])
        #asyncio.gather(send_recurring_telemetry([sensor_temp]), send_recurring_telemetry([sensor_humidity]))
        #asyncio.gather(send_recurring_telemetry([sensor_temp]))
    except KeyboardInterrupt:
        print("User initiated exit")
    except Exception:
        print("Unexpected exception!")
        raise
    finally:
        await device_client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())