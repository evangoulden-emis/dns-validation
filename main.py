import dns.resolver
from rich import inspect, table

ROUTE53_NAMESERVER = "205.251.199.154"
GOOGLE_NAMESERVER = "8.8.8.8"

nameserver_dict = {
    "google": GOOGLE_NAMESERVER,
    "route53": ROUTE53_NAMESERVER
}

dns_response_list = []



def main():
    resolve_dns_record(nameservers=nameserver_dict, record_name="www.google.com", query_type="A", dns_response_list=dns_response_list)
    resolve_dns_record(nameservers=nameserver_dict, record_name="epmaeastlancstrnidentityservice.emishealth.com", query_type="A", dns_response_list=dns_response_list)

def resolve_dns_record(nameservers: dict, record_name: str, query_type: str, dns_response_list: list):
    # Loop through the nameservers in the nameserver_dict
    rrset_data = {}
    for k,v in nameservers.items():
        resolver = dns.resolver.Resolver()
        print(f"Resolving {record_name} against nameserver: {v}")
        resolver.nameservers = [v]
        try:
            answer = resolver.resolve(qname=record_name, rdtype=query_type)
            if answer.nameserver is nameservers.get('google'):
                rrset_data['global_nameserver'] = answer.get('nameserver', 'Default')
                rrset_data['global_response'] = answer.get('rrset')
            elif answer.nameserver is nameservers.get('route53'):
                rrset_data['r53_nameserver'] = answer.get('nameserver', 'Default')
                rrset_data['r53_response'] = answer.get('rrset')
                
        except dns.resolver.NoAnswer:
            print(f"There was no response from the nameserver.")
        except dns.resolver.LifetimeTimeout:
            print(f"Resolution lifetime exceeded, this error is usually the result of a network problem.")
        except dns.resolver.NXDOMAIN:
            print(f"The domain name {record_name} does not exist / is not known by {v}.")
    dns_response_list.append(rrset_data)        
    print(f"rrset_data: {inspect(rrset_data)}")


if __name__ == "__main__":
    main()
