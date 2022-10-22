#-*-coding:utf-8
import os
import random
import re
from time import localtime, strftime
import time
from datetime import datetime
import ask_util

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET_DIR = "/static_site_repo"

BEST_CATEGORY_LIST  =["1001","1002","1003","1004","1005","1006","1007","1008","1010","1011","1012","1013","1014","1015","1016","1017","1018","1019","1020","1021","1024","1029"]
CATEGORY_NM = {"1001":"여성패션","1010":"뷰티","1015":"홈인테리어","1016":"가전디지털","1014":"생활용품","1002":"남성패션","1003":"베이비패션","1004":"여아패션","1005":"남아패션","1006":"스포츠패션","1007":"신발","1008":"패션잡화","1011":"유아동","1012":"식품","1013":"주방용품","1017":"레저","1018":"자동차용품","1019":"도서/음반/DVD","1020":"완구/취미","1021":"문구/오피스","1024":"식품","1029":"반려동물"}

class MakeSite:
	def __init__(self, baseUrl,category, ad):
		self.ad 			= ad
		self.color_list 	= ['F15F5F','BD24A9','A566FF','5A8DF3','CF36BB','A6A6A6','F361A6','35B62C','A57F92','D9418C','A566FF','4374D9','353535','FF6F00','FF1744','f44336','03A9F4','4CAF50','BF360C','9E9D24','4A148C','006064','7E57C2','43A047','1294AB']	
		self.color 			= ""	
		self.product_id 	= ""
		self.title_nm 		= ""		
		self.img_url 		= ""
		self.linkUrl 		= ""
		self.category 		= category
		self.rank_no 		= ""
		self.pre_rank_no 	= ""
		self.rank_up 		= ""
		self.rank_down 		= ""
		self.price 			= ""
		self.pre_price 		= ""
		self.price_up 		= ""
		self.price_down 	= ""
		self.toDay 			= ""
		self.baseUrl 		= baseUrl
		self.author 		= "Ask View Shop"
		self.postText 		= ""
		self.bestPage 		= ""
		self.indexPage 		= ""
		self.post_nm 		= ""
		self.page_nm 		= "main"
		self.descript 		= ""
		self.change_rank 	= None
		self.change_price 	= None
		self.regist_dt 		= ""
		self.dateCal 		= None 
		self.hour_24 		= 24
		self.powerLinkPage	= ""
		self.productList	= self.getBestList()		
		self.rankStock 		=""
		self.moneyStock 	=""
		
		self.mainIndexPage 	= ""

####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################
# calss Init
	def makePowerLink(self):
		resultLink = self.ad.selectAll("""SELECT USER_ID, POST_NO, KEYWORD_NM FROM ask_db.TB_BLOG_BACK_LINK ORDER BY rand() DESC LIMIT 5""" )
		page =""" <hr>
				  <p><h2>[파워링크]</h2></p>
					<div id="post_list" style="margin: 5px 5px 5px 5px;;text-align: left;"><span>"""
		if resultLink:
			for r in resultLink:
				page +="""<a href="%s" target="_blank">%s</a><br>""" % (r[1],r[2] )
		page +="""</span></div>"""	
		#print(page)
		self.powerLinkPage =  page
		self.writeFile('powerLink')
		

	def getBestList(self):
		return self.ad.selectAll("""
								SELECT A.PRODUCT_ID,
									 B.PRODUCT_NM, 		B.PRODUCT_IMG_URL,			B.PRODUCT_URL, 				B.CATEGORY_CD,
									 A.RANK_NO, 		IFNULL(C.PRE_RANK_NO,0), 	IFNULL(C.RANK_UP,'N'), 		IFNULL(C.RANK_DOWN,'N'),
									 B.PRODUCT_PRICE, 	IFNULL(C.PRE_PRICE,0), 		IFNULL(C.PRICE_UP,'N'), 	IFNULL(C.PRICE_DOWN,'N'),
									 B.UPDATE_DT,		B.REGIST_DT, ROUND(TIMESTAMPDIFF(MINUTE,B.REGIST_DT,NOW())/60), NOW()
								FROM TB_CUPPANG_BEST_RANK A
								INNER JOIN TB_CUPPANG_BEST_PRODUCT B
								ON (A.PRODUCT_ID = B.PRODUCT_ID AND A.CATEGORY_CD = B.CATEGORY_CD AND B.CATEGORY_CD= '%s')
								LEFT OUTER JOIN TB_CUPPANG_BEST_CHANGE AS C 
								ON (A.PRODUCT_ID = C.PRODUCT_ID AND A.CATEGORY_CD = C.CATEGORY_CD )																						
								ORDER BY RANK_NO
								
								""" % (self.category))

	def getFile_path(self, div):
		path = ""
		if div == 'post':
			path =  f'''{BASE_DIR}{TARGET_DIR}/_posts/{self.post_nm}.markdown'''
		elif div =='page':
			path = f'''{BASE_DIR}{TARGET_DIR}/_pages/{self.page_nm}.md'''
		elif div == 'index':
			path = f'''{BASE_DIR}{TARGET_DIR}/index.html'''
		elif div =='page_index':
			path = f'''{BASE_DIR}{TARGET_DIR}/_pages/index_{self.category}.html'''
		elif div == 'powerLink':
			path = f'''{BASE_DIR}{TARGET_DIR}/_includes/power_link.html'''
		#print(path)
		return path

	def writeFile(self, div):
		#print(self.getFile_path(div))
		f = open(self.getFile_path(div) ,'w', encoding='utf8')		
		if div == 'post':
			f.write(self.postText)
		elif div =='page':
			f.write(self.bestPage)
		elif div =='index':
			# print("div : ",div, f)
			# print(self.mainIndexPage)
			f.write(self.mainIndexPage)
		elif div =='page_index':
			f.write(self.indexPage)
		elif div =='powerLink':
			f.write(self.powerLinkPage)

		f.close()

	def setProductInit(self, product):
		self.product_id 	= product[0]
		self.title_nm 		= re.sub("]", "/",product[1])
		self.title_nm 		= self.getReplace(self.title_nm)
		self.img_url 		= product[2]
		self.linkUrl 		= product[3]
		self.category 		= product[4]
		self.rank_no 		= product[5]
		self.pre_rank_no	= product[6]
		self.rank_up 		= product[7]
		self.rank_down 		= product[8]
		self.price 			= product[9]
		self.pre_price 		= product[10]
		self.price_up 		= product[11]
		self.price_down 	= product[12]	
		self.regist_dt 		= product[14]
		self.dateCal 		= product[15]
		self.toDay  		= product[16]			
		self.post_nm 		= strftime("%Y-%m-%d")+"-"+self.product_id			
		self.descript 		= self.changeRankPrice()
		self.color 			= self.color_list[random.randrange(0,len(self.color_list))-1]		
####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################
# INDEX
	def repl_under(self, str):
		return re.sub("_", "",str)


	def repl_excp(self, repl_text):
		if repl_text.find('_') > -1:		
			repl_text = self.repl_under(repl_text)

		if repl_text.find('°') > -1:
			rd_max_cnt = repl_text.count("°")
			repl_text = repl_text.replace("°","",rd_max_cnt)

		if repl_text.find(':') > -1:
			rd_max_cnt = repl_text.count(":")
			repl_text = repl_text.replace(":","",rd_max_cnt)
			
		if repl_text.find('=') > -1:
			rd_max_cnt = repl_text.count("=")
			repl_text = repl_text.replace("=","",rd_max_cnt)
		if repl_text.find('*') > -1:
			rd_max_cnt = repl_text.count("*")
			repl_text = repl_text.replace("*","",rd_max_cnt)
		if repl_text.find('─') > -1:
			rd_max_cnt = repl_text.count("─")
			repl_text = repl_text.replace("─","",rd_max_cnt)
		if repl_text.find('ㅡ') > -1:
			rd_max_cnt = repl_text.count("ㅡ")
			repl_text = repl_text.replace("ㅡ","",rd_max_cnt)
		if repl_text.find('\"') > -1:
			rd_max_cnt = repl_text.count("\"")
			repl_text = repl_text.replace("\"","",rd_max_cnt)
		if repl_text.find('※') > -1:
			rd_max_cnt = repl_text.count("※")
			repl_text = repl_text.replace("※","",rd_max_cnt)
		if repl_text.find('◑') > -1:
			rd_max_cnt = repl_text.count("◑")
			repl_text = repl_text.replace("◑","",rd_max_cnt)
		if repl_text.find('☜') > -1:
			rd_max_cnt = repl_text.count("☜")
			repl_text = repl_text.replace("☜","",rd_max_cnt)
		if repl_text.find('☆☆☆☆☆☆☆☆☆☆') > -1:
			rd_max_cnt = repl_text.count("☆☆☆☆☆☆☆☆☆☆")
			repl_text = repl_text.replace("☆☆☆☆☆","",rd_max_cnt)
		if repl_text.find('♡♡♡♡') > -1:
			rd_max_cnt = repl_text.count("♡♡♡♡")
			repl_text = repl_text.replace("♡","",rd_max_cnt)		
		if repl_text.find('☆☆☆☆☆☆☆☆☆') > -1:
			rd_max_cnt = repl_text.count("☆☆☆☆☆☆☆☆☆")
			repl_text = repl_text.replace("☆☆☆☆☆☆☆☆☆","☆☆☆☆☆",rd_max_cnt)
		if repl_text.find('☆☆☆☆☆☆☆☆') > -1:
			rd_max_cnt = repl_text.count("☆☆☆☆☆☆☆☆")
			repl_text = repl_text.replace("☆☆☆☆☆☆☆☆","☆☆☆☆☆",rd_max_cnt)
		if repl_text.find('~') > -1:
			rd_max_cnt = repl_text.count("~")
			repl_text = repl_text.replace("~","",rd_max_cnt)
		if repl_text.find('—') > -1:
			rd_max_cnt = repl_text.count("—")
			repl_text = repl_text.replace("—","",rd_max_cnt)
		if repl_text.find(',,,,,') > -1:
			rd_max_cnt = repl_text.count(",,,,,")
			repl_text = repl_text.replace(",,,,,",",",rd_max_cnt)
		if repl_text.find(' and gt;<br/>') > -1:
			rd_max_cnt = repl_text.count(" and gt;<br/>")
			repl_text = repl_text.replace(" and gt;<br/>",">",rd_max_cnt)
		if repl_text.find('and lt;') > -1:
			rd_max_cnt = repl_text.count("and lt;")
			repl_text = repl_text.replace("and lt;","<",rd_max_cnt)
		if repl_text.find('@@@@@') > -1:
			rd_max_cnt = repl_text.count("@@@@@")
			repl_text = repl_text.replace("@@@@@","@",rd_max_cnt)
		if repl_text.find('➖') > -1:
			rd_max_cnt = repl_text.count("➖")
			repl_text = repl_text.replace("➖","",rd_max_cnt)
		if repl_text.find('•') > -1:
			rd_max_cnt = repl_text.count("•")
			repl_text = repl_text.replace("•","",rd_max_cnt)
		if repl_text.find('   ') > -1:
			rd_max_cnt = repl_text.count("   ")
			repl_text = repl_text.replace("   "," ",rd_max_cnt)
		if repl_text.find(' -<br/> -<br/> -<br/> -<br/>') > -1:
			rd_max_cnt = repl_text.count(" -<br/> -<br/> -<br/> -<br/>")
			repl_text = repl_text.replace(" -<br/> -<br/> -<br/> -<br/>","",rd_max_cnt)
		if repl_text.find('.<br/>.<br/>.<br/>.<br/>') > -1:
			rd_max_cnt = repl_text.count(".<br/>.<br/>.<br/>.<br/>")
			repl_text = repl_text.replace(".<br/>.<br/>.<br/>.<br/>","",rd_max_cnt)
					
		return repl_text

	def mainPage(self):		
		self.mainIndexPage ="""---\n"""
		self.mainIndexPage +="""layout: default\n"""		
		self.mainIndexPage +="""---\n"""
		self.mainIndexPage +="""<div class="main_text">%s<br>Best Top 랭킹 진입한 신규상품입니다.</div>\n""" %(self.toDay)
		self.mainIndexPage +="""<div class="main_text">		
		<!-- askview_메인_상단 -->
		<ins class="adsbygoogle"
		     style="display:block"
		     data-ad-client="ca-pub-3309468445717403"
		     data-ad-slot="1034729628"
		     data-ad-format="auto"
		     data-full-width-responsive="true"></ins>
		<script>
		     (adsbygoogle = window.adsbygoogle || []).push({});
		</script>
		</div>\n"""
		self.mainIndexPage +="""<div id="container" style="text-align: left;">\n"""
		self.mainIndexPage +="""<div id="grid" data-columns class="cols">\n"""		
		for self.category in BEST_CATEGORY_LIST:			
			self.productList = self.getBestList()			
			for product in self.productList:
				self.setProductInit(product)
				if self.hour_24 > self.dateCal:
				#if self.rank_no <5:
					self.mainIndexPage += self.mainLoopPage()			
				

		self.mainIndexPage +="""</div>\n"""
		self.mainIndexPage +="""</div>\n"""
		self.mainIndexPage +="""<script src="%s/js/salvattore.min.js"></script>""" %(self.baseUrl)
		#print(self.mainIndexPage)
		self.writeFile('index')
		
	def mainLoopPage(self):
		page = """    <div class="box" style="background-color:#%s">\n 	""" %(self.color)
		page +="""  		<div class="idxBkImg">\n"""		
		page +="""    <div class="idxStyle"><b>%s<b>%s <span class="category"><a href="/rank_%s/"> %s <u>more</u></a></span></div>\n""" %(self.descript,self.rankStock, self.category, CATEGORY_NM[self.category] )
		if self.price_up =='Y' or self.price_down =='Y':			
			#print(self.price_up, "|" ,self.price_down, "|", self.product_id, "|", self.pre_price,"|",self.change_price)
			page +="""     <div class="idxMoneyStyle">%s원%s </div>\n 		""" %(self.price, self.moneyStock)	
		else:
			page +="""      <div class="idxMoneyStyle">%s원</div>\n 		""" %(self.price)	
		page +="""  		</div>\n"""		
		page +="""      	<a href="/%s" target="_blank">\n 				""" %(self.product_id)
		page +="""      		<img class="feat-image lazyload" data-src="%s" alt="%s" >\n """ %(self.img_url, ask_util.clearTitle(self.title_nm))
		page +="""      	</a>\n"""
		page +="""        	<div class="container">\n"""
		page +="""				<div>\n""";
		#page +="""      	      <a href="/rank_%s/"> %s TOP.100 <u>MORE</u></a>\n""" %(self.category, CATEGORY_NM[self.category])
		if self.hour_24 > self.dateCal:
			print("new ~!~!~!   ", self.dateCal)
			#page +=""" <img src="/images/new_img_%s.png" alt="new" width="30" height="30"> <h3>%s</h3>"""%(ask_util.getRandom(1,3), self.title_nm)
			page +="""   	<img  class="lazyload" data-src="/images/new_img_%s.png" alt="new" width="30" height="30"> <h3>%s</h3>\n"""%(2, self.title_nm)
		else:
			page +="""   	<p>%s</p>\n """ %(self.title_nm)		

		review_list = self.ad.selectAll(""" SELECT REVIEW_DESC FROM TB_CUPPANG_BEST_PRODUCT_DESC WHERE PRODUCT_ID = '%s'  LIMIT 15 """ %(self.product_id))
		#last_cnt = ask_util.getRandom(10,100)
		page +="""			</div>\n""";	
		review_cnt = 0
		if review_list:
			page+="""	    <div class="action">\n 			<p>"""
			for review in review_list:
				review_cnt+=1
				#print(len(review[0]))
				if len(review[0]) > 60:
					
					#print("self.product_id ",self.product_id,review[0][:60])
					page +="""%s ...\n""" % (ask_util.getSqlReplace(self.repl_excp(review[0][:60])))
				else:
					#print("self.product_id ",self.product_id,review[0])
					page +="""%s""" % (ask_util.getSqlReplace(self.repl_excp(review[0])))
				#print(review_cnt,last_cnt)
				if review_cnt > 10:
				 	#print(review)
				 	break

			page+="""\n 	   </p>\n"""
			page+="""		</div>\n"""
			
		page +="""  		<div class="action">\n 	""" 
		page +="""      		<a href="/%s" target="_blank">\n""" %(self.product_id)
		page +="""      	    	MORE<i class="fa fa-arrow-right" aria-hidden="true"></i>\n"""
		page +="""      	    </a>\n"""
		page +="""      	</div>\n"""
		page +="""  	</div>\n"""
		page +=""" 	  </div>\n"""
		#print(page)
		return page






	def createIndexPage(self):		
		#pageIndex 만들기
		self.indexPage 	= self.makeIndexStartPage()		
		for product in self.productList:			
			self.setProductInit(product)
			
			if self.rank_no > 100:
				break
			else:								
				self.indexPage 	+= self.makeIndexLoopPage()

		self.indexPage 	+= self.makeIndexEndPage()
		self.writeFile('page_index')

	def makeIndexStartPage(self):
		page ="""---\n"""
		page +="""layout: default\n"""	
		page +="""permalink: /rank_%s/\n""" % (self.category)
		page +="""---\n"""
		page +="""<div class="index_text">UpDate. AM:10시 | FM:6시 </div>\n""" 
		page +="""<div class="main_text">
		<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>		
		<!-- askview_메인_상단 -->
		<ins class="adsbygoogle"
		     style="display:block"
		     data-ad-client="ca-pub-3309468445717403"
		     data-ad-slot="1034729628"
		     data-ad-format="auto"
		     data-full-width-responsive="true"></ins>
		<script>
		     (adsbygoogle = window.adsbygoogle || []).push({});
		</script>
		</div>\n"""
		page +="""<div id="container" style="text-align: left;">\n"""
		page +="""<div id="grid" data-columns class="cols">\n"""
		return page


	def makeIndexEndPage(self):
		page ="""</div>\n"""
		page +="""</div>\n"""
		page +="""<script src="%s/js/salvattore.min.js"></script>""" %(self.baseUrl)
		return page

	def makeIndexLoopPage(self):
		#page +="""	<input type="hidden" value="%s">\n				""" %(self.title_nm)
		page ="""<div class="box" style="background-color:#%s">\n 	""" %(self.color)
		
		page +=""" <div class="idxBkImg">\n"""
		#rank view
		page +="""    <div class="idxStyle"><b>%s<b> %s </div>\n""" %(self.descript,self.rankStock )
		
		#money view
		if self.price_up =='Y' or self.price_down =='Y':			
			#print(self.price_up, "|" ,self.price_down, "|", self.product_id, "|", self.pre_price,"|",self.change_price)
			page +="""     <div class="idxMoneyStyle">%s원 %s </div>\n 		""" %(self.price, self.moneyStock)	
		else:
			page +="""      <div class="idxMoneyStyle">%s원</div>\n 		""" %(self.price)	
	
		page +="""  </div>\n"""
		page +="""  <a href="/%s" target="_blank">\n 				""" %(self.product_id)
		page +="""  	<img class="feat-image lazyload" data-src="%s" alt="%s" >\n """ %(self.img_url, ask_util.clearTitle(self.title_nm))
		page +="""  </a>\n"""
		page +="""  <div class="container">\n"""
		page +="""  <div>\n"""


		if self.hour_24 > self.dateCal:
			print("new ~!~!~!   ", self.dateCal)
			#page +=""" <img src="/images/new_img_%s.png" alt="new" width="30" height="30"> <h3>%s</h3>"""%(ask_util.getRandom(1,3), self.title_nm)
			page +=""" <img  class="lazyload" data-src="/images/new_img_%s.png" alt="new" width="30" height="30"> <h3>%s</h3>\n"""%(2, self.title_nm)
		else:
			page +=""" <p>%s</p>\n """ %(self.title_nm)
		# if self.change_rank:
		# 	page +="""      <p>%s</p>""" %(self.change_rank)

		page +="""  </div>\n"""
		review_list = self.ad.selectAll(""" SELECT REVIEW_DESC FROM TB_CUPPANG_BEST_PRODUCT_DESC WHERE PRODUCT_ID = '%s'  LIMIT 15 """ %(self.product_id))
		#last_cnt = ask_util.getRandom(10,100)
		
		review_cnt = 0
		if review_list:
			page+="""	    <div class="action">\n 			<p>"""
			for review in review_list:
				review_cnt+=1
				#print(len(review[0]))
				if len(review[0]) > 60:
					
					#print("self.product_id ",self.product_id,review[0][:60])
					page +="""%s ...\n""" % (ask_util.getSqlReplace(self.repl_excp(review[0][:60])))
				else:
					#print("self.product_id ",self.product_id,review[0])
					page +="""%s""" % (ask_util.getSqlReplace(self.repl_excp(review[0])))
				#print(review_cnt,last_cnt)
				if review_cnt > 10:
				 	#print(review)
				 	break

			page+="""\n 	   </p>\n"""
			page+="""		</div>\n"""

		page +="""  	<div class="action">\n 	"""
		page +="""      	<a href="/%s" target="_blank">\n""" %(self.product_id)
		page +="""      	    MORE<i class="fa fa-arrow-right" aria-hidden="true"></i>\n"""
		page +="""          </a>\n"""
		page +="""      </div>\n"""
		page +="""  </div>\n"""
		page +="""</div>\n"""
		#print(page)
		return page


####################################################################################################################################
####################################################################################################################################
#####################################################################################################################################
# POST
	def selectPost(self):
		sqlId = """SELECT POST_NM FROM TB_CUPPANG_BEST_POST WHERE PRODUCT_ID = '%s'  """ %(self.product_id)		
		return self.ad.selectOne(sqlId)

	def insertPost(self):
		self.ad.insert("""INSERT INTO TB_CUPPANG_BEST_POST(POST_NM, PRODUCT_ID, CATEGORY_CD) VALUES('%s','%s','%s')""" %(self.post_nm, self.product_id,self.category))


	def createPost(self):		
		for product in self.productList:			
			self.setProductInit(product)
			
			postInfo = self.selectPost()
			print(postInfo)
			if postInfo:				
				continue
			else:
				self.insertPost()
				self.makePost()
				self.writeFile('post')	

	def makePost(self):
		post ="""---\n"""
		post +="""layout: post \n"""			
		post +="""title:  "%s" \n""" % (self.title_nm)
		post +="""description: %s ..\n""" % (self.title_nm[:15])
		post +="""date: %s+0900 \n""" % ( self.toDay)
		post +="""img: %s \n"""	%(self.img_url)
		post +="""linkUrl: %s \n""" 	% (self.linkUrl)
		post +="""categories: [%s] \n""" % (self.category)
		post +="""color: %s \n""" % (self.color)
		# post +="""rank: %s \n""" % (self.rank_no)
		post +="""price: %s \n""" % (self.price)
		post +="""author: %s \n""" % (self.author)
		post +="""---\n """
		self.postText = post

	def trim(self, s):
		pat = re.compile(r'\s+') 	
		return pat.sub('',s)


####################################################################################################################################


























	def makeBestStartPage(self):
		page ="""---\n"""
		page +="""layout: default\n"""
		page +="""permalink: /%s/\n""" %(self.page_nm)
		page +="""---\n"""
		page +="""<div id="container">\n"""
		page +="""<div id="grid" data-columns class="cols">\n"""
		return page


	def makeBestEndPage(self):
		page ="""</div>\n"""
		page +="""</div>\n"""
		page +="""<script src="%s/js/salvattore.min.js"></script>""" %(self.baseUrl)
		return page

	def makeBestLoopPage(self):
		page ="""<div class="box" style="background-color:#%s">""" %(self.color)
		#page +="""	<input type="hidden" value="%s">""" %(self.title_nm)
		page +="""  <a href="%s" target="_blank">""" %(self.linkUrl)
		page +="""  	<img class="feat-image lazyload" data-src="%s" alt="%s" >""" %(self.img_url, self.title_nm)
		page +="""  </a>"""
		page +="""  <div class="container">"""
		#print("self.pre_price : ", self.pre_price)
		
		print(self.hour_24 ,"|", self.dateCal)
		if self.hour_24 > self.dateCal:
			#print("new ~!~!~!   ", self.dateCal)
			page +=""" <img  class="lazyload" data-src="/images/new_img_%s.png" alt="new" width="30" height="30"> <h2>%s</h2>"""%(random.randrange(1,3), self.title_nm)
		else:
			page +=""" <h4>%s</h4>"""%(self.title_nm)
		page +="""      <p>%s</p>""" %(self.descript)
		
		# if self.change_rank:
		# 	page +="""      <p>%s</p>""" %(self.change_rank)
		if self.price_up =='Y' or self.price_down =='Y':			
			#print(self.price_up, "|" ,self.price_down, "|", self.product_id, "|", self.pre_price,"|",self.moneyStock)
			page +="""      <p>%s원 %s</p>""" %(self.price, self.moneyStock)	
		else:
			page +="""      <p>%s원</p>""" %(self.price)	
		page +="""  	<div class="action">Update:%s""" %(self.toDay)
		page +="""      	<a href="/%s" target="_blank">""" %(self.product_id)
		page +="""          	<i class="fa fa-arrow-right" aria-hidden="true"></i>"""
		page +="""          </a>"""
		page +="""      </div> """
		page +="""  </div>"""
		page +="""</div>"""
		return page
####################################################################################################################################	
# UTIL

	def getReplace(self, str):
		return re.sub("\[", "",str)

	def changeRankPrice(self):		
		descript ="TOP."+str(self.rank_no)		
		if self.rank_up == 'Y':
			#descript += " [<span style='font-size: 20px;'> ▲ "+ +"상승</span>]"
			self.rankStock ="""<span class="redSy">%s</span> """ %("▲(+"+str(self.pre_rank_no - self.rank_no)+")" )
		if self.rank_down == 'Y':
			#print(self.rank_no)
			#descript += " [<span style='font-size: 20px;'>▼"+ str(self.rank_no - self.pre_rank_no)+"하락</span>]"
			self.rankStock ="""<span class="blueSy">%s</span> """ %("▼("+str(self.pre_rank_no - self.rank_no)+")" )

		if self.price_up == 'Y':			
			#self.change_price = " [<span style='font-size: 20px;'>▲"+ str(self.price - self.pre_price)+"원 상승</span>]"
			self.moneyStock ="""<span class="redSy">%s</span> """ %("▲(+"+str(self.price - self.pre_price)+")" )
		if self.price_down == 'Y':
			#self.change_price = " [<span style='font-size: 20px;'>▼"+ str(self.pre_price - self.price) +"원 하락</span>]"
			self.moneyStock ="""<span class="blueSy">%s</span> """ %("▼("+str(self.price - self.pre_price)+")" )
		#print(descript)
		return descript
