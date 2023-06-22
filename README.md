# Team Calendar Generator for BambooHR

The BambooHR Team Calendar Generator is a helpful Python script that generates
an iCalendar file for selected time-offs (vacation, sickness, etc.) of a
specific team in [BambooHR]. This iCal file can then be used in external calendar
applications such as Google Calendar, Microsoft Outlook, Apple Calendar, etc.

Although BambooHR has a built-in feature for iCal publishing, it doesn't offer
customization options to select which employees and which time offs should be
included. This limitation can be challenging for larger organizations.

The script allows you to:
  - Select specific types of time-offs for generating the iCalendar file.
  - Define the set of employees to be included (e.g., a team, division, etc)
  - Publish the generated iCal file (.ics) to DigitalOcean Spaces,
    Amazon S3, or a local file.
  - Schedule multiple executions to publish calendars for different teams,
    each with unique settings.

[BambooHR]: https://www.bamboohr.com

## Deployment Options

The BambooHR Team Calendar Generator can operate in one of two modes:

  - As a [serverless function][functions] that uploads the iCalendar file 
    directly to a DigitalOcean Spaces.

  - As a Docker-based application executed locally or on a server. This mode
    allows saving the file locally or uploading it to DigitalOcean Spaces or
    Amazon S3.

[functions]: https://www.digitalocean.com/products/functions


## Time Off Groups

The script is run using a settings profile referred to as a _time off group_.
The default group is named `vac` (for vacations). Another possible example of a
time off group is `sick`, for sick leaves.

Since BambooHR can have a variety of time off types (e.g., Paid Vacation,
Unpaid Vacation), this feature allows the creation of a calendar for a specific
set of time off types and outputs it to a file with a designated path.

When paired with scheduled script executions, you could generate distinct
calendars—for example, one for vacations and another for sick leaves.



# Installation


## Prerequisites

1. **BambooHR API key**  

   To generate an [API key][bhr-api], log in to BambooHR and click your 
   username in the upper right-hand corner of any page to get to the user 
   context menu. If you have the necessary permissions, you will see
   an `API Keys` option in this menu, which will direct you to the relevant
   page.  
    
2. **Custom team report in BambooHR**  
   
   The set of employees used for iCal generation is defined by a 
   [custom report][bhr-rep]. This report should include all necessary
   employees, along with the fields used to display their names.

   To generate such a report:
   
   - 2.1. In BambooHR, go to `Reports - New Report`.
         Please consult the BambooHR Helpdesk for guidance on creating custom
         reports, and selecting appropriate fields and filters.
   
   - 2.2. Ensure to include the <samp>EEID</samp> field
         (employee ID, found in the Calculated group). Also, add one or several
         fields you want to use for displaying user records in calendar events.
         Typical choices might include <samp>First Name</samp>, <samp>Last
         Name</samp>, <samp>Preferred Name</samp>. You can later customize the
         display template based on these fields.
   
   - 2.3. Take note of the ID for the created report.
         You can find this ID as a number in the URL of the page when you visit
         the newly created report in your browser.

3. **[DigitalOcean][do] account** is required if you
   plan to run the script as a serverless function, or have
   [Docker][docker] installed if you plan to run it locally.

4. (Optional) [DigitalOcean Spaces][do-spaces] or [AWS S3][aws-s3] credentials
   are necessary if you opt to upload the generated file there.
   The script uses the [boto3][aws-boto] package to access these storage
   services. Consult the boto3 documentation to understand how to obtain these
   credentials. You will need access key, secret, region name and bucket.


[bhr-api]: https://documentation.bamboohr.com/docs/getting-started
[bhr-rep]: https://www.bamboohr.com/blog/custom-hr-reports-hints-tips
[do]: https://digitalocean.com/
[do-spaces]: https://www.digitalocean.com/products/spaces
[docker]: https://www.docker.com/
[aws-s3]: https://aws.amazon.com/s3/
[aws-boto]: https://aws.amazon.com/sdk-for-python/


## Setup and Settings

First, clone this repository.

   ```sh
   git clone git@github.com:tombazhal/bamboohr-team-cal.git
   ```

Then navigate to `dofunc/packages/bhrtools/bhrteamcal`.  
Copy `.env.example` to `.env` and `config.yml.example` to `config.yml`.

   ```sh
   cd bamboohr-team-cal/dofunc/packages/bhrtools/bhrteamcal
   cp .env.example .env
   cp config.yml.example config.yml
   ```

### 1. Edit `.env` File

Open the `.env` file in your text editor and set
the BambooHR API access variables:
 - API key
 - organization's subdomain.  

 If you intend to use the feature for uploading to DigitalOcean Spaces,
 provide the necessary credentials (key, secret, region, and bucket).


### 2. Edit `config.yml` file

Using your preferred text editor open the `config.yml` file.

#### 2.1. Time Off Groups

   First, edit the time off groups in the `timeoffs:` section.
   The default one is `vac` for vacations. There are comments
   explaining each variable.  
   For each group, you need to specify:
   - time off IDs to choose,
   - iCalendar name (title),
   - the pathname for the resulting iCal file.

#### 2.2. BambooHR Team Report and Naming Template

   Within the `bamboohr:` section
   - set the `BAMBOOHR_TEAM_REPORT_ID` variable to the ID of your
     custom team report from BambooHR.
   - Edit `BAMBOOHR_NAME_TEMPLATE` to define how each employee is 
     referenced in iCal. This should be done using the fields 
     from the custom report.


## Deployment and Execution

The script can run as a serverless function or be executed with Docker.

### :cloud:  Deploy as DigitalOcean Serverless Function   

The function code is already packaged for DigitalOcean inside the `dofunc`
directory. To deploy it, follow these steps:
  1. [Setup doctl][doctl]
  2. [Connect to a namespace][namespc]
  3. Navigate to the root of the repository and deploy the function:
     ```sh
     cd path/to/repository
     doctl serverless deploy dofunc --remote-build
     ```
     
  #### Execution

  You can execute the function in either of the following ways:

  - manually, from the DigitalOcean control panel
  - using the `doctl serverless functions invoke` command 
  - set up a **[trigger]** to execute it at specific intervals :alarm_clock:

  >  The following sample JSON **payload** (function input parameter)
  >  can be used to specify the time-offs group:
  >  ```json
  >  {
  >    "timeoffs": "vac"
  >  }
  >  ```

  Refer to the [DigitalOcean's documentation][functions] to learn
  more about using serverless functions.

[doctl]: https://docs.digitalocean.com/reference/doctl/how-to/install/
[namespc]: https://docs.digitalocean.com/products/functions/how-to/create-namespaces/
[trigger]: https://docs.digitalocean.com/products/functions/how-to/schedule-functions/



### :whale:    Deploy Using Docker    

If Docker is installed on your system, you can execute the script using
docker compose through the supplied `run.sh` script.

  1. Choose how to publish the :calendar: iCalendar file (.ics) - 
     upload to DigitalOcean Spaces or save to a local file.  
     The setting is controlled by the `SAVE_TO` environment variable.
     It is set in the `docker-compose.yml`, but can also be overriden
     by defining it in the `.env` file.  
      
     - `SAVE_TO=dospaces` - publish to DO Spaces
     - `SAVE_TO=file` - save to a local file.
                        The path for the file is defined in `config.yml`

  2. Build the Docker image:
     ```sh
     docker compose build
     ```

  3. Add executable permissions to the `run.sh` file:
     ```sh
     chmod +x run.sh
     ```

  4. Execute the script with the desired time-off group:
     ```bash
     ./run.sh timeoffs=vac
     ```

The above command will generate an iCalendar file for the `vac` group,
which corresponds to vacation time-offs.



## Disclaimer
Please note that this project is not affiliated with or endorsed by BambooHR®.


## Feedback
If you encounter any issues or have any suggestions, please open an issue in
this repository. All feedback is greatly appreciated!
