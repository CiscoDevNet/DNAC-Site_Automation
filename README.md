# Cisco DNA Center - Assign Network Devices to Site

Dynamically create and assign sites and devices using Cisco DNA Center APIs
- Obtain the Device to Site Mapping
- Source is a JSON 
- Get Site and Device information
- Assign Network Device to Site
- Ready for Cisco DNA Center Automation and Assurance

## Getting Started
Use the follwing command to create your sites in Cisco DNA Center. sites are defined in **site-info.json** file:

```bash
python create-site.py site-info.json
```

After you've succesfully setup your sites, you can start assigns devices to site. device to site assignment is defined in **device-to-site.json** file. run the command below once ready: 
```bash
python device-to-site.py device-to-site.json
```

> Note: You change the controller credentials either through environment variables or by editing the dnac_config.py file

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.
