#coding=utf-8
import MySQLdb
import xlwt,multiprocessing,re,time,sys,os
from multiprocessing import Pool

def run(sql):


    try:
        db = MySQLdb.connect(host='21.254.247.92',user='tongyf',passwd='1qaz@WSX',db='zabbix',charset='utf8')
       # cursor = db.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        cursor = db.cursor()

        try:
            cursor.execute(sql)
            result=cursor.fetchall()
            return result

        except Exception as e:
            print e
            db.rollback()

        db.close()

    except Exception as e:
        print e





def test(start,end):



   # start=raw_input("请输入起始日期，如20110309:")

   # end=raw_input("请输入截止日期，如20110310:")
#查询端口带宽
    sql1="select distinct A.value_max,B.key_,B.hostid from trends_uint as A INNER JOIN items as B on A.itemid=B.itemid  \
    where B.itemid=ANY(select itemid from items where key_ like 'ifSpeed%')"

#选择区间查询最大值
    sql2="select itemid,AVG(value_avg),MAX(value_max),MIN(value_min) from trends_uint  \
    where itemid in (select itemid from items where hostid=ANY(select hostid from hosts_groups where groupid=20) \
    and key_ like 'ifHCInOctets%%' ) and clock>UNIX_TIMESTAMP('%s') and clock<UNIX_TIMESTAMP('%s') GROUP BY itemid;" % (start,end)
 #   sql2="select itemid,AVG(value_avg),MAX(value_max),MIN(value_min) from trends_uint where itemid in (select itemid from items where hostid=10421 and (key_ like 'ifHCInOctets%' or key_ like 'ifHCOutOctets%')) GROUP BY itemid;"
  #  sql2="select itemid,AVG(value_avg),MAX(value_max),MIN(value_min) from trends_uint where itemid in (select itemid from items where hostid=ANY(select hostid from hosts_groups where groupid=20) and (key_ like 'ifHCInOctets%%' or key_ like 'ifHCOutOctets%%')) and clock>UNIX_TIMESTAMP('%s') and clock<UNIX_TIMESTAMP('%s') GROUP BY itemid;" % (start,end)
    sql4="select itemid,AVG(value_avg),MAX(value_max),MIN(value_min) from trends_uint  \
    where itemid in (select itemid from items where hostid=ANY(select hostid from hosts_groups where groupid=20) \
    and  key_ like 'ifHCOutOctets%%') and clock>UNIX_TIMESTAMP('%s') and clock<UNIX_TIMESTAMP('%s') GROUP BY itemid;" % (start,end)
#查询组所有items信息
    sql3 = "select A.itemid,A.key_,A.hostid,B.host,A.name,B.name from  items AS A INNER JOIN hosts as B on  A.hostid=B.hostid where A.hostid=ANY(select hostid from hosts_groups where groupid=20);"

    items_tun=run(sql3)
    bandwith_dict={}
    bandwith_tun=run(sql1)
    for i in bandwith_tun:


        bandwith_dict[(i[1],i[2])]=i[0]
       #生成字典{(hostid,key_):value}

    #print len(l)
    in_tun=run(sql2)
   #出入流量数据
    out_tun=run(sql4)

    dict={}
    for i in items_tun:
        itemid=i[0]
        key=i[1]
        hostid=i[2]
        host=i[3]
        hostname=i[5]
        name=i[4]#  端口描述
        dict[itemid]=[key,host,hostname,hostid,name]
#生成字典{itemid:[key,host,hostname,hostid,name]}  查询itemid 对应值


    file = xlwt.Workbook(encoding = 'utf-8')
   # nowtime=time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
   # table = file.add_sheet('骨干接口流量')
    nowtime=time.strftime("%Y-%m-%d", time.localtime())
    table = file.add_sheet('%s骨干接口流量' % nowtime)
    table.write(0,2,"In_avg(bps)")
    table.write(0,3,"In_max(bps)")
    table.write(0,4,"Out_avg(bps)")
    table.write(0,5,"Out_max(bps)")
    table.write(0,1,"Interface")
    table.write(0,0,"Host")
    table.write(0,6,"Bandwidth(bps)")
    m=1
    in_dict={}
    for i in in_tun:
        itemid=i[0]
        avg=i[1]
        max=i[2]
        min=i[3]
        key=dict[itemid][0]
       # key1=dict[itemid][0].split('.')[-1]
        key1=re.match(r'.*?(\[.*?\])',key).group(1)
        key2="ifSpeed."+ str(key1)
        #截取端口名重新组合生成ifspped.[] 键值
        host=dict[itemid][1]
        hostname=dict[itemid][2]
        hostid=dict[itemid][3]
        name=dict[itemid][4]
        dk=bandwith_dict[(key2,hostid)]
        in_dict[(hostid,key1)]=[avg,min,max,name,hostname,dk,key1]

    result={}
    for i in out_tun:
        itemid=i[0]
        avg=i[1]
        max=i[2]
      #  min=i[3]
        key=dict[itemid][0]
        key1=re.match(r'.*?(\[.*?\])',key).group(1)
        host=dict[itemid][1]
        hostname=dict[itemid][2]
        hostid=dict[itemid][3]
        name=dict[itemid][4]
        name=name.split("interface")[1]
       # print "%s" % (in_dict[(hostid,key1)])




        #result.append([hostname,name,in_dict[(hostid,key1)][0],in_dict[(hostid,key1)][2],avg,max,in_dict[(hostid,key1)][5]])
        table.write(m,2,in_dict[(hostid,key1)][0])
        table.write(m,3,in_dict[(hostid,key1)][2])
        table.write(m,4,avg)
        table.write(m,5,max)
        table.write(m,1,name)
        table.write(m,0,hostname)
        table.write(m,6,in_dict[(hostid,key1)][5])




        result[m]={'hostname':hostname,'name':name,'in-avg':int(in_dict[(hostid,key1)][0]),'in-max':in_dict[(hostid,key1)][2],'out-avg':int(avg),'out-max':max,'bandwith':in_dict[(hostid,key1)][5]}
        m=m+1
    try:
       os.remove("/usr/local/nginx/flask/file/gg.xls")
    except:
        pass
    file.save("/usr/local/nginx/flask/file/gg.xls" )
    return result


   # # pool.close()
   # # pool.join()
    #e_time=time.time()
   # print e_time-s_time
if __name__=='__main__':

    test(20180803,20180804)


