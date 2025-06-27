import csv
import json
import sys
import requests
import whois
import itoptop.exceptions
from itoptop import Itop
from config import Config


def obj2query(o):
    try:
        (c, id) = o.split("/")
    except Exception as e:
        raise Exception("Bad object url to parse! Use object/id")
    return [c, id, {'id': id}]

def print_object(o):
    if Config.c.output_format=="json":
        print(json.dumps(o))
    elif Config.c.output_format == "json-pretty":
        print(json.dumps(o, indent=2))
    elif Config.c.output_format == "csv":
        if Config.c.output_fields:
            c = csv.DictWriter(sys.stdout, fieldnames=Config.c.output_fields, extrasaction="ignore")
        else:
            c = csv.DictWriter(sys.stdout, fieldnames=o[0].keys())
        c.writeheader()
        for row in o:
            c.writerow(row)

def get_object(i, o):
    o = obj2query(o)
    data = i.schema(o[0]).find(o[2])
    if len(data) == 0 :
        raise Exception("Object %s not found.")
    print_object(data)

def list_objects(i, f):
    if len(f) > 1:
        if f[1].startswith("{"):
            filter = json.loads(f[1])
        elif f[1].startswith("SELECT"):
            filter = {'id': " ".join(f[1:])}
        else:
            if len(f) == 2:
                filter = {'id': f[1]}
            else:
                filter = {}
                for p in f[1:]:
                    if p.find("=") > 0:
                        (a, v) = p.split("=")
                        filter[a] = v
                    else:
                        raise Exception("Use attr=value [attr=value]")
        data = i.schema(f[0]).find(filter)
    else:
        data = i.schema(f[0]).find()
    if type(data) is dict:
        data = [data]
    if Config.c.count:
        print(len(data))
    else:
        print_object(data)

def create_object(i, data):
    if len(data) == 1:
        jsn = json.load(sys.stdin)
    elif len(data) > 1:
        jsn = json.loads(" ".join(data[1:]))
    else:
        raise Exception("add {json}")
    if type(jsn) is list:
        for o in jsn:
            print(o)
            try:
                ret = i.schema(data[0]).insert(o)
            except itoptop.exceptions.ItopError as e:
                if Config.c.continue_on_error:
                    print(e, sys.stderr)
                else:
                    print(e, sys.stderr)
                    sys.exit(1)
    else:
        ret = i.schema(data[0]).insert(jsn)

def update_domain_dates(i, d):
    domains = i.schema('Domain').find()
    for d in domains:
        print(d["name"])
        try:
            w = whois.whois(d["name"][:-1])
            jsn = {}
            if "creation_date" in w and w["creation_date"]:
                if type(w["creation_date"]) is list:
                    jsn["validity_start"] = w["creation_date"][0].strftime("%Y-%m-%d")
                else:
                    jsn["validity_start"] = w["creation_date"].strftime("%Y-%m-%d")
            if "expiration_date" in w and w["expiration_date"]:
                if type(w["expiration_date"]) is list:
                    jsn["validity_end"] = w["expiration_date"][0].strftime("%Y-%m-%d")
                else:
                    jsn["validity_end"] = w["expiration_date"].strftime("%Y-%m-%d")
            if jsn != {}:
                i.schema("Domain").update({'id': d["id"]}, jsn)
            else:
                print("No whois info")
        except Exception as e:
            pass

def fetch_zone(i, d):
    zone = d[0]
    data = {
            'version': i.version,
            'auth_user': i.auth_user,
            'auth_pwd': i.auth_pwd,
            'json_data': json.dumps({
                'operation': 'teemip/get_zone_file',
                'class': 'Zone',
                'key': {
                    'org_id': 1,
                    'name': zone
                    # 'view_id': 1,
                },
                'format': 'sort_by_record'
            })
        }
    r = requests.post(
        i.url,
        data=data
    )
    json_return = json.loads(r.content.decode('utf-8'))
    return_code = json_return['code']
    r.raise_for_status()
    if return_code == 0 and json_return["objects"]:
        print(list(json_return["objects"].values())[0]["text_file"])
    else:
        print("Error!", file=sys.stderr)
        print(json_return, file=sys.stderr)
        sys.exit(2)

def ansible_inventory(i, d):
    if len(d) < 3:
        raise Exception("Use ansible-inventory objects grp_attributes target [variables]")
    objects = d[0].split(",")
    attributes = d[1].split(",")
    target = d[2]
    if len(d) == 4:
        variables = d[3].split(",")
    else:
        variables = []
    inventory = {}
    for o in objects:
        if o not in inventory:
            inventory[o] = {}
        objs = i.schema(o).find()
        for fo in objs:
            inventory[o][fo["name"]] = fo
            for a in attributes:
                av = a + "_" + fo[a]
                if av not in inventory:
                    inventory[av] = {}
                inventory[av][fo["name"]] = fo
    for grp in inventory.keys():
        print("["+grp+"]")
        for h in inventory[grp]:
            host = inventory[grp][h][target]
            if host:
                print(host)
            else:
                print(f"; Missing {target} on {h}")

        print()

def main():
    Config.init()
    Config.parse()
    itop = Itop(Config.c.itop_url + "/webservices/rest.php", "1.3", Config.c.itop_user, Config.c.itop_password)
    if Config.c.action == "get":
        return get_object(itop, Config.c.data[0])
    elif Config.c.action == "list":
        return list_objects(itop, Config.c.data)
    elif Config.c.action == "add":
        return create_object(itop, Config.c.data)
    elif Config.c.action == "update-domain-dates":
        return update_domain_dates(itop, Config.c.data)
    elif Config.c.action == "fetch-zone":
        return fetch_zone(itop, Config.c.data)
    elif Config.c.action == "ansible-inventory":
        return ansible_inventory(itop, Config.c.data)
    else:
        raise Exception("Bad operation %s" % Config.c.action)
    pass


if __name__ == "__main__":
    main()
