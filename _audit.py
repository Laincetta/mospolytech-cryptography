# -*- coding: utf-8 -*-
import glob, re, importlib.util, io, contextlib, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
PASS, FAIL = [], []
def chk(cond, msg):
    (PASS if cond else FAIL).append(msg)

def load(name, fn):
    s = importlib.util.spec_from_file_location(name, fn)
    m = importlib.util.module_from_spec(s)
    with contextlib.redirect_stdout(io.StringIO()):
        s.loader.exec_module(m)
    return m

# ─── 1. Структурные проверки всех .drawio ───────────────────────────────────
DUAL = {'atbash','sblock','hill','vertical','cardano','feistel','shannon',
        'gamma','a51','magma','kuznyechik','rsa','elgamal','gost2012'}
for f in sorted(glob.glob('*_diagram.drawio')):
    base = f.replace('_diagram.drawio','')
    t = open(f, encoding='utf-8').read()
    cells = re.findall(r'<mxCell id="([^"]+)" value="([^"]*)" style="([^"]*)" (vertex|edge)="1"', t)
    verts = [(i,v,s) for i,v,s,k in cells if k=='vertex']
    nach = sum(1 for _,v,s in verts if v=='начало')
    kon  = sum(1 for _,v,s in verts if v=='конец')
    titles = [v for _,v,s in verts if 'text;html' in s]
    if base in DUAL:
        chk(nach==2 and kon==2, f"{base}: 2x начало/конец (нашёл {nach}/{kon})")
        chk(len(titles)==2, f"{base}: 2 титула (нашёл {titles})")
    else:
        chk(nach==1 and kon==1, f"{base}: 1x начало/конец (нашёл {nach}/{kon})")
    loopend = [v for _,v,s in verts if 'loopLimit' in s and 'flipV=1' in s and v.strip()]
    chk(not loopend, f"{base}: закрывающие границы цикла пусты (нарушители {loopend})")
    node_ids = [i for i,v,s in verts if 'text;html' not in s]
    edges = re.findall(r'edge="1" parent="1" source="([^"]+)" target="([^"]+)"', t)
    used = set()
    for a,b in edges: used.add(a); used.add(b)
    orphan = [i for i in node_ids if i not in used]
    chk(not orphan, f"{base}: нет висячих узлов (висят {orphan})")

# ─── 2. Англицизмы ───────────────────────────────────────────────────────────
BAN = re.compile(r'импорт|hex|stop-and-go|rot11| XOR |\bencrypt|\bdecrypt', re.I)
for f in sorted(glob.glob('*_diagram.drawio')):
    txt = ' '.join(re.findall(r'value="([^"]*)"', open(f,encoding='utf-8').read()))
    hits = BAN.findall(txt)
    chk(not hits, f"{f.replace('_diagram.drawio','')}: без англицизмов ({hits})")

# ─── 3. Компиляция ───────────────────────────────────────────────────────────
import py_compile
LABS = ['lab1_atbash','lab2_s_block','lab3_matrix','lab4_cardano','lab4_feistel',
        'lab4_vertical','lab5_shanon','lab5_gamma','lab6_a5-1','lab7_kyznechik',
        'lab7_magma','lab8_rsa','lab8_elgamal','lab10_gost2012','lab11_diffie_hellman']
for l in LABS:
    try:
        py_compile.compile(l+'.py', doraise=True); chk(True, f"{l}: компиляция")
    except Exception as e:
        chk(False, f"{l}: компиляция — {e}")

# ─── 4. Round-trip тесты ─────────────────────────────────────────────────────
_real = sys.stdout
sys.stdout = io.StringIO()   # глушим возможный вывод модулей во время тестов
TXT = "плохой работник, никогда не находит хорошего инструмента."

a = load('atb','lab1_atbash.py')
chk(a.decrypt(a.encrypt(TXT)) == TXT, "Атбаш: round-trip")

v = load('vrt','lab4_vertical.py')
enc = v.vertical_permutation_logic(TXT,'КОД','encrypt')
dec = v.vertical_permutation_logic(enc,'КОД','decrypt')
chk(dec.upper() == v.restore_text(v.prepare_text(TXT)).upper(), "Вертикальная: round-trip")

sb = load('sb','lab2_s_block.py')
chk(all(sb.t_inv(sb.t(x))==x for x in [0,0x12345678,0xFFFFFFFF,0xDEADBEEF]), "S-блок: t_inv(t(x))=x")

import math as _m
eg = load('eg','lab8_elgamal.py')
p,g,x=37,2,5; y=pow(g,x,p); kl=[k for k in range(2,p-1) if _m.gcd(k,p-1)==1]
chk(eg.decrypt(eg.encrypt("привет",p,g,y,kl),p,x).upper()=="ПРИВЕТ","Эль-Гамаль: round-trip")

a51 = load('a51','lab6_a5-1.py')
key=0x0123456789ABCDEF
proc=a51.replace("текст,тест.")
bits=a51.text_to_bits(proc)
gam=a51.A5_1(key).get_keystream(len(bits))
encb=[bits[i]^gam[i] for i in range(len(bits))]
enc_txt=a51.bits_to_text(encb)
bits2=a51.text_to_bits(enc_txt)
gam2=a51.A5_1(key).get_keystream(len(bits2))
decb=[bits2[i]^gam2[i] for i in range(len(bits2))]
chk(a51.restore(a51.bits_to_text(decb))=="текст,тест.","A5/1: round-trip")

mg = load('mg','lab7_magma.py')
ci = mg.Magma(bytes.fromhex("ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"))
blk=bytes.fromhex("fedcba9876543210")
chk(ci.decrypt_block(ci.encrypt_block(blk))==blk, "Магма: round-trip блока")

kz = load('kz','lab7_kyznechik.py')
ck = kz.Kuznyechik(bytes.fromhex("8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef"))
b16=bytes.fromhex("1122334455667700ffeeddccbbaa9988")
chk(ck.decrypt_block(ck.encrypt_block(b16))==b16, "Кузнечик: round-trip блока")

fe = load('fe','lab4_feistel.py')
k=int("ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff",16)
rk=fe._key_schedule(k); rkd=fe._key_schedule_decrypt(k)
a1,a0=0xfedcba98,0x76543210
e1,e0=a1,a0
for i in range(31): e1,e0=fe.G(rk[i],e1,e0)
e1,e0=fe.G_star(rk[31],e1,e0)
d1,d0=e1,e0
for i in range(31): d1,d0=fe.G(rkd[i],d1,d0)
d1,d0=fe.G_star(rkd[31],d1,d0)
chk((d1,d0)==(a1,a0), "Фейстель: round-trip блока")

cd = load('cd','lab4_cardano.py')
dec_c = cd.decrypt(cd.encrypt("привет, мир."))
chk('.' in dec_c and ',' in dec_c and 'ТЧК' not in dec_c.upper() and 'ЗПТ' not in dec_c.upper(),
    "Кардано: знаки препинания восстановлены")

sh = load('sh','lab5_shanon.py')
chk(sh.restore(sh.replace("да, нет."))=="да, нет.", "Шеннон: replace/restore")
chk(sh.numbers_to_text(sh.text_to_numbers("абвя"))=="абвя", "Шеннон: буквы<->числа")

rs = load('rs','lab8_rsa.py')
chk(rs.restore(rs.replace("Да, нет."))=="ДА, НЕТ.", "RSA: replace/restore")

dh = load('dh','lab11_diffie_hellman.py')
YA,YB,Ka,Kb = dh.compute_keys(23,5,6,15)
chk(Ka==Kb, "Диффи-Хеллман: общий ключ совпадает")

# ─── 5. Официальные тест-векторы ГОСТ Р 34.12-2015 ───────────────────────────
chk(sb.t(0xfdb97531) == 0x2a196f34, "S-блок: тест-вектор t(fdb97531)=2a196f34")
_MK = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
ci2 = mg.Magma(bytes.fromhex(_MK))
chk(ci2.encrypt_block(bytes.fromhex("fedcba9876543210")).hex()=="4ee901e5c2d8ca3d",
    "Магма: тест-вектор ГОСТ (fedcba9876543210 -> 4ee901e5c2d8ca3d)")
k2=int(_MK,16); rk2=fe._key_schedule(k2)
f1,f0=0xfedcba98,0x76543210
for i in range(31): f1,f0=fe.G(rk2[i],f1,f0)
f1,f0=fe.G_star(rk2[31],f1,f0)
chk(((f1<<32)|f0)==0x4ee901e5c2d8ca3d, "Фейстель: тест-вектор ГОСТ (-> 4ee901e5c2d8ca3d)")

sys.stdout = _real
print(f"\n[ИТОГ] ПРОЙДЕНО: {len(PASS)}    ПРОВАЛЕНО: {len(FAIL)}")
for m in FAIL:
    print("  [FAIL]", m)
print("\nВсё чисто — несоответствий не найдено." if not FAIL else "\nЕСТЬ ЧТО ИСПРАВИТЬ")
