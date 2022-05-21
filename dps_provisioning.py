import hashlib
import base64
import hmac
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import X509

# NOTE : Only for illustration purposes.
# This is how a device key can be derived from the group symmetric key.
# This is just a helper function to show how it is done.
# Please don't directly store the group master key on the device.
# Follow the following method to compute the device key somewhere else.


def derive_device_key(device_id, group_symmetric_key):
    """
    The unique device ID and the group master key should be encoded into "utf-8"
    After this the encoded group master key must be used to compute an HMAC-SHA256 of the encoded registration ID.
    Finally the result must be converted into Base64 format.
    The device key is the "utf-8" decoding of the above result.
    """
    message = device_id.encode("utf-8")
    signing_key = base64.b64decode(group_symmetric_key.encode("utf-8"))
    signed_hmac = hmac.HMAC(signing_key, message, hashlib.sha256)
    device_key_encoded = base64.b64encode(signed_hmac.digest())
    return device_key_encoded.decode("utf-8")

async def dps_register(auth_type="symmetric"):
    ### Specify ModelID for IoT Plug and Play DTDL ###
    model_id = "dtmi:iotDemoCentral:Raspberry_1ig;1"

    ### Required Configurations ###
    PROVISIONING_HOST = "global.azure-devices-provisioning.net"
    #ID_SCOPE = "0ne00462BED" # For my demo IoT Hub
    ID_SCOPE = "0ne00486E0D" # for my demo IoT Central
    auth_type = auth_type
    print(auth_type)

    if auth_type == "symmetric":
        print("DPS: Symmetric Key")
        #DEVICE_ID = "simulated-vm-dps-device1" # For my demo IoT Hub
        #DERIVED_KEY = derive_device_key(DEVICE_ID, "9ug7D8y5i9d534LKMwWUKzxrhtyp50/OltuRWm68WGGpPsuBiv0d9T6oJDENUQ/36B8vfNWObXpbc+EjVCWtrw==") # For my demo IoT Hub
        PRIMARY_KEY = "6WobjdlSK4b2Zkh9+iZDa11Wu/C6cOnFHDte1YA0WKyDgKIyhLwrTCeBj21ZIPHVbbS36ISVy2CFCKenEArbwA=="
        DEVICE_ID = "raspberry-iotdevice-17" # For my demo IoT Central
        DERIVED_KEY = derive_device_key(DEVICE_ID, PRIMARY_KEY) # For my demo IoT Central
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(PROVISIONING_HOST,DEVICE_ID,ID_SCOPE,DERIVED_KEY)

        ### Optional: Send ModelId to DPS to auto-assign template in IoT Central
        provisioning_device_client.provisioning_payload = {"modelId":model_id}
        ###

        prov_result = await provisioning_device_client.register()
        print("DPS Registration Information:")
        print(prov_result.registration_state)
        if prov_result.status == "assigned":
            iot_assigned_hub = prov_result.registration_state.assigned_hub
            device_client = IoTHubDeviceClient.create_from_symmetric_key(symmetric_key=DERIVED_KEY,hostname=iot_assigned_hub, device_id=DEVICE_ID)
            
    
    elif auth_type == "X509":
        print("DPS: X509")
        DEVICE_ID = "simulated-vm-dps-X509-device1"
        #X509_CERT_FILE = "certs_public/"+DEVICE_ID+".pem"
        X509_CERT_FILE = "certs_public/simulated-vm-dps-X509-device1.chain.pem"
        print(X509_CERT_FILE)
        X509_KEY_FILE = "certs_private/"+DEVICE_ID+".key.pem"
        #X509_KEY_FILE = "certs_private/simulated-vm-dps-X509-device2.key.pem"
        PASSPHRASE = "1234"
        x509 = X509(cert_file=X509_CERT_FILE, key_file=X509_KEY_FILE)
        provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(PROVISIONING_HOST,DEVICE_ID,ID_SCOPE,x509)
        prov_result = await provisioning_device_client.register()
        print("DPS Registration Information:")
        print(prov_result.registration_state)
        if prov_result.status == "assigned":
            iot_assigned_hub = prov_result.registration_state.assigned_hub
            device_client = IoTHubDeviceClient.create_from_x509_certificate(x509,hostname=iot_assigned_hub, device_id=DEVICE_ID)

    
    else:
        print("TPM attestation")
        #else:
        #    print("shit failed")
        #   raise "Device could not be registered with DPS"
    
    return device_client
