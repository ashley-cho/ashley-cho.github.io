import json, sys
import os
ROOT=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,ROOT)
# Country codes come from the committed cache, not a package (see build.py).
num2iso3=json.load(open(os.path.join(ROOT,'isocache.json')))['num2iso3']
num2iso3.update({'158':'TWN','736':'SDN','304':'GRL','732':'ESH','-99':None})

ent=json.load(open(os.path.join(ROOT,'entities.json')))
world=json.load(open(os.path.join(ROOT,'world_110m.json')))
CI={}
for e in ent['sites']+ent['metros']: CI.setdefault(e['c'], e['ci'])
CIFULL="AFG:2024 ALB:2024 DZA:2024 AGO:2024 ATG:2024 ARG:346 ARM:212 AUS:525 AUT:117 AZE:632 BHS:2024 BHR:2024 BGD:696 BRB:2024 BLR:309 BEL:150 BLZ:2024 BEN:2024 BTN:2024 BOL:481 BIH:571 BWA:2024 BRA:110 BRN:2024 BGR:276 BFA:2024 BDI:2024 KHM:499 CMR:2024 CAN:191 CPV:2024 TCD:2024 CHL:289 CHN:525 COL:187 COM:2023 COG:2024 CRI:24 CIV:2024 HRV:159 CUB:2024 CYP:489 CZE:401 COD:2024 DNK:114 DJI:2024 DMA:2023 DOM:537 TLS:2024 ECU:159 EGY:563 SLV:139 GNQ:2024 ERI:2024 EST:319 SWZ:2024 ETH:23 FJI:2024 FIN:57 FRA:41 GAB:2024 GMB:2024 GEO:146 DEU:330 GHA:2024 GRC:315 GRL:2024 GRD:2024 GTM:2024 GIN:2024 GNB:2024 GUY:2024 HTI:2024 HND:2024 HUN:163 ISL:2024 IND:670 IDN:2024 IRN:660 IRQ:2024 IRL:257 ISR:493 ITA:285 JAM:2024 JPN:477 JOR:2024 KAZ:805 KEN:95 KWT:635 KGZ:153 LAO:2024 LVA:139 LBN:2024 LSO:2022 LBR:2024 LBY:2024 LTU:138 LUX:123 MDG:2024 MWI:2024 MYS:602 MDV:2024 MLI:2024 MLT:484 MRT:2024 MUS:2024 MEX:474 MDA:633 MNG:816 MNE:264 MAR:596 MOZ:2024 MMR:2024 NAM:2024 NPL:2024 NLD:254 NCL:2024 NZL:93 NIC:2024 NER:2024 NGA:456 PRK:2024 MKD:441 NOR:28 OMN:544 PAK:347 PSE:2024 PAN:2024 PNG:2024 PRY:25 PER:238 PHL:588 POL:589 PRT:128 PRI:655 QAT:582 ROU:251 RUS:450 RWA:2024 STP:2023 SAU:2024 SEN:2024 SRB:696 SYC:2024 SLE:2024 SGP:497 SVK:95 SVN:183 SLB:2024 SOM:2024 ZAF:699 KOR:417 SSD:2024 ESP:154 LKA:329 SDN:2024 SUR:2024 SWE:35 CHE:39 SYR:2024 TWN:633 TJK:73 TZA:2024 THA:546 TGO:2024 TON:2024 TTO:2024 TUN:560 TUR:475 TKM:2024 UGA:2024 UKR:2022 ARE:2024 GBR:217 USA:384 URY:80 UZB:1000 VUT:2023 VEN:2024 VNM:461 YEM:2024 ZMB:2024 ZWE:2024"
CIFULL={a:int(b) for a,b in (x.split(':') for x in CIFULL.split())}
CIFULL['HKG']=CIFULL['CHN']

geo=[]
for c in world:
    iso = num2iso3.get(str(int(c['i']))) if c['i'] not in (None,'','-99') else None
    geo.append({'n':c['n'],'i':iso,'ci':CIFULL.get(iso),'r':c['r']})

NAT={"USA": [4519.8, 4904.1, 2025, 2024], "CAN": [652.4, 533.3, 2025, 2024], "BRA": [750.5, 483.0, 2025, 2024], "MEX": [357.0, 461.0, 2025, 2024], "CHL": [88.5, 78.7, 2025, 2024], "COL": [90.4, 92.7, 2025, 2024], "GBR": [292.3, 312.9, 2025, 2024], "IRL": [31.0, 33.3, 2025, 2024], "DEU": [500.5, 572.3, 2025, 2024], "NLD": [135.0, 114.8, 2025, 2024], "FRA": [570.0, 264.2, 2025, 2024], "FIN": [82.3, 29.8, 2025, 2024], "ESP": [287.9, 220.3, 2025, 2024], "ITA": [264.7, 301.9, 2025, 2024], "GRC": [58.3, 53.4, 2025, 2024], "CHE": [65.0, 32.1, 2025, 2024], "ISL": [2024, 3.8, 2024, 2024], "POL": [173.3, 272.9, 2025, 2024], "SWE": [170.7, 38.1, 2025, 2024], "NOR": [160.8, 37.2, 2025, 2024], "JPN": [1029.9, 961.9, 2025, 2024], "CHN": [10583.4, 12289.0, 2025, 2024], "SGP": [60.2, 53.9, 2025, 2024], "MYS": [201.1, 290.2, 2025, 2024], "IND": [2081.6, 3193.5, 2025, 2024], "KOR": [624.7, 583.7, 2025, 2024], "AUS": [286.3, 386.7, 2025, 2024], "HKG": [37.4, 33.3, 2024, 2024], "IDN": [2024, 812.2, 2024, 2024], "THA": [188.2, 267.8, 2025, 2024], "ARE": [2024, 222, 2024, 2024], "ZAF": [242.8, 439.8, 2025, 2024], "SAU": [2024, 692.1, 2024, 2024], "QAT": [56.2, 125.8, 2025, 2024], "BHR": [2024, 39, 2024, 2024], "NGA": [41.5, 135.8, 2025, 2024], "EGY": [245.7, 258.4, 2025, 2024], "KEN": [14.0, 21.2, 2025, 2024], "PRT": [51.1, 35.5, 2025, 2024], "WLD": [31772.4, 38598.6, 2025, 2024]}

# mark named campuses that sit inside a mapped metro (same country, <110 km) so they are not double counted
import math
def km(a,b,c,d):
    p=math.pi/180
    return 6371*math.acos(min(1,math.sin(a*p)*math.sin(c*p)+math.cos(a*p)*math.cos(c*p)*math.cos((d-b)*p)))
OVERRIDE={'OpenAI Stargate UAE (Abu Dhabi)':'Dubai / Abu Dhabi'}
for s in ent['sites']:
    s['inm']=OVERRIDE.get(s['n'])
    if s['inm']: continue
    for m in ent['metros']:
        if m['c']!=s['c']: continue
        if km(s['lat'],s['lon'],m['lat'],m['lon'])<110:
            s['inm']=m['n']; break

names={}
for _iso3,_i in json.load(open(os.path.join(ROOT,'isocache.json')))['iso3info'].items(): names[_iso3]=_i['name']
names['HKG']='Hong Kong'; names['TWN']='Taiwan'
COMPLETE={'USA':'us','CHN':'cn','IND':'in','GBR':'uk','BRA':'br'}
# published national statistics for data centre electricity share, where an official source exists
BENCH={'IRL':{'pct':23.0,'yr':'2025','src':'CSO Ireland, Data Centres Metered Electricity Consumption (Jul 2026)'}}

EU27="AUT BEL BGR HRV CYP CZE DNK EST FIN FRA DEU GRC HUN IRL ITA LVA LTU LUX MLT NLD POL PRT ROU SVK SVN ESP SWE".split()
AFR="DZA AGO BEN BWA BFA BDI CMR CPV CAF TCD COM COG COD CIV DJI EGY GNQ ERI SWZ ETH GAB GMB GHA GIN GNB KEN LSO LBR LBY MDG MWI MLI MRT MUS MAR MOZ NAM NER NGA RWA STP SEN SYC SLE SOM ZAF SSD SDN TZA TGO TUN UGA ZMB ZWE".split()
REG=[
 dict(k='us',n='United States',gw=53.7,ci=384,g=2.30,iso=['USA']),
 dict(k='cn',n='China',gw=31.9,ci=525,g=2.70,iso=['CHN','HKG']),
 dict(k='eu',n='European Union',gw=11.9,ci=210,g=1.75,iso=EU27),
 dict(k='jk',n='Japan & Korea',gw=6.6,ci=454,g=1.80,iso=['JPN','KOR']),
 dict(k='in',n='India',gw=3.6,ci=670,g=2.00,iso=['IND']),
 dict(k='ap',n='Other Asia Pacific',gw=3.1,ci=548,g=2.00,iso="IDN MYS SGP THA VNM PHL TWN PAK BGD LKA MMR KHM LAO BRN NPL MNG PRK MDV BTN TLS PNG FJI".split()),
 dict(k='uk',n='United Kingdom',gw=2.6,ci=217,g=1.75,iso=['GBR']),
 dict(k='oc',n='Australia & New Zealand',gw=1.6,ci=469,g=2.00,iso=['AUS','NZL']),
 dict(k='na',n='Canada & Mexico',gw=1.5,ci=291,g=2.00,iso=['CAN','MEX']),
 dict(k='af',n='Africa',gw=1.5,ci=529,g=2.00,iso=AFR),
 dict(k='la',n='Other Central & South America',gw=1.4,ci=268,g=2.00,iso="ARG CHL COL PER VEN ECU BOL PRY URY GUY SUR TTO PAN CRI GTM HND NIC SLV DOM JAM CUB HTI BLZ PRI BHS BRB".split()),
 dict(k='ea',n='Eurasia',gw=1.2,ci=495,g=2.00,iso="RUS KAZ UZB UKR BLR AZE ARM GEO KGZ TJK TKM MDA".split()),
 dict(k='me',n='Middle East',gw=1.1,ci=636,g=2.00,iso="SAU ARE ISR QAT KWT OMN BHR IRQ IRN JOR LBN SYR YEM TUR".split()),
 dict(k='br',n='Brazil',gw=0.6,ci=110,g=2.00,iso=['BRA']),
]
tot=sum(r['gw'] for r in REG); tot30=sum(r['gw']*r['g'] for r in REG)
K=8760*0.25*1.56/1000
print('2024 GW %.1f  -> %.0f TWh'%(tot,tot*K))
print('2030 GW %.1f  -> %.0f TWh'%(tot30,tot30*K))
print('2024 Mt %.0f'%(sum(r['gw']*K*r['ci'] for r in REG)))

for s in ent['sites']: s['b']='fac'
for m in ent['metros']: m['b']='it'
import datetime
meta=dict(built=datetime.date.today().isoformat(), K=K)
REGS=json.load(open(os.path.join(ROOT,'regs.json')))
CAL=json.load(open(os.path.join(ROOT,'calib.json')))
DISP=json.load(open(os.path.join(ROOT,'disputed.json')))
OVR=json.load(open(os.path.join(ROOT,'override.json')))
NL=json.load(open(os.path.join(ROOT,'newload.json')))
POL=json.load(open(os.path.join(ROOT,'policy.json')))
NEWS=json.load(open(os.path.join(ROOT,'news.json')))
AVERT=json.load(open(os.path.join(ROOT,'avert.json')))
AV_G={k:round(v*0.45359237,1) for k,v in AVERT['rates_lb'].items()}
# US new-load intensity is now per site (build.py). The country layer needs one
# number, so weight the site values by the new capacity they actually represent:
# announced pipeline MW. Robustness of that choice is reported below.
_us=[x for x in ent['sites'] if x['c']=='USA' and x.get('nci')]
_pipe=lambda x: max(0,(x.get('pmw') or 0)-x['mw'])
_wp=sum(_pipe(x) for x in _us) or 1
_wo=sum(x['mw'] for x in _us) or 1
_avg=round(sum(x['nci']*_pipe(x) for x in _us)/_wp)
_alt_avg=round(sum(x['nci']*x['mw'] for x in _us)/_wo)
NL['USA']=dict(NL['USA'], ci=_avg, flat=440,
  head='48% of new US capacity arrives with its own power station; the rest draws at the grid margin',
  note=("Of ~17 GW under construction, 36% is behind-the-meter and 12% is a utility building a "
        "dedicated plant; the other 52% draws on the ordinary grid. The dedicated half is weighted "
        "three parts on-site engines and simple-cycle turbines (~550 g) to one part combined-cycle "
        "(~375 g). The grid half is no longer the US average: each campus now uses the EPA AVERT "
        "marginal rate for its region, because the question is which generator ramps to serve the "
        "extra load, not what the average fleet emits. Site values run "
        f"{min(x['nci'] for x in _us)}-{max(x['nci'] for x in _us)} g/kWh; the country figure is the "
        f"pipeline-weighted mean, {_avg}."),
  avert=dict(AVERT['meta'], rates=AV_G,
             sites=len(_us), lo=min(x['nci'] for x in _us), hi=max(x['nci'] for x in _us),
             wpipe=_avg, wop=_alt_avg,
             split=sum(1 for x in _us if x['avc']=='split'),
             splitmw=round(sum(_pipe(x) for x in _us if x['avc']=='split')),
             pipemw=round(_wp),
             map={k:v for k,v in AVERT['map'].items()}))
print('US new-load CI: pipeline-weighted %d, operational-weighted %d (was flat 440)'%(_avg,_alt_avg))
_st=[m for m in ent['metros'] if m['yr']=='2023']
_tot=sum(m['mw'] for m in ent['metros'])
VINT=dict(staleMw=sum(m['mw'] for m in _st), totMw=_tot, n=len(_st),
          names=[m['n'] for m in sorted(_st,key=lambda x:-x['mw'])])
data=dict(news=NEWS, regs=REGS, disp=DISP, ovr=OVR, newload=NL, policy=POL, vint=VINT, meas=CAL['meas'], anchors=CAL['anchors'], meta=meta, geo=geo, sites=ent['sites'], metros=ent['metros'], regions=REG, ci=CIFULL, nat=NAT, names=names, complete=COMPLETE, bench=BENCH)
open(os.path.join(ROOT,'data.json'),'w').write(json.dumps(data,separators=(',',':')))

inside=sum(1 for s in ent['sites'] if s['inm'])
print('sites inside a mapped metro:', inside, 'of', len(ent['sites']))
byc={}
for m in ent['metros']: byc[m['c']]=byc.get(m['c'],0)+m['mw']
for s in ent['sites']:
    if not s['inm']: byc[s['c']]=byc.get(s['c'],0)+s['mw']
for k in sorted(byc,key=lambda k:-byc[k])[:8]:
    gen=NAT.get(k,[None])[0]
    print(' ',k, round(byc[k]), 'MW ->', (round(byc[k]*8760*.25*1.56/1e6,1) if gen else '?'),'TWh', (str(round(byc[k]*8760*.25*1.56/1e6/gen*100,1))+'% of national' if gen else ''))
import os; print('bytes', os.path.getsize(os.path.join(ROOT,'data.json')))
