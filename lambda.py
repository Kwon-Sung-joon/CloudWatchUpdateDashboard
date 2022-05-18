import copy
import datetime
import json
import os
import boto3


WIDGET_TEMPLATE = {
    'type': 'metric',
    'x': 0,
    'y': 0,
    'width': 15,
    'height': 6,
    'timezone': '+0900'
    'properties': {
        'view': 'timeSeries',
        'stacked': False,
        'metrics': [],
        'region': os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2'),
        'annotations': {}
    }
}


class CloudWatch:
    def __init__(self, dashboard_name):
        self.cw_client = boto3.client('cloudwatch')
        self.ec2_client = boto3.client('ec2')
        self.dashboard_name = dashboard_name
        self.dashboard = None

    def get_ec2_cpu_metrics(self):
        instances = []
        # CloudWatch metrics can only display max 500 metrics per widget
        results = self.ec2_client.describe_instances(MaxResults=500)
        for result in results['Reservations']:
            for instance in result['Instances']:
                """
                0 : pending
                16 : running
                32 : shutting-down
                48 : terminated
                64 : stopping
                80 : stopped
                """
                if instance['State']['Code'] != 48:
                    print('adding instance ID: {}'.format(instance['InstanceId']))
                    instances.append(instance['InstanceId'])
                else:
                    print('{} instance is terminated'.format(instance['InstanceId']))
        return instances
    def put_dashboard(self, dashboard_body):
        """Puts the updated dashboard into CloudWatch"""
        results = self.cw_client.put_dashboard(
            DashboardName=self.dashboard_name,
            DashboardBody=json.dumps(dashboard_body))
        print(results)


def format_widget(list_of_instance_ids):
    """
    results sample ... 
    result=[
            [ "AWS/EC2", "CPUUtilization", "InstanceId", "i-qwd...." ],
            ...
    ]
    """
    results = []
    for instance in list_of_instance_ids:
        # NameSpace ... Metrics... Dimensions... values...
        results.append(['AWS/EC2', 'CPUUtilization', 'InstanceId', instance])
    return results


def lambda_handler(event, context):
    
    
    cw = CloudWatch(os.getenv('DASHBOARD_NAME'))
    
    
    final_dashboard_body = {'widgets': []}
    
    
    all_instances = cw.get_ec2_cpu_metrics()
    
    
    metrics_list = format_widget(all_instances)
    
    widget = copy.deepcopy(WIDGET_TEMPLATE)
    widget['properties']['metrics'] = metrics_list
    widget['properties']['title'] = 'CPU Utilization: {} instances'.format(str(len(all_instances)))
    #widget['properties']['annotations']['vertical'] = [
    #    {'label': 'Last updated', 'value': datetime.datetime.utcnow().isoformat() + 'Z'}]
    final_dashboard_body['widgets'].append(widget)
    cw.put_dashboard(final_dashboard_body)
    
    
