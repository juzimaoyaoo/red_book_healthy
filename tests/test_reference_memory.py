import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from health_agent.reference_memory import load_reference_memory
from health_agent.production import ProductionAgent


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'config').mkdir()
        self.entries=[]
        for n in range(50):
            capture={'author':'a','title':str(n),'body':'unverified source statement','scope':'complete body'}
            cp,ch=self.write(str(n)+'-capture.json',capture)
            analysis={'analysis':{'usable_as':'contrast','visual_observation':'observed cover'},
                      'source_identity':{'source_sha256':ch,'images':{}}}
            ap,ah=self.write(str(n)+'-analysis.json',analysis)
            self.entries.append({'id':str(n),'capture':cp,'capture_sha256':ch,'analysis':ap,'analysis_sha256':ah,'images':{}})
        self.freeze()
    def tearDown(self):self.tmp.cleanup()
    def write(self,path,value):
        p=self.root/path;p.write_text(json.dumps(value));return path,hashlib.sha256(p.read_bytes()).hexdigest()
    def freeze(self):
        mp,mh=self.write('manifest.json',{'selected':self.entries,'limits':['editorial observations only']})
        self.write('config/reference-library.json',{'manifest':mp,'sha256':mh})
    def test_reference_can_never_be_official_fact(self):
        sources,identity=load_reference_memory(self.root)
        self.assertEqual(len(sources),100);self.assertEqual(identity['count'],50)
        self.assertTrue(all(s['kind']!='official_fact' and s['medical_evidence'] is False for s in sources))
    def test_stale_source_rejected(self):
        (self.root/'0-capture.json').write_text('{}')
        with self.assertRaises(ValueError):load_reference_memory(self.root)
    def test_relocated_images_keep_original_receipt_and_verify_exact_path(self):
        image=self.root/'cover.png';image.write_bytes(b'fixture image')
        digest=hashlib.sha256(image.read_bytes()).hexdigest()
        original='/original/computer/workspace'
        p=json.loads((self.root/'0-analysis.json').read_text())
        p['source_identity']['images']={original+'/cover.png':digest}
        _,h=self.write('0-analysis.json',p)
        self.entries[0].update(analysis_sha256=h,images={'cover.png':digest});self.freeze()
        config=json.loads((self.root/'config/reference-library.json').read_text())
        config['capture_root']=original;self.write('config/reference-library.json',config)
        sources,_=load_reference_memory(self.root)
        self.assertEqual(sources[1]['image_paths'],[str(image.resolve())])
        # Identical bytes in a different directory must not satisfy the receipt.
        (self.root/'other').mkdir();(self.root/'other/cover.png').write_bytes(image.read_bytes())
        self.entries[0]['images']={'other/cover.png':digest};self.freeze()
        config=json.loads((self.root/'config/reference-library.json').read_text())
        config['capture_root']=original;self.write('config/reference-library.json',config)
        with self.assertRaises(ValueError):load_reference_memory(self.root)
    def test_analysis_must_match_capture(self):
        p=json.loads((self.root/'0-analysis.json').read_text());p['source_identity']['source_sha256']='wrong'
        _,h=self.write('0-analysis.json',p);self.entries[0]['analysis_sha256']=h;self.freeze()
        with self.assertRaises(ValueError):load_reference_memory(self.root)
    def test_excluded_sample_rejected(self):
        p=json.loads((self.root/'0-analysis.json').read_text());p['analysis']['usable_as']='exclude'
        _,h=self.write('0-analysis.json',p);self.entries[0]['analysis_sha256']=h;self.freeze()
        with self.assertRaises(ValueError):load_reference_memory(self.root)
    def test_memory_loaded_into_production_and_read_gated(self):
        sources,identity=load_reference_memory(self.root)
        packet=self.root/'packet.json';packet.write_text('{"sources":[]}')
        class Dummy:usage=[]
        with patch('health_agent.production.load_reference_memory',return_value=(sources,identity)):
            agent=ProductionAgent(self.root/'run',packet,{},Dummy())
        self.assertIn('new50-0',agent.sources)
        c=[{'source_id':'new50-0','quote':'unverified source statement'}]
        with self.assertRaises(ValueError):agent.citations(c)
        agent.read_sources({'ids':['new50-0']});agent.citations(c)
        with self.assertRaises(ValueError):agent.citations(c,official=True)
        self.assertEqual(agent.state['snapshot']['reference_memory']['count'],50)
        with self.assertRaises(ValueError):agent.require_memory_application(['new50-0'],c)
        agent.sources['new50-0']['usable_as']='positive_editorial'
        with self.assertRaises(ValueError):agent.require_memory_application(['new50-0'],c)
        c[0].update({key:'concrete transfer' for key in ['mechanic','title_application','content_application','changed_audience_or_evidence','not_copying']})
        agent.require_memory_application(['new50-0'],c)
        with self.assertRaises(ValueError):agent.require_memory_application(['new50-0'],[])

