'''
Created on Feb 24, 2022

@author: bayden
'''

class Transaction(object):
    '''
    classdocs
    '''

    def __init__(self, tid: str, userTo: str, userFrom: str, amount: str, status: str, adcr: str):
        '''
        Constructor
        '''
        self.tid = tid
        self.userTo = userTo
        self.userFrom = userFrom
        self.amount = amount
        self.status = status
        self.adcr = adcr
        #ADC = Accepted, Denied, or Completed
        #Completed means that it is either fully complete, or
        # or that userTo hasnt Accepted or Denied yet
        
    def __str__(self):
        #return 'TID: {}\nUserTo: {}\nUserFrom: {}\nAmount: {}\nStatus: {}\nadcr: {}'.format(self.tid,self.userTo,self.userFrom,self.amount,self.status,self.adcr)
        return '{}\n{}\n{}\n{}\n{}\n{}'.format(self.tid,self.userTo,self.userFrom,self.amount,self.status,self.adcr)

    def __stri__(self):
        return 'Transaction ID: {}\nSent to: {}\nSent from: {}\nAmount: {}\nStatus: {}\nAccepted/Denied/Refund/Completed: {}'.format(self.tid,self.userTo,self.userFrom,self.amount,self.status,self.adcr)


