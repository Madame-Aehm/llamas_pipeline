# AWS - Amazon Web Services

[**AWS**](https://aws.amazon.com/) is a subsidiary of Amazon offering over 200 cloud computing services, including storage, networking, analytics, deployment, and machine learning. It is an enormous platform, and there are people whose entire jobs involve simply navigating their services, so don't let yourself get too overwhelmed!

## Lambda

We are going to use one of their most popular services: [**AWS Lambda**](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html). We've been writing code that requests and scrapes data and adds it to an online database, but we currently need to manually run that code each day to get the newest data. AWS Lambda is how we will automate that process, telling it to run once per day at the specified time.

The sign-up process is quite intense, requiring a phone number for MFA, and a credit card or bank account link to finalize registration. For our purpose, we should incur no charges, though it will take €1 to confirm payment validity. 

## Create a new function

From your AWS console, use the search to find the Lambda Dashboard and click **Create function**. Select **Author from scratch**, give your function a name, and set the **Runtime** to the version of Python you have set for the Anaconda Environment for this project (you can check this by finding the "python" package installed for that environment in Anaconda Navigator).

There is ready some template code in the editor. Edit this code to print the parameters, then on the right click "Deploy" to apply the changes. We can now test the code using "Test". We can see how the return of the function creates a Response object, and any print statements are able to be viewed as Function Logs. Notice that the `context` parameter gives you information about the function call, and the `event` parameter is logging the value set to **Event JSON** in the test. 

## Project Structure

It would be great if we could just copy and paste our code directly into this online code editor and fire away! But we are relying on a few external packages to make our code work (`requests`, `psycopg`, `bs4`, etc). Locally, we have Anaconda managing our packages for each environment, but AWS doesn't have access to this! So we are going to need to include the code files for these packages along with our own in order for everything to run properly.

To do this, we are going to install the packages not through Anaconda, but directly into our project folder and include them all in a [`.zip` file](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html). (An alternative is to use a [**layer**](https://docs.aws.amazon.com/lambda/latest/dg/python-layers.html), however the additional steps will extend this demonstration). 

For organisational purposes, at this point I recommend creating an `AWS` sub-folder. It will be necessary to edit some of our own code to make it compatible with AWS anyway, so here we will install the necessary packages, but also make copies of our own code to be edited for AWS as we need it. This way, you can still run your original code locally if needed.

Note that you won't need to download anything for packages that you didn't have to manually install. Some modules, like `datetime` and `os`, come directly from Python, and are therefore included. We also won't need the `.env` file or the `dotenv` package, so in the copy of the code in the `AWS` folder, we can remove that import along with the `load_dotenv()` function call. This is because we will enter our environment variables directly into AWS. The `os` module import is still required.

## .zip

To install the packages directly into your project folder, you will use a terminal to `pip install` the package to a specific target location. The [documentation](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-create-dependencies) recommends collecting all the packages in a folder called `package` in order to keep them away from our codebase files. Add the line `package/` to your `.gitignore` to ignore all folders called "package". From the `package` folder, run:

```shell
pip install package-name -t .
```

Continuing to follow the documentation steps, we are now going to compress this folder into a `.zip` file. If you are using MacOS or Linux operating systems, you can do this directly from the terminal (Windows users will need to install something like Windows Subsystem for Linux [**WSL**](https://learn.microsoft.com/en-us/windows/wsl/install), or simply use the Windows Explorer UI.) From the `package` folder, run:

```shell
zip -r ../my_deployment_package.zip .
```

When you're satisfied with your code, you can then move a copy of that file into the zipped folder as well. Drag and drop using File Explorer UI, or from the root run:

```shell
zip my_deployment_package.zip filename.py
```

This zip file can then be uploaded to AWS!

## Handler

The [**handler**](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html) is the "main" function to be called. By default, this is a function called `lambda_handler` in a file called `lambda_function`. If you follow this naming convention, then you don't need to change anything. But you can customize by scrolling down to **Runtime Settings** and setting the **Handler** to `your-file-name.your-function-name`.

You should now be able to run a test run of your function. 

The next step is to create a second function which will "catch" the return of the first function, the **destination**. This is the function that will add the data to the database. We should do this separately not only for organization, but to minimize the package size we are uploading to AWS. Too many libraries all uploaded at once can cause us problems! 

Follow the previous steps to create a new function. 

## Common blockers.....

### Psycopg

There are some problems uploading `psycopg` into AWS, and depending on the version of the package and the version of Python, there are some different solutions. 

If you are using `psycopg` version 3, use this script to install the package (edit the Python version and/or target file as needed):

```shell
pip install     --platform manylinux2014_x86_64     --target=package     --implementation cp     --python-version 3.11     --only-binary=:all: --upgrade     "psycopg[binary]"
```

The [documentation](https://www.psycopg.org/docs/install.html) for `psycopg2` also have instructions how to install the binary package, but some people have also created packages specifically compatible with AWS that you can install a bit more easily. [This](https://pypi.org/project/aws-psycopg2/) package is recommended. [This](https://github.com/jkehler/awslambda-psycopg2) GitHub repository also has compatible packages for different versions of Python. You would need to make a local clone of the repo, then copy the files for the version you need. 

If you are creating a layer, [this](https://medium.com/@bloggeraj392/creating-a-psycopg2-layer-for-aws-lambda-a-step-by-step-guide-a2498c97c11e) guide might be of some help!

### JSON data-type incompatibility

Some of the innate Python data types cannot be recognized by JSON, which is the format your return will take to be passed from one Lambda function to another. It might be necessary to cast types before and after sending the data from one function to another. E.g. cast a Python datetime into a string, then convert back into a datetime in the destination function. The same might be necessary for tuples and sets (use lists instead, then cast to the correct data type in the destination function.)

## Add Destination

You can "test" your destination function by putting the output of the first function into the **Event JSON**. Remember we can access this through the `event` parameter. This is the **trigger** for the function, which in our case is the successful run of the previous function. 

Navigate to your first function and click **Add destination** and set the settings:
  - **Source**: Asynchronous invocation
  - **Condition**: On success
  - **Destination type**: Lambda function
  - **Destination**: your destination function

When the first function succeeds, it will trigger an event that calls the second function. That event is passed as a parameter to the second function, and we can find the data we set as the return under `event["responsePayload"]`. **You will need to edit this in the second function's code!**

## Trigger with Event Bridge

We now need to set a **trigger** for our first function! Click **Add trigger** and select **EventBridge (CloudWatch Events)**. This will prompt you to **Create a new rule**. Give it a name and description, we are creating a [**Schedule expression**](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html#eb-create-scheduled-rule), which is set to trigger on an automated schedule. 

The **Schedule expression** is expecting either a [**cron expression**](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-scheduled-rule-pattern.html#eb-cron-expressions) (for specific times) or a [**rate expression**](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-scheduled-rule-pattern.html#eb-rate-expressions) (for regular intervals). If you are not interested in investigating this syntax, a cheat is to set the Schedule expression to the example, and the use the edit console. 

## Zero-Spend Budget

Since you've linked a credit card or bank account to this service, little piece-of-mind step you can take is to set up an alert if you go over the Free Tier limit:
  1. Use the search to find the **Billing and Cost Management** dashboard
  2. Select **Use a template** in **Budget setup**!SECTION
  3. Select **Zero spend budget** from **Templates**!SECTION
  4. Add your email address to the **Email recipients** (you can comma-separate multiple email addresses, if you want)
  5. **Create budget**