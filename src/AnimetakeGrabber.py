'''
Created on Mar 25, 2014

@author: Kyle Moy
'''
import os, sys, requests, urllib2, zipfile, shutil, smtplib
from HTMLParser import HTMLParser
from os.path import basename
from urlparse import urlsplit

class Parser(HTMLParser):
    links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    if ('tid=' in value):
                        value = value.strip()
                        self.links += [value]
    
    def getLinks(self):
        result = self.links
        self.links = []
        return result
                    
def main(argv):
    if (len(argv) < 2):
        print "Usage: <Anime Name> <limit>"
        sys.exit(2)
    base = "http://www.animetake.com/%s"
    show_name = argv[0]
    LIMIT = int(argv[1])
    #email = argv[2]
    ep_num = 0
    parser = Parser()
    next = base % show_name
    ''' Parse Anime Take Pages '''
    while (1):
        if (next == -1):
            print "No more pages"
            break
        print "Requesting page: " + next
        html = requests.get(next)
        if (html.status_code == 404 or ep_num > LIMIT):
            print "Page returned 404! Quitting..."
            break
        ep_num += 1
        html = html.text
        s_pos = html.find('<ul class="catg_list">')
        e_pos = html.find('</ul>',s_pos)
        next_s_pos = html.find('&nbsp;|&nbsp;<a href="')
        if (next_s_pos != -1) :
            next_e_pos = html.find('"',next_s_pos+22)
            next = html[next_s_pos+22:next_e_pos]
        else:
            next = -1
        html = html[s_pos:e_pos]
        parser.feed(html)
        print "Page found, parsing..."
        links = parser.getLinks()
        index = 0
        for link in links:
            print 'Downloading link %s of episode %s' % (index,ep_num)
            download(link, show_name, index)
            index += 1
    print 'Job Complete'    
    ''' WEB APPLICATION =============================
    if (os.path.isdir('tmp/' + show_name + '/')):
        if (not os.path.isdir('downloads/')):
            os.makedirs('downloads/')
        zipf = zipfile.ZipFile('downloads/' + show_name + '.zip', 'w')
        zipdir(show_name + '/', zipf)
        zipf.close()
        shutil.rmtree(show_name + '/')
        path = 'http://www.kylemoy.org/projects/animetake/downloads/%s.zip' % show_name
        message = 'Congrats! Parsing %s from animetake.com was successful!\nClick the link below to download the torrents.\n\n%s'  % (show_name, path)
    else:
        message = 'Sorry! We couldn\'t parse %s from animetake.com!\nCheck to make sure that show exists, is spelled correctly, and that animetake.com is up!'  % show_name
        

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail('kylelmoy@kylemoy.org', email, 'Subject: %s\n\n%s' % ('Your Animetake.com Links!', message))
        print "Successfully sent report"
    except smtplib.SMTPException:
        print "Error: unable to send report"
    '''
    
def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            thisPath = os.path.join(root, file)
            zip.write(thisPath,os.path.basename(thisPath))

def url2name(url):
    return basename(urlsplit(url)[2])

def download(url, path, index, localFileName = None):
    localName = url2name(url)
    req = urllib2.Request(url)
    r = urllib2.urlopen(req)
    if r.info().has_key('Content-Disposition'):
        # If the response has Content-Disposition, we take file name from it
        localName = r.info()['Content-Disposition'].split('filename=')[1]
        if localName[0] == '"' or localName[0] == "'":
            localName = localName[1:-1]
    elif r.url != url: 
        # if we were redirected, the real file name we take from the final URL
        localName = url2name(r.url)
    if localFileName: 
        # we can force to save the file as specified name
        localName = localFileName
    if (not os.path.isdir(path)):
        os.makedirs(path)
    f = open(path + '/[' + str(index) + ']' + localName, 'wb')
    f.write(r.read())
    f.close()
    
if __name__ == '__main__':
    main(sys.argv[1:])