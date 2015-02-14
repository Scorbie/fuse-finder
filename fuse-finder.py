# codeholic's FuseFinder script v0.2.0
#   Creates a new layer called "FuseTestLayer"
#   Writes to a FuseFinder subfolder in Golly's data directory.
#   Updates screen every hundred trials (why not?)
#   Uses g.new() as per simsim314's suggestion
#      (I noticed that Golly's Undo got very slow after running the old script) (?)
# hashsoup used instead randfill
# report to patterns folder
#SEED for datetime.now
import golly as g
import os
import time
import hashlib
import datetime
import itertools
import math

MAX_FUSE_PACE     = 10   # how many ticks it takes to burn one cell
MAX_FUSE_LENGTH   = 1000 # how long the test fuse is
MAX_IGNITION_TIME = 1000 # how long we wait for a fuse to be ignited
BASE = 16

step = int(math.log(MAX_FUSE_PACE * MAX_FUSE_LENGTH + MAX_IGNITION_TIME, BASE) + 0.5)

outpath=os.path.join(g.getdir("patterns"),"FuseFinder")
if not os.path.isdir(outpath): os.mkdir(outpath)

FUSENAME = "Diagpuffer"

selrect = g.getselrect()
if not selrect:
  g.exit('Select a fuse monomer.')

monomer = g.getcells(selrect)
if not monomer:
  g.exit('Selected region is empty.')

offset = int(g.getstring("Enter horizontal offset:", "0"))

seed = g.getstring("Enter soup seed:", str(datetime.datetime.now()))

for i in range(g.numlayers()):
  if g.getname(i)=="FuseTestLayer":
    r=g.getrect()
    if r is not []:
        g.select(r)
        g.clear(0)
    break
if not g.getname(i)=="FuseTestLayer":  g.addlayer()

g.setalgo('QuickLife')

x0, y0, width, height = selrect
for dx, dy in zip((i * offset for i in itertools.count(0)), range(0, MAX_FUSE_LENGTH, height)):
  g.putcells(monomer, dx, -dy)

TESTRECT = [x0 + dx, y0 - dy, width, height]

allcells=g.getcells(g.getrect())
cells = g.getcells(TESTRECT)

SOUP_SIZE = 16
SOUPSPERDISPLAY = 100

def hashsoup(instring):
    s = hashlib.sha256(instring).digest()
    thesoup = []
    for j in xrange(32):
        t = ord(s[j])
        for k in xrange(8):
            if (t & (1 << (7 - k))):
                thesoup.append(k + 8*(j % 2))
                thesoup.append(int(j / 2))

    return thesoup

def patterns_identical(cells1, cells2):
  if len(cells1) != len(cells2):
    return False
  return set(zip(cells1[::2], cells1[1::2])) == set(zip(cells2[::2], cells2[1::2]))

count, found = 0, 0

start_time = time.clock()

# For profiling
#
#init_time = 0
#gen_time = 0
#check_time = 0


while True:
  #mark = time.clock()
  g.new("FuseTestLayer")
  g.putcells(allcells)
  g.putcells(hashsoup(seed + str(count)), x0 + (width - SOUP_SIZE) / 2, y0 + height)
  #init_time += time.clock()-mark
  #mark = time.clock()
  g.setbase(BASE)
  g.setstep(step)

  #gen_time +=time.clock()-mark
  #mark = time.clock()
  changed = True
  for _ in range(0, 2):
    g.step()
    test = g.getcells(TESTRECT)
    if patterns_identical(test, cells):
      changed = False
      break

  count += 1

  if changed:
    g.reset()
    g.save(os.path.join(outpath, FUSENAME + str(count) + '.rle'), 'rle')
    g.show("Saved fuse to " + outpath + FUSENAME + str(count) + ".rle")
    found += 1

  if count % SOUPSPERDISPLAY == 0:
    end_time =time.clock()
    g.show('Count:' + str(count) + ' Found:' + str(found) + ' (' +\
        str(round(SOUPSPERDISPLAY/(end_time - start_time), 2)) + " soups per second)")
    #g.show('init: '+str(init_time*1000/count)+'ms gen: '+str(gen_time*1000/count)+'ms check: '+str(check_time*1000/count)+'ms')
    start_time = end_time
    g.setmag(2)
    g.update()
    #check_time += time.clock()-mark
