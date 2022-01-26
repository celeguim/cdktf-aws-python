# cdktf-aws-python

## **Prerequisites**

- AWS Account and Credentials
- AWS cli
- Terraform
- CDK for Terraform
- Node.js
- Python and pipenv

``` 
$ aws configure
$ cat ~/.aws/config
$ cat ~/.aws/credentials

$aws --version
$aws-cli/2.4.13 Python/3.8.8 Darwin/21.2.0 exe/x86_64 prompt/off

$ cdktf --version
0.8.6

```

Initialize the application

```
$ mkdir cdktf-aws-python
$ cd !$
$ cdktf-aws-python % cdktf init --template python --local
```

