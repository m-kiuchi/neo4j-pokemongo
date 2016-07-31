#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Creationline - CL Lab
#   Calcurate paths for Rare-Pokemon-Spots in Tokyo
# 2016/8/1: Mitsutoshi Kiuchi<m-kiuchi@creationline.com>
#
import itertools, sys
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client

gdb = GraphDatabase("http://neo4j:1234@localhost:7474/db/data/")

#
# 巡回経路マスタの作成
#
seqs = (401,) # スタート地点のID
seq = ()
results = gdb.query("MATCH (st:PokemonSpot) RETURN st;")
for i in results:
  seq += (i[0]["metadata"]["id"],)

pm = itertools.permutations(seq)
pmm = []
cnt = 0
for i in pm:
  pmm.append((401,) + i + (401,))
  #print pmm[cnt]
  cnt += 1
del pm
print "Num of traversal route: %d" % cnt

#
# 巡回経路ごとに所要時間を計算
#
icnt = 0
pmmm = []
cachedict = {}
for i in pmm:
   jcnt = 0
   cachecnt = 0
   #if icnt > 595:
   #  print i
   totalCost = 0
   for j in i:
      if jcnt == (len(i)-1):
        break
      source = i[jcnt]
      dest = i[jcnt+1]
      key = str(source) + "-" + str(dest)
      rest = ""
      if cachedict.has_key(key):
        rest = cachedict[key]
        cachecnt += 1
      else:
        qstr =  'START source=node(' + str(source) + '), dest=node(' + str(dest) + ') '
        qstr += 'MATCH p=allShortestPaths((source)-[r*1..10]-(dest)) '
        qstr += 'WITH p,reduce(s = 0, rel IN r | s + rel.cost) AS totalCost '
        qstr += 'RETURN p,totalCost ORDER BY totalCost LIMIT 1;'
        rest = gdb.query(qstr)
        cachedict[key] = rest
      if len(rest) > 0:
         totalCost += rest[0][1]
      else:
         # Traversal Error Found. Skip this route.
         sys.stderr.write("X")
         totalCost = 99999999
         break
      jcnt += 1
   if totalCost != 99999999:
     t = (icnt+1) % 1000
     if t == 0:
        #print "route %d traversalled" % (icnt+1)
        sys.stderr.write("\nroute %d traversalled\n" % (icnt+1))
     else:
        if cachecnt == len(i)-1:
          # All of Traversals has been cached.
          sys.stderr.write(".")
        else:
          # Some route hasn't been cached.
          sys.stderr.write("O")
          #print "route-no %d, totalCost is: %d" % ((icnt+1), totalCost)
   pmmm.append(totalCost)
   icnt += 1
print "All route has traversalled"

#
# 最短経路を表示
#
cnt = 0
stst = 99999999
ststcnt = 0
for i in pmmm:
  if stst > i:
    stst = i
    ststcnt = cnt
  cnt += 1
stst = stst/60
print "-----"
print "calculated fastest path to Rare-Pokemon-master !!"
print pmm[ststcnt]
print "estimated duration: %.2f hours" % stst
print "Good luck !!"

