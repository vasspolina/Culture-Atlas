"""Step 1 of the sender view: what a funder gets for its money, one entry per funder, space and kind of influence.

Reads institutions.json and writes data/influence_candidates.json: every sentence in a record that names one of the pilot
funders below beside a sign of influence (a name, a seat, a sponsored programme, a cancellation, access, licence to operate,
tax), with the record field it came from, the sources attached to that field, and a date where the sentence or case gives one.
Nothing is fetched and no record is changed. A candidate is not a finding: data/influence_review.json keeps the editor's
verdict on each one (keep with its kinds and a one-line summary, or drop with the reason), and only kept entries reach
assets/influence.json, which the Influence mode layer reads. Run:

    python3 -I tools/build_influence.py            # rebuild candidates, then assets/influence.json from the review
"""
import json, os, re, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The pilot: private and corporate senders that appear in the most records, and the flagged ones the money maps already
# name. Public arts councils are left out on purpose: the question is what private money buys, and a public grant is
# accountable by other means. key = the funder key of assets/money-maps.json, so the layer can find the funder's record.
FUNDERS = [
    ('bp', 'BP', 'corp', r'\bBP\b|British Petroleum'),
    ('shell', 'Shell', 'corp', r'\bShell\b(?! ?fish)'),
    ('totalenergies', 'TotalEnergies', 'corp', r'TotalEnergies|\bTotal\b(?= (?:SA|S\.A\.|Foundation|Fondation|sponsor|oil|gas))|Fondation Total'),
    ('chevron', 'Chevron', 'corp', r'\bChevron\b'),
    ('equinor', 'Equinor', 'corp', r'\bEquinor\b|\bStatoil\b'),
    ('eni', 'Eni', 'corp', r'\bEni\b'),
    ('sacklerfamily', 'Sackler family', 'family', r'Sackler'),
    ('right:koch', 'Koch', 'family', r'\bKoch\b'),
    ('right:griffin', 'Ken Griffin / Citadel', 'family', r'\bGriffin\b|\bCitadel\b'),
    ('blavatnikfamily', 'Blavatnik Family Foundation', 'family', r'Blavatnik'),
    ('bloomberg', 'Bloomberg Philanthropies', 'family', r'Bloomberg'),   # a foundation, drawn as one; L.P. and Connects entries say so
    ('bankofamerica', 'Bank of America', 'corp', r'Bank of America'),
    ('jpmorganchase', 'JPMorganChase', 'corp', r'JPMorgan|J\.P\. Morgan|JP Morgan'),
    ('ubs', 'UBS', 'corp', r'\bUBS\b'),
    ('rbc', 'RBC', 'corp', r'\bRBC\b|Royal Bank of Canada'),
    ('bmo', 'BMO', 'corp', r'\bBMO\b|Bank of Montreal'),
    ('bailliegifford', 'Baillie Gifford', 'corp', r'Baillie Gifford'),
    ('bmw', 'BMW', 'corp', r'\bBMW\b'),
    ('hyundaimotor', 'Hyundai Motor', 'corp', r'Hyundai'),
    ('chanel', 'Chanel', 'corp', r'\bChanel\b'),
    ('jti', 'Japan Tobacco International', 'corp', r'Japan Tobacco|\bJTI\b'),
    ('philipmorris', 'Altria (Philip Morris USA)', 'corp', r'Philip Morris|Altria'),
    ('rheinmetall', 'Rheinmetall', 'corp', r'Rheinmetall'),
    ('leonardo', 'Leonardo', 'corp', r'\bLeonardo S\.?p\.?A|Leonardo \(defen'),
    ('glencore', 'Glencore', 'corp', r'Glencore'),
    ('riotinto', 'Rio Tinto', 'corp', r'Rio Tinto'),
    ('vale', 'Vale', 'corp', r'\bVale\b(?! of)'),
    ('lauder', 'Lauder family', 'family', r'\bLauder\b'),
    # Private money that is not a company's (user, 17 Nov 2026: "add private funders not only corporations, like hedge funds
    # etc"): hedge fund and private equity fortunes, given in a person's or a family's name, and the firms where a record ties
    # the firm itself. Then billionaires whose money the records tie to a space directly. 'fund' is a firm that manages others'
    # money; 'family' is a person's or a family's own money, however it was made.
    ('leonblack', 'Leon Black (Apollo)', 'family', r'Leon Black|Apollo Global|Apollo Management'),
    ('right:cohen', 'Steven Cohen (Point72)', 'family', r'Steven (?:A\. )?Cohen|Steve Cohen|Point72|SAC Capital'),
    ('right:mercer', 'Mercer family (Renaissance Technologies)', 'family', r'Rebekah Mercer|Robert Mercer|Mercer Family Foundation|Renaissance Technologies'),
    ('glenndubin', 'Glenn Dubin (Highbridge Capital)', 'family', r'Glenn Dubin|\bDubin\b(?= (?:famil|Foundation))|Highbridge Capital'),
    ('schwarzman', 'Stephen Schwarzman (Blackstone)', 'family', r'Schwarzman|\bBlackstone\b(?! ?(?:Valley|River|Hotel))'),
    ('paulsonfamily', 'John Paulson (Paulson & Co.)', 'family', r'John Paulson|Paulson Family Foundation|Paulson & Co'),
    ('opensociety', 'Soros family / Open Society Foundations', 'family', r'\bSoros\b|Open Society Foundations?'),
    ('kanderses', 'Warren Kanders', 'family', r'Kanders'),
    ('kkr', 'KKR and the Kravis family', 'fund', r'\bKKR\b|Kohlberg Kravis|Kravis'),
    ('blackrock', 'BlackRock', 'fund', r'BlackRock|Larry Fink'),
    ('wintoncapitalmanagement', 'David Harding (Winton)', 'family', r'Winton Capital|David Harding'),
    ('romanabramovich', 'Roman Abramovich', 'family', r'Abramovich'),
    ('vladimirpotanin', 'Vladimir Potanin', 'family', r'Potanin|Norilsk Nickel|Nornickel|Interros'),
    ('leonidmikhelsonvac', 'Leonid Mikhelson / V-A-C', 'family', r'Mikhelson|V-A-C Foundation|Novatek'),
    ('viktorvekselberg', 'Viktor Vekselberg', 'family', r'Vekselberg'),
    # Added for one tie (user, 17 Nov 2026: "add the Sony LACMA link"): the leaked Sony emails put its lobbying at LACMA.
    ('sonypictures', 'Sony Pictures Entertainment', 'corp', r'\bSony\b'),
    # Batch 5 (user, 17 Nov 2026: "add african or other not covered contryes sponsors to the influense map, do same
    # proffesional datat research"): private and listed money headquartered in Africa, and in the regions the first four
    # batches left out (Latin America, Turkey, the Gulf, South and Southeast Asia). Keys reuse assets/hq.json's office keys
    # where it has one. A state-controlled listed company (Petrobras, Aramco) is kept, as Equinor and Eni are; a state body,
    # a state airline or a multilateral bank (Afreximbank) is not, since the question is what private money buys.
    ('standardbank', 'Standard Bank', 'corp', r'Standard Bank|Stanbic'),
    ('angloamerican', 'Anglo American and De Beers', 'corp', r'Anglo American|De Beers|Debswana|DTC Botswana'),
    ('oppenheimer', 'Oppenheimer family', 'family', r'Oppenheimer'),
    ('ecobank', 'Ecobank', 'corp', r'Ecobank'),
    ('mtn', 'MTN Group', 'corp', r'\bMTN\b'),
    ('seplat', 'Seplat Energy', 'corp', r'Seplat'),
    ('lekoilnigeria', 'Lekoil', 'corp', r'Lekoil'),
    ('azurapower', 'Azura Power West Africa', 'corp', r'Azura Power'),
    ('accessbank', 'Access Bank', 'corp', r'Access Bank'),
    ('ihstowers', 'IHS Towers', 'corp', r'\bIHS\b'),
    ('africell', 'Africell', 'corp', r'Africell'),
    ('almada', 'Al Mada and Attijariwafa bank', 'corp', r'Al Mada|Attijariwafa'),
    ('kamellazaar', 'Kamel Lazaar (Swicorp)', 'family', r'Lazaar|Swicorp'),
    ('lazraq', 'Lazraq family (Alliances)', 'family', r'Lazraq|Fondation Alliances|Alliances Group|Groupe Alliances'),
    ('texaf', 'Texaf', 'corp', r'Texaf|TEXAF'),
    ('fnbfirstrand', 'FNB (FirstRand)', 'corp', r'\bFNB\b|FirstRand'),
    ('bankwindhoek', 'Bank Windhoek (Capricorn Group)', 'corp', r'Bank Windhoek'),
    ('sococimcement', 'Sococim (Vicat)', 'corp', r'Sococim|SOCOCIM'),
    ('isabeldossantos', 'Sindika Dokolo and Isabel dos Santos', 'family', r'Dokolo|Isabel dos Santos'),
    ('zinsou', 'Zinsou family', 'family', r'Zinsou'),
    ('norval', 'Norval family', 'family', r'Louis Norval|Norval Foundation|Norval family'),
    ('javett', 'Javett family', 'family', r'Javett'),
    ('kirsh', 'Kirsh family', 'family', r'Kirsh'),
    ('shyllon', 'Yemisi Shyllon', 'family', r'Shyllon'),
    ('oyebode', 'Aisha and Gbenga Oyebode', 'family', r'Oyebode'),
    ('hiridjee', 'Hiridjee family (Axian)', 'family', r'Hiridjee|Axian'),
    ('nesr', 'Nesr family (Webcor)', 'family', r'\bNesr\b|Webcor'),
    ('ita', 'Itaú', 'corp', r'Itaú|\bItau\b'),
    ('bradesco', 'Bradesco', 'corp', r'Bradesco'),
    ('petrobras', 'Petrobras', 'corp', r'Petrobras'),
    ('corporateartcollectionoffemsa', 'FEMSA', 'corp', r'FEMSA|Femsa'),
    ('fundacinjumexgrants', 'Jumex (the López family)', 'family', r'Jumex'),
    ('carlosslim', 'Carlos Slim (Grupo Carso)', 'family', r'Carlos Slim|Grupo Carso|Telmex|\bSlim\b(?= (?:famil|Foundation|Helú))'),
    ('bancolombia', 'Bancolombia', 'corp', r'Bancolombia'),
    ('sura', 'Grupo SURA', 'corp', r'Grupo SURA|Grupo Sura|\bSura\b|\bSURA\b'),
    ('fortabat', 'Fortabat family (Loma Negra)', 'family', r'Fortabat|Loma Negra'),
    ('fundacincostantini', 'Eduardo Costantini', 'family', r'Costantini'),
    ('itsincludesoilrefinertpra', 'Koç family (Koç Holding)', 'family', r'Koç|Koc Holding|\bKoc\b'),
    ('eczacibasi', 'Eczacıbaşı family', 'family', r'Eczac[ıi]ba[şs][ıi]'),
    ('sabanci', 'Sabancı family', 'family', r'Sabanc[ıi]'),
    ('borusan', 'Borusan (Kocabıyık family)', 'family', r'Borusan|Kocab[ıi]y[ıi]k'),
    ('jameel', 'Jameel family (Abdul Latif Jameel)', 'family', r'Jameel'),
    ('alserkal', 'Alserkal family', 'family', r'Alserkal'),
    ('aramco', 'Saudi Aramco', 'corp', r'Aramco'),
    ('tata', 'Tata', 'corp', r'\bTata\b|\bTCS\b'),
    ('reliance', 'Reliance (Ambani family)', 'family', r'Reliance (?:Industries|Foundation)|Ambani'),
    ('nadar', 'Shiv and Kiran Nadar (HCL)', 'family', r"Kiran Nadar|Shiv Nadar|Roshni Nadar|\bHCL\b|\bNadar's"),
    ('adani', 'Adani Group', 'corp', r'Adani'),
    ('ayalapresentsshows', 'Ayala Corporation', 'corp', r'Ayala (?:Corporation|Foundation|Land|Museum|family)|Zobel de Ayala'),
    ('thaibev', 'ThaiBev (Sirivadhanabhakdi family)', 'family', r'ThaiBev|Thai Beverage|Sirivadhanabhakdi'),
    ('cpgroup', 'Chearavanont family (CP Group)', 'family', r'Charoen Pokphand|\bCP Group|Chearavanont'),
    # Batch 6 (user, 17 Nov 2026: "also add south korea and japan sponsors", "add nrth korea sponsors", "add russian
    # sponsors", "add ukranian sponsors"). North Korea's spaces are paid by the party and the state, so its senders here are
    # the private money the records tie to its venues (a client of a state studio, the airline that flew an orchestra in).
    # Russia adds the state-controlled listed companies and banks (as Gazprom's peers Equinor and Aramco are kept) and the
    # private fortunes beyond the four already read; Rostec and Rosatom, state corporations, are left out as public bodies.
    ('samsung', 'Samsung (Lee family)', 'corp', r'Samsung|Leeum|Lee Kun-hee|Hong Ra-hee'),
    ('lg', 'LG', 'corp', r'\bLG\b'),
    ('skgroup', 'SK Group', 'corp', r'\bSK (?:Group|Telecom|Innovation|Holdings)|Art Center Nabi|Chey Tae-won|Roh Soh-yeong'),
    ('amorepacific', 'Amorepacific', 'corp', r'Amorepacific|AmorePacific'),
    ('hanwha', 'Hanwha', 'corp', r'Hanwha'),
    ('shinsegae', 'Shinsegae', 'corp', r'Shinsegae'),
    ('kumhoasiana', 'Kumho Asiana Group', 'corp', r'Kumho'),
    ('benesse', 'Benesse (Fukutake family)', 'family', r'Benesse|Fukutake'),
    ('moribuilding', 'Mori Building', 'corp', r'Mori Building|Minoru Mori|Yoshiko Mori'),
    ('fastretailing', 'Uniqlo (Fast Retailing)', 'corp', r'Uniqlo|UNIQLO|Fast Retailing|Tadashi Yanai'),
    ('suntory', 'Suntory', 'corp', r'Suntory'),
    ('pola', 'Pola Orbis (Suzuki family)', 'corp', r'\bPola\b|\bPOLA\b'),
    ('ishibashi', 'Bridgestone and the Ishibashi Foundation', 'family', r'Bridgestone|Ishibashi'),
    ('mitsubishi', 'Mitsubishi', 'corp', r'Mitsubishi'),
    ('mitsui', 'Mitsui', 'corp', r'Mitsui'),
    ('panasonic', 'Panasonic', 'corp', r'Panasonic'),
    ('toyota', 'Toyota', 'corp', r'Toyota'),
    ('canon', 'Canon', 'corp', r'\bCanon\b'),
    ('asahi', 'Asahi', 'corp', r'Asahi'),
    ('obayashi', 'Obayashi', 'corp', r'Obayashi'),
    ('kajima', 'Kajima', 'corp', r'Kajima'),
    ('takenaka', 'Takenaka', 'corp', r'Takenaka'),
    ('tepco', 'TEPCO', 'corp', r'TEPCO|Tokyo Electric'),
    ('kao', 'Kao', 'corp', r'\bKao\b'),
    ('shiseido', 'Shiseido', 'corp', r'Shiseido'),
    ('mizuho', 'Mizuho', 'corp', r'Mizuho'),
    ('nomura', 'Nomura', 'corp', r'Nomura'),
    ('nipponfoundation', 'Nippon Foundation (Sasakawa)', 'family', r'Nippon Foundation|Sasakawa'),
    ('mondotv', 'Mondo TV', 'corp', r'Mondo TV'),
    ('yokonagaeceschina', 'Yoko Nagae Ceschina', 'family', r'Ceschina'),
    ('gazprom', 'Gazprom', 'corp', r'Gazprom(?!bank)'),
    ('gazprombank', 'Gazprombank', 'corp', r'Gazprombank|Belgazprombank'),
    ('sberbank', 'Sberbank', 'corp', r'Sberbank|\bSber\b'),
    ('vtb', 'VTB', 'corp', r'\bVTB\b'),
    ('rosneft', 'Rosneft', 'corp', r'Rosneft|Sechin'),
    ('lukoil', 'Lukoil', 'corp', r'Lukoil|LUKOIL|Alekperov'),
    ('promsvyazbank', 'Promsvyazbank (PSB)', 'corp', r'Promsvyazbank|\bPSB\b|Ananiev'),
    ('usmanov', 'Alisher Usmanov', 'family', r'Usmanov|Metalloinvest'),
    ('alfagroup', 'Alfa Group (Fridman and Aven)', 'family', r'Fridman|Alfa-Bank|Alfa Bank|Alfa Group|Aven\b'),
    ('prokhorov', 'Mikhail Prokhorov', 'family', r'Prokhorov'),
    ('mordashov', 'Alexei Mordashov (Severstal)', 'family', r'Mordashov|Severstal'),
    ('timchenko', 'Gennady Timchenko', 'family', r'Timchenko'),
    ('yandex', 'Yandex', 'corp', r'Yandex'),
    ('borismints', 'Boris Mints', 'family', r'Boris Mints|\bMints\b'),
    ('pinchuk', 'Victor Pinchuk', 'family', r'Pinchuk|Interpipe|EastOne'),
    ('mykhaylova', 'Liubov Mykhaylova', 'family', r'Mykhaylova|Mykhailova'),
    # Batch 7 (user, 17 Nov 2026: "add chinese sponsors"): private and listed money from mainland China, Hong Kong and
    # Macau. Most of China's spaces in the atlas are party or state museums with no sender; what is left are collectors'
    # and developers' museums, and companies abroad. State-owned enterprises (CNPC, Bank of China, OCT) are kept as listed
    # or commercial companies, as Aramco and Gazprom are; ministries, city bureaus and the West Bund Group's park are not.
    ('liuyiqian', 'Liu Yiqian and Wang Wei (Long Museum)', 'family', r'Liu Yiqian|Wang Wei\b|Sunline'),
    ('buditek', 'Budi Tek (Yuz Foundation)', 'family', r'Budi Tek|\bYuz Foundation'),
    ('pingan', 'Ping An', 'corp', r'Ping An'),
    ('wanda', 'Dalian Wanda (Wang Jianlin)', 'corp', r'\bWanda\b|Wang Jianlin'),
    ('bytedance', 'ByteDance (TikTok)', 'corp', r'ByteDance|TikTok|Douyin'),
    ('cnpc', 'CNPC (PetroChina)', 'corp', r'PetroChina|\bCNPC\b'),
    ('bankofchina', 'Bank of China', 'corp', r'Bank of China'),
    ('octgroup', 'OCT Group', 'corp', r'\bOCT\b|Overseas Chinese Town'),
    ('minsheng', 'Ningxia Minsheng Real Estate', 'corp', r'Minsheng'),
    ('timeschina', 'Times China', 'corp', r'Times China|Times Property'),
    ('qiaozhibing', 'Qiao Zhibing', 'family', r'Qiao Zhibing'),
    ('midea', 'He family (Midea)', 'family', r'Midea|He Xiangjian|He Jianfeng'),
    ('aranya', 'Aranya', 'corp', r'Aranya'),
    ('yanshijie', 'Yan Shijie and Cao Mei', 'family', r'Yan Shijie|Cao Mei'),
    ('zhenghao', 'Zheng Hao (Onehome)', 'family', r'Zheng Hao|Onehome'),
    ('byd', 'BYD (Denza)', 'corp', r'Denza|\bBYD\b'),
    ('langhamhotels', 'Great Eagle (Langham Hospitality)', 'corp', r'Langham|Great Eagle'),
    ('swire', 'Swire', 'corp', r'Swire'),
    ('jardine', 'Jardine Matheson', 'corp', r'Jardine'),
    ('nanfung', 'Nan Fung Group (Chen family)', 'family', r'Nan Fung|Vanessa Cheung|Mill6|D\. ?H\. Chen'),
    ('anta', 'Anta Sports', 'corp', r'\bAnta\b'),
    # Batch 8 (user, 17 Nov 2026: "add taiwan sponsors too"): Taiwan's bank and family foundations and its companies.
    # Epson, a Japanese company, is read here with MOCA Taipei's other sponsors. Applied Materials (US) and Thermos are
    # left out: the countries they answer to are already in the map.
    ('ctbc', 'CTBC (Koo family)', 'corp', r'CTBC|Chinatrust'),
    ('esun', 'E.SUN Financial', 'corp', r'E\.SUN|E\.Sun'),
    ('kingstownbank', "King's Town Bank", 'corp', r"King's Town"),
    ('taishin', 'Taishin Financial', 'corp', r'Taishin'),
    ('chewsculture', "Chew's Culture Foundation (Hong Gah)", 'family', r"Chew's|Chew Culture"),
    ('royalinn', 'Royal Inn', 'corp', r'Royal Inn'),
    ('epson', 'Epson', 'corp', r'Epson'),
    # HSBC (user, 17 Nov 2026: "add hsbc too"): founded in Hong Kong and Shanghai in 1865, head office in London since 1993.
    ('hsbc', 'HSBC', 'corp', r'HSBC|Hongkong and Shanghai Bank'),
    # India beyond the first four (user, 17 Nov 2026: "add indian sponsors too"): the industrial families and companies the
    # records name as donors, building donors and festival founders.
    ('bajaj', 'Bajaj family (Jamnalal Bajaj Foundation)', 'family', r'Bajaj'),
    ('munjal', 'Munjal family (Hero)', 'family', r'Munjal|Hero (?:Enterprise|MotoCorp|Insurance|Realty|Group)'),
    ('poddar', 'Abhishek Poddar', 'family', r'Abhishek Poddar|\bPoddar\b'),
    ('jindal', 'Jindal family (JSW)', 'family', r'Jindal|\bJSW\b'),
    ('piramal', 'Piramal family', 'family', r'Piramal'),
    ('godrej', 'Godrej', 'corp', r'Godrej'),
    ('hdfc', 'HDFC Bank', 'corp', r'HDFC'),
    ('infosys', 'Infosys (Murty and Nilekani families)', 'corp', r'Infosys|Murty|Nilekani'),
    ('wipro', 'Azim Premji (Wipro)', 'family', r'Wipro|Premji'),
    ('mittal', 'Lakshmi Mittal (ArcelorMittal)', 'family', r'Lakshmi (?:N\. )?Mittal|ArcelorMittal|\bMittal\b'),
    ('bharti', 'Bharti family (Airtel)', 'family', r'Bharti|Airtel'),
    ('biocon', 'Kiran Mazumdar-Shaw (Biocon)', 'family', r'Mazumdar|Biocon'),
    ('mphasis', 'Mphasis', 'corp', r'Mphasis'),
    ('apeejay', 'Apeejay (Paul family)', 'family', r'Apeejay'),
    ('tvs', 'TVS', 'corp', r'\bTVS\b'),
    # Europe beyond the first batches (user, 17 Nov 2026: "add european sponsors too"): the European companies, banks and
    # family fortunes the records name at three or more spaces. Auction houses and audit firms are left out: a sale or an
    # audit is a fee for a service, not a gift. Keys reuse assets/hq.json's office keys where it has one.
    ('rothschild', 'Rothschild family', 'family', r'Rothschild'),
    ('mercedesbenz', 'Mercedes-Benz', 'corp', r'Mercedes|Daimler'),
    ('roche', 'Roche (Hoffmann and Oeri families)', 'corp', r'\bRoche\b(?! [A-Z][a-z]+ (?:Bobois))|Hoffmann-La Roche'),
    ('novartis', 'Novartis', 'corp', r'Novartis'),
    ('bbva', 'BBVA', 'corp', r'\bBBVA\b'),
    ('volkswagen', 'Volkswagen Group (Audi, Porsche)', 'corp', r'Volkswagen|\bVW\b|\bAudi\b|\bPorsche\b'),
    ('deutschebank', 'Deutsche Bank', 'corp', r'Deutsche Bank'),
    ('orange', 'Orange', 'corp', r'\bOrange\b(?= (?:S\.A\.|SA|Foundation|Fondation|Group|Telecom|Mali|Côte|Senegal|Sénégal|Cameroun|RDC|Belgium|Polska|Moldova)|,? the (?:French )?tele)|Fondation Orange'),
    ('dnb', 'DNB and Sparebankstiftelsen DNB', 'corp', r'\bDNB\b'),
    ('bnpparibas', 'BNP Paribas', 'corp', r'BNP Paribas|\bBNP\b'),
    ('intesasanpaolo', 'Intesa Sanpaolo', 'corp', r'Intesa Sanpaolo|Gallerie d.Italia(?= .*Intesa)'),
    ('unicredit', 'UniCredit', 'corp', r'UniCredit|Bank Austria'),
    ('generali', 'Generali', 'corp', r'Generali\b'),
    ('bosch', 'Bosch', 'corp', r'\bBosch\b(?! (?:Bild|museum))'),
    ('siemens', 'Siemens', 'corp', r'Siemens'),
    ('henkel', 'Henkel', 'corp', r'Henkel'),
    ('allianz', 'Allianz', 'corp', r'Allianz'),
    ('bayer', 'Bayer', 'corp', r'\bBayer\b(?! (?:Leverkusen|family))'),
    ('eon', 'E.ON', 'corp', r'\bE\.ON\b'),
    ('carlsberg', 'Carlsberg and its foundations', 'corp', r'Carlsberg'),
    ('novonordisk', 'Novo Nordisk and its foundation', 'corp', r'Novo Nordisk'),
    ('telefonica', 'Telefónica', 'corp', r'Telef[óo]nica'),
    ('lacaixa', '"la Caixa" Foundation (CaixaBank)', 'corp', r'la Caixa|CaixaBank|CaixaForum'),
    ('santander', 'Santander (Botín family)', 'corp', r'Banco Santander|Santander (?:Bank|Group|UK|Foundation)|Fundación Banco Santander|\bBotín\b'),
    ('iberdrola', 'Iberdrola', 'corp', r'Iberdrola'),
    ('repsol', 'Repsol', 'corp', r'Repsol'),
    ('mapfre', 'Mapfre', 'corp', r'Mapfre|MAPFRE'),
    ('engie', 'Engie', 'corp', r'\bEngie\b|\bENGIE\b'),
    ('axa', 'AXA', 'corp', r'\bAXA\b'),
    ('socgen', 'Société Générale', 'corp', r'Société Générale|Societe Generale'),
    ('creditagricole', 'Crédit Agricole', 'corp', r'Crédit Agricole|Credit Agricole'),
    ('vinci', 'Vinci', 'corp', r'\bVinci\b(?! (?:Code))|\bVINCI\b'),
    ('bouygues', 'Bouygues', 'corp', r'Bouygues'),
    ('saintgobain', 'Saint-Gobain', 'corp', r'Saint-Gobain'),
    ('lvmhlouisvuitton', 'LVMH (Arnault family)', 'corp', r'LVMH|Louis Vuitton|\bDior\b|Bulgari|Bvlgari|Arnault'),
    ('kering', 'Kering (Pinault family)', 'corp', r'Kering|\bGucci\b|Pinault|Artémis|Bottega Veneta|Saint Laurent(?= (?:Rive|Paris|sponsor))'),
    ('hermes', 'Hermès', 'corp', r'Hermès|Fondation d.entreprise Herm'),
    ('cartier', 'Cartier (Richemont)', 'corp', r'Cartier|Richemont'),
    ('pernodricard', 'Pernod Ricard', 'corp', r'Pernod|Ricard\b'),
    ('prada', 'Prada', 'corp', r'\bPrada\b'),
    ('lavazza', 'Lavazza', 'corp', r'Lavazza'),
    ('enel', 'Enel', 'corp', r'\bEnel\b'),
    ('erstebank', 'Erste Group and ERSTE Foundation', 'corp', r'\bErste\b|\bERSTE\b'),
    ('raiffeisen', 'Raiffeisen banks (Swiss and Austrian groups)', 'corp', r'Raiffeisen'),
    ('omv', 'OMV', 'corp', r'\bOMV\b'),
    ('swarovski', 'Swarovski', 'corp', r'Swarovski'),
    ('rabobank', 'Rabobank', 'corp', r'Rabobank'),
    ('ing', 'ING', 'corp', r'\bING\b(?= (?:Bank|Group|Groep|Belgi|Nederland|Art|Collection|Discerning)|,|\.| sponsor| is | was )'),
    ('abnamro', 'ABN AMRO', 'corp', r'ABN AMRO|ABN Amro'),
    ('nordea', 'Nordea', 'corp', r'Nordea'),
    ('ikea', 'IKEA (Kamprad family)', 'corp', r'IKEA|Ikea|Kamprad'),
    ('barclays', 'Barclays', 'corp', r'Barclays'),
    ('baesystems', 'BAE Systems', 'corp', r'BAE Systems'),
    ('sainsbury', 'Sainsbury family', 'family', r'Sainsbury'),
    ('pictet', 'Pictet', 'corp', r'Pictet'),
    ('juliusbaer', 'Julius Baer', 'corp', r'Julius B[aä]er'),
    ('wurth', 'Würth (Reinhold Würth)', 'family', r'Würth|Wurth'),
    ('vitra', 'Vitra (Fehlbaum family)', 'family', r'\bVitra\b|Fehlbaum'),
    ('klm', 'Air France-KLM', 'corp', r'\bKLM\b|Air France'),
    # The United States beyond the first batches (user, 17 Nov 2026: "add us sponsors too"): the large private foundations,
    # whose money is old industrial fortunes (Mellon banking and oil, Ford, Getty oil, Rockefeller oil), the companies, and
    # the billionaire families the records tie to spaces. Elected officials acting in office are left out: the question is
    # what private money buys. Keys reuse assets/hq.json's office keys where it has one.
    ('mellon', 'Mellon (the Mellon Foundation and the Mellon family funds)', 'family', r'Mellon'),
    ('andywarhol', 'Andy Warhol Foundation', 'family', r'Warhol Foundation|Andy Warhol Foundation'),
    ('ford', 'Ford Foundation and Ford Motor', 'family', r'Ford Foundation|Ford Motor|Ford Fund'),
    ('getty', 'Getty (J. Paul Getty Trust and the Getty family)', 'family', r'\bGetty\b(?! Images)'),
    ('rockefellerbrothers', 'Rockefeller family and foundations', 'family', r'Rockefeller'),
    ('luce', 'Henry Luce Foundation', 'family', r'Luce Foundation|Henry Luce'),
    ('terra', 'Terra Foundation for American Art', 'family', r'Terra Foundation'),
    ('waltonfamily', 'Walton family (Walmart)', 'family', r'Walton (?:Family|family)|Alice Walton|Walmart|Crystal Bridges'),
    ('pritzkerfamily', 'Pritzker family (Hyatt)', 'family', r'Pritzker|\bHyatt\b'),
    ('broad', 'Eli and Edythe Broad', 'family', r'Eli Broad|Edythe Broad|Broad Foundation|The Broad\b'),
    ('tisch', 'Tisch family (Loews)', 'family', r'Tisch|\bLoews\b'),
    ('annenberg', 'Annenberg family and foundation', 'family', r'Annenberg'),
    ('geffen', 'David Geffen', 'family', r'Geffen'),
    ('wexner', 'Les Wexner (L Brands)', 'family', r'Wexner'),
    ('perelman', 'Ronald Perelman (MacAndrews & Forbes)', 'family', r'Perelman'),
    ('adelson', 'Adelson family (Las Vegas Sands)', 'family', r'Adelson|Las Vegas Sands'),
    ('murdoch', 'Murdoch family (News Corp, Fox)', 'family', r'Murdoch|News Corp|Fox Corporation'),
    ('crownfamily', 'Crown family (Henry Crown and Company)', 'family', r'Crown family|Henry Crown'),
    ('ericschmidt', 'Eric and Wendy Schmidt', 'family', r'Eric Schmidt|Wendy Schmidt|Schmidt Futures|Schmidt Family Foundation'),
    ('lucas', 'George Lucas and Mellody Hobson', 'family', r'George Lucas|Lucas Museum|Mellody Hobson'),
    ('bezos', 'Jeff Bezos and Amazon', 'family', r'Bezos|\bAmazon\b(?! (?:rainforest|basin|River))'),
    ('gates', 'Bill Gates and Microsoft', 'family', r'Bill Gates|Gates Foundation|Microsoft'),
    ('zuckerberg', 'Meta (Zuckerberg)', 'corp', r'\bMeta\b(?= (?:Platforms|Open Arts|sponsor|funded|paid))|Facebook|Instagram|Zuckerberg'),
    ('google', 'Google (Alphabet)', 'corp', r'Google|Alphabet Inc'),
    ('apple', 'Apple', 'corp', r'\bApple\b(?= (?:Inc|sponsor|Music|TV|Store|funded|paid|partner)|,? the tech)'),
    ('netflix', 'Netflix', 'corp', r'Netflix'),
    ('disney', 'Disney (the company and the Disney family)', 'corp', r'Disney'),
    ('dell', 'Michael Dell', 'family', r'Michael Dell|Dell Foundation|Dell Technologies'),
    ('hearst', 'Hearst', 'corp', r'Hearst'),
    ('americanexpress', 'American Express', 'corp', r'American Express|\bAmex\b'),
    ('mastercard', 'Mastercard', 'corp', r'Mastercard|MasterCard'),
    ('citi', 'Citi', 'corp', r'\bCiti\b(?! FM)|Citigroup|Citibank'),
    ('morganstanley', 'Morgan Stanley', 'corp', r'Morgan Stanley'),
    ('goldmansachs', 'Goldman Sachs', 'corp', r'Goldman Sachs'),
    ('northerntrust', 'Northern Trust', 'corp', r'Northern Trust'),
    ('wellsfargo', 'Wells Fargo', 'corp', r'Wells Fargo'),
    ('fidelity', 'Fidelity (Johnson family)', 'family', r'Fidelity (?:Investments|Foundation|UK Foundation|International)|Abigail Johnson'),
    ('cocacola', 'Coca-Cola', 'corp', r'Coca-Cola'),
    ('nike', 'Nike', 'corp', r'\bNike\b'),
    ('levistrauss', 'Levi Strauss & Co.', 'corp', r'Levi Strauss|Levi\'s'),
    ('delta', 'Delta Air Lines', 'corp', r'Delta Air'),
    ('boeing', 'Boeing', 'corp', r'Boeing'),
    ('lockheedmartin', 'Lockheed Martin', 'corp', r'Lockheed'),
    ('exxonmobil', 'ExxonMobil', 'corp', r'ExxonMobil|Exxon|Mobil\b'),
    ('conocophillips', 'ConocoPhillips', 'corp', r'ConocoPhillips'),
    ('occidental', 'Occidental Petroleum', 'corp', r'Occidental Petroleum|\bOxy\b'),
    ('schlumberger', 'Schlumberger (SLB) and the de Menil family', 'family', r'Schlumberger|\bSLB\b|de Menil|Menil Foundation'),
    ('wynn', 'Wynn Resorts (Steve Wynn)', 'corp', r'\bWynn\b'),
    ('heinz', 'Heinz family and endowments', 'family', r'Heinz'),
    ('merck', 'Merck & Co.', 'corp', r'Merck'),
    ('pfizer', 'Pfizer', 'corp', r'Pfizer'),
    ('ibm', 'IBM', 'corp', r'\bIBM\b'),
    ('caterpillar', 'Caterpillar', 'corp', r'Caterpillar Inc|Caterpillar Foundation'),
    ('moody', 'Moody Foundation', 'family', r'Moody Foundation'),
    ('nasher', 'Nasher family', 'family', r'Nasher'),
    ('millennium', 'Izzy Englander (Millennium Management)', 'family', r'Millennium Management|Englander'),
    # Australia (user, 17 Nov 2026: "add australian sponsors too"): mining and gas money, the banks, and the family
    # foundations the records tie to spaces. Murdoch is read with the US funders, Rio Tinto in the first batch.
    ('ianpotter', 'Ian Potter Foundation', 'family', r'Ian Potter|Potter Foundation'),
    ('gordondarling', 'Gordon Darling Foundation', 'family', r'Gordon Darling'),
    ('myer', 'Myer family (Sidney Myer Fund, Myer Foundation)', 'family', r'Sidney Myer|Myer Foundation|Myer Fund|\bMyer family'),
    ('gandel', 'Gandel family (Gandel Foundation)', 'family', r'Gandel'),
    ('belgiorno', 'Belgiorno-Nettis family (Transfield)', 'family', r'Belgiorno|Transfield'),
    ('neilson', 'Neilson Foundation (Kerr Neilson, Platinum)', 'family', r'Neilson Foundation|Kerr Neilson|Judith Neilson'),
    ('wesfarmers', 'Wesfarmers', 'corp', r'Wesfarmers'),
    ('qantas', 'Qantas', 'corp', r'Qantas'),
    ('inpex', 'Inpex', 'corp', r'\bInpex\b|\bINPEX\b'),
    ('south32', 'South32', 'corp', r'South32'),
    ('bhp', 'BHP', 'corp', r'\bBHP\b'),
    ('ampol', 'Ampol (Caltex Australia)', 'corp', r'Ampol|Caltex'),
    ('minderoo', 'Andrew and Nicola Forrest (Minderoo, Fortescue)', 'family', r'Minderoo|Fortescue|Andrew Forrest|Twiggy'),
    ('telstra', 'Telstra', 'corp', r'Telstra'),
    ('anz', 'ANZ', 'corp', r'\bANZ\b'),
    ('westpac', 'Westpac', 'corp', r'Westpac'),
    ('macquarie', 'Macquarie Group', 'corp', r'Macquarie (?:Group|Bank|Foundation)|Macquarie\b(?= (?:sponsor|is|was))'),
    ('nab', 'National Australia Bank', 'corp', r'\bNAB\b|National Australia Bank'),
    ('commbank', 'Commonwealth Bank', 'corp', r'Commonwealth Bank|CommBank'),
    ('lendlease', 'Lendlease', 'corp', r'Lendlease|Lend Lease'),
    ('mirvac', 'Mirvac', 'corp', r'Mirvac'),
    ('stockland', 'Stockland', 'corp', r'Stockland'),
    ('crownresorts', 'Crown Resorts (Packer family)', 'corp', r'Crown Resorts|James Packer|Packer family|Packer Family Foundation'),
    ('kerrystokes', 'Kerry Stokes (Seven Group)', 'family', r'Kerry Stokes|Seven Group'),
    ('besen', 'Besen family (Sussan)', 'family', r'Besen'),
    ('balnaves', 'Balnaves Foundation', 'family', r'Balnaves'),
    ('mordant', 'Simon Mordant', 'family', r'Mordant'),
    ('timfairfax', 'Tim Fairfax', 'family', r'Tim Fairfax'),
    ('canva', 'Canva', 'corp', r'\bCanva\b'),
    ('perpetual', 'Perpetual (trustee of charitable trusts)', 'corp', r'Perpetual (?:Limited|Trustee|Foundation|IMPACT)|\bPerpetual\b(?= (?:trust|grant))'),
    # Canada beyond RBC and BMO (user, 17 Nov 2026: "add canadian sponsors too"): the banks, the oil sands and mining
    # companies, and the family fortunes. Hydro-Québec, a state-owned utility, is kept as a company, as Equinor is; the
    # Caisse de dépôt, a public pension fund, is not. The Garfield Weston Foundation is the British arm of the Weston family.
    ('tdbank', 'TD Bank Group', 'corp', r'TD Bank|TD Ready|Toronto-Dominion|\bTD\b(?= (?:Securities|Asset|Wealth|Canada Trust|sponsor|is|was|Bank|Ready|Insurance))'),
    ('scotiabank', 'Scotiabank', 'corp', r'Scotiabank|Bank of Nova Scotia'),
    ('cibc', 'CIBC', 'corp', r'\bCIBC\b'),
    ('nationalbankcanada', 'National Bank of Canada', 'corp', r'Banque Nationale|National Bank of Canada|National Bank Financial'),
    ('desjardins', 'Desjardins Group', 'corp', r'Desjardins'),
    ('powercorp', 'Power Corporation (Desmarais family)', 'family', r'Power Corporation|Desmarais'),
    ('thomson', 'Thomson family (Woodbridge, Thomson Reuters)', 'family', r'Ken Thomson|Kenneth Thomson|David Thomson|Thomson family|Thomson Reuters|Woodbridge Company'),
    ('audain', 'Michael Audain (Polygon Homes)', 'family', r'Audain|Polygon Homes'),
    ('rogers', 'Rogers family (Rogers Communications)', 'family', r'Rogers Communications|Rogers Foundation|Ted Rogers|Rogers family|Rogers Sports'),
    ('hydroquebec', 'Hydro-Québec', 'corp', r'Hydro-Qu[ée]bec'),
    ('sobey', 'Sobey family (Empire, Sobeys)', 'family', r'Sobey'),
    ('bronfman', 'Bronfman family (Seagram)', 'family', r'Bronfman|Seagram'),
    ('aircanada', 'Air Canada', 'corp', r'Air Canada'),
    ('garfieldweston', 'Weston family (Garfield Weston Foundation, Loblaw)', 'family', r'Garfield Weston|Weston Family Foundation|Loblaw|George Weston'),
    ('molson', 'Molson family', 'family', r'Molson'),
    ('lassonde', 'Lassonde family', 'family', r'Lassonde'),
    ('teck', 'Teck Resources', 'corp', r'\bTeck\b'),
    ('imperialoil', 'Imperial Oil', 'corp', r'Imperial Oil'),
    ('cenovus', 'Cenovus Energy (with Husky)', 'corp', r'Cenovus|Husky Energy|\bHusky\b(?= (?:Oil|sponsor))'),
    ('suncor', 'Suncor', 'corp', r'Suncor|Petro-Canada'),
    ('enbridge', 'Enbridge', 'corp', r'Enbridge'),
    ('remai', 'Frank and Ellen Remai', 'family', r'Remai(?! Modern)|Ellen Remai|Frank and Ellen Remai'),
    ('jackman', 'Jackman family', 'family', r'Jackman'),
    ('bombardier', 'Bombardier (Beaudoin-Bombardier family)', 'family', r'Bombardier'),
    ('cpkc', 'Canadian Pacific', 'corp', r'Canadian Pacific'),
    ('barrick', 'Barrick Gold', 'corp', r'Barrick'),
    ('leechin', 'Michael Lee-Chin (Portland Holdings)', 'family', r'Lee-Chin'),
    ('bellcanada', 'BCE (Bell Canada)', 'corp', r'Bell Canada|Bell Media|\bBCE Inc'),
    # New Zealand (user, 17 Nov 2026: "add new zealand sponsors too"): the trusts, firms and families on its galleries'
    # partner lists. The gaming-machine trusts (Pub Charity, Lion Foundation, NZCT) give pokie money and are kept as
    # gambling money; Lotto NZ, a Crown entity, is not. Methanex (Vancouver) is read here for its one tie, at Bocas Lit Fest.
    ('chartwelltrust', 'Chartwell Trust (Gibson family)', 'family', r'Chartwell Trust|Chartwell Charitable'),
    ('mackelvie', 'Mackelvie Trust', 'family', r'Mackelvie'),
    ('anthonyharper', 'Anthony Harper (law firm)', 'corp', r'Anthony Harper'),
    ('jbwere', 'JBWere', 'corp', r'JBWere'),
    ('craigsinvestmentpartners', 'Craigs Investment Partners', 'corp', r'Craigs Investment|\bCraigs\b'),
    ('pubcharity', 'Pub Charity (gaming machines)', 'corp', r'Pub ?Charity'),
    ('lionfoundation', 'Lion Foundation (gaming machines)', 'corp', r'Lion Foundation'),
    ('nzct', 'NZCT (gaming machines)', 'corp', r'\bNZCT\b|New Zealand Community Trust'),
    ('skycity', 'SkyCity Entertainment', 'corp', r'Sky ?City'),
    ('foundationnorth', 'Foundation North', 'found', r'Foundation North'),
    ('stouttrust', 'Stout Trust', 'family', r'Stout Trust'),
    ('quartzreef', 'Quartz Reef', 'corp', r'Quartz Reef'),
    ('todd', 'Todd family (Todd Corporation)', 'family', r'Todd Corporation|Todd Energy|Todd Foundation|Todd family'),
    ('fletcher', 'Fletcher (Fletcher Building, Fletcher Trust)', 'corp', r'Fletcher Building|Fletcher Trust|Fletcher Challenge|Fletcher Construction'),
    ('gibbs', 'Alan and Jenny Gibbs', 'family', r'Jenny Gibbs|Alan Gibbs|Gibbs Farm'),
    ('sparknz', 'Spark New Zealand', 'corp', r'Spark (?:New Zealand|NZ|Foundation)|\bSpark\b(?= (?:sponsor|is|was))'),
    ('asb', 'ASB Bank', 'corp', r'\bASB\b'),
    ('bnz', 'Bank of New Zealand', 'corp', r'Bank of New Zealand|\bBNZ\b'),
    ('tsbnz', 'TSB and the TSB Community Trust', 'corp', r'TSB Community|TSB Bank|\bTSB\b(?= (?:Trust|Foundation))'),
    ('simpsongrierson', 'Simpson Grierson (law firm)', 'corp', r'Simpson Grierson'),
    ('steeltube', 'Steel & Tube', 'corp', r'Steel & Tube'),
    ('dulux', 'Dulux (Nippon Paint)', 'corp', r'Dulux'),
    ('methanex', 'Methanex', 'corp', r'Methanex'),
    # Latin America and the Caribbean beyond batch 5 (user, 17 Nov 2026: "add latin american"): the banks, the media and
    # tobacco families, and the companies on the region's sponsor lists. State companies that act as a ministry's arm
    # (PDVSA's art centre, NGC, EPM, Sabesp) and central-bank foundations are left out as public money.
    ('nubank', 'Nubank', 'corp', r'Nubank'),
    ('b3', 'B3 (the São Paulo stock exchange)', 'corp', r'\bB3\b'),
    ('cloudwalk', 'CloudWalk (InfinitePay)', 'corp', r'InfinitePay|CloudWalk'),
    ('grupoultra', 'Ultra (Ultrapar)', 'corp', r'Ultrapar|Grupo Ultra|\bUltra\b(?=,| is| sponsor)'),
    ('motiva', 'Motiva (formerly CCR)', 'corp', r'\bMotiva\b'),
    ('robertomarinho', 'Marinho family (Globo, Fundação Roberto Marinho)', 'family', r'Roberto Marinho|Grupo Globo|Marinho family'),
    ('credicorp', 'Credicorp (Romero family)', 'corp', r'Credicorp|Banco de Crédito del Perú|\bBCP\b'),
    ('bancopopular', 'Popular, Inc. (Banco Popular)', 'corp', r'Banco Popular(?! Español)|Popular, Inc'),
    ('pumaenergy', 'Puma Energy (Trafigura)', 'corp', r'Puma Energy|Trafigura'),
    ('newfortress', 'New Fortress Energy (Genera PR)', 'corp', r'New Fortress|Genera PR'),
    ('ferrerangel', 'Ferré-Rangel family (El Nuevo Día)', 'family', r'Ferr[ée]-Rangel|Ferré family|Luis A\. Ferré'),
    ('fonalledas', 'Fonalledas family (Empresas Fonalledas)', 'family', r'Fonalledas'),
    ('angelramos', 'Fundación Ángel Ramos', 'family', r'[ÁA]ngel Ramos'),
    ('harphelu', 'Alfredo Harp Helú', 'family', r'Harp Hel[úu]'),
    ('cuervo', 'José Cuervo (Beckmann family)', 'family', r'Jos[ée] Cuervo|Tequila 1800|Becle|Beckmann'),
    ('interceramic', 'Interceramic', 'corp', r'Interceramic'),
    ('paiz', 'Paiz family (Fundación Paiz)', 'family', r'\bPaiz\b'),
    ('patino', 'Patiño family and foundations', 'family', r'Pati[ñn]o (?:foundation|Foundation|family)|Simón I\. Patiño|Fundación Patiño|Patiño foundations'),
    ('leonjimenes', 'León Jimenes family (Grupo León Jimenes, tobacco)', 'family', r'Le[óo]n Jimenes'),
    ('ortizgurdian', 'Ortiz Gurdián family (Banpro, Promerica)', 'family', r'Ortiz Gurdi[áa]n|Ortiz Mayorga|Banpro|Promerica'),
    ('mendozafamily', 'Mendoza family (Fundación Eugenio Mendoza)', 'family', r'Fundación Sala Mendoza|Eugenio Mendoza|Mendoza (?:industrial )?family'),
    ('espinosayglesias', 'Espinosa Yglesias family (Fundación Amparo)', 'family', r'Espinosa Yglesias|Fundación Amparo'),
    ('gracekennedy', 'GraceKennedy', 'corp', r'Grace ?Kennedy'),
    ('digicel', 'Digicel (Denis O\'Brien)', 'corp', r'Digicel'),
    ('massy', 'Massy Group', 'corp', r'\bMassy\b'),
    ('ansamcal', 'ANSA McAL', 'corp', r'ANSA McAL'),
    ('naturgy', 'Naturgy', 'corp', r'Naturgy|Gas Natural Fenosa'),
    ('yarur', 'Yarur family (BCI)', 'family', r'Yarur'),
    ('megacable', 'Megacable', 'corp', r'Megacable'),
    ('bago', 'Laboratorios Bagó', 'corp', r'Bag[óo]\b'),
    ('grupohabita', 'Grupo Habita', 'corp', r'Grupo Habita'),
    ('aes', 'AES Corporation', 'corp', r'\bAES\b'),
]

# Head offices for the funders assets/hq.json has no office for. City-level, as hq.json is: the publicly listed head office,
# or for a family the company its money came from. Influence mode draws each funder here instead of the spaces.
HQ_EXTRA = {
    'sacklerfamily': {'n': 'Purdue Pharma (Sackler family)', 'c': 'Stamford', 'co': 'United States', 'lat': 41.0534, 'lon': -73.5387},
    'vale': {'n': 'Vale', 'c': 'Rio de Janeiro', 'co': 'Brazil', 'lat': -22.9068, 'lon': -43.1729},
    'jti': {'n': 'Japan Tobacco International', 'c': 'Geneva', 'co': 'Switzerland', 'lat': 46.2044, 'lon': 6.1432},
    'eni': {'n': 'Eni', 'c': 'Rome', 'co': 'Italy', 'lat': 41.9028, 'lon': 12.4964},
    'equinor': {'n': 'Equinor', 'c': 'Stavanger', 'co': 'Norway', 'lat': 58.9700, 'lon': 5.7331},
    'riotinto': {'n': 'Rio Tinto', 'c': 'London', 'co': 'United Kingdom', 'lat': 51.5074, 'lon': -0.1278},
    'philipmorris': {'n': 'Altria', 'c': 'Richmond, Virginia', 'co': 'United States', 'lat': 37.5407, 'lon': -77.4360},
    # Private money (user, 17 Nov 2026: "add private funders not only corporations, like hedge funds etc"): the firm the
    # fortune came from, at the city of its listed head office.
    'leonblack': {'n': 'Apollo Global Management (Leon Black)', 'c': 'New York', 'co': 'United States', 'lat': 40.7128, 'lon': -74.0060},
    'glenndubin': {'n': 'Highbridge Capital (Glenn Dubin)', 'c': 'New York', 'co': 'United States', 'lat': 40.7128, 'lon': -74.0060},
    'schwarzman': {'n': 'Blackstone (Stephen Schwarzman)', 'c': 'New York', 'co': 'United States', 'lat': 40.7128, 'lon': -74.0060},
    'paulsonfamily': {'n': 'Paulson & Co. (John Paulson)', 'c': 'New York', 'co': 'United States', 'lat': 40.7128, 'lon': -74.0060},
    'kkr': {'n': 'KKR', 'c': 'New York', 'co': 'United States', 'lat': 40.7128, 'lon': -74.0060},
    'kanderses': {'n': 'Kanders & Company (Warren Kanders)', 'c': 'Stamford', 'co': 'United States', 'lat': 41.0534, 'lon': -73.5387},
    'wintoncapitalmanagement': {'n': 'Winton (David Harding)', 'c': 'London', 'co': 'United Kingdom', 'lat': 51.5074, 'lon': -0.1278},
    'romanabramovich': {'n': 'Millhouse (Roman Abramovich)', 'c': 'Moscow', 'co': 'Russia', 'lat': 55.7558, 'lon': 37.6173},
    'vladimirpotanin': {'n': 'Interros (Vladimir Potanin)', 'c': 'Moscow', 'co': 'Russia', 'lat': 55.7558, 'lon': 37.6173},
    'leonidmikhelsonvac': {'n': 'Novatek (Leonid Mikhelson)', 'c': 'Moscow', 'co': 'Russia', 'lat': 55.7558, 'lon': 37.6173},
    'viktorvekselberg': {'n': 'Renova Group (Viktor Vekselberg)', 'c': 'Moscow', 'co': 'Russia', 'lat': 55.7558, 'lon': 37.6173},
    'lauder': {'n': 'Lauder family', 'c': 'New York', 'co': 'United States', 'lat': 40.7128, 'lon': -74.0060},
}

# Offices researched for batches 5 to 8 (17 Nov 2026), kept as data beside the review: data/influence_hq.json, the same
# fields, city level, the listed head office or for a family the company its money came from.
_hq_path = os.path.join(ROOT, 'data', 'influence_hq.json')
if os.path.exists(_hq_path):
    for _k, _v in json.load(open(_hq_path)).items():
        if not _k.startswith('_'):
            HQ_EXTRA.setdefault(_k, _v)

# Kinds of influence, in the order the ledger lists them. Each is a pattern over one sentence that names the funder.
KINDS = [
    ('name',      'Name',               r"\bnam(?:e|ed|es|ing)\b|\bwing\b|\bgallery\b(?= (?:is |was )?named)|\bpavilion\b|\bprize\b|\baward\b|\bcentre\b|\bcenter\b|\bgalleries\b|\broom\b|\bhall\b|\bcourt\b|\bstaircase\b|\bgarden\b|\bschool\b|\bfellowship\b"),
    ('seat',      'Seat',               r"\btrustees?\b|\bboard\b|\bchair(?:man|woman|s|ed)?\b|\bpresident\b|\bpatron\b|\bdirector\b(?! of (?:the )?museum)|\bcouncil member\b|\bcommittee\b"),
    ('programme', 'Programme',          r"\bsponsor(?:s|ed|ing|ship)?\b|\bexhibitions?\b|\bshows?\b|\bseason\b|\bprogramme\b|\bprogram\b|\bfestival\b|\bcommission(?:s|ed)?\b|\bpartner(?:ship)?\b|\btour\b|\bresidenc"),
    ('silence',   'Silence',            r"\bcensor|\bcancel+(?:ed|ation)\b|\bwithdr[ae]w|\bpulled\b|\bremoved (?:a |the )?(?:work|artwork|piece)|\bself-censor|\bgag|\bnon-disclosure|\bconfidential(?:ity)?\b|\bwithh[eo]ld|\brefused to (?:disclose|release|name)"),
    ('access',    'Access',             r"\bgalas?\b|\bcorporate (?:member|membership|partner|event|hire|entertain)|\bprivate view|\bvenue hire|\breceptions?\b|\bdinners?\b|\bhospitality\b|\bentertain"),
    ('licence',   'Licence to operate', r"\blobb|\bpermits?\b|\blicen[cs]e to operate\b|\bsocial licen|\bgreenwash|\bartwash|\bwhitewash|\breputation|\blegitimacy\b|\bimage\b|\bdrilling\b|\bconcession"),
    ('tax',       'Tax',                r"\btax\b|\btaxes\b|\bRouanet\b|\bdeduct"),
    ('building',  'Building',           r"\bmasterplan\b|\brefurbish|\brenovat|\bconstruction\b|\bcapital (?:campaign|project|gift|donor)|\bendow|\bnew (?:wing|building|campus)\b|\bbuilt\b"),
    # Set by the review only: a tie the records state, with nothing said about what came with the money.
    ('money',     'Money only',         r"(?!x)x"),
]
# What happened to the tie. Not influence bought, but whether the funder kept it.
ENDED = r"\bdropp(?:ed|ing)\b|\bended\b|\bend(?:s|ing)? (?:its|the) (?:sponsor|partner|deal|relationship)|\bcut ties\b|\bsever|\bcame off\b|\btaken down\b|\bremov(?:ed|al) (?:of )?(?:the |its )?(?:\w+ )?name|\bname (?:came|was taken|was removed)|\bwill not renew|\bnot renew|\bstepped down\b|\bresigned\b|\breturn(?:ed)? (?:the )?(?:gift|money|donation)|\brefus(?:ed|e) (?:further |future )?(?:gifts|money|donations|funding)"
PROTEST = r"\bprotest|\bcampaign|\bboycott|\bopen letter|\bpetition|\bdie-in|\bactivists?\b|\boccup(?:y|ied|ation)\b"

YEAR = re.compile(r"\b(19[5-9]\d|20[0-2]\d)\b")
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'‘“(])")


def segments(r):
    """Each piece of a record's own text, with the field it is in, its sources and a date if the field carries one."""
    base = [u for u in (r.get('sources') or []) if isinstance(u, str)]
    det = r.get('details') if isinstance(r.get('details'), dict) else {}
    det_src = [s if isinstance(s, str) else (s.get('url') if isinstance(s, dict) else None) for s in (det.get('sources') or [])]
    det_src = [u for u in det_src if u]
    base = base or det_src   # a record with no top-level sources still cites its details' sources
    for f in ('funding', 'watch', 'why_flagged', 'highlight', 'tier_note', 'affiliations_note', 'records_note', 'finances_note', 'other_findings'):
        v = r.get(f)
        if isinstance(v, str) and v.strip():
            yield f, v, base, None
    for f in ('overview', 'funding', 'red_flags', 'press', 'wider_context'):
        v = det.get(f)
        for t in (v if isinstance(v, list) else [v] if isinstance(v, str) else []):
            if isinstance(t, str) and t.strip():
                yield 'details.' + f, t, det_src or base, None
    g = r.get('gossip_data') or {}
    for c in g.get('real_cases', []) or []:
        src = [s.get('url') for s in c.get('sources', []) if isinstance(s, dict) and s.get('url')]
        parts = [c.get('title') or ''] + list(c.get('facts') or []) + [c.get('response') or '', c.get('outcome') or '']
        for t in parts:
            if t:
                yield 'case', t, src or base, c.get('event_date')
    for it in g.get('gossip', []) or []:
        if it.get('status') not in ('confirmed', 'resolved', 'documented'):
            continue   # outside Gossip mode only what is confirmed or resolved (notes/gossip-criteria.md); the same holds here
        src = [u for u in (it.get('urls') or []) if isinstance(u, str)]
        for t in (it.get('headline'), it.get('said'), it.get('outcome')):
            if t:
                yield 'report', t, src or base, it.get('when')
    # What a leaked document shows (WikiLeaks), one entry per document, with the document's own links.
    for w in r.get('wikileaks_records', []) or []:
        if isinstance(w, dict) and w.get('what_shows'):
            yield 'wikileaks', w['what_shows'], w.get('sources') or base, w.get('date')
    for c in r.get('case_notes', []) or []:
        if c.get('text'):
            yield 'case_note', c['text'], c.get('sources') or base, c.get('meta')


def urls(src):
    out = []
    for u in src or []:
        u = u.get('url') if isinstance(u, dict) else u
        if isinstance(u, str) and u.startswith('http') and u not in out:
            out.append(u)
    return out[:6]


def main():
    recs = json.load(open(os.path.join(ROOT, 'institutions.json')))
    fun = [(k, n, kind, re.compile(p)) for k, n, kind, p in FUNDERS]
    kinds = [(k, lab, re.compile(p, re.I)) for k, lab, p in KINDS]
    ended, protest = re.compile(ENDED, re.I), re.compile(PROTEST, re.I)
    out, seen = [], set()
    for r in recs:
        for field, text, src, date in segments(r):
            for s in SENT.split(text):
                s = s.strip()
                for fk, fname, fkind, fre in fun:
                    if not fre.search(s):
                        continue
                    ks = [k for k, _, kre in kinds if kre.search(s)]
                    key = (r['id'], fk, s)
                    if key in seen:
                        continue
                    seen.add(key)
                    y = YEAR.findall(s)
                    out.append({
                        'cid': hashlib.sha1(f"{r['id']}|{fk}|{s}".encode()).hexdigest()[:10],
                        'funder': fk, 'funder_name': fname, 'funder_kind': fkind,
                        'space': r['id'], 'space_name': r['name'], 'city': r.get('city', ''),
                        'field': field, 'text': s, 'kinds': ks,
                        'ended': bool(ended.search(s)), 'protest': bool(protest.search(s)),
                        'date': (str(date) if date else (y[0] if y else '')),
                        'sources': urls(src),
                    })
    out.sort(key=lambda c: (c['funder'], c['space'], c['field']))
    json.dump(out, open(os.path.join(ROOT, 'data', 'influence_candidates.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'{len(out)} candidate sentences')
    build_layer(out)


def build_layer(cands):
    """assets/influence.json from the candidates the review keeps, grouped by funder."""
    path = os.path.join(ROOT, 'data', 'influence_review.json')
    review = json.load(open(path)) if os.path.exists(path) else {}
    byc = {c['cid']: c for c in cands}
    missing = [cid for cid in review if cid not in byc and not cid.startswith('_')]
    if missing:
        print(f'warning: {len(missing)} reviewed candidates no longer in the records: {missing[:5]}')
    names = {k: (n, kind) for k, n, kind, _ in FUNDERS}
    offices = json.load(open(os.path.join(ROOT, 'assets', 'hq.json')))['org']
    funders = {}
    for cid, v in review.items():
        if cid.startswith('_') or cid not in byc or v.get('drop'):
            continue
        c = byc[cid]
        n, kind = names[c['funder']]
        if c['funder'] not in funders:
            o = offices.get(c['funder']) or HQ_EXTRA.get(c['funder'])
            hq = {k: o[k] for k in ('n', 'c', 'co', 'lat', 'lon', 'a') if o and k in o} if o else None
            funders[c['funder']] = {'key': c['funder'], 'name': n, 'kind': kind, 'hq': hq, 'ties': []}
        f = funders[c['funder']]
        f['ties'].append({
            'cid': cid, 'space': c['space'], 'space_name': c['space_name'], 'city': c['city'],
            # Only what the review states: the keyword flags of a candidate are a reading aid, not a finding.
            'kinds': v.get('kinds', []), 'ended': bool(v.get('ended')), 'protest': bool(v.get('protest')),
            'summary': v['summary'], 'quote': c['text'], 'field': c['field'],
            # A page found when checking the entry (not in the record's own list) is cited too: extra_sources in the review.
            'date': v.get('date', c['date']), 'sources': c['sources'] + [u for u in v.get('extra_sources', []) if u not in c['sources']],
            'check': v.get('check', 'record'),
            # Checked against its source pages (17 Nov 2026): the page that bears it out, and for a partly checked entry
            # the detail that page does not give.
            'checked_source': v.get('checked_source'), 'checked_missing': v.get('checked_missing'),
            # What ties a money measure to this space (assets/influence-mode.js shows US lobbying, EU lobbying or political
            # giving only at a space a record links it to): [{measure: 'us' | 'eu' | 'politics', text, source}].
            **({'links': v['links']} if v.get('links') else {}),
        })
    for f in funders.values():
        f['ties'].sort(key=lambda t: (t['space_name'], t['date']))
    # The sender's side (user, 17 Nov 2026: "If the money doesn't go to culture it doesn't disappear so who is at fault?"):
    # what each funder's money is made from and what else it pays for beside culture. Hand-sourced, one source per fact,
    # read on that page; keyed by the same funder keys. A funder with no entry simply has no such rows.
    spath = os.path.join(ROOT, 'data', 'influence_senders.json')
    senders = json.load(open(spath)) if os.path.exists(spath) else {}
    for k, v in senders.items():
        if k.startswith('_') or k not in funders:
            continue
        funders[k]['sender'] = {'made_from': v.get('made_from', ''), 'facts': v.get('facts', []), 'figures': v.get('figures', {})}
    data = {
        'about': 'What each pilot funder is stated to have got for its money, from the atlas records. Built by tools/build_influence.py from data/influence_review.json.',
        'kinds': [{'key': k, 'label': lab} for k, lab, _ in KINDS],
        'funders': sorted(funders.values(), key=lambda f: -len(f['ties'])),
    }
    json.dump(data, open(os.path.join(ROOT, 'assets', 'influence.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print(f"{sum(len(f['ties']) for f in funders.values())} entries for {len(funders)} funders in assets/influence.json")


if __name__ == '__main__':
    main()
