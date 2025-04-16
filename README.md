## How to Run

1. Make sure to provide your **NASA API key** in `infra/secrets.auto.tfvars`. A example of the file can be found in
   `infra/secrets.auto.tfvars.example`.

   ```hcl
   nasa_api_key = "YOUR-KEY-HERE"
   ```

2. Set up your AWS CLI profile and replace it in `infra/main.tf` with your profile name.

   ```hcl
   provider "aws" {
     # ...
     profile = "agnostk" # <- Replace with your AWS profile name
     # ...
   }
   ```

3. Run the following commands to create the infrastructure and deploy the application:

   ```bash
   # Initialize Terraform
   cd infra
   terraform init
   terraform apply
   ```

This will create all the necessary infrastructure in AWS and deploy the application.

After the infrastructure is created, you can access the **Amazon QuickSight dashboards** and the **Mosaic Creator
application**
using
the URLs provided in the output of the `terraform apply` command.

