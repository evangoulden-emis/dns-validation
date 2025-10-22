import dns.resolver
from rich.console import Console
from rich.table import Table
from pprint import pprint as pp

ROUTE53_NAMESERVER = "8.8.4.4"
GOOGLE_NAMESERVER = "8.8.8.8"

nameserver_dict = {
    "google": GOOGLE_NAMESERVER,
    "route53": ROUTE53_NAMESERVER
}

dns_response_list = []



def main():
    zone = read_zone_file(file_path="./test.txt", origin="emishealth.com")
    for name, node in zone.nodes.items():
        for rdset in node.rdatasets:
            resolve_dns_record(nameservers=nameserver_dict, record_name=name, query_type=rdset.rdtype, dns_response_list=dns_response_list)
    
    compare_dns_responses(dns_reponse_list=dns_response_list)


def compare_dns_responses(dns_reponse_list: list):
    
    console = Console()
    table = Table(show_lines=True)
    
    table.add_column("Global Response", style="cyan", max_width=80)
    table.add_column("R53 Response", style="magenta", max_width=80)
    table.add_column("Matches", style="green")
    for entry in dns_reponse_list:
        table.add_row(str(entry.get('global_response', "N/A")), 
                      str(entry.get('r53_response', "N/A")), 
                      str(entry.get('global_response') ==  entry.get('r53_response'))
        )

    console.print(table)



def resolve_dns_record(nameservers: dict, record_name: str, query_type: dns.rdatatype, dns_response_list: list):
    """
    Resolves DNS records of various different rdtypes (A, CNAME, TXT etc.) 
    
    Parameters:
    nameservers: a dictionary containing nameservers
    record_name: a str value for the FQDN
    query_type: a str value of the rdtype to query i.e. A, CNAME, MX, TXT etc
    dns_response_list: we append to this list so that it can be used elsewhere in the application
    
    Returns: None
    """
    rrset_data = {}
    for v in nameservers.values():
        resolver = dns.resolver.Resolver()
        print(f"Resolving {record_name} against nameserver: {v}")
        resolver.nameservers = [v]
        try:
            answer = resolver.resolve(qname=record_name, rdtype=query_type)
            if answer.nameserver is nameservers.get('google'):
                rrset_data['global_nameserver'] = answer.nameserver
                ips = [rdata.to_text() for rdata in answer]
                rrset_data['global_response'] = sorted(ips)
            elif answer.nameserver is nameservers.get('route53'):
                rrset_data['r53_nameserver'] = answer.nameserver
                ips = [rdata.to_text() for rdata in answer]
                rrset_data['r53_response'] = sorted(ips)
                
        except dns.resolver.NoAnswer:
            print(f"There was no response from the nameserver.")
        except dns.resolver.LifetimeTimeout:
            print(f"Resolution lifetime exceeded, this error is usually the result of a network problem.")
        except dns.resolver.NXDOMAIN:
            print(f"The domain name {record_name} does not exist / is not known by {v}.")
        except dns.resolver.NoNameservers:
            print(f"No nameservers are able to service this request.")
            
    if rrset_data: # Only append the dictionary to the list if it's not empty
        dns_response_list.append(rrset_data)        



def read_zone_file(file_path: str, origin: str, relativize: bool = False):
    """Load a BIND formatted DNS zone from file - we just need the filepath of the zonefile.

    Args:
        file_path (str): The filepath to an existing zonefile.
        origin (str): The origin of the zone i.e. google.com
        
    Defaults: 
        relativize (bool): By default we set relativize to False meaning any records imported by the zonefile
        will be prepended to the origin making a FQDN rather than a relative path.

    Returns:
        dns.zone.Zone: Returns a Zone object file
    """
    with open(file=file_path, mode='r') as r: 
        zone = dns.zone.from_file(r, origin=origin, relativize=relativize)
        return zone


if __name__ == "__main__":
    main()
