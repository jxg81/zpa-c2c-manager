# ZPA Client-to-Client and Server-to-Client Utilities

A collection of tools for managing name resolution and forwarding rules on ZPA infrastructure during and post migration to ZPA for client-to-client and server-to-client use cases.

> [!IMPORTANT]
> These utilities are not affiliated with, nor supported by Zscaler in any way.

## Client-to-client Segment Management
`manage_fqdn.py`

Allocate client device fqdns to app segments to manage client-to-client forwarding during migration to ZPA.

This script interrogates the Zscaler Client Connector registered devices and retrieves the mapping of device names to app profiles. Based on the assigned app profile the device will be allocated to an appropriate ZPA app segment to either enable or disable ZPA forwarding for client-to-client connections.

The following environment variables are required.

**ZPA_CLIENT_ID**

[ZPA API Client ID](https://admin.private.zscaler.com/#clientCredentials)

**ZPA_CLIENT_SECRET**

[ZPA API Secret](https://admin.private.zscaler.com/#clientCredentials)

**ZPA_CUSTOMER_ID**

[ZPA Tenant ID](https://admin.private.zscaler.com/#company)

**ZCC_CLIENT_ID**

[ZCC API Client ID](https://help.zscaler.com/client-connector/adding-api-key)

**ZCC_CLIENT_SECRET**

[ZCC API Secret](https://help.zscaler.com/client-connector/adding-api-key)

**ZCC_CLOUD**

ZCC Cloud Name, options are:
 - zscaler
 - zscalerone
 - zscalertwo
 - zscalerthree
 - zscloud
 - zscalerbeta
 - zscalerten

**CLIENT_ZPA_ON_SEGMENT_NAME_PREFIX**

Name prefix to be applied to app segments that contain fqdns where ZPA forwarding is *ENABLED*. Segments will be automatically chunked into groups not exceeding 2000 individual fqdns and prepended with a number starting from 0.

**CLIENT_ZPA_OFF_SEGMENT_NAME_PREFIX**

Name prefix to be applied to app segments that contain fqdns where ZPA forwarding is *DISABLED*. Segments will be automatically chunked into groups not exceeding 2000 individual fqdns and prepended with a number starting from 0.

**CLIENT_ZPA_SEGMENT_GROUP**

Segment group to be applied to ZPA app segments. This segment group should be referenced in access policy to permit or deny client-to-client access.

**CLIENT_ZPA_ON_PROFILE_NAME**

ZCC App Profile name assigned to users where ZPA forwarding will be *ENABLED*.

**CLIENT_ZPA_OFF_PROFILE_NAME**

ZCC App Profile name assigned to users where ZPA forwarding will be *DISABLED*.

**DOMAIN_SUFFIX**

ZCC devices are returned without a domain suffix. Set this value to add a common domain suffix to all devices. Suffix should include a leading dot.

Do This:

*DOMAIN_SUFFIX=.example.com*

Don't Do This:

*DOMAIN_SUFFIX=example.com*

### Packaging for AWS Lambda

The script has been designed to support packaging and deployment to AWS Lambda. Run the supplied bash script `package_lambda_function.sh` to download and package the script and dependencies into a Lambda deploy script named `lambda_package.zip`. The script is designed to run on unix/macos systems and should be executed from the root of the repo store.