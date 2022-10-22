import json

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkslb.request.v20140515.DescribeLoadBalancersRequest import DescribeLoadBalancersRequest
from aliyunsdkslb.request.v20140515.DescribeLoadBalancerListenersRequest import DescribeLoadBalancerListenersRequest
from aliyunsdkslb.request.v20140515.DescribeAccessControlListsRequest import DescribeAccessControlListsRequest
from aliyunsdkvpc.request.v20160428.DescribeEipAddressesRequest import DescribeEipAddressesRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainsRequest import DescribeDomainsRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkslb.request.v20140515.DescribeVServerGroupAttributeRequest import DescribeVServerGroupAttributeRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest

from aliyunsdkcore.request import RpcRequest


class AliCloud():
    def __init__(self, access_key, secret_key, region_id):
        credentials = AccessKeyCredential(access_key, secret_key)
        self.__client = AcsClient(region_id=region_id, credential=credentials)

    def do_request(self, request: RpcRequest):
        response = self.__client.do_action_with_exception(request)
        return json.loads(response)

    def slb_get_instances(self):
        """
        refers to https://next.api.aliyun.com/api/Slb/2014-05-15/DescribeLoadBalancers?sdkStyle=old&tab=DEBUG&lang=PYTHON&params={%22RegionId%22:%22cn-beijing%22}
        :return: SLB instance list
        """
        request = DescribeLoadBalancersRequest()
        page_number = 1
        total_counts = 100
        intance_counts = 0
        request.set_PageSize(100)
        while intance_counts < total_counts:
            request.set_PageNumber(page_number)
            response = self.do_request(request)
            for slb_instance in response['LoadBalancers']['LoadBalancer']:
                intance_counts += 1
                yield slb_instance
            total_counts = response['TotalCount']
            page_number += 1

    def slb_get_listeners_by_loadbalance(self, loadbalance_id):
        """
        refer to https://next.api.aliyun.com/api/Slb/2014-05-15/DescribeLoadBalancerListeners?sdkStyle=old&tab=DEBUG&params={%22LoadBalancerId%22:[%22lb-2ze7xa69nfb5wi8bpahnq%22],%22RegionId%22:%22cn-beijing%22}&lang=PYTHON
        :param loadbalance_id:
        :return:
        """
        request = DescribeLoadBalancerListenersRequest()
        request.set_LoadBalancerIds([loadbalance_id])
        request.set_MaxResults(100)
        next_token = None
        while True:
            response = self.do_request(request)
            for listener in response['Listeners']:
                yield listener
            next_token = response.get('NextToken')
            if next_token is None:
                break

    def slb_get_acls(self):
        """
        refer to https://next.api.aliyun.com/api/Slb/2014-05-15/DescribeAccessControlLists?sdkStyle=old&tab=DEBUG&lang=PYTHON&params={%22RegionId%22:%22cn-beijing%22}
        :return:
        """
        request = DescribeAccessControlListsRequest()
        request.set_PageSize(100)
        page_num = 1
        total_counts = 100
        acl_counts = 0
        while acl_counts < total_counts:
            request.set_PageNumber(page_num)
            response = self.do_request(request)
            for acl in response['Acls']['Acl']:
                acl_counts += 1
                yield acl
            total_counts = response['TotalCount']
            page_num += 1

    def slb_get_vservergroup(self, vservergroup_id):
        """
        refer to https://next.api.aliyun.com/api/Slb/2014-05-15/DescribeVServerGroupAttribute?sdkStyle=old&tab=DEMO&lang=PYTHON
        :param loadbalance_id:
        :return:
        """
        request = DescribeVServerGroupAttributeRequest()
        request.set_VServerGroupId(vservergroup_id)
        for instance in self.do_request(request)['BackendServers']['BackendServer']:
            yield  instance


    def eip_get_eips(self):
        """
        refer to https://next.api.aliyun.com/api/Vpc/2016-04-28/DescribeEipAddresses?sdkStyle=old
        :return:
        """
        request = DescribeEipAddressesRequest()
        request.set_PageSize(100)
        page_num = 1
        total_counts = 100
        eip_counts = 0
        while eip_counts < total_counts:
            request.set_PageNumber(page_num)
            response = self.do_request(request)
            for eip in response['EipAddresses']['EipAddress']:
                eip_counts += 1
                yield eip
            total_counts = response['TotalCount']
            page_num += 1

    def dns_get_domains(self):
        """
        refer to https://next.api.aliyun.com/api/Alidns/2015-01-09/DescribeDomains?sdkStyle=old&tab=DOC&lang=PYTHON
        :return:
        """
        request = DescribeDomainsRequest()
        request.set_PageSize(100)
        page_number = 1
        dns_counts = 0
        total_counts = 100
        while dns_counts < total_counts:
            request.set_PageNumber(page_number)
            response = self.do_request(request)
            for domain in response['Domains']['Domain']:
                dns_counts += 1
                yield domain
            total_counts = response['TotalCount']
            page_number += 1

    def dns_get_domainrecord_by_domain(self, domain):
        """
        refer to https://next.api.aliyun.com/api/Alidns/2015-01-09/DescribeDomainRecords?sdkStyle=old&tab=DOC&lang=PYTHON
        :return:
        """
        request = DescribeDomainRecordsRequest()
        request.set_DomainName(domain)
        request.set_PageSize(100)
        page_number = 1
        dns_counts = 0
        total_counts = 100
        while dns_counts < total_counts:
            request.set_PageNumber(page_number)
            response = self.do_request(request)
            for domain_record in response['DomainRecords']['Record']:
                dns_counts += 1
                yield domain_record
            total_counts = response['TotalCount']
            page_number += 1

    def ecs_get_instances(self):
        """
        refer to https://next.api.aliyun.com/api/Ecs/2014-05-26/DescribeInstances?sdkStyle=old
        :return:
        """
        request = DescribeInstancesRequest()
        request.set_PageSize(100)
        page_number = 1
        total_counts = 100
        instance_counts = 0
        while instance_counts < total_counts:
            request.set_PageNumber(page_number)
            response = self.do_request(request)
            for instance in response['Instances']['Instance']:
                instance_counts += 1
                yield instance
            page_number += 1
            total_counts = response['TotalCount']
        return