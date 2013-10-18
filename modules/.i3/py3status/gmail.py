#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import imaplib

username="@EMAIL@"
password="@PASSWORD@"


class Py3status:

    def __init__(self):
        self.unread = 0
        self.init = True

    def __check_mail(self):
        gmail = imaplib.IMAP4_SSL('imap.gmail.com','993')
        gmail.login(username, password)
        gmail.select()
        self.unread = len(gmail.search(None, 'UnSeen')[1][0].split())

    def unread_mail_count(self, json, i3statuscfg):
        """Counts unread mail in gmail inbox."""
        response = {'full_text' : '', 'name' : 'gmail'}
        self.__check_mail()
        if self.unread > 0:
            response.update({'color' : '#FF0000'})
            response['full_text'] = "@"
        return (3, response)


if __name__ == '__main__':
    p = Py3status().unread_mail_count(0, 1)
    print(p)
