# WHMAPI SSL Auto Installer

This application is designs for a fully automated installation of a ComodoCA Domain Verified SSL Certifacate on a cPanel server. While it will work just fine if run manually from a command line, using the required arguments, the program is designed to be called by a front end, such as a customer portal where the customer purchases the SSL certificate, and then the program will take any necessary arguments from the front end, and automatically install the certificate. The application has very extensive logging and is set to DEBUG by default.  

## Getting Started

To get started, clone the repo or download the included files to your IDE working path. This was developed using python3.7, but has been tested in an environment running python3.6 and 3.7. No testing has been done using other versions of Python3. This will not work as is for Python2.x . All imported modules should be included in the core Python modules, with the posible exception of argparse and requests. I found in my Python installation, that there was a Requests module already included in python, but it wasn't the one needed. See Prerequisites for more details.

See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You will need Python3.6 or Python3.7. The following modules are imported in the script, but are included in the Python Standard Library:

  argparse
  json
  os
  getpass
  sys
  time
  random
  string
  subprocess
  urllib.parse
  pwd
  grp
  datetime

The following modules will be required, and depending on your Python environment may or may not already be installed:
  requests v2.21.0 ( http://docs.python-requests.org )  
  
This will have to be run on a server with cPanel / WHM 11+ . This must be run with root privileges ( sudo works fine ). 

You will also need to have a valid account with Comodo / Sectigo that has API access. As far as I know, any Tier2 or Reseller account with them has API access. However, in order to call the AutoApplySSL API with the test = Y flag, and order a "test SSL certificate" you will have to contact Comodo support to get that enabled. Further information regarding Comodo's API can be found here: ( https://secure.comodo.net/api/ )

### Installing

1) Clone repo

```
git clone https://github.com/twmsllc/whm-ssl-autoinstall.git
```
2) cd to project directory

```
cd whm-ssl-autoinstall
```

2) Install requests ( This example installs it using pip. Be sure you run the pip executable for python3.6 or python3.7 depending on which one you plan to use when running this. the exact command for that version of pip will depend on your system. Mine is pip3

```
pip3 install requests
```

3) Create your comodocreds.json file using the following format:

```
{
  "loginName": "<yourusernamehere>",
  "loginPassword": "<yourloginpasswordhere"
}
```
4) If you want to run the script without entering the script's full path every time, create a symlink to your /usr/bin dir
```
ln -s /path/to/git/clone/whm-ssl-autoinstall/sslinstall.py /usr/bin/sslinstall
```


### Running the tests

In order to perform a basic automated test to verify that WHMAPI is working, you can pass the -T=Y (case sensite) argument in the command line when executing the script. This will use test data files from the /test/ project directory rather than generating new CSR, SSL, etc.

NOTE: You will need to adjust the values in the test data files to match a domain that exists on your server if you want the tests to pass. 

This will also bypass any interaction with Comodo's API. You should not see any output to your terminal. Instead, you can check the generated log file. This can be found in the /path/to/git/clone/whm-ssl-autoinstall/logs/ directory

```
sslinstall -d=testdomain.com -T=Y
```

In order to perform a test that goes through the all the standard functions, generates the CSR & Key, CSR hashes, DCV files, and orders a "Test SSL Certificate" from Comodo, then pass the -t=Y argument, but not the T=Y argument.

```
sslinstall -d=testdomain.com -t=Y
```

## Deployment

When deploying in a production environment, no additional steps are required in order for the application to function, however, you may want to adjust the logging level from the default DEBUG to INFO instead. Otherwise, you will start to see some really large log files. 

Please note that the RSA Private Key, CSR, Comodo Order Number, and SSL are all printed to the log files. 

## Contributing

I am not currently looking for any contributions. If you do wish to make a contribution, then you may contact me at dev@twmsllc.com

## Built With

[Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
[WHMAPI1](https://documentation.cpanel.net/display/DD/Guide+to+WHM+API+1) - The API used to interface with cPanel / WHM 
[Requests: HTTP for Humans™](http://docs.python-requests.org) - The Module used to make HTTP requests to Comodo's API
[COMODO CA  Partner API](https://secure.comodo.net/api/) - Comodo CA's API used to obtain SSL certs

## Authors

* **James Rosado** - *Initial work* - [twmsllc](https://github.com/twmsllc)

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the LICENSE file for details

## Acknowledgments

    Thanks to Dustin Weber for giving me his Python crash course book.
        I don't know if I would have ever picked up Python without that.
