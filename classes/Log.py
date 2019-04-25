import logging, os
from datetime import datetime

class Log():
    def __init__(self):
        """Logger class"""

        self.messages = {
            'stored_csrinfo' : 'Received and Stored CSR Info : ',
            'start_class_inst' : 'Started Class Instantiation : ',
            'end_class_inst' : 'End Class Instantiation : ',
            'start_method' : 'Started Method : ',
            'end_method' : 'End Method : ',
            'validapicall' : 'Api Call was Valid. Result data was : ',
            'apifailure' : 'WHMAPI Failure - Error: ',
            'storecsrinfo' : 'Stored CSR input data : ',
            'gotdomdata' : 'Dom Data retrieved : ',
            'storedcsrdata' : 'CSR Data stored : ',
            'storeddcvdata' : 'DCV Data stored : ',
            'mkdirerror' : ' directory could not be created : ',
            'dircreated' : ' directory created successfully : ',
            'chowndone' : ' operation completed successfully : ',
            'chownerror' : ' error when trying to chown : ',
            'dcvfailnot200' : 'DCV Failed. The Response Code was not 200 . Response code = ',
            'dcvfailhashmismatch' : 'DCV Failed. DCV file and Hashes do not match : ',
            'dcvsuccess' : 'Self DCV Validation Success',
            'sslordersuccess' : 'SSL Order was Successful :',
            'sslordererror' : 'There was an error submitting your SSL Order : ',
            'sslcollecterror' : 'There was an error trying to collect the SSL Cert from Comodo : ',
            'collectSslSuccess' : 'SSL Successfully Collected from Comodo : ',
            'inputargs' : 'Input Arguments Parsed : ',
            'comodoargs' : 'Comodo.args has been stored as : '
        }
        
        timestamp = datetime.today().strftime("%Y-%m-%d")
        path = os.path.dirname(os.path.realpath(__file__))

        filename = path + '/../logs/sslinstall_' + timestamp + '.log'

        logging.basicConfig(
            filename=filename,
            filemode='a', 
            format='%(asctime)s ::[ %(levelname)s ]:: %(message)s',
            level=logging.DEBUG
            )

        self.logger = logging.getLogger('general')
    
    #DEBUG Methods

    def debug_startinst(self, debug_location):
        self.logger.debug('%s : %s', self.messages['start_class_inst'], 
            debug_location.__class__.__name__)

    def debug_endinst(self, debug_location):
        self.logger.debug('%s : %s', self.messages['start_class_inst'], 
            debug_location.__class__.__name__)

    def debug_startmethod(self, debug_location):
        self.logger.debug('%s : %s', self.messages['start_method'], 
            debug_location.__name__)

    def debug_endmethod(self, debug_location):
        self.logger.debug('%s : %s', self.messages['end_method'], 
            debug_location.__name__)
    
    def debug(self, message):
        self.logger.debug('%s', message)   

    def debug_comodoargs(self, debug_location, comodoargs):
        self.logger.debug('%s : %s : %s', 
            debug_location.__class__.__name__, 
            self.messages['comodoargs'], comodoargs) 

    #INFO Methods
   
    def info_argsparsed(self, debug_location, input_args):
        self.logger.info('%s : %s : %s', 
            debug_location.__class__.__name__, self.messages['inputargs'], 
            input_args)

    def info_validapi(self, debug_location, api_results):
        self.logger.info('%s : %s : %s', 
            debug_location.__class__.__name__, self.messages['validapicall'], 
            api_results)

    def info_storecsr(self, debug_location, csr_info):
        self.logger.info('%s : %s : %s', 
            debug_location.__class__.__name__, self.messages['storecsrinfo'], 
            csr_info)

    def info_gotdomdata(self, debug_location, dom_data):
        self.logger.info('%s : %s : %s', 
            debug_location.__class__.__name__, self.messages['gotdomdata'], 
            dom_data)

    def info_storedcsrdata(self, debug_location, csr_data):
        self.logger.info('%s : %s : %s', 
            debug_location.__class__.__name__, self.messages['storedcsrdata'], 
            csr_data)
    
    def info_storeddcvdata(self, debug_location, dcv_data):
        self.logger.info('%s : %s : %s', 
            debug_location.__class__.__name__, self.messages['storeddcvdata'], 
            dcv_data)

    def info_chowndone(self, debug_location, username, groupname):
        self.logger.info('%s chown %s:%s %s', 
            debug_location.__name__, username,
            groupname, self.messages['chowndone'])

    def info_dircreated(self, debug_location, filepath):
        self.logger.info('%s : %s : %s', 
            debug_location.__name__, filepath, 
            self.messages['dircreated'])

    def info_collectSslSuccess(self, debug_location, collectSslResponse):
        self.logger.info('%s : %s : %s', 
            debug_location.__name__, self.messages['collectSslSuccess'], 
            collectSslResponse,)

    def info_dcvsuccess(self, debug_location):
        self.logger.info('%s : %s', 
            debug_location.__name__,
            self.messages['dcvsuccess'])
    def info_sslOrderSuccess(self, debug_location, sslOrder):
        self.logger.info('%s : %s : %s', debug_location, 
            self.messages['sslordersuccess'], sslOrder)

    #ERROR messages

    def error_apifailure(self, debug_location, api_results):
        self.logger.error('%s : %s : %s', 
            debug_location.__class__.__name__, self.messages['apifailure'],
            api_results)
    
    def error_mkdirerror(self, debug_location, filepath, reqError):
        self.logger.error('%s : %s : %s : %s', 
            debug_location.__class__.__name__, filepath, self.messages['mkdirerror'],
            reqError)

    def error_chown(self, debug_location, username, groupname, exception):
        self.logger.error('%s : %s : %s : %s %s', 
            debug_location.__name__, username, 
            groupname, self.messages['chownerror'], 
            exception)
            
    def error_dcvfailnot200(self, debug_location, url, errorCode):
        self.logger.error('%s : %s : %s : %s', 
            debug_location.__name__, url, 
            self.messages['dcvfailnot200'], 
            errorCode)
    
    def error_dcvfailhashmismatch(self, debug_location, responseContent, dcvContent):
        self.logger.error('%s : %s DCV file contents: %s Required contents: %s', 
            debug_location.__name__, 
            self.messages['dcvfailhashmismatch'],
            responseContent,
            dcvContent)
    def error_failedSslOrder(self, debug_location, sslOrderError):
        self.logger.error('%s : %s : %s', debug_location.__name__,
            self.messages['sslordererror'], sslOrderError)

    def error_failedCollectSSL(self, debug_location):
        self.logger.error('%s : %s', debug_location.__name__,
            self.messages['sslcollecterror'])    
