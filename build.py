from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, random, base64, io, collections, re, html
P=Path(__file__).parent
rng=random.Random(20261126)
chap={1:'Makanan Bergizi untuk Kesehatan Pencernaanmu',2:'Tarik dan Embuskan',3:'Jejak Sang Pahlawan'}
rows=[]; groups=[]; bank=[]; images={}; seq=0
for l in (P/'konsep.txt').read_text().splitlines():
 if l.startswith('#'):
  a,b,c=l[1:].split('|'); g={'bab':int(a),'sub':b,'topik':c,'items':[]};groups.append(g)
 else:
  t,d,s,e=l.split('|');g['items'].append((t,d,s,e))

def add(g,setid,typ,lev,q,correct,wrong=None,exp='',img=None,aliases=None):
 global seq
 seq+=1
 obj=dict(id=f'IPAS-{seq:04}',set=setid,bab=g['bab'],sub=g['sub'],topik=g['topik'],jenis=typ,level=lev,soal=q,jawaban=correct,pembahasan=exp)
 if typ=='PG':
  opts=[correct]+list(wrong);assert len(set(opts))==4,(q,opts);rng.shuffle(opts);obj['opsi']=opts
 else: obj['alternatif']=aliases or []
 if img:obj['gambar']=img
 bank.append(obj)

aliases={'kerongkongan':['esofagus'],'usus halus':['intestinum tenue'],'usus besar':['kolon'],'rektum':['rectum'],'kantong empedu':['kandung empedu'],'peristaltik':['gerak peristaltik'],'pencernaan mekanis':['pencernaan mekanik'],'pencernaan kimiawi':['pencernaan kimia'],'vitamin A':['vit a'],'vitamin C':['vit c'],'air':['h2o'],'GERD':['gastroesophageal reflux disease'],'cuci tangan pakai sabun':['cuci tangan dengan sabun','mencuci tangan dengan sabun','ctps'],'menu seimbang':['gizi seimbang','menu bergizi seimbang'],'penyimpanan dingin':['pendinginan','refrigerasi'],'membaca label pangan':['membaca label makanan','membaca label gizi'],'trakea':['batang tenggorokan'],'bronkiolus':['bronkiol'],'alveolus':['alveoli'],'inspirasi':['inhalasi'],'ekspirasi':['ekshalasi'],'pertukaran gas':['pertukaran oksigen dan karbon dioksida'],'oksigen':['o2'],'karbon dioksida':['co2'],'karbon monoksida':['co'],'partikulat':['partikel','partikel halus'],'aktivitas fisik teratur':['olahraga teratur'],'etika batuk':['adab batuk'],'lingkungan bebas asap rokok':['kawasan tanpa rokok','kawasan bebas asap rokok'],'frekuensi napas':['frekuensi pernapasan'],'variabel bebas':['variabel independen'],'variabel terikat':['variabel dependen'],'variabel kontrol':['variabel terkendali'],'rempah-rempah':['rempah','rempah rempah'],'tanam paksa':['cultuurstelsel','sistem tanam paksa'],'VOC':['vereenigde oostindische compagnie'],'Pangeran Diponegoro':['diponegoro'],'Pattimura':['thomas matulessy'],'Tuanku Imam Bonjol':['imam bonjol'],'Cut Nyak Dien':['cut nyak dhien','cut nyak din'],'R.A. Kartini':['kartini','raden ajeng kartini','ra kartini'],'Ki Hadjar Dewantara':['ki hajar dewantara','ki hadjar dewantoro','ki hajar dewantoro'],'Budi Utomo':['boedi oetomo'],'Soekarno':['sukarno','ir soekarno','ir sukarno'],'Mohammad Hatta':['mohammad hatta','mohamad hatta','muhammad hatta','m hatta','bung hatta'],'Sayuti Melik':['sayuti malik'],'sumber primer':['sumber sejarah primer'],'sumber sekunder':['sumber sejarah sekunder'],'verifikasi sumber':['kritik sumber','verifikasi'],'rela berkorban':['pengorbanan']}
for gi,g in enumerate(groups):
 for k,(t,d,s,e) in enumerate(g['items']):
  sid=f'K{gi+1:02}-{k+1}'; others=[r for j,r in enumerate(g['items']) if j!=k]; ts=[r[0] for r in others];ds=[r[1] for r in others];ss=[r[2] for r in others];es=[r[3] for r in others];ex=f'{t.capitalize()} adalah {d}. {e}'
  def pg(l,q,a,w):add(g,sid,'PG',l,q,a,w,ex)
  def fill(l,q):add(g,sid,'Isian',l,q,t,exp=ex,aliases=aliases.get(t,[]))
  pg('Mudah',f'Istilah atau nama yang tepat untuk {d} adalah ....',t,ts)
  pg('Mudah',f'Manakah penjelasan paling tepat tentang {t}?',d,ds)
  pg('Mudah',f'Pilih pasangan yang benar jika fokus pembahasan adalah {t}.',f'{t} — {d}',[f'{t} — {x}' for x in ds])
  pg('Sedang',f'Perhatikan situasi berikut: {s} Konsep atau tokoh yang paling tepat terkait situasi tersebut adalah ....',t,ts)
  pg('Sedang',f'Siswa akan membuat kartu contoh untuk materi {t}. Situasi yang paling tepat ditulis pada kartu adalah ....',s,ss)
  pg('Sedang',f'{s} Manakah penjelasan yang paling sesuai dengan situasi tersebut?',e,es)
  pg('Sukar',f'Kelompok siswa mengamati situasi: {s} Mereka harus menghubungkan situasi dengan konsep dan alasannya. Pilih pasangan yang paling tepat.',f'{t} — {e}',[f'{r[0]} — {es[(j+1)%3]}' for j,r in enumerate(others)])
  # paired statements: distractors are other terms with shifted definitions, all mismatched
  pairwrong=[f'{r[0]} — {others[(j+1)%3][1]}' for j,r in enumerate(others)]
  pg('Sukar',f'Sebuah poster tentang {g["topik"].lower()} akan diperiksa. Catatan yang hendak diperiksa: {s} Manakah pasangan istilah/nama dan keterangan yang tepat?',f'{t} — {d}',pairwrong)
  fill('Mudah',f'Tuliskan istilah atau nama untuk {d}.')
  fill('Sedang',f'{s} Tuliskan istilah atau nama yang paling tepat untuk situasi itu.')

font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(n,b=False):return ImageFont.truetype(bold if b else font,n)
def draw_visual(i,title,unit,labels,vals,note):
 im=Image.new('RGB',(1000,490),'#fbfaf5');dr=ImageDraw.Draw(im);dr.rounded_rectangle((12,12,988,478),18,fill='#ffffff',outline='#b8c8bf',width=2)
 # wrap text by pixel
 def wrapped(s,x,y,maxw,font,fill,step):
  line=''
  for w in s.split():
   cand=(line+' '+w).strip()
   if dr.textlength(cand,font=font)>maxw and line:dr.text((x,y),line,font=font,fill=fill);y+=step;line=w
   else:line=cand
  dr.text((x,y),line,font=font,fill=fill);return y+step
 y=wrapped(title,35,30,930,f(27,True),'#103f32',34)
 dr.text((35,y+3),('Kronologi peristiwa' if unit=='tahun' else 'Satuan: '+unit),font=f(18),fill='#49655b')
 if unit=='tahun':
  for j,(lab,v) in enumerate(zip(labels,vals)):
   yy=125+j*74;dr.rounded_rectangle((35,yy,965,yy+58),8,fill='#edf4ef');dr.text((50,yy+12),lab,font=f(21),fill='#103f32');dr.text((895,yy+12),str(v),font=f(24,True),fill='#103f32',anchor='ra')
 else:
  mx=max(vals)*1.15
  for j,(lab,v) in enumerate(zip(labels,vals)):
   yy=132+j*69;dr.text((35,yy+8),lab,font=f(21),fill='#103f32');w=int(v/mx*580);dr.rounded_rectangle((300,yy,300+w,yy+37),5,fill='#19765a' if j%2==0 else '#467d6b');dr.text((312+w,yy+4),str(v),font=f(23,True),fill='#103f32')
 wrapped(note,35,419,930,f(15),'#54645b',20)
 bio=io.BytesIO();im.save(bio,'PNG',optimize=True);return 'data:image/png;base64,'+base64.b64encode(bio.getvalue()).decode()
for i,line in enumerate((P/'data_visual.txt').read_text().splitlines(),1):
 b,sub,title,unit,note,raw=line.split('|');g=dict(bab=int(b),sub=sub,topik=title);items=[x.rsplit(':',1) for x in raw.split(';')];labs=[a for a,v in items];vs=[int(v) for a,v in items];d=dict(zip(labs,vs));rank=sorted(labs,key=d.get);lo,mid1,mid2,hi=rank;sid=f'V{i:02}';img=sid;images[img]=draw_visual(i,title,unit,labs,vs,note);time=unit=='tahun';pre='Berdasarkan gambar, ';ex='; '.join(f'{a}: {v} {unit}' for a,v in zip(labs,vs))+'. '+note
 def pg(l,q,a,w):add(g,sid,'PG',l,q,str(a),list(map(str,w)),ex,img)
 def fill(l,q,a,al=None):add(g,sid,'Isian',l,q,str(a),exp=ex,img=img,aliases=al)
 pg('Mudah',pre+('peristiwa paling awal adalah ....' if time else 'kategori dengan nilai terbesar adalah ....'),lo if time else hi,[x for x in labs if x!=(lo if time else hi)])
 pg('Mudah',pre+f'berapa {"tahun peristiwa" if time else "nilai ("+unit+") untuk"} {mid1}?',d[mid1],[x for x in vs if x!=d[mid1]])
 pg('Sedang',pre+('peristiwa paling akhir adalah ....' if time else 'kategori dengan nilai terendah adalah ....'),hi if time else lo,[x for x in labs if x!=(hi if time else lo)])
 pg('Sedang',pre+f'{"peristiwa kedua paling awal" if time else "kategori dengan nilai terbesar kedua"} adalah ....',mid1 if time else mid2,[x for x in labs if x!=(mid1 if time else mid2)])
 diff=d[hi]-d[lo];ww=list(dict.fromkeys([d[hi]-d[mid1],d[hi]-d[mid2],d[mid1]-d[lo],diff+1,diff+2]));ww=[x for x in ww if x!=diff][:3]
 pg('Sedang',pre+f'selisih antara nilai terbesar dan terkecil adalah berapa {"tahun" if time else unit}?',diff,ww)
 pg('Sedang',pre+(f'peristiwa manakah yang terjadi setelah {mid1} tetapi sebelum {hi}?' if time else f'kategori manakah yang nilainya lebih besar dari {mid1} tetapi lebih kecil dari {hi}?'),mid2,[lo,mid1,hi])
 pairs=[f'{a}, {b}' for a,b in [(lo,hi),(lo,mid1),(mid1,mid2),(mid2,hi)]]
 pg('Sukar',pre+f'pasangan manakah yang memiliki selisih {"tahun" if time else "nilai"} paling besar?',pairs[0],pairs[1:])
 if time:
  good=' → '.join(rank);bad=[' → '.join([rank[j] for j in order]) for order in [(1,0,2,3),(0,2,1,3),(3,2,1,0)]];pg('Sukar',pre+'urutan kronologis yang benar dari awal hingga akhir adalah ....',good,bad)
 else:
  good=f'{hi} memiliki nilai tercatat lebih tinggi daripada {lo}.';bad=[f'{lo} memiliki nilai tertinggi.',f'{mid1} dan {mid2} memiliki nilai yang sama.','Gambar ini saja membuktikan penyebab seluruh perbedaan nilai.'];pg('Sukar',pre+'simpulan manakah yang didukung oleh data tanpa membuat klaim berlebihan?',good,bad)
 fill('Sedang',pre+f'tuliskan nilai angka untuk {lo} (tanpa satuan).',d[lo],[f'{d[lo]} {unit}'])
 delta=d[mid2]-d[mid1];fill('Sukar',pre+f'tuliskan selisih angka antara {mid1} dan {mid2} (tanpa satuan).',delta,[f'{delta} {unit}'])
assert len(bank)==1000 and len({q['soal'] for q in bank})<1000 # shared stems across visuals are valid when image differs
assert len({(q['soal'],q.get('gambar')) for q in bank})==1000,[(k,n) for k,n in collections.Counter((q['soal'],q.get('gambar')) for q in bank).items() if n>1]
assert collections.Counter(q['jenis'] for q in bank)=={'PG':800,'Isian':200}
assert sum('gambar' in q for q in bank)==200
(P/'bank_soal.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2))
(P/'gambar').mkdir(exist_ok=True)
for k,v in images.items():(P/'gambar'/f'{k}.png').write_bytes(base64.b64decode(v.split(',')[1]))
print('bank',collections.Counter((q['bab'],q['jenis']) for q in bank),'level',collections.Counter(q['level'] for q in bank),'visual',collections.Counter(q['jenis'] for q in bank if 'gambar'in q))
tpl=(P/'template.html').read_text();embed=tpl.replace('__BANK__',json.dumps(bank,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')).replace('__IMAGES__',json.dumps(images,separators=(',',':')))
(P/'BLOGGER_LANGSUNG.html').write_text(embed)
full='<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Prediksi SAS Ganjil IPAS Kelas VI SD/MI | Pendamping Akademik</title><meta name="description" content="Prediksi SAS Ganjil IPAS kelas 6 SD/MI: 1.000 soal, 40 soal acak, timer 90 menit, nilai dan pembahasan otomatis."><style>body{margin:0;padding:0 10px;background:#edf1ec}</style></head><body>'+embed+'</body></html>'
(P/'index.html').write_text(full)
# readable bank with all keys, explanations and local PNG assets
out=['<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Bank Soal SAS IPAS VI</title><style>body{max-width:960px;margin:30px auto;padding:12px;font:16px/1.6 Arial,sans-serif;color:#18352a}h1,h2{color:#103f32}article{border-bottom:1px solid #b5c7bb;padding:15px 0;break-inside:avoid}img{max-width:100%;height:auto}summary{cursor:pointer;color:#19765a}small{color:#52665b}nav a{margin-right:12px}</style></head><body><h1>Bank 1.000 Soal SAS Ganjil IPAS VI</h1><p>Pendamping Akademik. 800 PG dan 200 isian; 100 kelompok stimulus, masing-masing 10 variasi. Kunci dan pembahasan tersedia. Tingkat kesulitan merupakan estimasi penyusun.</p><nav><a href="#bab1">Bab 1</a><a href="#bab2">Bab 2</a><a href="#bab3">Bab 3</a></nav>']
for b in range(1,4):
 out.append(f'<h2 id="bab{b}">Bab {b}. {chap[b]}</h2>')
 for q in [x for x in bank if x['bab']==b]:
  out.append(f'<article><small>{q["id"]} | {q["jenis"]} | {q["level"]} | {q["sub"]}</small><p><b>{html.escape(q["soal"])}</b></p>')
  if q.get('gambar'):out.append(f'<img loading="lazy" src="gambar/{q["gambar"]}.png" alt="{html.escape(q["topik"])}">')
  if q['jenis']=='PG':out.append('<ol type="A">'+''.join('<li>'+html.escape(o)+'</li>' for o in q['opsi'])+'</ol>')
  out.append(f'<details><summary>Kunci dan pembahasan</summary><p><b>{html.escape(q["jawaban"])}</b></p><p>{html.escape(q["pembahasan"])}</p></details></article>')
out.append('</body></html>');(P/'BANK_SOAL_GURU.html').write_text(''.join(out))
