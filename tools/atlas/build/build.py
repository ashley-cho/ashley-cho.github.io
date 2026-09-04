import json, sys, re
import os
ROOT=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,ROOT)
from sites import EPOCH, METROS
# Geocoding runs off committed caches so a rebuild needs nothing but Python.
# The zipcodes / geonamescache packages are only imported if a lookup misses,
# which happens only when a new site with an unseen ZIP is added to sites.py.
ZIPCACHE = json.load(open(os.path.join(ROOT, 'zipcache.json')))
_iso = json.load(open(os.path.join(ROOT, 'isocache.json')))
num2iso3, iso3info = _iso['num2iso3'], _iso['iso3info']

def _zip_miss(z):
    try:
        import zipcodes
    except ImportError:
        raise SystemExit(
            f"ZIP {z} is not in zipcache.json and the 'zipcodes' package is not "
            f"installed. Run: pip3 install zipcodes  — then rerun to extend the cache.")
    m = zipcodes.matching(z)
    if not m:
        return None
    r = m[0]
    rec = [float(r['lat']), float(r['long']), r['city'], r['state']]
    ZIPCACHE[z] = rec
    json.dump(ZIPCACHE, open(os.path.join(ROOT, 'zipcache.json'), 'w'), indent=0)
    print(f'  zipcache extended: {z} -> {rec[2]}, {rec[3]}')
    return rec

CI = """AFG:131 ALB:25 DZA:633 AGO:185 ATG:595 ARG:346 ARM:212 AUS:525 AUT:117 AZE:632 BHS:653 BHR:902 BGD:696 BRB:595 BLR:309 BEL:150 BLZ:170 BEN:584 BTN:24 BOL:481 BIH:571 BWA:851 BRA:110 BRN:892 BGR:276 BFA:562 BDI:184 KHM:499 CMR:226 CAN:191 CPV:462 CAF:0 TCD:622 CHL:289 CHN:525 COL:187 COM:643 COG:716 CRI:24 CIV:405 HRV:159 CUB:643 CYP:489 CZE:401 COD:28 DNK:114 DJI:450 DMA:600 DOM:537 TLS:667 ECU:159 EGY:563 SLV:139 GNQ:644 ERI:578 EST:319 SWZ:131 ETH:23 FJI:278 FIN:57 FRA:41 GUF:245 GAB:523 GMB:667 GEO:146 DEU:330 GHA:469 GRC:315 GRL:150 GRD:667 GTM:301 GIN:181 GNB:625 GUY:645 HTI:535 HND:322 HUN:163 ISL:28 IND:670 IDN:680 IRN:660 IRQ:683 IRL:257 ISR:493 ITA:285 JAM:563 JPN:477 JOR:530 KAZ:805 KEN:95 KIR:500 KWT:635 KGZ:153 LAO:232 LVA:139 LBN:390 LSO:21 LBR:316 LBY:827 LTU:138 LUX:123 MDG:432 MWI:55 MYS:602 MDV:612 MLI:539 MLT:484 MRT:512 MUS:642 MEX:474 MDA:633 MNG:816 MNE:264 MAR:596 MOZ:129 MMR:503 NAM:49 NRU:600 NPL:24 NLD:254 NCL:561 NZL:93 NIC:301 NER:674 NGA:456 PRK:341 MKD:441 NOR:28 OMN:544 PAK:347 PSE:414 PAN:221 PNG:514 PRY:25 PER:238 PHL:588 POL:589 PRT:128 PRI:655 QAT:582 ROU:251 RUS:450 RWA:354 KNA:609 LCA:650 VCT:600 WSM:375 STP:556 SAU:692 SEN:540 SRB:696 SYC:556 SLE:48 SGP:497 SVK:95 SVN:183 SLB:636 SOM:512 ZAF:699 KOR:417 SSD:643 ESP:154 LKA:329 SDN:154 SUR:322 SWE:35 CHE:39 SYR:706 TWN:633 TJK:73 TZA:345 THA:546 TGO:423 TON:571 TTO:682 TUN:560 TUR:475 TKM:1306 UGA:59 UKR:250 ARE:468 GBR:217 USA:384 URY:80 UZB:1000 VUT:500 VEN:86 VNM:461 YEM:592 ZMB:120 ZWE:384"""
CI = {a:int(b) for a,b in (x.split(':') for x in CI.split())}
CI['HKG'] = CI['CHN']

# US state -> eGRID2023 subregion CO2e rate (g/kWh) and subregion label
EG = {
 'VA':(271,'SRVC'),'NC':(271,'SRVC'),'SC':(271,'SRVC'),
 'GA':(384,'SRSO'),'AL':(384,'SRSO'),
 'MS':(336,'SRMV'),'LA':(336,'SRMV'),'AR':(336,'SRMV'),
 'TN':(410,'SRTV'),'KY':(410,'SRTV'),
 'FL':(356,'FRCC'),'TX':(334,'ERCT'),
 'OK':(397,'SPSO'),'KS':(394,'SPNO'),
 'NE':(420,'MROW'),'IA':(420,'MROW'),'MN':(420,'MROW'),'ND':(420,'MROW'),'SD':(420,'MROW'),
 'WI':(637,'MROE'),'IL':(566,'SRMW'),'MO':(566,'SRMW'),'MI':(443,'RFCM'),
 'OH':(416,'RFCW'),'IN':(416,'RFCW'),'WV':(416,'RFCW'),
 'PA':(272,'RFCE'),'NJ':(272,'RFCE'),'MD':(272,'RFCE'),'DE':(272,'RFCE'),
 'NY':(110,'NYUP'),
 'MA':(246,'NEWE'),'CT':(246,'NEWE'),'RI':(246,'NEWE'),'NH':(246,'NEWE'),'VT':(246,'NEWE'),'ME':(246,'NEWE'),
 'AZ':(320,'AZNM'),'NM':(320,'AZNM'),'NV':(288,'NWPP'),
 'CA':(195,'CAMX'),
 'OR':(288,'NWPP'),'WA':(288,'NWPP'),'ID':(288,'NWPP'),'UT':(288,'NWPP'),'MT':(288,'NWPP'),
 'CO':(473,'RMPA'),'WY':(473,'RMPA'),
}

def geo(z):
    r = ZIPCACHE.get(z) or _zip_miss(z)
    if not r: return None
    return r[0], r[1], r[2], r[3]

sites=[]
miss=[]
for name,mw,op,iso,z,ll,pmw,pyr in EPOCH:
    city=state=None
    if z:
        g=geo(z)
        if not g: miss.append((name,z)); continue
        lat,lon,city,state=g
    else:
        lat,lon = ll
    ci = CI.get(iso,450); ci_lbl = iso3info.get(iso,{}).get('name',iso)
    if iso=='USA' and state in EG:
        ci, sub = EG[state]; ci_lbl = f"{state} · eGRID {sub}"
    status = 'operational' if mw>0 else 'pipeline'
    sites.append(dict(t='site',n=name,o=op,c=iso,lat=round(lat,3),lon=round(lon,3),
                      mw=mw,pmw=pmw,py=pyr,st=status,ci=ci,cil=ci_lbl,
                      loc=(f"{city}, {state}" if city else None),yr='Sep 2026',src='Epoch AI Frontier Data Centers'))
metros=[]
for name,iso,lat,lon,mw,pmw,yr,src in METROS:
    ci=CI.get(iso,450); cil=iso3info.get(iso,{}).get('name',iso)
    metros.append(dict(t='metro',n=name,o=None,c=iso,lat=lat,lon=lon,mw=mw,pmw=pmw,py=None,
                       st='operational',ci=ci,cil=cil,loc=None,src=src,yr=yr))

print('sites',len(sites),'miss',miss)
print('metros',len(metros),'metro MW',sum(m['mw'] for m in metros))
print('site MW',sum(s['mw'] for s in sites))
json.dump({'sites':sites,'metros':metros}, open(os.path.join(ROOT,'entities.json'),'w'))
