'''
Created on Feb 24, 2022

@author: bayden
'''

class Cuser(object):
    '''
    classdocs
    '''

    def __init__(self, u: str, p: str, a: str):
        '''
        Constructor
        '''
        self._username = u
        self._password = p
        self._alias = a
        
    def __str__(self):
        return 'Alias:{}\nUsername:{}\n'.format(self._alias,self._username)


  
    def login(self, u: str, p: str) -> bool:
        if ((self._username == u) and (self._password == p)):
            return True
        else:
            return False
