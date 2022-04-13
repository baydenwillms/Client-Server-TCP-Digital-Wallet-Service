'''
Created on Mar 3, 2022

@author: bayden
'''
from email import message
import socket
from cprotocol import Cprotocol
from cmessage import Cmessage
from random import randint
from transaction import Transaction
import sys

class Cclientops(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._cproto = Cprotocol()
        self._login = False
        self._done = False
        self._debug = True
        
    def _debugPrint(self, m: str):
        if self._debug:
            print(m)
            
    def _connect(self):
        commsoc = socket.socket()
        commsoc.connect(("localhost",50001))
        self._cproto = Cprotocol(commsoc)
            
    def _doLogin(self):
        u = input('Username: ')
        p = input('Password: ')

        global USERNAME
        USERNAME = u
        
        self._connect()
        
        req = Cmessage()
        req.setType('LGIN')
        req.addParam('username', u)
        req.addParam('password', p)
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()
        if resp:
            print(resp.getParam('message'))
            if resp.getType() == 'GOOD':
                self._login = True
            else:
                self._cproto.close()

    def _doRegister(self):
        new_u = input('Enter your desired username: ')
        new_p = input('Enter your desired password: ')
        new_a = str(randint(1,2000))  #alias
        new_pin = input('Enter a 4 digit PIN for your Digital Wallet: ')
        new_b = input('Initial Deposit: ')

        global USERNAME
        USERNAME = new_u

        self._connect()

        req = Cmessage()
        req.setType('REGI')
        req.addParam('username', new_u)
        req.addParam('password', new_p)
        req.addParam('alias', new_a)
        #req.addParam('pin', new_pin)
        self._cproto.putMessage(req)
#up to here is working as i thought 1:45 am
        
        resp = self._cproto.getMessage()
        if resp:
            print(resp.getParam('message'))
            if resp.getType() == 'GOOD':
                #create the new user's digital wallet:
                filename = str((new_u) + 'DigitalWallet.txt')
                with open(filename, 'a') as f:
                    pin_to_write = str('PIN:' + new_pin + '\n')
                    f.write(pin_to_write)
                    owner_to_write = str("Owner:" + new_u + '\n')
                    f.write(owner_to_write)
                    balance_to_write = str("Balance:" + new_b + '\n')
                    f.write(balance_to_write)
                    f.write('Completed Transactions:' + '\n')
                    f.close()

                self._cproto.close()
            else:
                self._cproto.close()

    def _doLogout(self):
        req = Cmessage()
        req.setType('LOUT')
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()
        if resp:
            print(resp.getParam('message'))
        self._login = False
    
    def _doSearch(self):
        cid = input('Course id:')
        
        req = Cmessage()
        req.setType('SRCH')
        req.addParam('cid', cid)
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()
        if resp:
            if resp.getType() == 'DATA':
                print('Course id: {}\nName: {}\nCredits: {}\n'.format(resp.getParam('cid'),
                                                                      resp.getParam('name'),
                                                                      resp.getParam('credits')))
            else:
                print(resp.getParam('message'))

    def _shutdown(self):
        if self._login:
            self._doLogout()
            self._cproto.close()
        self._login = False
        self._done = True

    def _doSignInWallet(self):
        username = input('Enter your username: ')
        pin = input('Enter your PIN: ')

        global USERNAME 
        USERNAME = username

        filename = str(username + 'DigitalWallet.txt')
        try:
            with open(filename) as f:
                lines = f.readlines()
                pin_entered = str('PIN:' + pin)
                pin_in_file = lines[0]
                pin_in_file = pin_in_file.strip()
                pin_entered = pin_entered.strip()

                if pin_in_file == pin_entered:
                    self._openWalletOperations()
                    #lines = f.readlines()
                    #for line in lines:
                        #print(line)
                else:
                    self._openWalletMenu()
        except IOError as e:
            self._openWalletMenu()

    def _doCheckBalance(self):
        walletname = str(USERNAME + "DigitalWallet.txt")
        file = open(walletname)
        content = file.readlines()
        balance = content[2]
        print(balance)
        self._openWalletOperations()

    def _doMakeDeposit(self):
        deposit = input("Enter the amount of dollars to deposit: ")
        deposit_in_file = str('Balance:' + deposit)
        walletname = str(USERNAME + 'DigitalWallet.txt')
        file = open(walletname)
        content = file.readlines()
        file.close()
        prev_balance = content[2]
        #prev_balance_copy = prev_balance
        prev_balance = prev_balance.strip()
        prev_balance_copy = prev_balance

        # balance_add = 0
        # actual_balance_number = [int(i) for i in prev_balance.split() if i.isdigit()]
        # for i in actual_balance_number: 
        #     i = int(i)
        #     balance_add = i + balance_add

        #prev_balance = prev_balance.replace(content[2],'')
        #int(prev_balance)
        balance_a = prev_balance[8:]
        balance_add = int(balance_a)
        new_balance = int(int(deposit) + balance_add)
        new_balance = str(new_balance)
        new_balance_in_file = str('Balance:' + new_balance)
        
        file = open(walletname, "r")
        replacement = ""
        for line in file:
            line = line.strip()
            changes = line.replace(prev_balance_copy, new_balance_in_file)
            replacement = replacement + changes + "\n"
        file.close()
    

        fout = open(walletname, 'w')
        fout.writelines(replacement)
        fout.close()
        print("Deposited " + deposit + " to your account")
        self._openWalletOperations()

    def _doCheckTransactions(self):
        walletname = str(USERNAME + "DigitalWallet.txt")
        file = open(walletname)
        content = file.readlines()
        for line in content:
            line = line.strip()
        transactions = content[3:]
        print(transactions)
        self._openWalletOperations

    def _doPayRequest(self):
        userTo = input('Send to: ')
        userFrom = USERNAME
        amount = input('Payment Amount: ')
        req = Cmessage()
        req.setType('PAYR')
        req.addParam('userTo', userTo)
        req.addParam('userFrom', userFrom)
        req.addParam('amount', amount)
        transaction_id = str(randint(10000,99999))
        req.addParam('tid', transaction_id)
        self._cproto.putMessage(req)

        resp = self._cproto.getMessage()
        print(resp.getParam('message'))
        self._doMainMenu()

    def _doCheckM(self):  
        #first see if there are any new messages
        req = Cmessage()
        req.setType('CHKM')
        req.addParam('user', USERNAME)
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()
        m_type = resp.getType()
        message = resp.getParam('message')
        print(message)
        #display if new messages
        #if no new messages, then go back to previous menu
        if m_type == 'ERRO':
            self._doMainMenu()
        else:
            req = Cmessage()
            req.setType('GETM')
            req.addParam('user', USERNAME)
            self._cproto.putMessage(req)

            resp = self._cproto.getMessage()
            message_type = resp.getType()
            message = resp.getParam('message')
            tid = resp.getParam('tid')
            userFrom = resp.getParam('userFrom')
            userTo = resp.getParam('userTo')
            adcr = resp.getParam('adcr')
            status = resp.getParam('status')
            amount = resp.getParam('amount')

            t = Transaction(tid, userTo, userFrom, amount, status, adcr)
            t_copy = Transaction(tid, userTo, userFrom, amount, status, adcr)

            if message_type == 'WOOH': #GPAY get payment, someone payed you
                print(message)
                t.adcr = 'C'
                t.status = 'C'

            
            else: #PAYI means Pay in
            # if you are receiving a payment request
                print(message)
                user_input = input("Type A to accept, or D to deny.")
                if user_input == 'A':
                    #subtract amount from my wallet
                    #change ADCR of transaction
                    
                    if message_type == 'PAYI':
                        t.adcr = 'A'
                        t.status = 'P'

                    if message_type == 'RFNI':
                        t.adcr = 'Z'
                        t.status = 'C'
                
                #subtracting from wallet
                    amount = int(t.amount) * -1
                    amount = str(amount)
                    walletname = str(USERNAME + 'DigitalWallet.txt')
                    file = open(walletname)
                    content = file.readlines()
                    file.close()
                    prev_balance = content[2]
                    prev_balance = prev_balance.strip()
                    prev_balance_copy = prev_balance
                    balance_a = prev_balance[8:]
                    balance_add = int(balance_a)
                    new_balance = int(int(amount) + balance_add)
                    new_balance = str(new_balance)
                    new_balance_in_file = str('Balance:' + new_balance)
        
                    file = open(walletname, "r")
                    replacement = ""
                    for line in file:
                        line = line.strip()
                        changes = line.replace(prev_balance_copy, new_balance_in_file)
                        replacement = replacement + changes + "\n"
                    file.close()
    

                    fout = open(walletname, 'w')
                    fout.writelines(replacement)
                    fout.close()

                    file = open(walletname, "a")
                    transaction_add = ""
                    new_n_t = Transaction(t.tid, t.userTo, t.userFrom, t.amount, 'C', 'C')
                    transaction_add = str(new_n_t.__stri__())
                    file.write(transaction_add)
                    file.close()

                if user_input == 'D':
                    #change the ADCR of the transaction in transactions
                    t.adcr = 'D'
                    t.status = 'C'
                    
                
                req = Cmessage()
                req.setType('TRAN')  #update transactions
                req.addParam('tid', t.tid)
                req.addParam('userTo', t.userTo)
                req.addParam('userFrom', t.userFrom)
                req.addParam('amount', t.amount)
                req.addParam('status', t.status)
                req.addParam('adcr', t.adcr)
                self._cproto.putMessage(req)
                resp = self._cproto.getMessage()
                updatedT = resp.getType()
                if updatedT == 'ERRO':
                    self._doMainMenu()
                if updatedT == 'GOOD':
                    print("Transaction updated successfully.")
                self._doMainMenu()
            
        print("Message: ", message)
        self._doMainMenu()

    def _doRefund(self):
        userFrom = USERNAME
        tid = input("Enter the Transaction ID (TID) of the payment you want to refund: ")
        tid_in_wallet = 'Transaction ID: ' + str(tid)
        wallet_name = USERNAME + 'DigitalWallet.txt'
        file = open(wallet_name, 'r')
        for line in file:
            line = line.strip()
            if line == tid_in_wallet:
                file.close()
                req = Cmessage()
                req.setType('RFND')  #update transactions
                req.addParam('tid', tid)
                req.addParam('userTo', USERNAME)
                req.addParam('status', 'P')
                req.addParam('adcr', 'R')
                self._cproto.putMessage(req)
                resp = self._cproto.getMessage()
                updatedT = resp.getType()
                if updatedT == 'ERRO':
                    file.close()
                    self._doMainMenu()
                if updatedT == 'GOOD':
                    print("Transaction updated successfully.") 
                    file.close()
                    self._doMainMenu()          

    def _doCancel(self):
        userFrom = USERNAME
        userTo = input("Input the user you sent the payment to: ")
        req = Cmessage()
        req.setType('CANC')
        req.addParam('userFrom', USERNAME)
        req.addParam('userTo', userTo)
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()
        message_type = resp.getType()
        if message_type == 'ERRO':
            print(resp.getParam('message'))
            self._doMainMenu()
        if message_type == 'GOOD':
            print(resp.getParam('message'))
            tid = resp.getParam('tid')
            req = Cmessage()
            req.setType('CANT') #cant is cancel transaction in trasactions.txt
            req.addParam('tid', tid)
            self._cproto.putMessage(req)
            resp = self._cproto.getMessage()
            print("Transaction canceled")

        self._doMainMenu()

    def _openWalletOperations(self):
        print("-------Welcome to your Digital Wallet-------")
        menu = [' 1. Check Balance', ' 2. Make a deposit',' 3. View Transaction History',' 98. Back', ' 99. Exit']
        choices = {'1': self._doCheckBalance, '2': self._doMakeDeposit, 
                    '3': self._doCheckTransactions, '98': self._openWalletMenu, '99': self._shutdown}
        print('\n'.join(menu))
        choice = input('> ')
        if choice in choices:
            m = choices[choice]
            m()    
            
    def _openWalletMenu(self):
        print("-------Digital Wallet Sign-In Menu-------")
        menu1 = [' 1. Sign in to Wallet',' 98. Back', ' 99. Exit']
        if self._login == True:
            choices = {'1': self._doSignInWallet, '2': self._doMakeDeposit, '98': self._doMainMenu, '99': self._shutdown}
        if self._login == False:
            choices = {'1': self._doSignInWallet, '2': self._doMakeDeposit, '98': self._doTopLevelMenu, '99': self._shutdown}
        print('\n'.join(menu1))
        choice = input('> ')
        if choice in choices:
            m = choices[choice]
            m()

    #client side menu before connecting to server   
    # edited successfully for adding register account     
    def _doTopLevelMenu(self):
        print("-------Login Menu-------")
        menu = [' 1. Login', ' 2. Open my Digital Wallet', ' 3. Register an Account',' 99. Exit']
        choices = {'1': self._doLogin, '2': self._openWalletMenu, '3': self._doRegister, '99': self._shutdown}
        print('\n'.join(menu))
        choice = input('> ')
        if choice in choices:
            m = choices[choice]
            m()
        
    def _doMainMenu(self):
        print("-------Main Menu-------")
        menu = [' 1. Open Inbox', ' 2. Open my Digital Wallet', ' 3. Refund a payment', ' 4. Cancel a payment', ' 5. Send Payment Request', ' 6. Search', ' 98. Back', ' 99. Exit']
        choices = {'1': self._doCheckM, '2': self._openWalletMenu, '3': self._doRefund, '4': self._doCancel, '5': self._doPayRequest, '6': self._doSearch, '98': self._doLogout, '99': self._shutdown}
        print('\n'.join(menu))
        choice = input('> ')
        if choice in choices:
            m = choices[choice]
            m()
    
    def run(self):
        while (self._done == False):
            if (self._login == False):
                self._doTopLevelMenu()
            else:
                self._doMainMenu()
        self._shutdown()
        