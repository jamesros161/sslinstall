import requests, sys, json, time, random, string, os
from classes.Log import Log
log = Log()

class Comodo():
    def __init__(self, isTestSsl):
        """Class used to make calls to Comodo's API
        """

        log.debug_startinst(self)

        self.urls = {
	        'decode' : 'https://secure.comodo.net/products/%21DecodeCSR',
	        'autoapplyssl' : 'https://secure.comodo.net/products/!AutoApplySSL',
	        'collectssl' : 'https://secure.comodo.net/products/download/CollectSSL'
        }
        #Comodo login Credentials stored in a seperate Credentials file
        #JSON format {"loginName": "<login username>", "loginPassword": "<login password>"}
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path + '/../comodocreds.json', 'r') as comodoCreds:
                self.creds = json.load(comodoCreds)
        	
        self.headers = {
	        'Content-Type' : 'application/x-www-form-urlencoded',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
	    }
        randomString = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
        uniqueValue = randomString.upper()
        self.args = {
	        "showCSR" : "N",
            "showErrorCodes" : "N",
            "showErrorMessages" : "Y",
            "showFieldNames" : "N",
	        "showEmptyFields" : "N",
            "showCN" : "N",
            "showAddress" : "N",
            "showCSRHashes2" : "Y",
            "product" : "488",
            "years" : "1",
            "serverSoftware" : "22",
            "uniqueValue" : uniqueValue,
            "dcvMethod" : "HTTP_CSR_HASH",
            "isCustomerValidated" : "Y",
            "test" : isTestSsl
        }
    
        log.debug_comodoargs(self, {'creds': self.creds, 'headers': self.headers, 'args':self.args})
        log.debug_endinst(self)

    def setDcvMethod(self, dcvmethod):
        """This Method is used to set the dcvMethod to Https if necessary
        
        Arguments:
            dcvmethod {string} -- If called, this should likely be 'https
        """
        log.debug_startmethod(self.setDcvMethod)

        self.args['dcvMethod'] = dcvmethod

    def request(self, requestUrl, requestData):
        """Use requests module to send request to comodo's API
        
        Arguments:
            requestUrl {string} -- the  URL of the specific Comodo API
            requestData {dict} -- list of data / parameters for Comodo
        
        Returns:
            object  -- Requests Response object
        """

        log.debug_startmethod(self.request)

        response = requests.post(requestUrl, 
            headers=self.headers, data=requestData)
        responseDecoded = response.text.splitlines()

        log.debug_endmethod(self.request)

        return responseDecoded

    def get_csr_hashes(self, csr_data):
        """Connect to the DecodeCSR API to get hashes from CSR
        
        Arguments:
            csr_data {string} -- CSR string
        
        Returns:
            dict -- md5 and sha256 strings in dictionary
        """
        log.debug_startmethod(self.get_csr_hashes)

        request_data={
            'loginName': self.creds["loginName"],
            'loginPassword': self.creds["loginPassword"],
            'showCsr': self.args["showCSR"],
            'showErrorCodes': self.args["showErrorCodes"],
            'showErrorMessages': self.args["showErrorMessages"],
            'showFieldNames': self.args["showFieldNames"],
            'showEmptyFields': self.args["showEmptyFields"],
            'showCN': self.args["showCN"],
            'showAddress': self.args["showAddress"],
            'showCSRHashes2': self.args["showCSRHashes2"],
            'product': self.args["product"],
            'csr': csr_data
            }
        log.debug(request_data)
        response = self.request(self.urls['decode'], 
            request_data)

        if response[0] == '0':

            log.debug(response)
            
            md5 = response[1].split('=')
            sha256 = response[3].split('=')
            responseDecoded = {
                'md5' : md5[1],
                'sha256' : sha256[1]
            }
        if response[0] != '0':
            print("\tThe data you entered is invalid!\n\t" + 
            "Take a deep hard look at yourself\n\tAnd reconsider " + 
            "whether or not you know what you are doing...\n")
            sys.exit()

        log.debug_endmethod(self.request)

        return responseDecoded
    
    def orderSsl(self, csr):
        """Places order request to Comodo
        
        Arguments:
            csr {string} -- CSR String
        
        Returns:
            list -- list containing response code and ssl Order number
        """
        log.debug_startmethod(self.orderSsl)

        request_data={
            'loginName': self.creds["loginName"],
            'loginPassword': self.creds["loginPassword"],
            'product': self.args["product"],
            'years' : self.args["years"],
            'serverSoftware' : self.args['serverSoftware'],
            'uniqueValue' : self.args['uniqueValue'],
            'dcvMethod' : self.args['dcvMethod'],
            'isCustomerValidated' : self.args['isCustomerValidated'],
            'test' : self.args['test'],
            'csr' : csr
        }

        response = self.request(self.urls['autoapplyssl'], 
            request_data)
        sslOrder = response
        if int(sslOrder[0]) != 0:
            print("Comodo SSL Order Failed\n \
                Comodo Error message : " + str(sslOrder[1]))
            log.error_failedSslOrder(self.orderSsl, sslOrder[1])

        if int(sslOrder[0]) == 0:
            log.info_sslOrderSuccess(self.orderSsl, sslOrder[1])

        log.debug_endmethod(self.orderSsl)

        return sslOrder

    def collectSsl(self, sslOrderNumber):
        """Collects SSL Certificate from Comodo
         
         Arguments:
            sslOrderNumber {string} -- SSL Order Number

         Returns:
            list -- list containing raw SSL Cert strings
        """
        request_data={
            'loginName': self.creds["loginName"],
            'loginPassword': self.creds["loginPassword"],
            'orderNumber': sslOrderNumber,
            'queryType' : 1,
            'responseEncoding' : 0,
            'responseFormat' : 0,
	        'responseType' : 3
        }
        request = requests.post(self.urls["collectssl"],
            request_data)
        request = request.text.splitlines()

        #This section is important:
        #if The request[0] == 0, that means comodo is still proccessing
        #the script will wait 60 seconds between retries up to 10 retries

        x = 0
        while int(request[0])  == 0:
            if x == 10:
                log.error_failedCollectSSL(self.collectSsl)
                sys.exit(1)
            print('Waiting for Comodo to Process Order...')
            time.sleep(60)
            request = requests.post(self.urls["collectssl"],
            request_data)
            request = request.text.splitlines()
            x = x + 1
        if int(request[0]) < 0:
            return request[1]
        if int(request[0]) == 2:
            log.info_collectSslSuccess(self.collectSsl, request)
            return request
