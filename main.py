import imaplib
import email
from email.header import decode_header
import os
import re
from credentials import username, password


#Global Variables
download = False        #Activates the downloading of the attached file, if the email contains it
username = username        #The username/email that gets scrubbed through. Imported from credentials.py
password = password     #The Password to the email address. Imported from credentials.py


def fetchEmailData(username, password):
    
    payouts = []
    soNumbers = []
    lots = []
    emailcount = 0  
    
    # create an IMAP4 class with SSL
    conn = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    conn.login(username, password)

    # select a mailbox (in this case, the inbox mailbox)
    # use imap.list() to get the list of mailboxes
    conn.select("INBOX")
    

    
    (retcode, messages) = conn.search(None, "(UNSEEN)")
    if retcode == 'OK':
        
        for num in messages[0].split():
            emailcount += 1
            typ, data = conn.fetch(num, "(RFC822)")
            for response_part in data:
                if isinstance(response_part, tuple):
                    original = email.message_from_bytes(data[0][1])
                    
                    print(original['From'])
                    print(original['Subject'])
                    if original.is_multipart():
                        for part in original.walk():
                            if (part.get_content_type() == 'text/plain') and (part.get('Content-Disposition') is None):
                                payout = textProcessing(str(part.get_payload()), 1)
                                payouts += payout
                            else:
                                if(part.get_filename() is not None):
                                    lotAndSO = re.findall(r'.+(?=[S][O])|\d{6}', str(part.get_filename()))
                                    if (len(lotAndSO) >= 2):
                                        lots.append(lotAndSO[0])
                                        soNumbers.append(lotAndSO[1])

                    typ, data = conn.store(num, "+FLAGS", "\\Seen")   
    
    
    # close the connection and logout
    conn.close()
    conn.logout()
    
    return lots, soNumbers, payouts, emailcount
 
def textProcessing(text, option):
     
    if (option == 1):
        output = re.findall(r'((?<=[\D])\d+[.]\d\d(?!\d))', text)
        return output
    

         
        
    
def main():
    lots, soNumbers, payouts, emailcount = fetchEmailData(username, password)
    print(payouts)
    print(soNumbers)
    print(lots)
    print(emailcount)
    
    

if __name__ == '__main__':
    main()