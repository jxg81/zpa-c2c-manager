#!/usr/bin/env python
from manage_ip import manage_hosts_file
import argparse


def main(override_file=None, add_hosts=None):
    manage_hosts_file(override_file=override_file, add_hosts=add_hosts)
    
if __name__ == "__main__":
    override_file = None
    argParser = argparse.ArgumentParser(prog='zpa_host_file_update.py',
                    description='This utility will automatically overwrite the local hosts file entries with hostname to IP mappings from ZPA. Existing entires will NOT be maintained',
                    epilog='Platform detection is automatic, override file is only required for testing to prevent writes to actual host file. If adding additional hosts, csv file should be formatted with one "ip, host" per line and no headings')
    argParser.add_argument("--override_file", "-o", default=None, type=str, help="Override path to write host file entries")
    argParser.add_argument("--add_hosts", "-a", default=None, type=str, help="Supply a csv with additional host entires to combine with ZPA data")
    args = argParser.parse_args()
    override_file = args.override_file
    add_hosts = args.add_hosts
    main(override_file=override_file, add_hosts=add_hosts)  