#-*-coding:utf-8
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import hmac
import hashlib
import binascii
import time
import json
import re
import urllib.request
from urllib.parse import urlencode
import mysql_ask_db

import make_post
import socket
import ask_util


db_info = os.getenv('DB_INFO')
db_arr  = db_info.split("|")
host	=db_arr[0]
user	=db_arr[1]
pw 		=db_arr[2]
db 		=db_arr[3]

cup_key = os.getenv('CUP_KEY') #ask
cup_arr  = cup_key.split("|")

#1001   여성패션 #1002  남성패션 #1003  베이비패션 (0~3세) #1004  여아패션 (3세 이상) #1005  남아패션 (3세 이상) #1006  스포츠패션 #1007  신발 #1008  가방/잡화 #1010  뷰티 #1011  출산/유아동 #1012  식품 #1013  주방용품 #1014  생활용품 #1015  홈인테리어 #1016  가전디지털 #1017  스포츠/레저 #1018  자동차용품 #1019  도서/음반/DVD #1020  완구/취미 #1021  문구/오피스 #1024  헬스/건강식품 #1025  국내여행 #1026  해외여행 #1029  반려동물용품
BEST_CATEGORY_LIST  =['1001','1002','1003','1004','1005','1006','1007','1008','1010','1011','1012','1013','1014','1015','1016','1017','1018','1019','1020','1021','1024','1029']
#BEST_CATEGORY_LIST  =[]

class bestCuppang:
	def __init__(self):
		self.access_key			=	cup_arr[0]
		self.secret_key			=	cup_arr[1]
		self.domain				=	'https://api-gateway.coupang.com'	
		self.url				=	'/v2/providers/affiliate_open_api/apis/openapi'	
		self.channel_id  		=	"ahnPublicAsk"
		self.limit 				= 	"100"		
		self.item 				=""
		self.category_cd 		=""		
		self.product_id			=""		
		self.category_nm		=""
		self.rank_no			=""
		self.product_nm			=""
		self.product_price 		=""
		self.product_img_url	=""
		self.product_url		=""
		

	def getUrl(self, url_info):			
		return self.url + url_info 

	def dictFind(self, str, dictParam):
		return str in dictParam

	def sTrim(self, s):
		pat = re.compile(r'\s+') 	
		return pat.sub('',s)

	def generateHmac(self,method, url):	
	    path, *query = url.split("?")	    
	    os.environ["TZ"] = "GMT+0"
	    datetime = time.strftime('%y%m%d')+'T'+time.strftime('%H%M%S')+'Z'
	    print("datetime : ",datetime)
	    message = datetime + method + path + (query[0] if query else "")

	    signature = hmac.new(bytes(self.secret_key, "utf-8"),
	                         message.encode("utf-8"),
	                         hashlib.sha256).hexdigest()

	    return "CEA algorithm=HmacSHA256, access-key={}, signed-date={}, signature={}".format(self.access_key, datetime, signature)
###########################################################################################################################
###########################################################################################################################
############################################################################################################################


	def isCodeCheck(self,json_result):		
		rCode = json_result['rCode']
		print("rCode .... ",rCode)	
		if rCode == '0':		
			return True
		elif rCode == '429':		
			print("rCode 429 : ",json_result['rMessage'])
			return False
		else:				
			return False

	def isShortUrlCodeCheck(self, json_result):
		#print(json_result)
		try:
			if self.dictFind('rCode',json_result):
				rCode = json_result['rCode']
				if rCode == '0':
					if len(json_result['data'][0]['shortenUrl']) > 0:
						return True
					else: 
						return False				
				elif rCode == '429':		
					print("rCode 429 : ",json_result['rMessage'])
					return False
				elif rCode == '400':
					print("rCode 400  : ",json_result['rMessage'])
					return False
				else:				
					return False
			else:			
				return False		
		except Exception as e:
			print(json_result['code'])			
			print(e)
			raise e



	def initBestRank(self):		
		ad.delete(""" DELETE FROM TB_CUPPANG_BEST_RANK WHERE CATEGORY_CD = '%s' """ % (self.category_cd) )

	def getProduct(self):
		sqlId = """ SELECT RANK_NO, PRODUCT_PRICE, PRODUCT_NM, PRODUCT_IMG_URL, PRODUCT_URL  FROM TB_CUPPANG_BEST_PRODUCT WHERE PRODUCT_ID = '%s' AND CATEGORY_CD = '%s' """ % (self.product_id	, self.category_cd)
		#print(sqlId)
		return ad.selectOne(sqlId)

	def searchInsert(self, category_cd): 
		#print("searchInsert start")
		self.category_cd = category_cd
		tp_url = "/products/bestcategories/"+str(self.category_cd)+"?"
		print(tp_url)
		itemUrl =  self.getUrl(tp_url)			
		data = "limit="+self.limit+"&subId="+self.channel_id
		itemUrl = "{}{}".format(itemUrl, data)
		header = self.generateHmac('GET',itemUrl)
		url = "{}{}".format(self.domain, itemUrl)
		print("header : ",header)
		print("url : ",url)
		

		#print(url)
		request = urllib.request.Request(url)
		request.add_header("Authorization", header)
		response = urllib.request.urlopen(request)    
		rescode = response.getcode()
		#print("searchItem end")
		if(rescode==200):
		    response_body = response.read()
		    search_result = json.loads(response_body.decode('utf-8'))
		    if self.isCodeCheck(search_result):
		    	print("del bestRank s")
		    	self.initBestRank()
		    	print("del bestRank e")
		    	return self.insertProduct(search_result)
		    else:
		    	return False
		else:
			return False
		    	
	def insertProduct(self, search_result):
		#cnt =0
		#print(len(search_result['data']))
		isResult = False
		for item in search_result['data']:
			#cnt+=1
			#print(cnt)
			isChange = False
			isInsert = False
			self.product_id			= item['productId']
			self.category_nm		= item['categoryName']
			self.rank_no			= item['rank']
			self.product_nm			= ask_util.getSqlReplace(item['productName'])
			self.product_price 		= item['productPrice']
			self.product_img_url	= item['productImage']
			self.product_url		= item['productUrl']			
			product = self.getProduct()
			
			if product:
				isChange = self.isProductChange(product)
			else:	
				isInsert = True
			rank_sql ="""INSERT INTO ask_db.TB_CUPPANG_BEST_RANK(PRODUCT_ID, CATEGORY_CD, RANK_NO) VALUES('%s', '%s', %s) """ % (self.product_id, self.category_cd, self.rank_no ) 
			print(rank_sql)
			ad.insert(rank_sql)

			print("상품등록 체크:","|",isInsert, isChange)
			if isInsert or isChange:
				print("rank : ",str(self.rank_no))
				print("insert or change")				
				best_sql = """ INSERT INTO TB_CUPPANG_BEST_PRODUCT(PRODUCT_ID, CATEGORY_CD, CATEGORY_NM,  RANK_NO, PRODUCT_NM, PRODUCT_PRICE , PRODUCT_IMG_URL, PRODUCT_URL)
				VALUES('%s','%s','%s','%s','%s','%s','%s','%s')					
				"""  % (self.product_id, self.category_cd, self.category_nm, self.rank_no, self.product_nm, self.product_price, self.product_img_url,self.product_url)
				best_sql += """ ON DUPLICATE KEY UPDATE PRODUCT_NM = '%s',RANK_NO = '%s', PRODUCT_PRICE = '%s',PRODUCT_IMG_URL = '%s',PRODUCT_URL = '%s'
				""" % (self.product_nm, self.rank_no, self.product_price, self.product_img_url,self.product_url)
				best_sql += """ , UPDATE_DT = NOW() """
				#print(best_sql)
				ad.insert(best_sql)
				isResult = True
		return isResult	



	#등록된 상품 확인
	def isProductChange(self, product):	
		result = False
		db_rank_no  	= product[0]
		db_price 		= product[1]
		db_product_nm 	= product[2]

		item_rank 		= self.rank_no
		item_price 		= self.product_price
		item_product_nm = self.product_nm

		rank_up=rank_down=price_up=price_down = 'N'
		#print("랭크 체크 : ","|", db_rank_no ,"|", item_rank ,"|", db_price ,"|", item_price)
		if db_rank_no != item_rank or db_price != item_price:
			if db_rank_no != item_rank and item_rank < db_rank_no :
				rank_up = 'Y'
			elif db_rank_no != item_rank and item_rank > db_rank_no :
				rank_down = 'Y'
			else:
				rank_down ='N'


			if db_price != item_price and item_price < db_price :
				price_down = 'Y'
			elif db_price != item_price and item_price > db_price :
				price_up = 'Y'
			else:
				price_up ='N'

			if rank_up=='Y' or rank_down=='Y' or price_down=='Y' or price_up=='Y':
				change_sql = """
							INSERT INTO TB_CUPPANG_BEST_CHANGE(PRODUCT_ID, CATEGORY_CD, PRE_RANK_NO, NOW_RANK_NO, RANK_UP ,RANK_DOWN ,PRE_PRICE, NOW_PRICE, PRICE_UP ,PRICE_DOWN ) 
							VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
							ON DUPLICATE KEY UPDATE PRE_RANK_NO = '%s',NOW_RANK_NO = '%s',RANK_UP  = '%s',RANK_DOWN  = '%s',PRE_PRICE = '%s',NOW_PRICE = '%s',PRICE_UP  = '%s',PRICE_DOWN = '%s'
						  """  % (self.product_id, self.category_cd, db_rank_no, item_rank, rank_up, rank_down, db_price, item_price, price_up, price_down,     db_rank_no, item_rank, rank_up, rank_down, db_price, item_price, price_up, price_down)
				#print(change_sql)
				ad.insert(change_sql)

				changeHis_sql = """
								INSERT INTO TB_CUPPANG_BEST_CHANGE_HIS(RANK_YMDH, PRODUCT_ID, CATEGORY_CD, PRE_RANK_NO, NOW_RANK_NO, RANK_UP ,RANK_DOWN ,PRE_PRICE, NOW_PRICE, PRICE_UP ,PRICE_DOWN ) 
								VALUES (DATE_FORMAT(NOW(),"%Y%m%d%H")
								""" 
				changeHis_sql +="""
								,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
							  """  % (self.product_id, self.category_cd, db_rank_no, item_rank, rank_up, rank_down, db_price, item_price, price_up, price_down)
				changeHis_sql +="""
								ON DUPLICATE KEY UPDATE  PRE_RANK_NO = '%s',NOW_RANK_NO = '%s',RANK_UP  = '%s',RANK_DOWN  = '%s',PRE_PRICE = '%s',NOW_PRICE = '%s',PRICE_UP  = '%s',PRICE_DOWN = '%s'						
							  """  % (db_rank_no, item_rank, rank_up, rank_down, db_price, item_price, price_up, price_down)
				#print(change_sql)
				#print(changeHis_sql)
				ad.insert(changeHis_sql)
				return True
		else:
			return False		



def getWriteCount():
	# COUNT(*)
	rtn = ad.selectOne(f'''SELECT CATEGORY_CD  FROM ask_db.TB_CUPPANG_CATEGORY WHERE WRITE_YN = 'N' LIMIT 1 ''')
	if rtn == None :		
		initTable()
		return getWriteCount()
	else:
		category_cd = rtn[0]
		writeUpdate(category_cd)
		return rtn[0]
			
def initTable():
	ad.update (f''' UPDATE ask_db.TB_CUPPANG_CATEGORY SET WRITE_YN = 'N' ''')

def writeUpdate(category_cd):
	ad.update (f''' UPDATE ask_db.TB_CUPPANG_CATEGORY SET WRITE_YN = 'Y' WHERE CATEGORY_CD = '{category_cd}' ''')


if __name__ == '__main__':
	
	best = bestCuppang()
	isOk = True
	ad = mysql_ask_db.AskDb(host,user,pw,db)
	try:
		BEST_CATEGORY_LIST = []
		BEST_CATEGORY_LIST = [getWriteCount()]				
		for category_cd in BEST_CATEGORY_LIST:
			#print("category_cd ... S %s",(category_cd))
			isOk = best.searchInsert(category_cd)		
			print("isOk ",isOk)
			# quit()
			if isOk:
				m = make_post.MakeSite("https://sangkuahn.github.io",category_cd,ad)
				m.createPost()	
				m.createIndexPage()	
				# if category_cd == '1001':
				print("category_cd : ",category_cd)
				m.mainPage()
				m.makePowerLink()
				#quit()		
				
			else:				
				print("getCupBestItme not change or insert")
			#quit()			
			ad.closeConn()			
			#print("closeConn")
			print("category_cd ... E  timesleep 60*7 ", category_cd)
			# time.sleep(60*7)
			

	except Exception as e:
		print("__MAIN__  EXCEPT SLEEP .... ",e)
		#time.sleep(60*60)
		raise e
	# os.system(r'/usr/local/share/sangkuAhn.github.io/start_auto_push.sh')	
