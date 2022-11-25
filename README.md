# ansible-automation-pst

## Explore environment

## Execution
>
> N.B.: You will need the root certificate `keysight.cer` on the same path when running the `curl` command below. Else use `-k` option 
> 

- To sync our AWX project after 
```shell
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/projects/VMT++Product-Security-SGP/update/ -X POST
```
```shell
# Update Project 
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/projects/VMT++Product-Security-SGP/update/ -X POST

# Update Variable Data
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/hosts/vmt++VMT-Hosts++Product-Security-SGP/variable_data/ \
  -X PUT -H "Content-Type: application/json" \
  --data '{
    "ansible_host": "10.244.33.199",
    "ansible_user": "Ubuntu-20p04",
    "ansible_password": "Ubuntu-20p04",
    "ansible_become": true,
    "ansible_become_password": "Ubuntu-20p04"
    "git_username": "'"$GIT_USERNAME"'",
    "git_password": "'"$GIT_PASSWORD"'"
  }'
  
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/hosts/vmt++VMT-Hosts++Product-Security-SGP/variable_data/ \
  -X PUT -H "Content-Type: application/json" \
  --data '{
    "ansible_host": "10.244.33.200",
    "ansible_user": "AmazonLinux-2",
    "ansible_password": "AmazonLinux-2",
    "ansible_become": true,
    "ansible_become_password": "AmazonLinux-2",
    "git_username": "'"$GIT_USERNAME"'",
    "git_password": "'"$GIT_PASSWORD"'"
  }'

# Launch job templates
export JOB_ID=$(curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/job_templates/215/launch/ -X POST | jq ".id")

# Check job status
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/jobs/$JOB_ID/job_host_summaries/ | jq ".results[0].summary_fields.job.status"

# Get audit result
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/jobs/$JOB_ID/stdout/?format=txt | grep -oP '"msg": "\\\\r\\\\n\K.*(?=\\\\r\\\\n)'
```