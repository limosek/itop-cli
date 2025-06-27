
import argparse
import os.path
import sys


class Config:

    @classmethod
    def init(cls):
        cls.p = argparse.ArgumentParser()
        cls.p.add_argument("--itop-url", type=str, required=True)
        cls.p.add_argument("--itop-user", type=str, required=True)
        cls.p.add_argument("--itop-password", type=str, required=True)
        cls.p.add_argument("--output-format", type=str, choices=["json", "json-pretty", "csv"], default="json-pretty")
        cls.p.add_argument("--count", type=int, choices=[0, 1], default=0, help="Do not return objects, but their count")
        cls.p.add_argument("--output-fields", type=str, default="name,id")
        cls.p.add_argument("--continue-on-error", type=int, default=0, choices=[0, 1])
        cls.p.add_argument("action", type=str, choices=["get", "list", "add", "update", "delete", "update-domain-dates", "fetch-zone", "ansible-inventory"])
        cls.p.add_argument("data", nargs="*", help="Object or OQL",type=str)

    @classmethod
    def parse(cls):
        if os.path.exists("itop-cli.cfg"):
            with open("itop-cli.cfg", "r") as f:
                args1 = f.readlines()
            args = []
            for a in args1:
                args.append(a.strip())
        else:
            args = []
        args.extend(sys.argv[1:])
        cls.c = cls.p.parse_args(args)
        if cls.c.output_fields == "*":
            cls.c.output_fields = []
        else:
            cls.c.output_fields = cls.c.output_fields.split(",")


