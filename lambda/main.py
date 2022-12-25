import boto3
import os

ec2_client = boto3.client('ec2')
lambda_client = boto3.client('lambda')
THIS_FUNCTION_NAME = os.getenv('THIS_FUNCTION_NAME')
PRIMARY_NETWORK_INTERFACE = os.getenv('PRIMARY_NETWORK_INTERFACE')

def lambda_handler(event, context):
    
    CURRENT_ALLOCATION_ID = os.getenv('CURRENT_ALLOCATION_ID')
    CURRENT_ASSOCIATION_ID = os.getenv('CURRENT_ASSOCIATION_ID')

    # validate input
    assert THIS_FUNCTION_NAME, 'Lambda function cannot be None'
    assert PRIMARY_NETWORK_INTERFACE, 'Primary network interface cannot be None'
    assert CURRENT_ALLOCATION_ID, 'Allocation id cannot be None'
    assert CURRENT_ASSOCIATION_ID, 'Association id cannot be None'
    
    # allocate new EIP
    resp = ec2_client.allocate_address(
        Domain='vpc',
        TagSpecifications=[
            {
                'ResourceType': 'elastic-ip',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'primary_eip'
                    },
                ]
            },
        ]
    )
    print(resp)

    allocation_id = resp['AllocationId']
    
    

    # disassociate EIP from the primary ENI
    resp = ec2_client.disassociate_address(
        AssociationId=CURRENT_ASSOCIATION_ID
    )
    print(resp)

    # associate new EIP to the primary ENI
    resp = ec2_client.associate_address(
        AllocationId=allocation_id,
        AllowReassociation=False,
        NetworkInterfaceId=PRIMARY_NETWORK_INTERFACE
    )
    print(resp)
    
    association_id = resp['AssociationId']

    # release the previous EIP (for cycle EIP slot, default = 5 EIPs)
    resp = ec2_client.release_address(
        AllocationId=CURRENT_ALLOCATION_ID
    )
    print(resp)

    # update current eip allocation_id to the lambda
    resp = lambda_client.update_function_configuration(
        FunctionName=THIS_FUNCTION_NAME,
        Environment={
            'Variables': {
                'THIS_FUNCTION_NAME': THIS_FUNCTION_NAME,
                'PRIMARY_NETWORK_INTERFACE': PRIMARY_NETWORK_INTERFACE,
                'CURRENT_ALLOCATION_ID': allocation_id,
                'CURRENT_ASSOCIATION_ID': association_id
            }
        }
    )
    