import boto3

def lambda_handler(event, context):
    # Initialize AWS clients
    ec2_client = boto3.client('ec2')
    ec2_resource = boto3.resource('ec2')

    # Get list of active EC2 instances (running and stopped)
    instances = ec2_resource.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}]
    )

    # Get list of EBS snapshots owned by the same account
    snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])['Snapshots']

    # Iterate through each snapshot
    for snapshot in snapshots:
        # Check if the snapshot is associated with a volume
        if 'VolumeId' in snapshot:
            volume_id = snapshot['VolumeId']
            
            # Check if the volume is associated with any active instance
            is_volume_in_use = any(instance.block_device_mappings[0].get('Ebs', {}).get('VolumeId') == volume_id for instance in instances)
            
            # If the volume is not associated with any active instance, delete the snapshot
            if not is_volume_in_use:
                print(f"Deleting stale snapshot: {snapshot['SnapshotId']}")
                ec2_client.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
