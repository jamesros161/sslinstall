import sys, os, subprocess, json, urllib.parse
from classes.Log import Log

log = Log()
class WHM():
    """This is the class used to make calls to WHM
    
    Arguments:
        APIClient {Class} -- [https://github.com/0x6c/whmapi.git]
    
    Returns:
        [NONE] -- [NONE]
    """
    def call(self, function, req_params):
        """Method to run WHMAPI function via subprocess module
        
        Arguments:
            function {string} -- [provides the function to be called]
            req_params {dict} -- [dictionary of key + values]
        """

        log.debug_startmethod(self.call)

        popen_args = ["whmapi1", function ,'--output=json']

        for key , value in req_params.items():
            x = str(key) + "=" + str(value)
            popen_args.append(x)

        reqOutput, reqError = subprocess.Popen(popen_args, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
            ).communicate()

        data = json.loads(reqOutput)
        log.info_validapi(self, [reqOutput,reqError])
        resultCode = data['metadata']['result']
        resultReason = data['metadata']['reason']

        #if the result is successfull, pass the result's data as return value
        if resultCode == 1:
            resultData = data['data']
            return(resultData)

        #If the result is not successfull, print error message and exit with code 1
        else:
            print("""The data you entered is invalid!\n
            Take a deep hard look at yourself\n
            And reconsider whether or not you 
            know what you are doing...""")
            print(str(resultCode) + " --- " + str(resultReason))
            sys.exit(1)
    
    def get_domain_data(self, domain_name):
        """Get Domain and user Data information
        
        Arguments:
            domain_name {string} -- The domain name provided by command line earlier
        
        Returns:
            dict -- collection of domain / user data
        """

        log.debug_startmethod(self.get_domain_data)
        
        return self.call(
            function = 'domainuserdata',
            req_params = {
                'domain': domain_name
            })

    def get_csr_data(self, domain_data):
        """Generate's CSR and Private Key
        
        Arguments:
            domain_data {dict} -- domain data & CSR request data
        
        Returns:
            dict -- CSR and Private Key
        """

        log.debug_startmethod(self.get_csr_data)

        return self.call(
            function = 'generatessl',
            req_params = {
                'domains': domain_data['domain_name'],
                'emailAddress' : domain_data['emailAdd'],
                'countryName' : domain_data['country'],
                'stateOrProvinceName' : domain_data['state'],
                'localityName' : domain_data['city'],
                'organizationName' : domain_data['company'],
                'unitName' : domain_data['division'],
                'keysize' : 2048,
                'skip_certificate' : 1,
                'output' : 'json'
            })

    def install_ssl(self, domain, key, cert, bundle):
        """Installs SSL Certificate on Domain
        
        Arguments:
            domain {string} -- domain name
            key {string} -- Private Key
            cert {string} -- Certificate
            bundle {string} -- CA Bundle
        
        Returns:
            string  -- Success Message
        """

        log.debug_startmethod(self.get_csr_data)

        response = self.call(
            function = 'installssl',
            req_params = {
                'domain' : domain,
                'crt' : cert,
                'cab' : bundle,
                'key' : urllib.parse.quote_plus(key)
            })

        if int(response['status']) == 1:
            return "SSL Certificate installed Successfully"
        if int(response['status']) != 1:
            print("SSL Certificate Installation Failed \n \
                WHMAPI Error Message : " + str(response['message']))

            sys.exit(1)
