import json, os, subprocess, sys, urllib.parse, requests
from pwd import getpwnam
from grp import getgrnam

from classes.Log import Log
from classes.whm import WHM
from classes.Comodo import Comodo
from classes.Commands import Commands

log = Log()
whm = WHM()
options = Commands()
com = Comodo(options.input_args['testssl'])

class Domain():
    def __init__(self):
        """Domain class handles collection, and storage of domain info and SSL data
        
        Arguments:
            input_args {dict} -- input arguments
        """

        #sets whether or not to use test data or live data
        
        self.testMode = options.input_args['testmode']
        log.debug_startinst(self)

        #Uses test data for testing / debugging
        if self.testMode:
            path = os.path.dirname(os.path.realpath(__file__))
            with open(path + '/../test/testCsrInputData.json', 'r') as testCsrInputData:
                self.csr_input_data = json.load(testCsrInputData)
                log.info_storecsr(self, self.csr_input_data)
            with open(path + '/../test/testDomainData.json', 'r') as testDomainData:
                self.domain_data = json.load(testDomainData)
                log.info_gotdomdata(self,self.domain_data)
            with open(path + '/../test/testCsrData.json', 'r') as testCsrData:
                self.csr_data = json.load(testCsrData)
                log.info_storedcsrdata(self,self.csr_data)
            with open(path + '/../test/testDcvData.json', 'r') as testDcvData:
                self.dcv_data = json.load(testDcvData)
                log.info_storeddcvdata(self,self.dcv_data)
            with open(path + '/../test/testSslOrder.json', 'r') as testSslOrder:
                self.sslOrder = json.load(testSslOrder)
                log.info_sslOrderSuccess('testMode' ,self.sslOrder[1])
            with open(path + '/../test/testSslCert.json', 'r') as testSslCert:
                self.SslCertRaw = json.load(testSslCert)
            self.sslCert = self.urlEncodeCrt()

        #uses live data
        if not self.testMode:
            self.csr_input_data = {
                'domain_name' : options.input_args['domain'],
                'emailAdd' : options.input_args['email'],
                'city' : options.input_args['city'],
                'state' : options.input_args['state'],
                'country' : options.input_args['country'],
                'company' : options.input_args['organization'],
                'division' : options.input_args['unit']
            }
            
            log.info_storecsr(self, self.csr_input_data)

            #This is where the WHMAPI call is made to obtain domain / user data
            self.get_domain_data = whm.get_domain_data(self.csr_input_data['domain_name'])
            self.domain_data = {
                'domain_name' : self.csr_input_data['domain_name'],
                'documentroot' : self.get_domain_data['userdata']['documentroot'], 
                'homedir' : self.get_domain_data['userdata']['homedir'], 
                'group': self.get_domain_data['userdata']['group'], 
                'user': self.get_domain_data['userdata']['user'], 
                'ip' : self.get_domain_data['userdata']['ip']
            }
            log.info_gotdomdata(self,self.domain_data)

            #This is where the WHMAPI call is made to obatian the CSR and Private Key
            self.get_csr_data = whm.get_csr_data(self.csr_input_data)
            self.csr_data = {
                'csr' : self.get_csr_data['csr'],
                'csr_file' : self.get_csr_data['csrfile'],
                'key' : self.get_csr_data['key'],
                'key_file' : self.get_csr_data['keyfile']
            }
        
            log.info_storedcsrdata(self,self.csr_data)

            self.dcv_data = {}

            #This is where the Comodo API is called to obtain CSR Hashes
            self.get_csr_hashes = com.get_csr_hashes(
                self.csr_data['csr'])
            log.debug(self.get_csr_hashes)

            self.dcv_data['sub_dir'] = '/.well-known/pki-validation'
            self.dcv_data['full_dir'] = self.domain_data['documentroot'] + \
                self.dcv_data['sub_dir']
            self.dcv_data['filename'] = '/' + self.get_csr_hashes['md5'] + \
                '.txt'
            self.dcv_data['filepath'] = self.dcv_data['full_dir'] + \
                self.dcv_data['filename']
            self.dcv_data['url'] = self.domain_data['domain_name'] + \
                self.dcv_data['sub_dir'] + self.dcv_data['filename']
            self.dcv_data['dcv_method'] = 'http'
            self.dcv_data['http_url'] = 'http://' + self.dcv_data['url']
            self.dcv_data['https_url'] = 'https://' + self.dcv_data['url']
            self.dcv_data['md5'] = self.get_csr_hashes['md5']
            self.dcv_data['sha256'] = self.get_csr_hashes['sha256']
            self.dcv_data['dcvcontent'] = self.dcv_data['sha256'] + \
                ' comodoca.com\n' + com.args['uniqueValue']

            log.info_storeddcvdata(self, self.dcv_data)
            
            #DCV Directory and Files are created here, the self validated using Requests
            self.makedir()
            self.makedcvfile()
            self.selfValidateDCV()

            #This is where the Order is placed
            self.sslOrder = com.orderSsl(self.csr_data['csr'])

            #This is where the SSL Is collected
            self.SslCertRaw = com.collectSsl(self.sslOrder[1])
            self.sslCert = self.urlEncodeCrt()


        log.debug_endinst(self)

    def makedir(self):
        """This Method uses subprocess to make the DCV Directory"""

        log.debug_startmethod(self.makedir)

        popen_args = ["mkdir", '-pvm' , '755', self.dcv_data['full_dir']]

        reqError = subprocess.Popen(popen_args, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
            ).communicate()
        if len(reqError[1]) > 0:
            log.error_mkdirerror(self.makedir, self.dcv_data['full_dir'], reqError[1])
            sys.exit('There was a problem creating the directory')
        if len(reqError[1]) == 0:
            log.info_dircreated(self.makedir, self.dcv_data['full_dir'])

        log.debug_endmethod(self.makedir)
    

    def makedcvfile(self):
        """This Method creates the DCV File itself"""

        log.debug_startmethod(self.makedcvfile)
        
        f = open(self.dcv_data['filepath'], 'w')
        f.write(self.dcv_data['dcvcontent'])

        try:
            os.chown(self.dcv_data['filepath'], 
                getpwnam(self.domain_data['user']).pw_uid, 
                getgrnam(self.domain_data['group']).gr_gid)
        except KeyError as e:
            log.error_chown(self.makedcvfile, self.domain_data['user'], 
            self.domain_data['group'], str(e))
            print('There was a problem setting file permissions\n \
                for the DCV file: ' + self.dcv_data['filepath'])
            sys.exit(1)
        else:
            log.info_chowndone(self.makedcvfile, self.domain_data['user'],
            self.domain_data['group'])
        log.debug_endmethod(self.makedcvfile)

    def selfValidateDCV(self):
        """Validates DCV file and determines HTTP or HTTPS DCV"""

        requestUrl = self.dcv_data['http_url']
        
        response = requests.get(requestUrl, allow_redirects=False)
        if response.status_code != 200:
            if response.status_code == 301:
                requestUrlHttps = self.dcv_data['https_url']
                responseHttps = requests.get(requestUrlHttps, allow_redirects=False, verify=False)
                if responseHttps.status_code != 200:
                    self.dcv200fail(responseHttps.status_code, requestUrlHttps)
                if responseHttps.status_code == 200:
                    self.isDcvContentMatch(responseHttps)
                    com.setDcvMethod('HTTPS_CSR_HASH')
            else:
                self.dcv200fail(response.status_code, requestUrl)
                            
        if response.status_code == 200:
            self.isDcvContentMatch(response)
        
    def dcv200fail(self, httpsStatusCode, requestUrlHttps):
        """Logs error for DCV responses other than 200
        
        Arguments:
            httpsStatusCode {string} -- Returned status code
            requestUrlHttps {URL} -- URL
        """
        
        log.error_dcvfailnot200(self.dcv200fail,requestUrlHttps, httpsStatusCode)
    
    def isDcvContentMatch(self, response):
        """Verifies that the DCV file contents match Hashes
        
        Arguments:
            response {object} -- Requests Response object
        """
        if response.text != self.dcv_data['dcvcontent']:
            log.error_dcvfailhashmismatch(self.selfValidateDCV, 
                response.text, self.dcv_data['dcvcontent'])
            sys.exit(1)
        if response.text == self.dcv_data['dcvcontent']:
            self.dcv_data['dcv_method'] = 'https'
            log.info_dcvsuccess(self.selfValidateDCV)

    def urlEncodeCrt (self):
        """Encodes Cert and CA Bundle to an acceptable format
           for use by WMHAPI1
        
        Returns:
            dict  -- Dict containing cabundle and certificate
        """
        beginString = [i for i, x in enumerate(self.SslCertRaw) if x == "-----BEGIN CERTIFICATE-----"]
        endString = [i for i, x in enumerate(self.SslCertRaw) if x == "-----END CERTIFICATE-----"]
        s = '\n'
        sslCert = {
            'cabundle' : urllib.parse.quote_plus((s.join(self.SslCertRaw[beginString[0]:endString[0] + 1]))),
            'certificate' : urllib.parse.quote_plus((s.join(self.SslCertRaw[beginString[1]:endString[1] + 1])))
        }

        return sslCert
        
