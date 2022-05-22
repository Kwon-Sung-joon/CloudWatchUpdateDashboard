import json
import boto3
import copy
import os

WIDGET_TEMPLATE = {
    'type':'metric',
    'period': 60,
    'properties' : {
        'view':'timeSeries',
        'stacked':False,
        'metrics':[],
        'region':os.getenv('REGION'),
        'annotations' : {}
    }

}

class CloudWatch:
    
    def __init__(self,dashboard_name):
        self.cw_client=boto3.client('cloudwatch');
        self.ec2_client=boto3.client('ec2');
        self.dashboard_name=dashboard_name;
        self.rds_client=boto3.client('rds');
        self.redis_client=boto3.client('elasticache');
        self.tg_albs=boto3.client('elbv2');
        self.asg_client=boto3.client('autoscaling');
        
    def get_ec2_instance_ids(self):
        instances=[]
        results=self.ec2_client.describe_instances(MaxResults=100);
        for result in results['Reservations']:
            for instance in result['Instances']:
                if instance['State']['Code'] != 48:
                    #print('add instance : {}'.format(instance["InstanceId"]))
                    instances.append(instance['InstanceId'])
                else:
                    print('{} instance is terminated. '.format(instance["InstanceId"]))
        return instances;
        
    def get_rds_insatnce_identifier(self):
        dbInstances=[]
        results=self.rds_client.describe_db_instances();
        for result in results['DBInstances']:
            #print('add dbInstance : {}'.format(result['DBInstanceIdentifier']))
            dbInstances.append(result['DBInstanceIdentifier'])
            
        return dbInstances;
        
    def get_elasticache_clusterIds(self):
        clusterIds=[]
        results=self.redis_client.describe_cache_clusters();
        for result in results['CacheClusters']:
            #print('add cacheClusterIds : {}'.format(result['CacheClusterId']))
            clusterIds.append(result['CacheClusterId'])
        return clusterIds;        


    def get_targetGroup_albs(self):
        tg=[]
        lb=[]
        results=self.tg_albs.describe_target_groups();
        for i in results['TargetGroups']:
            try:
                if str(i['LoadBalancerArns'])[int(str(i['LoadBalancerArns']).rindex('loadbalancer/'))+13:-2].startswith('app'):
                    #print(  str(i['TargetGroupArn'])[int(str(i['TargetGroupArn']).rindex(':'))+1::])
                    tg.append(str(i['TargetGroupArn'])[int(str(i['TargetGroupArn']).rindex(':'))+1::])
                    #print(str(i['LoadBalancerArns'])[int(str(i['LoadBalancerArns']).rindex('loadbalancer/'))+13::])
                    lb.append(str(i['LoadBalancerArns'])[int(str(i['LoadBalancerArns']).rindex('loadbalancer/'))+13:-2])
                else:
                    continue;
            except ValueError:
                continue;
        return tg,lb;
    def get_asg_instances(self):
        
        results=self.asg_client.describe_auto_scaling_instances();
        
        
        for i in results['AutoScalingInstances']:
            print(i);

        return 0;
        
    def put_dashboard(self,dashboard_body):
        
        results=self.cw_client.put_dashboard(
                DashboardName=self.dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
        #print(results);


def get_widget(metrics_list,title):
    widget=copy.deepcopy(WIDGET_TEMPLATE);
    widget['properties']['metrics']=metrics_list
    widget['properties']['title']=title
    
    return widget

def get_widget_format_with_insatnce_ids(instance_ids,namespace,metric,title):
    results=[]
    for i in instance_ids:
        results.append([namespace,metric,'InstanceId',i])

    widget=get_widget(results,title);

    return widget
    
def get_widget_format_with_db_identifier(db_identifiers,namespace,metric,title):
    results=[]
    for i in db_identifiers:
        results.append([namespace,metric,'DBInstanceIdentifier',i])

    widget=get_widget(results,title);

    return widget    

def get_widget_format_with_elasticache_cluster_ids(cacheClusterIds,namespace,metric,title):
    results=[]
    for i in cacheClusterIds:
        results.append([namespace,metric,'CacheClusterId',i])

    widget=get_widget(results,title);

    return widget

def get_widget_format_with_alb_tg(tg_albs,namespace,metric,title):
    results=[]
    for i in range(len(tg_albs[0])):
        results.append([namespace,metric,'TargetGroup',tg_albs[0][i],'LoadBalancer',tg_albs[1][i]]);
    widget=get_widget(results,title);
    return widget

def lambda_handler(event, context):
    
    cw=CloudWatch(os.getenv('DASHBOARD_NAME'))
    
    body={'widgets':[]}

    instances=cw.get_ec2_instance_ids();
    dbInstances=cw.get_rds_insatnce_identifier();
    cacheClusterIds=cw.get_elasticache_clusterIds();
    tg_albs=cw.get_targetGroup_albs();
    asg=cw.get_asg_instances();
    
    if instances :
        widget=get_widget_format_with_insatnce_ids(instances,'AWS/EC2','CPUUtilization','EC2-CPU');
        widget['properties']['annotations']['horizontal'] = [{'label': 'CPU Warning','value':70 } ]
        body['widgets'].append(widget)

        
        
        widget=get_widget_format_with_insatnce_ids(instances,'AWS/EC2','NetworkIn','EC2-NetworkIn');
        body['widgets'].append(widget)
        
        widget=get_widget_format_with_insatnce_ids(instances,'AWS/EC2','NetworkOut','EC2-NetworkOut');
        body['widgets'].append(widget)    
    
        widget=get_widget_format_with_insatnce_ids(instances,'AWS/EC2','EBSReadOps','EC2-EBSReadOps');
        body['widgets'].append(widget)

    
    else:
        print("No Instances..")
        
    '''
    if dbInstances:
        widget=get_widget_format_with_db_identifier(dbInstances,"AWS/RDS", "CPUUtilization", "RDS-CPU");
        body['widgets'].append(widget)
        widget=get_widget_format_with_db_identifier(dbInstances,"AWS/RDS", "FreeStorageSpace", "RDS-FreeStorageSpace");
        body['widgets'].append(widget)    
    else:
        print("No RDS ...")
    '''
    
    
    if cacheClusterIds:
        widget=get_widget_format_with_elasticache_cluster_ids(cacheClusterIds,'AWS/ElastiCache','CurrConnections','ElastiCache-CurrConnections');
        body['widgets'].append(widget)
        
        widget=get_widget_format_with_elasticache_cluster_ids(cacheClusterIds,'AWS/ElastiCache','SwapUsage','ElastiCache-SwapUsage');
        widget['properties']['annotations']['horizontal'] = [{'label': 'SwapUsage Limits','value':50 } ]
        body['widgets'].append(widget)
    else:
        print("No ElastiCache...")
        
    if tg_albs:
        widget=get_widget_format_with_alb_tg(tg_albs,"AWS/ApplicationELB", "UnHealthyHostCount","ALB UnhealthyHost");
        widget['properties']['annotations']['horizontal'] = [{'label': 'UnHealthyHost','value':1 } ]
        body['widgets'].append(widget)
    
        widget=get_widget_format_with_alb_tg(tg_albs,"AWS/ApplicationELB", "HTTPCode_Target_5XX_Count","ALB HTTPCode_Target_5XX_Count");
        widget['stat']='Sum'
        body['widgets'].append(widget)

        widget=get_widget_format_with_alb_tg(tg_albs,"AWS/ApplicationELB", "RequestCount","ALB RequestCount");
        body['widgets'].append(widget)
    else:
        print("No ALB ..")
        
    
   # cw.put_dashboard(body);
'''
    clt=boto3.client('elbv2');
    rsp=clt.describe_target_groups();
    a=rsp['TargetGroups']
    tg=[]
    lb=[]
    for i in a:
       # print("TG",i['TargetGroupArn'])
        try:
            #print(  str(i['TargetGroupArn'])[int(str(i['TargetGroupArn']).rindex(':'))+1::])
            tg.append(str(i['TargetGroupArn'])[int(str(i['TargetGroupArn']).rindex(':'))+1::])
            #print(str(i['LoadBalancerArns'])[int(str(i['LoadBalancerArns']).rindex('loadbalancer/'))+13::])
            lb.append(str(i['LoadBalancerArns'])[int(str(i['LoadBalancerArns']).rindex('loadbalancer/'))+13::])
        except ValueError:
            continue;
    print(tg);
    print(lb);
    '''
    

    
