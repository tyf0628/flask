#coding=utf-8
import MySQLdb
import xlwt,multiprocessing,re,time,sys
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



#选择区间查询最大值
    sql1="select itemid,AVG(value_avg),MAX(value_max),MIN(value_min) from trends_uint  \
    where itemid in (371069,371011,374634,387107,371016,371074,371014,371009,371067,371072,1615712,1615713,1615710,1615714) \
     and clock>UNIX_TIMESTAMP('%s') and clock<UNIX_TIMESTAMP('%s') GROUP BY itemid;" % (start,end)
    sql3="select itemid,AVG(value_avg),MAX(value_max),MIN(value_min) from trends_uint  \
    where itemid in (371343,371285,375397,387892,371290,371348,371288,371283,371341,371346,1615816,1615817,1615814,1615818) \
     and clock>UNIX_TIMESTAMP('%s') and clock<UNIX_TIMESTAMP('%s') GROUP BY itemid;" % (start,end)
#查询组所有items信息
    sql2 = "select A.itemid,A.key_,A.hostid,B.host,A.name,B.name from  items AS A INNER JOIN hosts as B on  A.hostid=B.hostid where A.hostid=ANY(select hostid from hosts_groups where groupid=21);"
    message=run(sql1)
    sql4="select distinct A.value_max,B.key_,B.hostid from trends_uint as A INNER JOIN items as B on A.itemid=B.itemid  \
    where B.itemid=ANY(select itemid from items where key_ like 'ifSpeed%')"
    #print message
    items_tun=run(sql2)
    in_tun=run(sql1)
    out_tun=run(sql3)
    bandwith_tun=run(sql4)

    bandwith_dict={}
    for i in bandwith_tun:


        bandwith_dict[(i[1],i[2])]=i[0]
   #

    dict={}
    for i in items_tun:
        itemid=i[0]
        key=i[1]
        hostid=i[2]
        host=i[3]
        name=i[4]
        hostname=i[5]
        dict[itemid]=[key,host,name,hostid,hostname]

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
        name=dict[itemid][4]
        hostid=dict[itemid][3]
        hostname=dict[itemid][2]
        dk=bandwith_dict[(key2,hostid)]
        in_dict[(hostid,key1)]=[avg,min,max,name,hostname,dk,key1]

    file = xlwt.Workbook(encoding = 'utf-8')
   # nowtime=time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
   # table = file.add_sheet('出口流量')
    nowtime=time.strftime("%Y-%m-%d", time.localtime())
    table = file.add_sheet('%s出口流量' % nowtime)
    table.write(0,0,"host")
    table.write(0,1,"interface")
    table.write(0,2,"In_max")
    table.write(0,3,"In_avg")
    table.write(0,4,"Out_max")
    table.write(0,5,"Out_avg")
    table.write(0,6,"bandwidth")

    m=1
    result={}
    for i in out_tun:
        itemid=i[0]
        avg=i[1]
        max=i[2]
      #  min=i[3]
        key=dict[itemid][0]
        key1=re.match(r'.*?(\[.*?\])',key).group(1)
        host=dict[itemid][1]
        hostname=dict[itemid][4]
        hostid=dict[itemid][3]
        name=dict[itemid][2]
        name=name.split("interface")[1]
        table.write(m,0,hostname)
        table.write(m,1,name)
        table.write(m,2,in_dict[(hostid,key1)][2])
        table.write(m,3,in_dict[(hostid,key1)][0])
        table.write(m,4,max)
        table.write(m,5,avg)
        table.write(m,6,in_dict[(hostid,key1)][5])

   #
        result[m]={'hostname':hostname,'name':name,'in-avg':int(in_dict[(hostid,key1)][0]),'in-max':in_dict[(hostid,key1)][2],'out-avg':int(avg),'out-max':max,'bandwith':in_dict[(hostid,key1)][5]}
        m=m+1
    try:
       os.remove("/usr/local/nginx/flask/file/ck.xls")
    except:
        pass
    file.save("/usr/local/nginx/flask/file/ck.xls" )
    return result


if __name__=='__main__':

    test(20180801,20180806)


