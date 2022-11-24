```shell
# Update Project 
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/projects/VMT++Product-Security-SGP/update/ -X POST

# Playbooks
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/projects/VMT++Product-Security-SGP/playbooks/
  
# Update Variable Data
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/hosts/vmt++VMT-Hosts++Product-Security-SGP/variable_data/ \
  -X PUT -H "Content-Type: application/json" \
  --data '{
    "ansible_host": "10.244.33.199",
    "ansible_user": "Ubuntu-20p04",
    "ansible_password": "Ubuntu-20p04",
    "ansible_become": true,
    "ansible_become_password": "Ubuntu-20p04"
  }'
  
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/hosts/vmt++VMT-Hosts++Product-Security-SGP/variable_data/ \
  -X PUT -H "Content-Type: application/json" \
  --data '{
    "ansible_host": "10.244.33.200",
    "ansible_user": "AmazonLinux-2",
    "ansible_password": "AmazonLinux-2",
    "ansible_become": true,
    "ansible_become_password": "AmazonLinux-2"
  }'

# Launch job templates
export JOB_ID=$(curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/job_templates/215/launch/ -X POST | jq ".id")

# Job
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/jobs/$JOB_ID/stdout/?format=txt
```