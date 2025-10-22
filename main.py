import dns.resolver
from rich import inspect, table
from pprint import pprint as pp

ROUTE53_NAMESERVER = "8.8.4.4"
GOOGLE_NAMESERVER = "8.8.8.8"

nameserver_dict = {
    "google": GOOGLE_NAMESERVER,
    "route53": ROUTE53_NAMESERVER
}

dns_response_list = []



def main():
    # resolve_dns_record(nameservers=nameserver_dict, record_name="www.google.com", query_type="A", dns_response_list=dns_response_list)
    # resolve_dns_record(nameservers=nameserver_dict, record_name="epmaeastlancstrnidentityservice.emishealth.com", query_type="A", dns_response_list=dns_response_list)
    # resolve_dns_record(nameservers=nameserver_dict, record_name="emishealth.com", query_type="MX", dns_response_list=dns_response_list)
    # resolve_dns_record(nameservers=nameserver_dict, record_name="_dmarc.emishealth.com", query_type="TXT", dns_response_list=dns_response_list)
    zone = read_zone_file("./emishealth.com.converted.txt")
    for name, node in zone.nodes.items():
        # print(inspect(node, all=True))
        print(name, node.rdatasets)
    pp(zone)

 

def resolve_dns_record(nameservers: dict, record_name: str, query_type: str, dns_response_list: list):
    # Loop through the nameservers in the nameserver_dict
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
    dns_response_list.append(rrset_data)        
    

def read_zone_file(file_path: str) -> dns.zone.Zone:
    with open(file=file_path, mode='r') as r: 
        zone = dns.zone.from_file(r, origin="emishealth.com", relativize=False)
        print(type(zone))
        return zone


if __name__ == "__main__":
    main()
