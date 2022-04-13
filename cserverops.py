'''
Created on Mar 3, 2022

@author: bayden
'''
from contextlib import nullcontext
from cmessage import Cmessage
from cprotocol import Cprotocol
from cuser import Cuser
from transaction import Transaction

class Cserverops(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._users = {}
        self._transactions = {}
        self.sproto = Cprotocol()
        self.connected = False
        self._login = False
        self._route = {'LGIN': self._doLogin, 
                       'LOUT': self._doLogout,
                       'SRCH': self._doSearch,
                       'REGI': self._doRegister,
                       'PAYR': self._doPayRequest,
                       'CHKM': self._doCheckM,
                       'GETM': self._doGetM,
                       'TRAN': self._doUpdateTransactions,
                       'RFND': self._doUpdateTransactions,
                       'CANC': self._doCancel,
                       'CANT': self._doUpdateTransactions}
        self._debug = True
        
    def _debugPrint(self, m: str):
        if self._debug:
            print(m)
        
    def load(self, uname: str, cname: str):
        with open(uname) as fp:
            for line in fp:
                line = line.strip()
                values = line.split()
                user = Cuser(values[0],values[1],values[2])
                self._users[values[0]] = user
                
        with open(cname) as fp:
            for line in fp:
                line = line.strip()
                #tid = fp.readline().strip()
                userTo = fp.readline().strip()
                userFrom = fp.readline().strip()
                amount = fp.readline().strip()
                status = fp.readline().strip()
                adcr = fp.readline().strip()
                t = Transaction(line, userTo, userFrom, amount, status, adcr)
                self._transactions[line] = t
            
    def _doLogin(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        u = req.getParam('username')
        p = req.getParam('password')
        if u in self._users:
            if self._users[u].login(u,p):
                resp.setType('GOOD')
                resp.addParam('message', 'Login successful')
                
                global CURRENT_USER
                CURRENT_USER = u
                
                self._login = True
            else:
                resp.setType('ERRO')
                resp.addParam('message', 'Bad login')
                self.connected = False;
        else:
            resp.setType('ERRO')
            resp.addParam('message', 'Bad login')
            self.connected = False
        return resp

    def _doRegister(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        new_u = req.getParam('username')
        new_p = req.getParam('password')
        new_a = req.getParam('alias')

        if new_u in self._users:
            resp.setType('ERRO')
            resp.addParam('message', 'Username already exists.')
            self.connected = False;
        else:
            #adding the new user to users.txt
            with open('users.txt', 'a') as f:
                string_to_write = ''
                string_to_write = '\n' + new_u + ' ' + new_p + ' ' + new_a
                f.write(string_to_write)
                f.close()
            
            resp.setType('GOOD')
            resp.addParam('message', 'Account created.')

        return resp

    
    def _doLogout(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        resp.setType('GOOD')
        resp.addParam('message','Logout successful')
        self._login = False
        self.connected = False
        return resp
    
    def _doCancel(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        userFrom = req.getParam('userFrom')
        userTo = req.getParam('userTo')
        for i in self._transactions:
            t = self._transactions[i]
            if t.userFrom == userFrom and t.userTo == userTo and t.status == 'P' and t.adcr == 'C':
                tid = t.tid
                resp.addParam('tid', tid)
                resp.addParam('message', 'Transaction successfully canceled')
                resp.setType('GOOD')
        return resp


    def _doSearch(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        cid = req.getParam('cid')
        if cid in self._courses:
            c = self._courses[cid]
            resp.setType('DATA')
            resp.addParam('cid', c.cid)
            resp.addParam('name', c.name)
            resp.addParam('credits', c.credits)
        else:
            resp.setType('ERRO')
            resp.addParam('message', 'course not found')
        return resp

    def _doPayRequest(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        userTo = req.getParam('userTo')
        userFrom = req.getParam('userFrom')
        amount = req.getParam('amount')
        tid = req.getParam('tid')
        if tid in self._transactions:
            resp.setType('ERRO')
            resp.addParam('message', 'Error on Server Side')
        if userTo in self._users:
            resp.setType('GOOD')
            resp.addParam('message', 'Payment Request Sent')
            t = Transaction(tid, userTo, userFrom, amount, status='P', adcr='C')
            file = open('transactions.txt', 'a')
            transaction_readable = t.__str__()
            transaction_readable = str(transaction_readable)
            file.write(transaction_readable)
            file.write('\n')
            file.close()
        else:
            resp.setType('ERRO')
            resp.addParam('message', 'User not found')
        return resp

    def _doCheckM(self, req: Cmessage) -> Cmessage:
        counter = 0
        resp = Cmessage()
        user_requesting = req.getParam('user')
        user_requesting_from = "UserFrom: " + user_requesting
        user_requesting_to = "UserTo: " + user_requesting
        for i in self._transactions:
            t = self._transactions[i]
            if t.userFrom == user_requesting and t.status == 'P' and t.adcr == 'A':
                #if a payment has been accepted while u were gone
                print("PayDAY!")
                counter = counter + 1
            if t.userTo == user_requesting and t.status == 'P' and t.adcr == 'C':
                #if someone is requesting you to pay them
                print("SOMEONE TRYNA HAVE MY PAY THEM")
                counter = counter + 1
            if t.userTo == user_requesting and t.status == 'P' and t.adcr == 'R':
                #if someone has requested a refund
                print("SOMEONE REQUESTING REFUND")
                counter = counter + 1
            if t.userFrom == user_requesting and t.status == 'C' and t.adcr == 'Z':
                print("PAYDAY! (Refund)")
                counter = counter + 1
                #someone payed your refund request
                
        if counter == 0:
            resp.setType('ERRO')
            counter = str(counter)
            message = "You have " + counter + " new messages"
            resp.addParam('message', message)
        else:
            counter = str(counter)
            resp.setType('GOOD')
            message = "You have " + counter + " new messages"
            resp.addParam('message', message)
        return resp

    def _doGetM(self, req: Cmessage) -> Cmessage:
        refund_or_pay = 0
        #refund = 0, pay = 1
        resp = Cmessage()
        print('got to the doGetM')
        user_requesting = req.getParam('user')
        for i in self._transactions:
            t = self._transactions[i]
            if(t.userFrom == user_requesting and t.status == 'P' and t.adcr == 'A') or (t.userFrom == user_requesting and t.status == 'C' and t.adcr == 'Z'):
                refund_or_pay = 1
                resp.setType('WOOH')
                if t.userFrom == user_requesting and t.status == 'C' and t.adcr == 'Z':
                #someone payed me my refund request while I was gone
                    refund_or_pay = 0
                    message = t.userFrom + " has payed you a refund of " + t.amount + " dollars."
                    resp.addParam('message', message)
         
        
                #if a payment has been accepted while u were gone
                walletname = ''
                walletname = user_requesting + "DigitalWallet.txt"
                f = open(walletname, "r")
                content = f.readlines()
                balance = content[2]
                balance = balance.strip()
                prev_balance_copy = balance
                balance1 = balance
                balance1 = balance[8:]
                balance1 = int(balance1)
                balance3 = t.amount.strip()
                balance3 = t.amount
                add = int(balance3)
                balance2 = balance1 + add
                balance2 = str(balance2)
                new_balance_in_file = str("Balance:" + balance2)
                f.close()

                file = open(walletname, "r")
                replacement = ''
                for line in file:
                    line = line.strip()
                    changes = line.replace(prev_balance_copy, new_balance_in_file)
                    replacement = replacement + changes + "\n"
                file.close()
                fout = open(walletname, 'w')
                fout.writelines(replacement)
                fout.close()

                new_t = Transaction(t.tid, t.userTo, t.userFrom, t.amount, 'C', 'C')
                
                if refund_or_pay == 1:
                    message = ''
                    add = str(add)
                    message = t.userTo + " payed you " + add + " dollars."
                    resp.addParam('message', message)
            
                fadd = open(walletname, 'a')

                transaction_readable = new_t.__stri__()
                transaction_readable = str(transaction_readable)

                fadd.write(transaction_readable)
                fadd.close()
                    
                #update transactions
                file = open("transactions.txt")
                replacement = ""
                changes = ""
                marker = 0
                marker2 = 0
                initial = 0
                for line in file:
                    line = line.strip()
                    if marker != 0:
                        marker2 = marker2 + 1
                    if marker2 == 4:
                        changes = line.replace(t.status, new_t.status)
                        replacement = replacement + changes + "\n"
                    if marker2 == 5:
                        changes == line.replace(t.adcr, new_t.adcr)
                        replacement = replacement + changes + "\n"
                        marker = 0
            
                    if line == t.tid:
                        marker = 1

                    if marker2 != 4 and marker2 != 5:
                        if initial == 1:
                            replacement = replacement + line + "\n"
                        
                        if initial == 0:
                            replacement = line + "\n"
                            initial = 1

                    if marker2 == 5:
                        marker2 = 0
                file.close()
                fout = open("transactions.txt", 'w')
                fout.writelines(replacement)
                fout.close()

                break
            #if a payment has been accepted while u were gone
            
            
            if t.userTo == user_requesting and t.status == 'P' and t.adcr == 'R':
                #if someone has requested a refund
                message = t.userFrom + " has requested for you to refund them " + t.amount + " dollars."
                resp.addParam('message', message)
                resp.setType('RFNI') #refund request coming in
                break    

            if t.userTo == user_requesting and t.status == 'P' and t.adcr == 'C':
            #if someone is requesting you to pay them
                message = t.userFrom + "has requested for you to pay them " + t.amount + " dollars."
                resp.addParam('message', message)
                resp.setType('PAYI')
                break
                
                
            # if t.userFrom == user_requesting and t.status == 'P' and t.adcr == 'R':
            #     #if someone has requested a refund
            #     print("SOMEONE REQUESTING REFUND")
            #     message = t.userTo + " is requesting a refund of " + t.amount + " dollars from previous payment ID: " + t.tid + "."
            #     resp.addParam('message', message)
            #     resp.setType('RPAY')
            #     break

        _tid = t.tid
        _userFrom = t.userFrom
        _userTo = t.userTo
        _adcr = t.adcr
        _status = t.status
        _amount = t.amount
        resp.addParam('tid', _tid)
        resp.addParam('userFrom', _userFrom)
        resp.addParam('userTo', _userTo)
        resp.addParam('adcr', _adcr)
        resp.addParam('status', _status)
        resp.addParam('amount', _amount)


        
        return resp
                        
    def _process(self, req: Cmessage) -> Cmessage:
        m = self._route[req.getType()]
        return m(req)
    
    def shutdown(self):
        self.sproto.close()
        self.connected = False
        self._login = False
        
    def _doUpdateTransactions(self, req: Cmessage) -> Cmessage:
        #loop with _transactions[] updating transactions file
        
        
        message_type = req.getType()
        if message_type == 'CANT':
            tid = req.getParam('tid')
            for i in self._transactions:
                tii = self._transactions[i]
                if tii.tid == tid:
                    tid_null = 0
                    userTo = 'null'
                    userFrom = 'null'
                    amount = 'null'
                    adcr = 'null'
                    status = 'null'
        
        if message_type == 'RFND':
            tid = req.getParam('tid')
            #at this point, userTo and userFrom have switched,
            #because this is a refund
            userFrom = req.getParam('userTo')
            adcr = req.getParam('adcr')
            status = req.getParam('status')
            userTo = ''
            amount = ''
            for i in self._transactions:
                ti = self._transactions[i]
                if ti.tid == tid:
                    userTo =  ti.userFrom
                    amount = ti.amount

        if message_type == 'TRAN':
            tid = req.getParam('tid')
            userFrom = req.getParam('userFrom')
            userTo = req.getParam('userTo')
            adcr = req.getParam('adcr')
            status = req.getParam('status')
            amount = req.getParam('amount')
        
        to_write = ""
        f = open("transactions.txt", "r+")
        f.truncate(0)
        f.close()

        f = open("transactions.txt", 'a')

        for i in self._transactions:
            t = self._transactions[i]
            if t.tid == tid:
                if message_type == 'CANT':
                    t.tid = 0
                t.userFrom = userFrom
                t.userTo = userTo
                t.adcr = adcr
                t.status = status
                t.amount = amount
            to_write = t.__str__() + "\n"
            f.write(to_write)
        f.close()
        resp = Cmessage()
        resp.setType('GOOD')
        return resp

    def run(self):
        try:
            #self.doUpdateTransactions()
            #self._transactions.clear()
            #self._users.clear()
            self.load("users.txt","transactions.txt")
            while (self.connected):
                #get message
                self._transactions.clear()
                self._users.clear()
                self.load("users.txt", "transactions.txt")
                req = self.sproto.getMessage()
                self._debugPrint(req)
                
                # process request
                #resp = self._process(req)
                resp = self._process(req)
                print('Resp = ', resp, '\n')
                self._debugPrint(resp)

                # send response
                self.sproto.putMessage(resp)
                
        except Exception as e:
            print(e)
            
        self.shutdown()
    