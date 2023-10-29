# via/province_data.py
# Part of timetable_kit
#
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module says which province each VIA station is in.
Generated by station_to_province/province_scrape.py and some text files.
"""

from __future__ import annotations  # for Optional[] typing


def stop_code_to_province(stop_code: str) -> Optional[str]:
    "Given a VIA stop code, return the capitalized two-letter code for the province or state, or None if unknown."
    return _stop_code_to_province.get(stop_code)


_stop_code_to_province = {
    # AB stations
    "CALG": "AB",
    "EDMO": "AB",
    "EDSN": "AB",
    "EVAN": "AB",
    "HINT": "AB",
    "JASP": "AB",
    "VKNG": "AB",
    "WAIN": "AB",
    # BC stations
    "ABBO": "BC",
    "AGAS": "BC",
    "ALZL": "BC",
    "ASHN": "BC",
    "BEND": "BC",
    "BLUE": "BC",
    "BBAR": "BC",
    "BRNL": "BC",
    "CASS": "BC",
    "CEDA": "BC",
    "CHIL": "BC",
    "CLWT": "BC",
    "DOMC": "BC",
    "DORR": "BC",
    "DNST": "BC",
    "ENDA": "BC",
    "FFRA": "BC",
    "GOAT": "BC",
    "HRVY": "BC",
    "HOPE": "BC",
    "HOUS": "BC",
    "HUTT": "BC",
    "KAMN": "BC",
    "KATZ": "BC",
    "KITW": "BC",
    "KWIN": "BC",
    "LWTH": "BC",
    "LOOS": "BC",
    "MCBR": "BC",
    "MCGR": "BC",
    "MSNH": "BC",
    "NHAZ": "BC",
    "NBND": "BC",
    "PACI": "BC",
    "PENN": "BC",
    "PGEO": "BC",
    "PRUP": "BC",
    "SINM": "BC",
    "SMTR": "BC",
    "TELK": "BC",
    "TRRC": "BC",
    "UFRZ": "BC",
    "USKX": "BC",
    "VLMT": "BC",
    "VCVR": "BC",
    "VDRH": "BC",
    "WILR": "BC",
    # MB stations
    "AMRY": "MB",
    "ARNO": "MB",
    "ATKL": "MB",
    "BACK": "MB",
    "BLCH": "MB",
    "BIRD": "MB",
    "BOYD": "MB",
    "BRTL": "MB",
    "BRGR": "MB",
    "BUDD": "MB",
    "BUTT": "MB",
    "BYLO": "MB",
    "CHLB": "MB",
    "CHES": "MB",
    "CHUR": "MB",
    "CORM": "MB",
    "CROM": "MB",
    "DAUP": "MB",
    "DERI": "MB",
    "DIGG": "MB",
    "DUNL": "MB",
    "DYCE": "MB",
    "EARC": "MB",
    "ELMA": "MB",
    "FING": "MB",
    "GLBP": "MB",
    "GILL": "MB",
    "GSTO": "MB",
    "GLNA": "MB",
    "GVIE": "MB",
    "HALC": "MB",
    "HERC": "MB",
    "HOCK": "MB",
    "ILFO": "MB",
    "KLTT": "MB",
    "KETR": "MB",
    "LPRS": "MB",
    "LAMP": "MB",
    "LRIE": "MB",
    "LAWL": "MB",
    "LEVN": "MB",
    "LUKE": "MB",
    "LYDD": "MB",
    "MCCR": "MB",
    "MCLI": "MB",
    "MUNK": "MB",
    "NONS": "MB",
    "OCHR": "MB",
    "ODAY": "MB",
    "ODHI": "MB",
    "OPHR": "MB",
    "OROK": "MB",
    "PATE": "MB",
    "PIKW": "MB",
    "PIPN": "MB",
    "PITS": "MB",
    "PLUM": "MB",
    "PNTN": "MB",
    "PLPX": "MB",
    "RAWE": "MB",
    "RVRS": "MB",
    "RBLN": "MB",
    "SILC": "MB",
    "SIPI": "MB",
    "TPAS": "MB",
    "THIB": "MB",
    "THKP": "MB",
    "THOM": "MB",
    "TIDL": "MB",
    "TREM": "MB",
    "TURN": "MB",
    "WBDN": "MB",
    "WEIR": "MB",
    "WEKU": "MB",
    "WILD": "MB",
    "WNPG": "MB",
    "WNTB": "MB",
    "WVHO": "MB",
    "": "MB",
    # NB stations
    "BATH": "NB",
    "CBTN": "NB",
    "CHLO": "NB",
    "JACR": "NB",
    "MIRA": "NB",
    "MCTN": "NB",
    "PROC": "NB",
    "RGRV": "NB",
    "SACK": "NB",
    # NS stations
    "AMHS": "NS",
    "HLFX": "NS",
    "SPRJ": "NS",
    "TRUR": "NS",
    # ON stations
    "ALDR": "ON",
    "ALEX": "ON",
    "ALWB": "ON",
    "AMYO": "ON",
    "ARMG": "ON",
    "AUDN": "ON",
    "AZIL": "ON",
    "BLVL": "ON",
    "BENN": "ON",
    "BISC": "ON",
    "BOLK": "ON",
    "BRMP": "ON",
    "BRTF": "ON",
    "BRKV": "ON",
    "CNYK": "ON",
    "CAPR": "ON",
    "CARA": "ON",
    "CART": "ON",
    "CSLM": "ON",
    "CHAP": "ON",
    "CHAT": "ON",
    "CHEL": "ON",
    "CBRG": "ON",
    "COLL": "ON",
    "COPE": "ON",
    "CWLL": "ON",
    "COTO": "ON",
    "DALT": "ON",
    "DEVN": "ON",
    "ELSA": "ON",
    "ESHR": "ON",
    "FALL": "ON",
    "FARL": "ON",
    "FELX": "ON",
    "FERL": "ON",
    "FLTL": "ON",
    "FOLE": "ON",
    "FRKS": "ON",
    "FRNZ": "ON",
    "GANA": "ON",
    "GEOR": "ON",
    "GIRD": "ON",
    "GLNC": "ON",
    "GOGA": "ON",
    "GRIM": "ON",
    "GUEL": "ON",
    "GUIL": "ON",
    "HLSP": "ON",
    "HNPN": "ON",
    "INGR": "ON",
    "KGON": "ON",
    "KINO": "ON",
    "KITC": "ON",
    "KORM": "ON",
    "LAFO": "ON",
    "LARC": "ON",
    "LEVA": "ON",
    "LOCH": "ON",
    "LNDN": "ON",
    "LLAC": "ON",
    "MLCH": "ON",
    "MALT": "ON",
    "MCKC": "ON",
    "MTGM": "ON",
    "MNKI": "ON",
    "MSBI": "ON",
    "MUDR": "ON",
    "MUSK": "ON",
    "NAKI": "ON",
    "NAPN": "ON",
    "NEME": "ON",
    "NIAG": "ON",
    "NICH": "ON",
    "OAKV": "ON",
    "OBAX": "ON",
    "OBRI": "ON",
    "OSHA": "ON",
    "OTTW": "ON",
    "OTTM": "ON",
    "PARS": "ON",
    "SPAR": "ON",
    "POGA": "ON",
    "PHOP": "ON",
    "RAMS": "ON",
    "RLRX": "ON",
    "RDDT": "ON",
    "RCLK": "ON",
    "RCHN": "ON",
    "RBRT": "ON",
    "RUEL": "ON",
    "SARN": "ON",
    "SAVL": "ON",
    "SHEA": "ON",
    "SNKR": "ON",
    "SLKT": "ON",
    "SMTF": "ON",
    "SCAT": "ON",
    "SMYS": "ON",
    "STRL": "ON",
    "STRF": "ON",
    "STRR": "ON",
    "SUDB": "ON",
    "SUDJ": "ON",
    "SULT": "ON",
    "SWAN": "ON",
    "TRTO": "ON",
    "TRNJ": "ON",
    "WSHG": "ON",
    "WSTR": "ON",
    "WHTR": "ON",
    "WDON": "ON",
    "WOMR": "ON",
    "WOOD": "ON",
    "WYOM": "ON",
    # QC stations
    "ASIC": "QC",
    "AMQU": "QC",
    "ANJO": "QC",
    "BARA": "QC",
    "BIMA": "QC",
    "BGQU": "QC",
    "BVNT": "QC",
    "BRMT": "QC",
    "BRQU": "QC",
    "CANN": "QC",
    "CAPL": "QC",
    "CARI": "QC",
    "CARL": "QC",
    "CASY": "QC",
    "CAUS": "QC",
    "CHBD": "QC",
    "CHND": "QC",
    "CHRT": "QC",
    "CHNY": "QC",
    "CHER": "QC",
    "CLOV": "QC",
    "BDNC": "QC",
    "BLGC": "QC",
    "GRGC": "QC",
    "IRQC": "QC",
    "JACC": "QC",
    "KPTC": "QC",
    "LIZO": "QC",
    "MWWC": "QC",
    "NCLC": "QC",
    "RTAC": "QC",
    "SSCC": "QC",
    "SMMC": "QC",
    "TRTC": "QC",
    "VMLC": "QC",
    "WGWC": "QC",
    "CBAT": "QC",
    "COQU": "QC",
    "COTO": "QC",
    "CRSM": "QC",
    "DRLL": "QC",
    "DESS": "QC",
    "DIXX": "QC",
    "DORV": "QC",
    "DRMV": "QC",
    "DUPL": "QC",
    "FALR": "QC",
    "FERG": "QC",
    "FITZ": "QC",
    "FORS": "QC",
    "GAGN": "QC",
    "GARN": "QC",
    "GASP": "QC",
    "GDRV": "QC",
    "GMRE": "QC",
    "GRNG": "QC",
    "HEBV": "QC",
    "HERV": "QC",
    "HIBB": "QC",
    "HRDL": "QC",
    "JOLI": "QC",
    "JONQ": "QC",
    "KISK": "QC",
    "KOND": "QC",
    "LPOC": "QC",
    "LTUQ": "QC",
    "LBOU": "QC",
    "LDAR": "QC",
    "LDES": "QC",
    "LEDW": "QC",
    "LMAL": "QC",
    "PRLL": "QC",
    "LNGL": "QC",
    "LASS": "QC",
    "LGAR": "QC",
    "MJBG": "QC",
    "MTPD": "QC",
    "MCCA": "QC",
    "MCTC": "QC",
    "MEGI": "QC",
    "MIQK": "QC",
    "MNET": "QC",
    "MJLI": "QC",
    "MMGY": "QC",
    "MTRL": "QC",
    "NCAR": "QC",
    "NRCH": "QC",
    "NOUV": "QC",
    "OSKL": "QC",
    "PARE": "QC",
    "PERC": "QC",
    "PATX": "QC",
    "PBDT": "QC",
    "PDAN": "QC",
    "PRSS": "QC",
    "QBEC": "QC",
    "RAPB": "QC",
    "RMSK": "QC",
    "OSKR": "QC",
    "RAPX": "QC",
    "RDLX": "QC",
    "ROUS": "QC",
    "SFOY": "QC",
    "SHPN": "QC",
    "SHYA": "QC",
    "SJUS": "QC",
    "SLAM": "QC",
    "SMRB": "QC",
    "SPAU": "QC",
    "STIT": "QC",
    "SANF": "QC",
    "SANM": "QC",
    "SAUV": "QC",
    "SAYA": "QC",
    "SENN": "QC",
    "SHWN": "QC",
    "SIGN": "QC",
    "STAD": "QC",
    "STRN": "QC",
    "SMQU": "QC",
    "TIMB": "QC",
    "TPIS": "QC",
    "VBRU": "QC",
    "VDRY": "QC",
    "WYMT": "QC",
    "WNDG": "QC",
    # SK stations
    "BIGG": "SK",
    "CANO": "SK",
    "ENDV": "SK",
    "HBAY": "SK",
    "KAMS": "SK",
    "MELV": "SK",
    "MIKA": "SK",
    "RSRV": "SK",
    "SASK": "SK",
    "STGS": "SK",
    "TOGO": "SK",
    "UNIT": "SK",
    "VERE": "SK",
    "WATR": "SK",
    # NY stations
    "NFNY": "NY",
    "BUFX": "NY",
    "BUFF": "NY",
    "ROCH": "NY",
    "SYRA": "NY",
    "ROME": "NY",
    "UTIC": "NY",
    "AMST": "NY",
    "SCHE": "NY",
    "ALBY": "NY",
    "HUDS": "NY",
    "RHIN": "NY",
    "POUG": "NY",
    "CROT": "NY",
    "YONK": "NY",
    "NEWY": "NY",
}
