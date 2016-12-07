#!/usr/bin/env python

import pickle
import sys
import pandas as pd
from collections import defaultdict
import os
import shutil

outpath = sys.argv[1]
data = pd.read_csv(outpath +'/combined.csv')

id2go = pickle.load( open( outpath +'/fasta/id2go.p', 'rb' ) )
id2kegg = pickle.load( open( outpath +'/fasta/id2kegg.p', 'rb' ) )

try:
    os.mkdir(outpath +'/gsea')
except:
    shutil.rmtree(outpath +'/gsea')
    os.mkdir(outpath +'/gsea')

def keggintersect(val):
    vals = val.split('\n')
    setlist = []
    for val in vals:
        vset = id2kegg[val]
        setlist.append(vset)
    union = set.union(*setlist)
    if len(union) >0:
        return ';'.join(union)

def gointersect(val):
    vals = val.split('\n')
    setlist = []
    for val in vals:
        vset = id2go[val]
        setlist.append(vset)
    union = set.union(*setlist)
    if len(union) > 0:
        return ';'.join(union)

data = data[data['_combined_orf_ids'].notnull()]

data['_go.term.union']   = data['_combined_orf_ids'].apply(gointersect)
data['_kegg.term.union'] = data['_combined_orf_ids'].apply(keggintersect)

go2pg = defaultdict(set)
def go2gene(df):
    go_terms = df['_go.term.union']
    pg = df['Identifier']
    try:
        go_terms = go_terms.split(';')
        for _ in go_terms:
            go2pg[_].add(pg)
    except:
        pass
data.apply(go2gene,axis=1)

kegg2pg = defaultdict(set)
def kegg2gene(df):
    kegg_terms = df['_kegg.term.union']
    pg = df['Identifier']
    try:
        kegg_terms = kegg_terms.split(';')
        for _ in kegg_terms:
            kegg2pg[_].add(pg)
    except:
        pass
data.apply(kegg2gene,axis=1)

go_df = pd.DataFrame()
go_df['GO_ID'] = pd.Series(list(go2pg.keys()))
go_df['GENES'] = pd.Series(list(go2pg.values())).apply( lambda x  : '|'.join(x))
go_df.to_csv(outpath +'/gsea/go2proteingroups.csv')

kegg_df = pd.DataFrame()
kegg_df['KEGG_ID'] = pd.Series(list(kegg2pg.keys()))
kegg_df['KEGG_ID'] = kegg_df['KEGG_ID'].apply(str)
kegg_df['GENES'] = pd.Series(list(kegg2pg.values())).apply( lambda x  : '|'.join(x))
kegg_df.to_csv(outpath +'/gsea/kegg2proteingroups.csv')
