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

$ aws --version
$ aws-cli/2.4.13 Python/3.8.8 Darwin/21.2.0 exe/x86_64 prompt/off

$ cdktf --version
0.8.6

```

## Initialize the application

```
$ mkdir cdktf-aws-python
$ cd !$
$ cdktf-aws-python % cdktf init --template python --local
```

## Add AWS Provider

```
{
  "language": "python",
  "app": "pipenv run python main.py",
  "projectId": "ed97eb62-7ecb-4ef5-8ee2-5dcb934ba35e",
  "terraformProviders": [
    "hashicorp/aws@~> 3.67.0"
  ],
  "terraformModules": [],
  "codeMakerOutput": "imports",
  "context": {
    "excludeStackIdFromLogicalIds": "true",
    "allowSepCharsInLogicalIds": "true"
  }
}

$ cdktf get
cdktf-aws-python % cdktf get          
⠦ downloading and generating modules and providers...

```

## Do-it
```
$ cdktf apply
$ cdktf destroy
$ cdktf diff
```

