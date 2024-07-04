import os
from pyzscaler import ZPA, ZCC
from box import Box, BoxList
from time import sleep

from const import ZPA_CLIENT_ID, ZPA_CLIENT_SECRET, ZPA_CUSTOMER_ID, ZCC_CLIENT_ID, ZCC_CLIENT_SECRET, ZCC_CLOUD, DOMAIN_SUFFIX, SLEEP_TIME, CREATE_OFF_SEGMENTS, DOWNLOAD_DEVICES
from const import CLIENT_ZPA_ON_SEGMENT_NAME_PREFIX, CLIENT_ZPA_OFF_SEGMENT_NAME_PREFIX, CLIENT_ZPA_ON_PROFILE_NAME, CLIENT_ZPA_OFF_PROFILE_NAME, CLIENT_ZPA_SEGMENT_GROUP


def chunk_list(lst: list, chunk_size: int = 2000) -> list:
    """
    Create a list of lists of nominated chunk size
    
    Args:
        lst: The source list to be broken down
        chunk_size: Target size of chunks (default is 2000)
    """
    chunked_lists = []
    while lst:
        chunk, lst = lst[:chunk_size], lst[chunk_size:]
        chunked_lists.append(chunk)
    return chunked_lists

def collect_zcc_data(zcc: ZCC) -> list:
    """
    Get a list of all devices with ZPA ON profile and ZPA OFF profile
    
    Args:
        zcc: ZCC AP Session Client
    """
    zcc_devices: Box = zcc.devices.list_devices(page_size=5000)
    zpa_on_zcc_devices = []
    zpa_off_zcc_devices = []
    
    for device in zcc_devices:
        if device.policy_name == CLIENT_ZPA_ON_PROFILE_NAME and device.registration_state != 'Removed':
            zpa_on_zcc_devices.append(f"{device.machine_hostname.lower()}{DOMAIN_SUFFIX}")
        if device.policy_name == CLIENT_ZPA_OFF_PROFILE_NAME and device.registration_state != 'Removed':
            zpa_off_zcc_devices.append(f"{device.machine_hostname.lower()}{DOMAIN_SUFFIX}")
    return zpa_on_zcc_devices, zpa_off_zcc_devices

def collect_zcc_data_download_devices(zcc: ZCC) -> list:
    """
    Alternate method to list of all devices with ZPA ON profile and ZPA OFF profile
    
    This method uses the 'downloadDevices' API to download the full list of devices which is heavily rate limited by Zscaler
    MAX 3 CALLS PER DAY
    
    Args:
        zcc: ZCC AP Session Client
    """
    zcc.devices.download_devices(filename='zcc-devices.csv')
    
    with open('zcc-devices.csv', 'r') as file:
        data = file.read()
        zcc_devices: Box = BoxList.from_csv(data)
    
    os.remove('zcc-devices.csv')
    
    zpa_on_zcc_devices = []
    zpa_off_zcc_devices = []
    
    for device in zcc_devices:
        if device.policy_name == CLIENT_ZPA_ON_PROFILE_NAME and device.registration_state != 'Removed':
            zpa_on_zcc_devices.append(f"{device.machine_hostname.lower()}{DOMAIN_SUFFIX}")
        if device.policy_name == CLIENT_ZPA_OFF_PROFILE_NAME and device.registration_state != 'Removed':
            zpa_off_zcc_devices.append(f"{device.machine_hostname.lower()}{DOMAIN_SUFFIX}")
    return zpa_on_zcc_devices, zpa_off_zcc_devices
    
def manage_zpa_segments(zpa: ZPA, zpa_on_lists: list, zpa_off_lists: list) -> None:
    """
    Delete all existing c2c app segments and re-create with updated data
    
    Args:
        zpa: ZPA AP Session Client
        zpa_on_lists: A list of lists with device host names to be routed via ZPA
        zpa_off_lists: A list of lists with device host names to be bypassed for ZPA
    """
    # Grab segment group id to be used in app segment creation
    segment_group_id = [group.id for group in zpa.segment_groups.list_groups() if group.name == CLIENT_ZPA_SEGMENT_GROUP][0]
    
    # Grab existing c2c app segments from ZPA
    app_segments: Box = zpa.app_segments.list_segments()
    zpa_on_segments: list = [segment for segment in app_segments if segment.name[0:len(CLIENT_ZPA_ON_SEGMENT_NAME_PREFIX)] == CLIENT_ZPA_ON_SEGMENT_NAME_PREFIX]
    zpa_off_segments: list = [segment for segment in app_segments if segment.name[0:len(CLIENT_ZPA_OFF_SEGMENT_NAME_PREFIX)] == CLIENT_ZPA_OFF_SEGMENT_NAME_PREFIX]
    
    # delete existing c2c segment groups
    for segment in zpa_on_segments:
        sleep(SLEEP_TIME)
        zpa.app_segments.delete_segment(segment.id)
    
    if CREATE_OFF_SEGMENTS:
        for segment in zpa_off_segments:
            sleep(SLEEP_TIME)
            zpa.app_segments.delete_segment(segment.id)
        
    # create new c2c segment groups
    for zpa_on_list in zpa_on_lists:
        sleep(SLEEP_TIME)
        zpa.app_segments.add_segment(f'{CLIENT_ZPA_ON_SEGMENT_NAME_PREFIX}_{zpa_on_lists.index(zpa_on_list)}',
                                     zpa_on_list,
                                     segment_group_id,
                                     [],
                                     ['1', '52', '54', '65534'],
                                     ['1', '52', '54', '65534'],
                                     bypass_type = 'NEVER',
                                     health_check_type = 'NONE',
                                     is_cname_enabled = True)
    if CREATE_OFF_SEGMENTS:
        for zpa_off_list in zpa_off_lists:
            sleep(SLEEP_TIME)
            zpa.app_segments.add_segment(f'{CLIENT_ZPA_OFF_SEGMENT_NAME_PREFIX}_{zpa_off_lists.index(zpa_off_list)}',
                                        zpa_off_list,
                                        segment_group_id,
                                        [],
                                        [],
                                        [],
                                        bypass_type = 'ALWAYS ',
                                        health_check_type = 'NONE',
                                        is_cname_enabled = True)

def manage_segments():
    # Setup session with ZCC and ZPA
    zcc: ZCC = ZCC(client_id=ZCC_CLIENT_ID, client_secret=ZCC_CLIENT_SECRET, cloud=ZCC_CLOUD, override_url=f"https://api-mobile.{ZCC_CLOUD}.net/papi")
    zpa: ZPA = ZPA(client_id=ZPA_CLIENT_ID, client_secret=ZPA_CLIENT_SECRET, customer_id=ZPA_CUSTOMER_ID)
    
    # Get flat lists of all devices from zcc with zpa on or zpa off profiles and format the names with the correct domain suffix
    if DOWNLOAD_DEVICES:
        zpa_on_zcc_devices, zpa_off_zcc_devices= collect_zcc_data_download_devices(zcc)
    else:
        zpa_on_zcc_devices, zpa_off_zcc_devices= collect_zcc_data(zcc)
    
    # Chunk lists in to groups of 2000 or less
    zpa_on_zcc_devices_chunked: list = chunk_list(zpa_on_zcc_devices)
    zpa_off_zcc_devices_chunked: list = chunk_list(zpa_off_zcc_devices)
    
    # Delete and recreate app_segments based on chunked device lists
    manage_zpa_segments(zpa, zpa_on_zcc_devices_chunked, zpa_off_zcc_devices_chunked)

if __name__ == "__main__":
    manage_segments()