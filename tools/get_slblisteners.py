from Clouds.AliCloud import AliCloud

if __name__ == '__main__':
    from secrets import access_key, secret_key

    ali = AliCloud(access_key, secret_key, 'cn-beijing')
    slbs = [slb for slb in ali.slb_get_instances()]
    ecss = {ecs['InstanceId']: ecs['InstanceName'] for ecs in ali.ecs_get_instances()}
    eip_with_slb = {eip['InstanceId']: eip for eip in ali.eip_get_eips() if eip['InstanceType'] == "SlbInstance"}
    acls = {acl['AclId']: acl for acl in ali.slb_get_acls()}
    dns_records = {}
    for domain in ali.dns_get_domains():
        for domain_record in ali.dns_get_domainrecord_by_domain(domain['PunyCode']):
            if dns_records.get(domain_record['Value']) is None:
                dns_records[domain_record['Value']] = []
            dns_records[domain_record['Value']].append(".".join([domain_record['RR'],
                                                                 domain_record['DomainName']]))
    # 监听列表规整
    listeners = []
    for slb in slbs:
        for lsn in ali.slb_get_listeners_by_loadbalance(slb['LoadBalancerId']):
            public_ip = eip_with_slb[slb['LoadBalancerId']]['IpAddress'] if eip_with_slb.get(
                slb['LoadBalancerId']) else ""
            if slb['AddressType'] == "internet":
                public_ip = slb['Address']

            backends = []
            if lsn.get('VServerGroupId'):
                for backend in ali.slb_get_vservergroup(lsn['VServerGroupId']):
                    backend.update({"servername": ecss.get(backend['ServerId']) if backend['Type'] == "ecs" else
                        backend['ServerId']})
                    backends.append("{Type}:{servername}:{Port}".format(**backend))
            elif lsn.get('HTTPListenerConfig') and lsn['HTTPListenerConfig']['ListenerForward'] == 'on':
                backends.append("Forword to {}".format(lsn['HTTPListenerConfig']['ForwardPort']))
            #!TODO :  默认服务器组

            listener = {
                "LoadBalance IP": slb['Address'],
                "Public IP": public_ip,
                "Port": lsn['ListenerPort'],
                "Protocol": lsn['ListenerProtocol'],
                "Listener Name": lsn['Description'],
                "LoadBalance Name": slb['LoadBalancerName'],
                "Status": lsn['Status'],
                "AclName": acls.get(lsn['AclId'])['AclName'] if lsn.get('AclStatus') == "on" else "",
                'AclType': lsn.get('AclType'),
                "Bandwidth": slb['Bandwidth'],
                "PayType": slb['PayType'],
                "DomainName": "|".join(dns_records[public_ip]) if dns_records.get(public_ip) else "",
                "Backends": "|".join(backends)
            }
            listeners.append(listener)

    # 结果写入
    import csv

    headers = [key for key in listeners[0]]
    with open('listener.csv', 'w', encoding='utf-8') as f:
        listener_result = csv.DictWriter(f, fieldnames=headers)
        listener_result.writeheader()
        listener_result.writerows(listeners)
