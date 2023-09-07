from os import getenv

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

# API Auth data for ZPA tenant
ZPA_CLIENT_ID: str = getenv('ZPA_CLIENT_ID')
ZPA_CLIENT_SECRET: str = getenv('ZPA_CLIENT_SECRET')
ZPA_CUSTOMER_ID: str = getenv('ZPA_CUSTOMER_ID')

# API Auth data for ZCC portal
ZCC_CLIENT_ID: str = getenv('ZCC_CLIENT_ID')
ZCC_CLIENT_SECRET: str = getenv('ZCC_CLIENT_SECRET')
ZCC_CLOUD: str = getenv('ZCC_CLOUD')

# Name prefix for c2c on and off segments. Segment names will be created using name_prefix_n format where n is a number 0 or greater
CLIENT_ZPA_ON_SEGMENT_NAME_PREFIX: str = getenv('CLIENT_ZPA_ON_SEGMENT_NAME_PREFIX')
CLIENT_ZPA_OFF_SEGMENT_NAME_PREFIX: str = getenv('CLIENT_ZPA_OFF_SEGMENT_NAME_PREFIX')

# ZPA segment group to be referenced in c2c segment creation and access policy (script does not update access policy)
CLIENT_ZPA_SEGMENT_GROUP: str = getenv('CLIENT_ZPA_SEGMENT_GROUP')

# ZCC profile name used to indicate ZPA is either ON or OFF for a client
CLIENT_ZPA_ON_PROFILE_NAME: str = getenv('CLIENT_ZPA_ON_PROFILE_NAME')
CLIENT_ZPA_OFF_PROFILE_NAME: str = getenv('CLIENT_ZPA_OFF_PROFILE_NAME')

# Domain name suffix to be added to the host names retrieved from ZCC
DOMAIN_SUFFIX: str = getenv('DOMAIN_SUFFIX')