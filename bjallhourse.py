# -*- coding:utf-8;-*-

import time, re
#from cPAMIE import PAMIE
from sgmllib import SGMLParser
import urllib, urllib2, cookielib, Cookie, codecs
import threading
from time import ctime, sleep
from Queue import Queue
from random import randint
from datetime import date
from threadpool import ThreadPool, makeRequests

NUM_DICT = {}
REF_URL = 'http://beijing.homelink.com.cn/webregister/login.php'
LIANJIA_URL = 'http://beijing.homelink.com.cn'
COMMUNITY = []
TO_MAILS = ['v-chuans@microsoft.com','act.of.war.sunzi@hotmail.com','bessie.yan@thomsonreuters.com']
SAVEFILEPATH = r'D:\\work\\pyoutput\\bjallhourse\\%s%s.csv'
#number of valid char
CHAR_NUM = 4


def LoginPage():
    '''
    login in the web page with username pwd and code
    '''  
    
    # Get login web page
    req = urllib2.Request('http://beijing.homelink.com.cn/webregister/login.php')
    opener = urllib2.urlopen(req)
    cookie = Cookie.SimpleCookie(opener.headers['set-cookie'])

    # get cookie info
    ret = ''
    for v in cookie.values():
        ret += "%s=%s; " % (v.key, v.value)
    #print ret

    # build headers
    headers = { 'Referer' : 'http://beijing.homelink.com.cn',
                'Cookie' : ret,
                'User-Agent' : 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'}

    # get the valicode
    Downloadcode(headers)
    valicode = GetCode(CodeFilter())
    #print valicode

    # build Post data
    login_data = urllib.urlencode({'username' : 'email',#qq email
                                   'password' : 'pwd', #figure pwd
                                   'validateCode': valicode,
                                   'dologin' : '登录'
                                   })

    # POST Login web page
    req.add_data(login_data)
    for (key, val) in headers.items():
        req.add_header(key,val)
    resp = urllib2.urlopen(req)
    content = resp.read()
    if content[:3]==codecs.BOM_UTF8:
        content = content[3:]    
    #print content
    #if content contains info "179095423", it's successful.
    #you are now logged in and can access "members only" content.
    #when your all done be sure to close it
    opener.close()
    resp.close()
    return headers


def OpenWebPage(url,headers):
    '''
    read the content of web page
    '''
    req = urllib2.Request(url, headers=headers)
    opener = urllib2.urlopen(req)
    content = opener.read()
    if content[:3]==codecs.BOM_UTF8:
        content = content[3:]    
    #print content
    opener.close()
    return content


def Downloadcode(headers,savefile='code.gif',url=r'http://beijing.homelink.com.cn/validreg.php'):
    '''
    download code image from url
    '''
    import urllib2
    req = urllib2.Request(url, headers=headers)
    res_img = urllib2.urlopen(req)
    f = open(savefile, 'wb')
    f.write(res_img.read())
    f.close()


def DownloadcodeForTrain(savefile='code.gif',url=r'http://beijing.homelink.com.cn/validreg.php'):
    '''
    download code image from url
    '''
    import urllib2
    req = urllib2.Request(url)
    #req.add_header("Cookie", cookie)
    req.add_header("Referer", REF_URL)
    res_img = urllib2.urlopen(req)
    f = open(savefile, 'wb')
    f.write(res_img.read())
    f.close()


def CodeFilter(fromfile='code.gif', tofile='code_temp.png'):
    '''
    pre-process the image.
    '''
    import Image,ImageEnhance,ImageFilter, ImageDraw
    import sys
    image_name = 'code.gif'
    im = Image.open(image_name)
    im_new = im.convert('L')    
    draw = ImageDraw.Draw(im_new)
    draw.line((0, 0, im.size[0], 0), fill=255)
    draw.line((0, 0, 0, im.size[1]), fill=255)
    draw.line((0, im.size[1]-1, im.size[0], im.size[1]-1), fill=255)
    draw.line((im.size[0]-1, 0, im.size[0]-1, im.size[1]-1), fill=255)
    enhancer = ImageEnhance.Brightness(im_new)
    im_new = enhancer.enhance(2.0) 
    enhancer = ImageEnhance.Contrast(im_new)
    im_new = enhancer.enhance(4) 
    im_new.convert('1')
    im_new.filter(ImageFilter.MedianFilter)
    im_new.save(tofile)
    return im_new


def TrainCode(im, sname='code.txt'):
    '''
    train the data
    '''
    fh = open(sname,'a')
    for img in GetFourNumImage(im):
        fh.write(ImageToString(img)+'\n')
    fh.close()


def GetCode(im):
    '''
    get the four code numbers.
    '''
    retVal = ''
    LoadCodeFromTrain()
    for img in GetFourNumImage(im):
        retVal += NUM_DICT[ImageToString(img)]
    return retVal

    
def GetFourNumImage(img):    
    w,h = img.size
    ws = w/CHAR_NUM
    rValue = []    
    im = img.load()
    for i in range(CHAR_NUM):
        left = i*ws
        upper = 0
        right = (i+1)*ws+1
        lower = h
        breakout = False
        for ww in range(i*ws, (i+1)*ws):
            for hh in range(upper,h):
                #print ww,' ',hh, ' ', im[ww,hh]
                #print 'im %d' %im[ww,hh]
                if im[ww,hh]!=255: 
                    left = ww
                    breakout = True
                    break;
            if breakout: break;            
        #print left
        
        breakout = False
        for ww in range((i+1)*ws-1, left,-1):
            for hh in range(upper,h):
                if im[ww,hh]!=255: 
                    right = ww
                    breakout = True
                    break;                
            if breakout: break;
        #print right

        breakout = False
        for hh in range(upper,h):
            for ww in range(left,right):
                if im[ww,hh]!=255: 
                    upper = hh
                    breakout = True
                    break;
            if breakout: break;
        #print upper

        breakout = False
        for hh in range(h-1,upper,-1):
            for ww in range(left,right):
                if im[ww,hh]!=255: 
                    lower = hh
                    breakout = True
                    break;
            if breakout: break;        
        #print lower

        charImage = img.crop((left,upper,right+1,lower+1))
        charImage.save('fstnum%s.png' %i)
        rValue.append(charImage)
    return rValue


def ImageToString(img):
    '''
    convert image to string with "0" and "1"
    '''
    im = img.load()
    nstr = ''
    for x in xrange(img.size[0]): 
        for y in xrange(img.size[1]):
            if im[x, y] == 255:
                nstr += '0'
            else:
                nstr += '1'
    return nstr


def LoadCodeFromTrain(fName='code.txt'):
    with open(fName) as f:
        for line in f:
            (key, val) = line.split()
            NUM_DICT[key] = val


def SendMail(data,subject):
    import smtplib
    from email.MIMEText import MIMEText
    fromaddr = 'sc369963@gmail.com'  
    toaddrs  = TO_MAILS

    msg = MIMEText(data, 'plain','gb2312')
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = ";".join(toaddrs)
    #msg = 'There was a terrible error that occured and I wanted you to know!'  
  
  
    # Credentials (if needed)  
    username = 'sc369963@gmail.com'  
    password = 'sc369963'  
    
    # The actual mail send  
    server = smtplib.SMTP('smtp.gmail.com:587')  
    server.starttls()  
    server.login(username,password)  
    server.sendmail(fromaddr, toaddrs, msg.as_string())  
    server.quit()


def DealSaledInfoData(list):
    if False:
        print '+'.join(list)    
    result = []
    #result.append(community) #0 community name
    result.append(list[5]) # 1: sale time
    result.append(list[7]) # 2: apartment structure
    result.append(re.findall('\d+\.?\d+',list[9])[0]) # 3: apartment area
    result.append(list[11]) # 4 apartment floar
    result.append(list[13]) # 5: apartment direction
    result.append(re.findall('\d+\.?\d?', list[15])[0]) # 5: unit price
    result.append(re.findall('\d+\.?\d?', list[18])[0]) # 6: total price
    result.append(list[22]) # 7: the employee name
    return result


class GetSaledInfo(SGMLParser):            
    def reset(self):
        self._totalResult = []        
        self._pieces = []
        self._url = ''
        self._inTag_table = False  
        self._test = 0        
        SGMLParser.reset(self)

    def start_table(self, attrs):        
        for k, v in attrs:
            if k=='class' and v=='ccczyc':
                self._inTag_table = True
                break

    def end_table(self):
        if self._inTag_table:
            self._inTag_table = False
            temp = DealSaledInfoData(self._pieces)
            self._totalResult.append(temp)
            self._pieces = []
            
            

    def handle_data(self, text):           
        if self._inTag_table:            
            #self._pieces.append(text.encode('gb2312'))
            text = text.replace('\r','').replace('\n','').replace(' ','').replace('\t','')            
            self._pieces.append(text)
            #print text


    def output(self):              
        """Return processed HTML as a single string"""            
        #for v in self._totalResult:
        #    self._test = 0
        #    for vv in v:
        #        print self._test, '-', vv
        #        self._test += 1
        #    print '-----------END--------------'
        return self._totalResult


def DealSaleInfoData(list):
    if True:
        print '+'.join(list)
    result = []   
    result.append(list[6]) # 0: detail info url    
    result.append(list[3]) # 1: community name
    result.append(list[1]+list[2]+list[3]+list[4]) # 2: address
    result.append(list[7]) # 3: title
    str_temp = list[10].split(',')    
    result.append(str_temp[0]) # 4: apartment structure
    result.append(str_temp[1]) # 5: apartment area
    result.append(str_temp[2]) # 6: apartment float
    str_temp = re.findall('\d+\.?\d?',list[11])
    result.append(str_temp[0]) # 7: unit price
    result.append(list[13])    # 8: total price
    result.append(str_temp[1]) # 9: the number of first should give money
    result.append(str_temp[2]) # 10: the number of every month given money
    result.append(list[18]) # 11: should tax or not
    return result
    

class GetSaleInfo(SGMLParser):
            
    def reset(self):
        self._totalResult = []        
        self._pieces = []
        self._url = ''
        self._div_riljf = False
        self._div_fengren = False
        self._div_junren = False        
        self._div_renfeng = False
        self._div_indetail = False
        self._div_particular = False
        self._div_dujia = False

        self._li_nei_three = False
        self._ol_wuju = False
        self._ul_clearfix = False

        self._test = 0
                
        SGMLParser.reset(self)

    def start_div(self, attrs):        
        for k, v in attrs:
            #print k, v
            if k=='class':
                if v=='riljf':
                    self._div_riljf = True
                    break
                if v=='fengren' and self._div_riljf:
                    self._div_fengren = True
                    break 
                if v=='junren' and self._div_riljf:
                    self._div_junren = True
                    break                 
                if v=='renfeng':
                    self._div_renfeng = True
                    break
                if v=='indetail clearfix':
                    self._div_indetail = True;
                    break
                if v=='particular':
                    self._div_particular = True
                    break
                if v=='dujia':
                    self._div_dujia = True
                    break            
                

    def end_div(self):
        if self._div_riljf:
            if self._div_fengren:
                self._div_fengren = False
                return
            if self._div_junren:
                self._div_junren = False
                return
            if self._div_renfeng and self._div_indetail and self._div_particular and not self._div_dujia:
                self._div_indetail = False
                self._div_renfeng = False
                self._div_particular = False
                if self._ol_wuju:
                    self._pieces.append('免税')
                    self._ol_wuju = False
                else:
                    self._pieces.append('有税')
                self._div_riljf = False 
                #print '+'.join(self._pieces)
                temp = DealSaleInfoData(self._pieces)
                self._totalResult.append(temp)
                self._pieces = []
                #end of <div class='riljf' ...>
                return
            if self._div_dujia:
                self._div_dujia = False
                

    def start_a(self, attrs):
        if self._div_riljf and self._div_junren:
            for k, v in attrs:
                if k=='href':
                    self._pieces.append(LIANJIA_URL+v)
            

    def end_a(self):
        pass

    def start_li(self, attrs):
        if self._div_particular:
            for k,v in attrs:
                if k=='class' and v=='nei_three':
                    self._li_nei_three = True
    
    def end_li(self):
        if self._li_nei_three:
            self._li_nei_three = False

    def start_ol(self, attrs):        
        if self._div_particular:
            self._ol_wuju = True

    def end_ol(self):
        pass

    def start_ul(self, attrs):
        if self._div_particular:
            self._ul_clearfix = True

    def end_ul(self):
        if self._ul_clearfix:
            self._ul_clearfix = False
            
            

    def handle_data(self, text):           
        if self._div_riljf and (self._div_fengren or self._div_junren or self._ul_clearfix) \
                and not (self._li_nei_three or self._ol_wuju or self._div_dujia):
            if self._div_dujia: print '-----------------------'
            text = text.replace('\r','').replace('\n','')
            #self._pieces.append(text.strip().decode('utf-8').encode('utf-8'))
            self._pieces.append(text.strip())
            #print text


    def output(self):              
        """Return processed HTML as a single string"""
        if False:
            for v in self._totalResult:
                self._test = 0
                for vv in v:
                    print str(self._test), '-', vv
                    self._test += 1
                print '----------END-------------'
        return self._totalResult


class MyThreading(threading.Thread):
    '''
    mutithread class
    '''
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.name = name
    def run(self):
        print 'starting ', self.name, ' at: ', ctime()
        self.res = apply(self.func, self.args)
        print self.name, ' finished at: ', ctime()
    def getResult(self):
        return self.res


def WriteFile(filename, queue):
    time.sleep(randint(2,5))
    li = queue.get(block=True, timeout=30)
    fh = codecs.open(SAVEFILEPATH %(filename, str(date.today())), 
                     mode='a')#, encoding='utf-8')
    for v in li:
        temp = ','.join(v)
        #print temp
        fh.write(temp)
        fh.write('\n')
    fh.close()
            

def DealWithSaleInfo(header, page, queue_save, queue):
    '''
    deal with sale info, it will be callde by threadpool
    the data will be put in two queues, one for file writer,
    anther for saledinfo get.
    the return value is true or false,
    true means having data in internet,
    false means nothing in internet
    '''
    url = r'http://beijing.homelink.com.cn/ershoufang/cto0pg%d/' %page
    content = OpenWebPage(url,header)
    #print content
    saleInfo = GetSaleInfo()
    saleInfo.reset()
    saleInfo.feed(content)
    saleInfo.close()
    result = saleInfo.output()
    if len(result)==0: return False
    #WriteFile('saleinfo', result)
    #while queue.full(): time.sleep(randint(1,3))
    # for save to file
    queue_save.put(result, block=True)
    # for deal with saled info
    queue.put(result,block=True)    
    return True



def DealWithSaledInfo(header, queue_save, queue):
    #while queue.empty(): time.sleep(randint(2,5))
    url = r'http://beijing.homelink.com.cn/ershoufang/xqcj/pg%d/%s'
    saleInfo = queue.get(block=True, timeout=30)
    for v in saleInfo:
        if v[1] in COMMUNITY: break
        COMMUNITY.append(v[1])
        url_temp = v[0].split('/')[-1]
        for i in range(1,99):
            content = OpenWebPage(url %(i,url_temp), header)
            saledInfo = GetSaledInfo()
            saledInfo.reset()
            saledInfo.feed(content)
            saledInfo.close()
            result = saledInfo.output()            
            if len(result)==0: break
            print 'page: ',i, ' url: ' ,url %(i, url_temp)
            for vv in result:
                vv.append(v[0])
            queue_save.put(result, block=True)
    
    

if __name__=='__main__':
    
    # for train to get valid code sample
    if False:
        DownloadcodeForTrain()    
        print GetCode(CodeFilter())
        TrainCode(CodeFilter())

    # login in the lianjia web page, get the header
    header = LoginPage()
    num = 5
    
    # get the on sale apartment information, for test
    if False:
        url = r'http://beijing.homelink.com.cn/ershoufang/cto0pg0/'
        content = OpenWebPage(url,header)
        #print content
        saleInfo = GetSaleInfo()
        saleInfo.reset()
        saleInfo.feed(content)
        saleInfo.close()
        saleInfo.output()
        for v in saleInfo.output():
            print ','.join(v)

    # get the saled apartment information, for test
    if False:
        content = None
        #url = r'http://beijing.homelink.com.cn/ershoufang/xqcj/pg1/BJSY84944237.shtml'
        #url = r'http://beijing.homelink.com.cn/ershoufang/xqcj/pg1/BJCY84974980.shtml'
        #content = OpenWebPage(url, header)
        
        if True:
            content =open(r'd:\\cc.html').read()
        saledInfo = GetSaledInfo()
        saledInfo.reset()
        saledInfo.feed(content)
        saledInfo.close()
        saledInfo.output()

    if False:
        # get the total page
        url = r'http://beijing.homelink.com.cn/ershoufang/cto0/'
        content = OpenWebPage(url,header)
        num_apartment = int(re.findall('<strong>(\d+)</strong>', content)[0])
        num = num_apartment / 12
        if num_apartment%12 != 0: num += 1
        print num_apartment, '-', num

    #if True:    
    queue = Queue()
    queue_save_saleInfo = Queue()
    queue_save_saledInfo = Queue()

    #if True:
    dealSaleThread = ThreadPool(10)  
    dealSaledThread = ThreadPool(10)
    saveSaleThread = ThreadPool(1)
    saveSaledThread = ThreadPool(1)
    
    if False:
        #num = 5
        dealSaleParam = [((header, i,queue_save_saleInfo,queue),{}) for i in range(1,num+1)]    
        requests_dealSale = makeRequests(DealWithSaleInfo,dealSaleParam)
        [dealSaleThread.putRequest(req) for req in requests_dealSale]
        
        dealSaledParam = [((header, queue_save_saledInfo, queue),{}) for i in range(1,num+1)]
        request_dealSaled = makeRequests(DealWithSaledInfo, dealSaledParam)
        [dealSaledThread.putRequest(req) for req in request_dealSaled]
        
        saveSaleParam = [(('saleinfo',queue_save_saleInfo),{}) for i in range(1, num+1)]
        requests_saveSale = makeRequests(WriteFile, saveSaleParam)
        [saveSaleThread.putRequest(req) for req in requests_saveSale]
        
        saveSaledParam = [(('saledinfo',queue_save_saledInfo),{}) for i in range(1, num+1)]
        requests_saveSaled = makeRequests(WriteFile, saveSaledParam)
        [saveSaledThread.putRequest(req) for req in requests_saveSaled]

        dealSaleThread.wait()
        dealSaledThread.wait()
        saveSaleThread.wait()
        saveSaledThread.wait()
        while not queue_save_saledInfo.empty():
            WriteFile('saledinfo', queue_save_saledInfo)
        

    if True:
        #num = 5
        for i in range(1,num):
            DealWithSaleInfo(header, i, queue_save_saleInfo, queue)
        print queue.qsize()
        for i in range(1,num):
            DealWithSaledInfo(header, queue_save_saledInfo, queue)
        print queue_save_saledInfo.qsize()    
        if not queue_save_saledInfo.empty():
            WriteFile('saledinfo', queue_save_saledInfo)
        
    
    
    
    
    

