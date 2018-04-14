Import AWS EC2 Tags to AlertLogic Console
==========================================
This is adaptation from the original code: https://github.com/ryanholland/tools

This revision includes:

* Support to update Threat Manager appliance
* Options to replace all tags or skip replace
* Optimized for environment with 3000+ ec2 instances

AlertLogic API end-point that used in the script:
* Cloud Defender API (https://docs.alertlogic.com/developer/)

Requirements
------------
* AWS credentials with sufficient permission to deploy Lambda, IAM roles, SNS, KMS key and launch Cloud Formation (optional)
* Alert Logic Account ID (CID)
* Credentials to Alert Logic Cloud Defender API (API KEY)

Sample Usage
------------
* Use the provided Cloud Formation to quickly deploy the stack.
* Alternatively you can use the provided Lambda packages and deploy it by your self.
* Or adapt the source code and use it on your own custom Lambda code.

Contributing
------------
Since this is just an example, the script will be provided AS IS, with no long-term support.
