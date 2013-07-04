#!/usr/bin/env python
# -*-coding:utf-8-*-
import re, urllib2, datetime, json, urllib
from flask import Flask
app = Flask(__name__)

yahoo = 'http://tw.stock.yahoo.com/q/q?s={0}'
counter = {
    5483:u'中美晶',
    6182:u'合晶',
    3579:u'尚志',
    3519:u'綠能',
    4944:u'兆遠'
}
offer = {} # for 法人
yuanurl = "http://justdata.yuanta.com.tw/z/zc/zcl/zcl_{0}.asp.htm"
def get_yuanta(key):
  response = urllib2.urlopen(yuanurl.format(key))
  html = response.read()
  html5 = html.decode('cp950')
  pat = u't3n0.*\n(.*)\n(.*)\n(.*)\n'
  regex = re.compile(pat, re.U)
  match = regex.search(html5)
  # line 1: 外資
  outside = re.search(u">([-\d.]+)<", match.group(1)).group(1)
  # line 2: 投信
  pitch = re.search(u">([-\d.]+)<", match.group(2)).group(1)
  # line 2: 投信
  self = re.search(u">([-\d.]+)<", match.group(3)).group(1)
  offer[key] = {}
  offer[key]['outside'] = u'{0}'.format(int(outside))
  offer[key]['pitch'] = u'{0}'.format(int(pitch))
  offer[key]['self'] = u'{0}'.format(int(self))
  offer[key]['all'] = u'{0}'.format(int(outside)+int(pitch)+int(self))
  offer[key]['key'] = u'{0}'.format(key)

#otc_url = 'http://www.otc.org.tw/php/result.php?url=http://www.otc.org.tw/ch/stock/3insti/DAILY_TradE/BIGD_{0}S_Q.html'
otc_url = 'http://www.otc.org.tw/ch/stock/3insti/DAILY_TradE/BIGD_{0}S_Q.html'
csv_url = 'http://www.otc.org.tw/ch/stock/3insti/DAILY_TradE/BIGD_{0}S_Q.CSV'

@app.route('/legal_test')
def get_legalman():
  html = ''
  b = datetime.datetime.now() + datetime.timedelta(hours=8) + \
      datetime.timedelta(days=1)
  while True:
    b = b - datetime.timedelta(days=1)
    c = '{0:03}{1:02}{2:02}'.format(b.year-1911,b.month,b.day)
    url = csv_url.format(c)
    try:
      response = urllib2.urlopen(url)
      html = response.read()
      break
    except: pass
  return html.decode('cp950')

def get_legal_buy_sell(html):
  # 3579, 3519: must get from yuanta
  get_yuanta(3579)
  get_yuanta(3519)
  for key in counter.keys():
    k = u'{0}   '.format(key)
    idx = html.find(k)
    if idx == -1: continue
    end = html[idx:].find('\n')
    line = html[idx:idx + end]
    finds = line.split('","')
    finds = [i.strip() for i in finds]
    offer[key] = {}
    offer[key]['all'] = u'{0}'.format(int(int(finds[11][:-1].replace(',','')) / 1000))
    # 外資
    offer[key]['outside'] = u'{0}'.format(int(int(finds[4].replace(',','')) / 1000))
    # 投信
    offer[key]['pitch'] = u'{0}'.format(int(int(finds[7].replace(',','')) / 1000))
    # 自營商
    offer[key]['self'] = u'{0}'.format(int(int(finds[10].replace(',','')) / 1000))
    offer[key]['key'] = u'{0}'.format(key)

emerging = {
  5221: u'合晶光電',
  4990: u'晶美應材',
  4969: u'鑫晶鑽',
  5217: u'旭泓'
}
emer_result = {}
emerging_url = "http://www.gretai.org.tw/storage/emgstk/emgstk.txt"
  # {"14":"5226","11":42000,"2":16.11,"10":16.2,"7":16.4,"8":16}
  # "14": ID
  # "11": value / 1000 = excel 張數, count
  # "2" : 前日均價，來算漲跌
  # "7" : 最高, max
  # "10" : 成交價, deal
  # "8": 最低, min
def get_emerging():
  response = urllib2.urlopen(emerging_url)
  html = response.read()
  a = json.loads(html)
  dat = a['aaData']
  for key in emerging:
    k = u'{0}'.format(key)
    line = [ dat[i] for i in xrange(len(dat)) if dat[i][u'14'] == k]
    if line:
      line = line[0]
      emer_result[key] = {}
      emer_result[key]['name'] = emerging[key]
      emer_result[key]['id'] = key
      emer_result[key]['max_price'] = (u'{0}'.format(line[u'7'])).encode('utf-8')
      emer_result[key]['min_price'] = (u'{0}'.format(line[u'8'])).encode('utf-8')
      emer_result[key]['deal']  = (u'{0}'.format(line[u'10'])).encode('utf-8')
      emer_result[key]['count'] = (u'{0}'.format(line[u'11'] / 1000)).encode('utf-8')
      # can't find data in URL?
      emer_result[key]['direction'] = u'N/A'.encode('utf-8')
      emer_result[key]['updown'] = u'N/A'.encode('utf-8')
      emer_result[key]['legal'] = u'N/A'.encode('utf-8')

stockurl = 'http://tw.stock.yahoo.com/q/q?s={0}'
# yahoo caption: 成交、張數、漲跌、最高、最低
# excel caption: 成交價、張數、漲跌幅、最高點、最低點
stock = {}
def get_stock():
  for key in counter.keys():
    response = urllib2.urlopen(stockurl.format(key))
    html = response.read()
    html5 = html.decode('cp950')
    pat = u'stocklist=' + u'{0}'.format(key) + u'.*\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n(.*)\n'
    regex = re.compile(pat, re.U)
    match = regex.search(html5)
    # line 2: 成交
    deal = re.search(u">([\d.]+)<", match.group(2)).group(1)
    # line 5: 漲跌
    updown = re.search(u"([\d.]+)$", match.group(5)).group(1)
    #direction = re.search(u'\u25bd',match.group(5)) and u"down" or u"up"
    direction = re.search(u'\u25bd',match.group(5)) and u"-" or u""
    # line 6: 張數
    count = re.search(u">([\d,]+)<", match.group(6)).group(1)
    # line 9: 最高
    max_price = re.search(u">([\d.]+)<", match.group(9)).group(1)
    # line 10: 最低
    min_price = re.search(u">([\d.]+)<", match.group(10)).group(1)
    stock[key] = {}
    stock[key]['name'] = counter[key]
    stock[key]['id'] = key
    stock[key]['deal'] = deal.encode('utf-8')
    stock[key]['updown'] = updown.encode('utf-8')
    stock[key]['direction'] = direction.encode('utf-8')
    stock[key]['count'] = count.encode('utf-8')
    stock[key]['max_price'] = max_price.encode('utf-8')
    stock[key]['min_price'] = min_price.encode('utf-8')
    stock[key]['legal'] = u'0'

def get_all():
  response = urllib2.urlopen('http://tw.stock.yahoo.com')
  html = response.read()
  html5 = html.decode('cp950')
  regex = re.compile(u'tse_quote[^v]*', re.U)
  match = regex.search(html5, re.MULTILINE)
  line = html5[match.start():match.end()]
  regex = re.compile(u'"dx">([^<]*)<', re.U)
  match = regex.search(line)
  total = match.group(1)
  line = line[match.end():]
  regex = re.compile(u'>([\d.]+)<(.*?)$', re.U)
  match = regex.search(line)
  delta = match.group(1)
  if re.search("down",line):
    direction = "down"
  else:
    direction = "up"
  return dict(total=total.encode('utf-8'),delta=delta.encode('utf-8'),direction=direction.encode('utf-8'))

sunpower_url = 'http://investors.sunpowercorp.com'
def get_sunpower():
  regex = re.compile(u'">([^<]+)', re.U)
  response = urllib2.urlopen(sunpower_url)
  html = response.read()
  a, b = html.split('Price')
  a, b = b.split('Change')
  price = regex.search(a).group(1).encode('utf-8')
  a, b = b.split('Day High')
  delta = regex.search(a).group(1)
  if re.search('\+', delta):
    is_neg = False
  else:
    is_neg = True
  delta = re.split('[\+\- ]',delta)[-1]
  delta = delta.encode('utf-8')
  a = b.split('Volume')[1].split('clear')[0]
  vol = regex.search(a).group(1).replace(',','').encode('utf-8')
  return dict(who='Sunpower',vol=vol,delta=delta,is_neg=is_neg,price=price)

okmetic_url = 'http://ir2.flife.de/data/okmetic/download_e.php?action=download'
# post to okmetic_url
# content: ir_format=html&aday=2&amonth=5&ayear=2005&eday=2&emonth=7&eyear=2013
def get_okmetic():
  html = urllib2.urlopen(okmetic_url).read()
  lines = html.split('\n')
  args = {'ir_format':'html'}
  a = [i.strip() for i in lines if re.search(u'selected',i) or re.search(u'select.*name',i)]
  curkey = ''; curval = ''
  for i in a:
    if i.find('name=') != -1:
      curkey = re.search('name="([^"]+)"', i).group(1)
    else:
      curval = re.search('value="([^"]+)"', i).group(1)
      args[curkey] = curval
  n = datetime.datetime.now()
  need_keys = ['aday','amonth','ayear','eday','emonth','eyear']
  [args.setdefault(i,getattr(n, re.sub('^[ae]','',i))) for i in need_keys if not i in args]
  data = urllib.urlencode(args) # returns like abc=123&def=456&cde=789
  req = urllib2.Request(okmetic_url, data)
  response = urllib2.urlopen(req)
  html = response.read()
  res = html.split('Turnover')[1].split('tr')[2].replace('\t\t\t','')
  res = res.split('td>\n')
  price = re.search('">([^<]+)',res[1]).group(1)
  vol = re.search('">([^<]+)',res[-3]).group(1).replace(',','')
  return dict(who='OKMETIC',vol=vol,price=price, delta=u"0", is_neg=False)

memcpower_url = 'http://phx.corporate-ir.net/phoenix.zhtml?c=106680&p=irol-stockQuote'
def get_memc():
  response = urllib2.urlopen(memcpower_url)
  html = response.read()
  price = re.search(u'ccbnPrice">\$([^<]+)',html).group(1).encode('utf-8')
  a, b = html.split('(%)')
  a = b.split('ccbn')[1]
  if re.search('Neg', a):
    is_neg = True
  else:
    is_neg = False
  delta = re.search(u'">([^<]+)', a).group(1).encode('utf-8')
  a = b.split('Volume')[1].split('ccbn')[1]
  vol = re.search(u'">([^<]+)<', a).group(1).replace(',','').encode('utf-8')
  return dict(who='MEMC', price=price, delta=delta, vol=vol, is_neg=is_neg)


twse_html = u'\n\
<h6>大盤: {0[direction]} {0[delta]}</h6>\n\
<h6>加權指數: {0[total]}</h6>'

result = u'<!doctype html><head>\n\
<title>stock price</title>\n\
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n\
</head>\n\
<body>\n\
<div class="page">\n\
<div id="status">waiting to load</div>\n\
<div id="twse_html"></div>\n\
<div id="stock"></div> \n\
<div id="emer"></div> \n\
<div id="foreign"></div> \n\
</div>'

scr= u'\n\
<script>\n\
var done = 0; \n\
var xhr1 = new XMLHttpRequest(); \n\
var xhr2 = new XMLHttpRequest(); \n\
reuse_xhr = function() { \n\
  xhr2.open(\'GET\', \'/legal_data\'); \n\
  xhr2.onreadystatechange = function () { \n\
    if (xhr2.readyState == 4 && xhr2.status == 200) { \n\
      var newelem = document.createElement(\'div\'); \n\
      newelem.innerHTML = xhr2.responseText; \n\
      var tables = newelem.querySelectorAll(\'table\');\n\
      for (var i = 0; i < tables.length; ++i) { \n\
        var id = tables[i].getAttribute(\'who\'); \n\
        var all_sell = tables[i].getAttribute(\'all\'); \n\
        var selector = "h6[who=\'" + id + "\']"; \n\
        var curelem = document.querySelector(selector);\n\
        var nexttable = curelem.nextSibling.nextSibling; \n\
        var allelem = nexttable.querySelector(\'tr:last-child td\'); \n\
        allelem.textContent = all_sell; \n\
        nexttable.parentNode.insertBefore(tables[i],nexttable.nextSibling); \n\
      } \n\
      done += 1; \n\
    } \n\
  }; \n\
  xhr2.send(null);\n\
}; \n\
xhr1.open(\'GET\', \'/twse\'); \n\
xhr1.onreadystatechange = function () { \n\
  if (xhr1.readyState == 4 && xhr1.status == 200) { \n\
    var twse_elem = document.querySelector(\'#twse_html\'); \n\
    twse_elem.innerHTML = xhr1.responseText; \n\
    done += 1; \n\
  } \n\
}; \n\
xhr1.send(null); \n\
xhr2.open(\'GET\', \'/stock_data\'); \n\
xhr2.onreadystatechange = function () { \n\
  if (xhr2.readyState == 4 && xhr2.status == 200) { \n\
    var stock_elem = document.querySelector(\'#stock\'); \n\
    stock_elem.innerHTML = xhr2.responseText; \n\
    done += 1; \n\
    reuse_xhr(); \n\
  } \n\
}; \n\
xhr2.send(null); \n\
var xhr3 = new XMLHttpRequest(); \n\
xhr3.open(\'GET\', \'/emer_data\'); \n\
xhr3.onreadystatechange = function () { \n\
  if (xhr3.readyState == 4 && xhr3.status == 200) { \n\
    var emer_elem = document.querySelector(\'#emer\'); \n\
    emer_elem.innerHTML = xhr3.responseText; \n\
    done += 1; \n\
  } \n\
}; \n\
xhr3.send(null); \n\
var xhr4 = new XMLHttpRequest(); \n\
xhr4.open(\'GET\', \'/foreign\'); \n\
xhr4.onreadystatechange = function () { \n\
  if (xhr4.readyState == 4 && xhr4.status == 200) { \n\
    var foreign_elem = document.querySelector(\'#foreign\'); \n\
    foreign_elem.innerHTML = xhr4.responseText; \n\
    done += 1; \n\
  } \n\
}; \n\
xhr4.send(null); \n\
reload_color = function(){\n\
  var a = document.querySelector(\'#status\'); \n\
  a.innerHTML = \'<strong><i>Updating Done</i></strong>\'; \n\
  var ps = document.getElementsByClassName("deltaprice");\n\
  for (var i = 0; i < ps.length; ++i) {\n\
    if (ps[i].textContent[0] == "-" || ps[i].getAttribute("is_neg") == "True") {\n\
      ps[i].style.color = "#ff0000";\n\
    }\n\
  }\n\
};\n\
check = function() {\n\
  if (done == 5) { \n\
    reload_color(); \n\
  } else { \n\
    setTimeout(check, 1000); \n\
  } \n\
} \n\
setTimeout(check, 1000); \n\
</script>\n\
</body></html>'

order = [5483, 6182, 3579, 3519, 5221, 4990, 4969, 4944, 5217]
entry = u'\n\
<h6 who="{0[id]}">{0[name]}，代號: {0[id]}</h6>\n\
<table border="1">\n\
<tr><th>成交價</th><td>{0[deal]}</td></tr>\n\
<tr><th>張數</th><td>{0[count]}</td></tr>\n\
<tr><th>漲跌幅</th><td class="deltaprice">{0[direction]} {0[updown]}</td></tr>\n\
<tr><th>最高點</th><td>{0[max_price]}</td></tr>\n\
<tr><th>最低點</th><td>{0[min_price]}</td></tr>\n\
<tr><th>法人買賣超</th><td class="deltaprice">{0[legal]}</td></tr>\n\
</table><table></table>\n'

legal_result = u'\n\
<table border="1" who="{0[key]}" all="{0[all]}">\n\
<tr><th>外資&陸資淨買股數</th><th>投信淨買股數</th><th>自營淨買股數</th></tr>\n\
<tr><td class="deltaprice">{0[outside]}</td><td class="deltaprice">{0[pitch]}</td><td class="deltaprice">{0[self]}</td></tr>\n\
</table>\n'

foreign_entry = u'\n\
<h6>{0[who]}</h6>\n\
<table border="1">\n\
<tr><th>成交價</th><td>{0[price]}</td></tr>\n\
<tr><th>張數</th><td>{0[vol]}</td></tr>\n\
<tr><th>漲跌幅</th>\n\
<td class="deltaprice" is_neg="{0[is_neg]}">{0[delta]}</td></tr>\n\
</table>\n'


@app.route('/foreign')
def get_foreign():
  okmetic = get_okmetic()
  memc = get_memc()
  sunpower = get_sunpower()
  return foreign_entry.format(okmetic) + \
      foreign_entry.format(memc) + \
      foreign_entry.format(sunpower)

@app.route('/twse')
def get_twse_html():
  twse = get_all()
  return twse_html.format(twse)

@app.route('/legal_data')
def get_legal_html():
  # not all counter stocks has legal buy/sell
  get_legal_buy_sell(get_legalman())
  entries = ""
  for key in offer.keys():
    entries += legal_result.format(offer[key])
  return entries

@app.route('/emer_data')
def get_emer_html():
  get_emerging()
  entries = ""
  for key in order:
    if key in emer_result.keys():
      entries += entry.format(emer_result[key])
  return entries

@app.route('/stock_data')
def get_stock_html():
  get_stock()
  entries = ""
  for key in order:
    if key in stock.keys():
      entries += entry.format(stock[key])
  return entries

@app.route('/')
def index():
  return result + scr
  #return render_template('stockprice.html')

if __name__ == '__main__':
  #app.run(debug=True)
  app.run()
