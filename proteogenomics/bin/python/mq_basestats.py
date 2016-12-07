#!/usr/bin/env python

import pandas as pd
import sys
import importlib.machinery
import Bio; from Bio import SeqIO
import sequtils
import shutil
import os
from collections import defaultdict
import pickle

loader = importlib.machinery.SourceFileLoader('config', sys.argv[1])
config = loader.load_module()

output = sys.argv[2]

peptides = pd.read_csv(config.mq_txt + 'peptides.txt', sep='\t',engine='python')
peptides = peptides[(peptides['Potential contaminant'] != '+') & (peptides['Reverse'] != '+')]
data = pd.read_csv(output +'/combined.csv')

stats = output +'/stats'
try:
    os.mkdir(stats)
except:
    shutil.rmtree(stats)
    os.mkdir(stats)


def collist(df, col):
    peps = set()
    for pepset in df[col].dropna().tolist():
        for pep in pepset.split('\n'):
            peps.add(pep)
    return peps
    
novel_peptides = collist(data,'_combined.specific.novel.peptides')

strain_all_peptides = defaultdict(set)

for col in data.columns:
    rex = '_all.peptides.strain.'
    if col.startswith(rex):
        strain = col.split(rex)[1]
        peptides = data[col].dropna().tolist()
        for pepset in peptides:
            for pep in pepset.split('\n'):
                strain_all_peptides[strain].add(pep)
        st_peptides = strain_all_peptides[strain]
        st_novel =  st_peptides & novel_peptides

        w = open( stats +'/all.peptides.strain.{}.txt'.format(strain),'w')
        w.write('\n'.join(st_peptides))
        w.close()

        w = open( stats +'/specific.novel.peptides.strain.{}.txt'.format(strain),'w')
        w.write('\n'.join(st_novel))
        w.close()
    
    
    rex = '_specific.peptides.strain.'
    if col.startswith(rex):
        strain = col.split(rex)[1]
        strain_pg = [str(i) for i in list(data[col].dropna().index)] 
        w = open( stats +'/protein.groups.strain.{}.txt'.format(strain),'w')
        w.write('\n'.join(strain_pg))
        w.close()
        
    rex = '_exclusive.peptides.strain.'
    if col.startswith(rex):
        strain = col.split(rex)[1]
        peptides = collist(data, col)

        w = open( stats +'/exclusive.peptides.strain.{}.txt'.format(strain),'w')
        w.write('\n'.join(peptides))
        w.close()
    rex = '_unmapped.peptides.strain.'
    if col.startswith(rex):
        strain = col.split(rex)[1]
        peptides = collist(data, col)

        w = open( stats +'/unmapped.peptides.strain.{}.txt'.format(strain),'w')
        w.write('\n'.join(peptides))
        w.close()

ref = data[data['_reference.entries.mapped'].notnull()]
ref_unmapped = data[~data['_reference.entries.mapped'].notnull()]
taxon = data[data['_taxon.best.matches'].notnull()]
taxon_unmapped = data[~data['_taxon.best.matches'].notnull()]

print(len(ref))
print(len(ref_unmapped))

print(len(taxon))
print(len(taxon_unmapped))
#print(data.columns.tolist())

