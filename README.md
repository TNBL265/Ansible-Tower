# ansible-automation-pst

## AWX Project Overview


## Execution
>
> N.B.: You will need the root certificate `keysight.cer` on the same path when running the `curl` command below. Else use `-k` option 
> 

- To sync our AWX project after updating bitbucket repository
```shell
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/projects/VMT++Product-Security-SGP/update/ -X POST
```
```shell
# Update Variable Data
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/hosts/vmt++VMT-Hosts++Product-Security-SGP/variable_data/ \
  -X PUT -H "Content-Type: application/json" \
  --data '{
    "ansible_host": "10.244.33.199",
    "ansible_user": "Ubuntu-20p04",
    "ansible_password": "Ubuntu-20p04",
    "ansible_become": true,
    "ansible_become_password": "Ubuntu-20p04",
    "git_username": "'"$GIT_USERNAME"'",
    "git_password": "'"$GIT_PASSWORD"'"
  }' \
  -o /dev/null
  
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
  }' \
  -o /dev/null
  
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/hosts/vmt++VMT-Hosts++Product-Security-SGP/variable_data/ \
  -X PUT -H "Content-Type: application/json" \
  --data '{
    "ansible_host": "10.244.33.201",
    "ansible_user": "RHatELinux-8",
    "ansible_password": "RHatELinux-8",
    "ansible_become": true,
    "ansible_become_password": "RHatELinux-8",
    "git_username": "'"$GIT_USERNAME"'",
    "git_password": "'"$GIT_PASSWORD"'"
  }' \
  -o /dev/null

# Launch job templates
export JOB_ID=$(curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/job_templates/goss-adit++Product-Security-SGP/launch/ -X POST | jq ".id")

# Check job status
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/jobs/$JOB_ID/job_host_summaries/ | jq ".results[0].summary_fields.job.status"

# View ansible progress
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/jobs/$JOB_ID/stdout/?format=ansi

# Get audit result
curl -s --cacert keysight.cer -H "Authorization: Bearer $AWXTOKEN" https://awx.it.keysight.com/api/v2/jobs/$JOB_ID/stdout/?format=txt |
  tr -d '\\' | sed 's/"rn//g' | sed 's/rn"//g' | # trim escape characters in AmazonLinux2 
  sed -n '/"msg"/,/^$/p' | sed 's/"msg"://'    | # get the main debug message
  sed 's/}$//' | sed -e '$a}'                  | # remove all } and add back one } for valid json
  jq                                             # check json format
```