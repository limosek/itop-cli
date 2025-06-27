# itop-cli
iTop CLI client used to fetch, get or modify objects within iTop using CLI.
It uses REST API calls.

## Install
```
git clone https://github.com/limosek/itop-cli.git
cd itop-cli
pip3 -r requirements.txt

python3 itop-cli.py --help
```

## Configure

If you do not want to enter all config variables on every run,
create itop-cli.cfg in actual directory and configure as arguments.
```
--output-format=json
--itop-url=https://itop.instance.test
--itop-user=user
--itop-password=password
--continue-on-error=1

```

## Examples

### Search for all VirtualMachines and return full json on one line
```
python3 itop-cli.py list VirtualMachine
[{"name": "db1-brno", "description": "", "org_id": "71", "organization_name": "Acme, a.s.", "business_criticity": "high", ...
```

### Search for all VirtualMachines and return nice json
```
python3 itop-cli.py --output-format=json-pretty list VirtualMachine
[
  {
    "name": "db1-brno",
    "description": "",
    "org_id": "71",
    "organization_name": "Acme, a.s.",
    "business_criticity": "high",
    "move2production": "",
    "contacts_list": [],
    "documents_list": [],
    "applicationsolution_list": [
      {
        "applicationsolution_id": "109",
        "applicationsolution_name": "ERP",
        "friendlyname": "ERP / db1-brno",
        "applicationsolution_id_friendlyname": "ERP",
        "applicationsolution_id_obsolescence_flag": ""
      }
    ],
    "softwares_list": [
      {
 ...
       }
    ],
    "providercontracts_list": [],
    "services_list": [],
    "tickets_list": [],
    "status": "production",
    "logicalvolumes_list": [],
    "virtualhost_id": "99",
    "virtualhost_name": "Pve-farm1-Brno",
    "osfamily_id": "15",
    "osfamily_name": "Debian",
    "osversion_id": "43",
    "osversion_name": "12.0 Bookworm",
    "oslicence_id": "0",
    "oslicence_name": "",
    "cpu": "",
    "ram": "",
    "logicalinterface_list": [],
    "managementip_id": "0",
    "managementip_name": "",
    "finalclass": "VirtualMachine",
    "friendlyname": "db1-brno",
    "obsolescence_flag": false,
    "obsolescence_date": "",
    "org_id_friendlyname": "Acme, a.s.",
    "org_id_obsolescence_flag": "",
    "virtualhost_id_friendlyname": "Pve-farm1-Brno",
    "virtualhost_id_finalclass_recall": "Farm",
    "virtualhost_id_obsolescence_flag": "",
    "osfamily_id_friendlyname": "Debian",
    "osversion_id_friendlyname": "12.0 Bookworm",
    "oslicence_id_friendlyname": "",
    "oslicence_id_obsolescence_flag": "",
    "managementip_id_friendlyname": "",
    "managementip_id_finalclass_recall": "",
    "id": "106"
  },
  ...
  
```

### Search for all VirtualMachines and return CSV
```
python3 itop-cli.py --output-format=csv list VirtualMachine
name,id
db1-brno,106
docker1,46
...
```

```
python3 itop-cli.py --output-fields=id,name,business_criticity,org_id --output-format=csv list VirtualMachine
id,name,business_criticity,org_id
106,db1-brno,high,71
46,docker1,low,1
...
```

### Use OQL to filter objects
```
python3 itop-cli.py --output-format=csv list VirtualMachine "SELECT VirtualMachine WHERE org_id=71"
name,id
db1-brno,106
Windows-VM-Brno,130
www1-brno,105

```

### Fetch DNS zone (ipam plugin must be installed)
```
python3 itop-cli.py fetch-zone internal.lan.

$TTL 86400
@ IN SOA internal.lan. root.internal.lan. (
                 2220    ; Serial
                 900     ; Refresh
                 600     ; Retry
                 604800  ; Expire
                 300 )   ; Negative caching

;
; Name servers
;

;
; IPv4 addresses for the canonical names
;
host1                       IN A          192.168.1.2
host2                       IN A          192.168.1.3

```

```
python3 itop-cli.py fetch-zone 168.192.in-addr.arpa.

$TTL 86400
@ IN SOA internal.lan. root.internal.lan. (
                 3       ; Serial
                 900     ; Refresh
                 600     ; Retry
                 604800  ; Expire
                 300 )   ; Negative caching

;
; Name servers
;

;
; Addresses point to canonical names
;

2       IN PTR some-other.internal.lan
```

## Generate Ansble inventory
Generates ansible inventory.
First parameter VirtualMachine defines expected objects to search
Second parameter org_id defines which groups to create based on attribute values
Third parameter defines which attribute to use as a reference for host
```
python3 itop-cli.py ansible-inventory VirtualMachine osfamily_id_friendlyname name

[VirtualMachine]
db1-brno

[osfamily_id_friendlyname_Debian]
db1-brno
```

```
python3 itop-cli.py ansible-inventory VirtualMachine,Server osfamily_id_friendlyname managementip_name

[VirtualMachine]
; Missing managementip_name on db1-brno
db2-brno.local.

[Server]
db3-brno.local.

[osfamily_id_friendlyname_Debian]
db2-brno.local.

```

