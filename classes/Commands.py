import argparse
from classes.Log import Log
log = Log()
class Commands():
  def __init__(self):
    """Creates Parser to accept Command Line arguments"""
    log.debug_startinst(self)


    parser = argparse.ArgumentParser(description='Command Line CSR Input Options')
    parser.add_argument('-d', '--domain', required=True, help='Domain Name')
    parser.add_argument('-e', '--email', default='', help='Email Address')
    parser.add_argument('-c', '--city', default='', help='City / Locality')
    parser.add_argument('-s', '--state', default='', help='State / Province')
    parser.add_argument('-C', '--country', default='', help='Country Code - 2 Chars')
    parser.add_argument('-o', '--org', default='', help= 'Organization / Company')
    parser.add_argument('-u', '--unit', default='', help='Unit / Division')
    parser.add_argument('-t', '--testssl', default='N', choices=['Y', 'N'], metavar='Comodo Test SSL Purchasing')
    parser.add_argument('-T', '--testmode', default='N', help=['Y', 'N'], metavar='Run Script w/ Test Data')
    args = parser.parse_args()
 
    self.input_args = {
      'domain': args.domain,
      'email': args.email,
      'city': args.city,
      'state': args.state,
      'country': args.country,
      'organization': args.org,
      'unit': args.unit
    }
    
    self.input_args['testssl'] = args.testssl
    
    if args.testmode == 'Y':
      self.input_args['testmode'] = True
    if args.testmode == 'N':
      self.input_args['testmode'] = False

    log.info_argsparsed(self, self.input_args)

    log.debug_endinst(self)
