# RAS - Random AWS Scripts
Collection of random, useful AWS scripts

## Get EIPs
By default checks all regions of all configured profiles and prints EIPs (Public IPs) per region

Can be configured to just check specific configured profiles or regions
#### Usage
To get all EIPs in all regions for all configured aws profiles:
`get_eips.py`

To get all EIPs in all regions for specified aws profiles:
`get_eips.py --aws-profile profile1 profile2`

To get all EIPs in specified regions :
`get_eips.py  --region eu-west-1 eu-west-2 us-east-1`

