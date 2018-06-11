from node import Node
from entities_generated import *
from interpretation_constants import *


'''
class Coding(Node):
    """We need Coding because Allele is defined in terms of it"""
    def __init__(self,iri=None):
        self.data = {}
        if iri is not None:
            self.data[DMWG_ID_KEY] = iri
        self.data[DMWG_TYPE_KEY] = 'Coding'
    def set_code(self,x):
        self.data['code'] = x
    def get_code(self):
        return self.data['code']
    def set_system(self,x):
        self.data['system'] = x
    def get_system(self):
        return self.data['system']
    def set_display(self,x):
        self.data['display'] = x
    def get_display(self):
        return self.data['display']
'''

#This is not necessarily useful outside of the DMWG Interpretation Library because we are keeping the 
# data in the format expected for the InterpretationEncoder. In particular, rather than having 
# data members, we just shove all the data into the self.data element.
#
# TODO Fix all the type names and stuff.
class Variant(Node):
    def __init__(self,ar_rep):
        self.data={}        
        self.data[DMWG_ID_KEY] = ar_rep[ALLELE_REGISTRY_ID_KEY]
        self.data[DMWG_TYPE_KEY] = 'CanonicalAllele'
        self.data['canonicalAlleleType'] = ar_rep['type']
        #todo: double check this?
        self.data['complexity'] = 'simple'  
        if 'externalRecords' in ar_rep:
            er = ar_rep['externalRecords']
            if 'ClinVarVariations' in er:
                label = None
                if (len(er['ClinVarVariations']) == 1) and \
                    ('ClinVarAlleles' in er) and \
                    ( len(er['ClinVarAlleles']) == 1) :
                    label=er['ClinVarAlleles'][0]['preferredName']
                for cva in er['ClinVarVariations']:
                    self.add_external_identifier('ClinVar', cva['variationId'], label)
            if 'dbSNP' in er:
                for rsid in er['dbSNP']:
                    self.add_external_identifier('dbSNP', rsid['rs'])
        self.data['relatedContextualAllele'] = []
        for ca in ar_rep['genomicAlleles']:
            self.data['relatedContextualAllele'].append( ContextualAllele( ca, ar_rep[ALLELE_REGISTRY_ID_KEY], 'genomic') )
    def add_external_identifier(self,source,value,display=None):
        if 'relatedIdentifier' not in self.data:
            self.data['relatedIdentifier'] = []
        #if source == 'ClinVar':
        #    system = 'http://www.ncbi.nlm.nih.gov/clinvar/variation/'
        #elif source == 'dbSNP':
        #    system = 'http://www.ncbi.nlm.nih.gov/snp/'
        ext_identifier = { "id": "%s:%s" % (source,value)  }
        if display is not None:
            ext_identifier = { "label" : display }
        self.data['relatedIdentifier'].append(ext_identifier)
    def get_allele(self,ref_genome):
        for cxa in self.data['relatedContextualAllele']:
            if cxa.ref_genome == ref_genome:
                return cxa.data['allele']
        return None
    def get_ref_allele(self,ref_genome):
        for cxa in self.data['relatedContextualAllele']:
            if cxa.ref_genome == ref_genome:
                return cxa.data['referenceCoordinate']['refAllele']
        return None

class ContextualAllele(Node):
    def __init__(self,ar_rep,canonical_allele_id, atype):
        self.data = {}
        self.data[DMWG_TYPE_KEY] = 'ContextualAllele'
        self.data['CanonicalAllele'] = canonical_allele_id
        self.data['contextualAlleleType'] = atype
        self.data['allele'] = ar_rep['coordinates'][0]['allele']
        self.data['alleleName'] = []
        seqnames = []
        for hgvs in ar_rep['hgvs']:
            nm = { 'nameType':'hgvs', 'name':hgvs }
            self.data['alleleName'].append(nm)
            seqnames.append( hgvs.split(':')[0] )
        #print '-----------'
        #print ar_rep.keys()
        #print '-----------'
        if 'referenceGenome' in ar_rep:
            self.ref_genome = ar_rep['referenceGenome']
            if (ar_rep['referenceGenome'] == 'GRCh38'):
                self.data['preferred'] = True
        bestname = ''
        for seqname in seqnames:
            if seqname.startswith('NC'):
                bestname = seqname
        ref_sequence = {'reference': ar_rep['referenceSequence'], 'display': bestname }
        start = {'index': ar_rep['coordinates'][0]['start'] }
        end = {'index': ar_rep['coordinates'][0]['end'] }
        ra = ar_rep['coordinates'][0]['referenceAllele']
        ref_coord = {'referenceSequence': ref_sequence, 'start':start, 'end':end, 'refAllele': ra }
        self.data['referenceCoordinate'] = ref_coord

    
