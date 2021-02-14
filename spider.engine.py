import os
import re
import requests
# you know what, fuck these fancy coders. I'm going to have to use a global variable here
# because that helps me organize everyything in my head while writing this script

yetToCrawl = []
urlstart = ''
host = ''
maxdepth = 0
depthnow = 0
download = False
dontscrape = []
hostonlydl = True
hostonly = False
linkstotal = []
dllimit = 0
dlnow = 0


def recursivecrawl(pagedata):
    global linkstotal
    global host
    global maxdepth
    global depthnow
    global download
    global dontscrape
    global hostonlydl
    global hostonly
    global yetToCrawl
    global dlnow
    global depthnow

    ##download is boolean
    ##linkstotal is all links yet to crawl
    ##host is host duh
    ##hostonly is boolean
    ##if pagedata is '', continue, if not, then its

    ##try to replace for // links here
    if pagedata != '':
        varlinks = pullLinks(pagedata)
    else:
        varlinks = ''

    if type(varlinks) is list:
        for x in varlinks:
            ##dont add if its not a host link
            if hostonly == True:
                if x.find(host) <= -1:
                    break
            ##add if not in lists
            if x not in yetToCrawl and x not in linkstotal and x != '':
                yetToCrawl.append(x)
                linkstotal.append(x)
                ##dl it
                filelen = x.split('/')

                if filelen[len(filelen) - 1] == '':
                    filename = filelen[len(filelen) - 2]
                    filename = filename + 'index'
                else:
                    filename = filelen[len(filelen) - 1]


                if hostonlydl == True and x.find(host) > -1 or hostonlydl == False:
                    dlIt = dlFile(x, os.getcwd() + '/mines/' + filename)
                    print(dlIt)
                    dlnow += 1
    ##stop if its empty

    if depthnow >= maxdepth or len(yetToCrawl) == 0:
        print('Completed. \n')
        stringlinks = ''
        for x in linkstotal:
            print(x + '\n')
            stringlinks += x + '\n'
        a = open(os.getcwd() + '/links.txt', 'w')
        a.write(stringlinks)
        a.close()
        return
    ##continue, when recursing, this is where we will end up if its like a jpg or something.
    cont = yetToCrawl.pop(0)
    if cont.endswith('/') or cont.endswith('.js') or cont.endswith('.php') or cont.endswith('.htm') or cont.endswith('.html'):
        print('getting: ' + cont + '\n')
        req = requests.get(cont, timeout = 7)
        if req.ok:
            vardata = req.text
            recursivecrawl(vardata)
        else:
            recursivecrawl('')
    else:
        depthnow += 1
        recursivecrawl('')


def dlFile(link, path):
    global dllimit
    global dlnow
    if dlnow >= dllimit:
        return('max dl limit achieved\n')

    req = requests.get(link, stream=True)
    if req.ok:
        print(str(dlnow) + ' of ' + str(dllimit) + '\n')

        with open(path, 'wb') as f:
            f.write(req.content)
        del f
        return('Written to: ' + path)
    else:
        return(req.status_code)

def pullLinks(str):
    linksfound = []
    if str.find('"') > -1 and str.find("'") > -1:
        linksplit = str.split('"')
        linksplit2 = str.split("'")
        for x in linksplit:
            strsplit = x.split('"')[0]
            strsplit = strsplit.replace('u002F', '')
            if strsplit.startswith('https://') or strsplit.startswith('http://'):
                if strsplit not in linksfound:
                    linksfound.append(strsplit)
        for x in linksplit2:
            strsplit = x.split("'")[0]
            if strsplit.startswith('https://') or strsplit.startswith('http://'):
                if strsplit not in linksfound:
                    linksfound.append(strsplit)
    if len(linksfound) > 0:
        return(linksfound)
    elif len(linksfound) == 0:
        return('No links found..\n')

def main(config):
    ##vars
    global host
    global urlstart
    global maxdepth
    global download
    global dontscrape
    global hostonlydl
    global hostonly
    global dllimit
    global dlnow

    a = open(os.getcwd() + '/config.cfg')
    opts = a.read()
    a.close()
    options = opts.splitlines()
    ##config begin
    for x in options:

        if x.find('HERE') > -1:
            x = x.replace('HERE', os.getcwd())

        if x.find('url host ') > -1:
            host = x.split('url host ')[1]
        if x.find('url start ') > -1:
            urlstart = x.split('url start ')[1]
        if x.find('config download true') > -1:
            download = True
        if x.find('config download false') > -1:
            download = False
        if x.find('config crawldepth') > -1:
            maxdepth = int(x.split('config crawldepth ')[1])
        if x.find('config dldepth ') > -1:
            dllimit = int(x.split('config dldepth ')[1])
        if x.find('config hostonlydl true') > -1:
            hostonlydl = True
        if x.find('config hostonlydl false') > -1:
            hostonlydl = False
        if x.find('config hostonly false') > -1:
            hostonly = False
        if x.find('config hostonly true') > -1:
            hostonly = True
        if x.find('config donotscrape ') > -1:
            a = open(x.split('config donotscrape ')[1])
            b = a.read()
            a.close()
            donotscrape = b.splitlines()
    ##config end
    ##options begin
    print('1. recursive crawl\n')
    print('2. simply get links\n')
    inp = input('').rstrip()
    if inp == str(2):
        inp2 = input('url: \n').rstrip()
        req = requests.get(inp2, timeout = 7)
        if req.ok:
            vardata = req.text
            varlist = pullLinks(vardata)
            if type(varlist) is list:
                for x in varlist:
                    print(x)
                    print('\n')
            main()
        else:
            print('error retrieving url\n')
            main()
    if inp == str(1):
        depthnow = 0
        dlnow = 0
        print('getting ' + urlstart + '\n')
        req = requests.get(urlstart)
        if req.ok:
            pagevar = req.text
            print(dlnow)
            recursivecrawl(pagevar)
        else:
            print('Error grabbing page. quitting..')

if __name__=="__main__":
    dat = open(os.getcwd() + '/config.cfg')
    data = dat.read()
    dat.close()
    comfig = data.splitlines()
    main(comfig)
