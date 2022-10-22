from Clouds.AliCloud import AliCloud

if __name__ == '__main__':
    from secrets import access_key, secret_key
    ali = AliCloud(access_key, secret_key, 'cn-beijing')
    slbs = [slb for slb in ali.slb_get_instances()]
    eip_with_slb = {eip['InstanceId']: eip for eip in ali.eip_get_eips() if eip['InstanceType'] == "SlbInstance"}
    acls = {acl['AclId']: acl for acl in ali.slb_get_acls()}
    listeners = []
    for slb in slbs:
        for lsn in ali.slb_get_listeners_by_loadbalance(slb['LoadBalancerId']):
            public_ip = eip_with_slb[slb['LoadBalancerId']]['IpAddress'] if eip_with_slb.get(slb['LoadBalancerId']) else ""
            if slb['AddressType'] == "internet":
                public_ip = slb['Address']
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
            }
            listeners.append(listener)
    import csv

    headers = [key for key in listeners[0]]
    with open('listener.csv', 'w', encoding='utf-8') as f:
        listener_result = csv.DictWriter(f, fieldnames=headers)
        listener_result.writeheader()
        listener_result.writerows(listeners)